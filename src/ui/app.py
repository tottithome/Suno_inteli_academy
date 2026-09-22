"""Dashboard Streamlit: carrossel de noticias e matriz persistente."""

from __future__ import annotations

import json
import time
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
    "formats": "Gerando carrossel e roteiro (DeepSeek)",
    "evaluator": "Avaliando (Flesch, jargao, Jev)",
}


def _init_state() -> None:
    st.session_state.setdefault("noticias", [])
    st.session_state.setdefault("noticia_idx", 0)
    st.session_state.setdefault("resultado", None)


def _rodar_pipeline(entrada: dict) -> None:
    grafo = build_graph()
    estado: dict = {}
    logs: list[dict] = []
    inicio = time.perf_counter()
    marca = inicio
    with st.status("Processando a requisicao...", expanded=True) as status:
        for trecho in grafo.stream(entrada):
            nome = next(iter(trecho))
            agora = time.perf_counter()
            segundos = round(agora - marca, 1)
            marca = agora
            logs.append({"etapa": nome, "rotulo": ETAPAS.get(nome, nome), "segundos": segundos})
            estado.update(trecho[nome])
            status.write(f"{ETAPAS.get(nome, nome)} — {segundos}s")
        total = round(time.perf_counter() - inicio, 1)
        logs.append({"etapa": "total", "rotulo": "Total", "segundos": total})
        status.update(label=f"Concluido em {total}s", state="complete")
    estado["logs"] = logs
    st.session_state.resultado = estado


def _pacote(estado: dict) -> str:
    linhas = ["# Suno Content — pacote da execucao", ""]
    linhas.append("## Tempos")
    for item in estado.get("logs") or []:
        linhas.append(f"- {item['rotulo']}: {item['segundos']}s")
    if estado.get("adapter_aviso"):
        linhas.extend(["", "## Avisos", estado["adapter_aviso"]])
    linhas.extend(["", "## Ancoras", json.dumps(estado.get("anchors") or {}, ensure_ascii=False, indent=2)])
    outputs = estado.get("outputs") or {}
    for audiencia in AUDIENCIAS:
        linhas.append(f"\n## {audiencia}")
        for formato in FORMATOS:
            linhas.append(f"\n### {formato}\n")
            linhas.append(outputs.get(audiencia, {}).get(formato, ""))
    linhas.extend([
        "",
        "## Avaliador",
        json.dumps(estado.get("eval_reports") or {}, ensure_ascii=False, indent=2),
    ])
    if estado.get("falhas_para_reflexao"):
        linhas.extend(["", "## Falhas do retry", json.dumps(estado["falhas_para_reflexao"], ensure_ascii=False)])
    return "\n".join(linhas).strip() + "\n"


def _slides(texto: str) -> list[str]:
    linhas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    return linhas or [texto]


def _mostrar_formato(formato: str, texto: str) -> None:
    if formato == "carrossel":
        slides = _slides(texto)
        cols = st.columns(min(len(slides), 3) or 1)
        for i, slide in enumerate(slides):
            with cols[i % len(cols)]:
                st.container(border=True).markdown(slide)
        return
    if formato == "roteiro":
        for linha in _slides(texto):
            st.markdown(f"`{linha}`" if linha.startswith("[") else linha)
        return
    st.markdown(texto)


def _mostrar_resultado(estado: dict) -> None:
    aviso = estado.get("adapter_aviso") or ""
    if "falhou" in aviso or "indisponivel" in aviso or "JSON" in aviso or "formato local" in aviso:
        st.warning(aviso)
    elif aviso:
        st.caption(aviso)
    if not estado.get("source_text"):
        st.error("Nao veio texto da fonte.")
        return

    pacote = _pacote(estado)
    tempos = " · ".join(
        f"{item['rotulo']} {item['segundos']}s" for item in (estado.get("logs") or [])
    )
    if tempos:
        st.caption(tempos)
    st.download_button(
        "Baixar pacote (conteudo, juiz e tempos)",
        data=pacote,
        file_name="suno_execucao.txt",
        mime="text/plain",
    )
    with st.expander("Copiar pacote para colar no chat"):
        st.text_area("Pacote", pacote, height=220)

    outputs = estado.get("outputs") or {}
    reports = estado.get("eval_reports") or {}
    abas = st.tabs([nome.capitalize() for nome in AUDIENCIAS])
    for aba, audiencia in zip(abas, AUDIENCIAS):
        with aba:
            rel = reports.get(audiencia) or {}
            passou = "passou" if rel.get("passou") else "reprovou"
            st.caption(
                f"Juiz: {passou} · Flesch {rel.get('flesch_pt', '—')} · "
                f"Jev {((rel.get('jev') or {}).get('nivel_aparente') or '—')}"
            )
            formato = st.radio(
                "Formato",
                FORMATOS,
                horizontal=True,
                key=f"fmt-{audiencia}",
            )
            _mostrar_formato(formato, outputs.get(audiencia, {}).get(formato, ""))

    with st.expander("Ancoras e relatorio completo"):
        st.json(estado.get("anchors") or {})
        st.json(reports)
        if estado.get("falhas_para_reflexao"):
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
