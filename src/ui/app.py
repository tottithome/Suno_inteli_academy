"""Dashboard Streamlit: matriz de saídas e telemetria do avaliador."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import config  # noqa: F401  carrega .env
from graph.pipeline import build_graph
from graph.state import AUDIENCIAS, FORMATOS

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "samples" / "copom_sintetico.txt"


def main() -> None:
    st.set_page_config(page_title="Suno Content", layout="wide")
    st.title("Suno Content")
    st.caption(
        "Adaptação de documentos financeiros por persona e formato, "
        "com avaliador híbrido determinístico."
    )

    uploaded = st.file_uploader("PDF ou texto da ata/release", type=["pdf", "txt", "md"])
    url = st.text_input(
        "Ou URL publica (HTML/PDF) — Scrapling + trafilatura",
        placeholder="https://www.bcb.gov.br/...",
    )
    texto_manual = st.text_area("Ou cole o texto fonte", height=180)
    usar_amostra = st.checkbox(
        "Usar amostra sintetica do Copom",
        value=not texto_manual and not url,
    )

    if st.button("Rodar pipeline", type="primary"):
        source_text = texto_manual.strip()
        source_path = None
        source_url = url.strip()
        if uploaded is not None:
            dest = Path("data") / "uploads" / uploaded.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(uploaded.getvalue())
            source_path = str(dest)
            source_text = ""
            source_url = ""
        elif source_url:
            source_text = ""
        elif usar_amostra and SAMPLE.exists():
            source_text = SAMPLE.read_text(encoding="utf-8")

        if not source_text and not source_path and not source_url:
            st.error("Envie um arquivo, cole um texto, use a amostra ou uma URL.")
            return

        grafo = build_graph()
        estado = grafo.invoke(
            {
                "source_path": source_path or "",
                "source_text": source_text,
                "source_url": source_url,
                "retries": 0,
            }
        )
        if estado.get("scrape_aviso"):
            st.info(estado["scrape_aviso"])
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
