"""Dashboard Streamlit: matriz de saídas e telemetria do avaliador."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import config  # noqa: F401  carrega .env
from graph.pipeline import build_graph
from graph.state import AUDIENCIAS, FORMATOS

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "samples" / "copom_sintetico.txt"

ETAPAS = {
    "extract": "Lendo fonte e extraindo ancoras",
    "adapters": "Gerando textos (OpenRouter)",
    "formats": "Montando artigo, carrossel e roteiro",
    "evaluator": "Avaliando (Flesch, jargao, Jev)",
}


def main() -> None:
    st.set_page_config(page_title="Suno Content", layout="wide")
    st.title("Suno Content")
    st.caption(
        "Adaptação de documentos financeiros por persona e formato, "
        "com avaliador híbrido determinístico."
    )

    auto_noticias = st.checkbox("Coletar noticias publicas automaticamente (BCB/CVM)", value=True)
    uploaded = st.file_uploader("PDF ou texto da ata/release", type=["pdf", "txt", "md"])
    url = st.text_input(
        "Ou URL publica (HTML/PDF) — Scrapling + trafilatura",
        placeholder="https://www.bcb.gov.br/...",
        disabled=auto_noticias,
    )
    texto_manual = st.text_area("Ou cole o texto fonte", height=180, disabled=auto_noticias)
    usar_amostra = st.checkbox(
        "Usar amostra sintetica do Copom",
        value=False,
        disabled=auto_noticias,
    )

    if st.button("Rodar pipeline", type="primary"):
        source_text = "" if auto_noticias else texto_manual.strip()
        source_path = None
        source_url = "" if auto_noticias else url.strip()
        if not auto_noticias and uploaded is not None:
            dest = Path("data") / "uploads" / uploaded.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(uploaded.getvalue())
            source_path = str(dest)
            source_text = ""
            source_url = ""
        elif not auto_noticias and source_url:
            source_text = ""
        elif not auto_noticias and usar_amostra and SAMPLE.exists():
            source_text = SAMPLE.read_text(encoding="utf-8")

        if (
            not auto_noticias
            and not source_text
            and not source_path
            and not source_url
        ):
            st.error("Envie um arquivo, cole um texto, use a amostra, uma URL ou a coleta automatica.")
            return

        grafo = build_graph()
        entrada = {
            "source_path": source_path or "",
            "source_text": source_text,
            "source_url": source_url,
            "coletar_noticias": auto_noticias,
            "retries": 0,
        }
        estado: dict = {}
        with st.status("Processando a requisicao...", expanded=True) as status:
            for trecho in grafo.stream(entrada):
                nome = next(iter(trecho))
                estado.update(trecho[nome])
                status.write(ETAPAS.get(nome, nome))
            status.update(label="Concluido", state="complete")

        if estado.get("scrape_aviso"):
            st.info(estado["scrape_aviso"])
        if estado.get("noticias_urls"):
            st.write("Noticias coletadas:")
            for item in estado["noticias_urls"]:
                st.write(f"- {item}")
        if not estado.get("source_text"):
            st.error("Nao veio texto da fonte. Tente outra URL ou cole o texto.")
            return

        st.subheader("Âncoras extraídas")
        st.json(estado.get("anchors") or {})

        st.subheader("Matriz de saídas")
        cols = st.columns(len(AUDIENCIAS))
        outputs = estado.get("outputs") or {}
        for col, audiencia in zip(cols, AUDIENCIAS):
            with col:
                st.markdown(f"### {audiencia}")
                formato = st.selectbox(
                    "Formato", FORMATOS, key=f"fmt-{audiencia}"
                )
                st.text_area(
                    "Conteúdo",
                    outputs.get(audiencia, {}).get(formato, ""),
                    height=280,
                    key=f"out-{audiencia}",
                )

        st.subheader("Relatório do avaliador")
        st.json(estado.get("eval_reports") or {})
        if estado.get("falhas_para_reflexao"):
            st.warning("Falhas injetadas no reflection loop:")
            st.write(estado["falhas_para_reflexao"])


if __name__ == "__main__":
    main()
