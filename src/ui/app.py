"""Dashboard Streamlit: carrossel de noticias e matriz persistente."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

import config  # noqa: F401  carrega .env
from graph.pipeline import build_graph
from graph.state import AUDIENCIAS, FORMATOS
from scraping.news import listar_noticias

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "samples" / "copom_sintetico.txt"

ETAPAS = {
    "extract": "Lendo fonte e extraindo ancoras",
    "adapters": "Gerando textos (OpenRouter)",
    "formats": "Montando artigo, carrossel e roteiro",
    "evaluator": "Avaliando (Flesch, jargao, Jev)",
}


def _init_state() -> None:
    st.session_state.setdefault("noticias", [])
    st.session_state.setdefault("noticia_idx", 0)
    st.session_state.setdefault("resultado", None)


def _rodar_pipeline(entrada: dict) -> None:
    grafo = build_graph()
    estado: dict = {}
    with st.status("Processando a requisicao...", expanded=True) as status:
        for trecho in grafo.stream(entrada):
            nome = next(iter(trecho))
            estado.update(trecho[nome])
            status.write(ETAPAS.get(nome, nome))
        status.update(label="Concluido", state="complete")
    st.session_state.resultado = estado


def _mostrar_resultado(estado: dict) -> None:
    if estado.get("adapter_aviso"):
        st.warning(estado["adapter_aviso"])
    if estado.get("scrape_aviso"):
        st.info(estado["scrape_aviso"])
    if not estado.get("source_text"):
        st.error("Nao veio texto da fonte.")
        return

    st.subheader("Ancoras extraidas")
    st.json(estado.get("anchors") or {})

    st.subheader("Matriz de saidas")
    cols = st.columns(len(AUDIENCIAS))
    outputs = estado.get("outputs") or {}
    for col, audiencia in zip(cols, AUDIENCIAS):
        with col:
            st.markdown(f"### {audiencia}")
            formato = st.selectbox("Formato", FORMATOS, key=f"fmt-{audiencia}")
            st.text_area(
                "Conteudo",
                outputs.get(audiencia, {}).get(formato, ""),
                height=280,
                key=f"out-{audiencia}",
            )

    st.subheader("Relatorio do avaliador")
    st.json(estado.get("eval_reports") or {})
    if estado.get("falhas_para_reflexao"):
        st.warning("Falhas injetadas no reflection loop:")
        st.write(estado["falhas_para_reflexao"])


def _carrossel() -> dict | None:
    noticias = st.session_state.noticias
    if not noticias:
        return None
    n = len(noticias)
    idx = min(max(st.session_state.noticia_idx, 0), n - 1)
    st.session_state.noticia_idx = idx
    esquerda, meio, direita = st.columns([1, 6, 1])
    with esquerda:
        if st.button("←", disabled=idx <= 0, key="prev-noticia"):
            st.session_state.noticia_idx = idx - 1
            st.rerun()
    with direita:
        if st.button("→", disabled=idx >= n - 1, key="next-noticia"):
            st.session_state.noticia_idx = idx + 1
            st.rerun()
    item = noticias[idx]
    with meio:
        st.markdown(f"**{item['titulo']}**")
        st.caption(f"{idx + 1} / {n} — {item['url']}")
        st.write(item["resumo"])
    return item


def main() -> None:
    st.set_page_config(page_title="Suno Content", layout="wide")
    _init_state()
    st.title("Suno Content")
    st.caption(
        "Adaptação de documentos financeiros por persona e formato, "
        "com avaliador híbrido determinístico."
    )

    modo = st.radio(
        "Fonte",
        ["Carrossel de noticias (CVM/BCB)", "Arquivo, URL ou texto"],
        horizontal=True,
    )

    if modo.startswith("Carrossel"):
        if st.button("Buscar noticias publicas"):
            with st.status("Coletando noticias...", expanded=True) as status:
                status.write("Scrapling nas listagens da CVM e do BCB")
                itens = listar_noticias()
                st.session_state.noticias = [n.as_dict() for n in itens]
                st.session_state.noticia_idx = 0
                st.session_state.resultado = None
                status.update(
                    label=f"{len(itens)} noticia(s) pronta(s)" if itens else "Nenhuma noticia",
                    state="complete" if itens else "error",
                )
        escolhida = _carrossel()
        if escolhida and st.button("Adaptar esta noticia", type="primary"):
            _rodar_pipeline(
                {
                    "source_path": "",
                    "source_text": escolhida["texto"],
                    "source_url": "",
                    "retries": 0,
                }
            )
    else:
        uploaded = st.file_uploader("PDF ou texto da ata/release", type=["pdf", "txt", "md"])
        url = st.text_input("URL publica (HTML/PDF)", placeholder="https://...")
        texto_manual = st.text_area("Ou cole o texto fonte", height=180)
        usar_amostra = st.checkbox("Usar amostra sintetica do Copom", value=False)
        if st.button("Rodar pipeline", type="primary"):
            source_text = texto_manual.strip()
            source_path = ""
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
            else:
                _rodar_pipeline(
                    {
                        "source_path": source_path,
                        "source_text": source_text,
                        "source_url": source_url,
                        "retries": 0,
                    }
                )

    if st.session_state.resultado:
        _mostrar_resultado(st.session_state.resultado)


if __name__ == "__main__":
    main()
