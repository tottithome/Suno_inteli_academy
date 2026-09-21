"""Extração de âncoras factuais do documento fonte."""

from __future__ import annotations

import re
from pathlib import Path

from contracts.models import Anchors
from graph.state import ContentState

NUMERO = re.compile(
    r"(?<!\w)(\d{1,3}(?:\.\d{3})*(?:,\d+)?%?|\d+(?:,\d+)?%)(?!\w)"
)


def extrair_texto(
    caminho: str | None,
    texto: str | None,
    url: str | None = None,
    auto_noticias: bool = False,
) -> tuple[str, str]:
    if texto and texto.strip():
        return texto.strip(), ""
    if auto_noticias:
        from scraping.news import coletar_noticias

        coletado, urls = coletar_noticias()
        aviso = "noticias automaticas: " + (", ".join(urls) if urls else "nenhuma URL")
        return coletado, aviso
    if url and url.strip():
        from scraping.fetch import coletar_url

        coletado = coletar_url(url.strip())
        if not coletado:
            return "", f"Scrapling/trafilatura nao trouxe texto de {url}"
        return coletado, f"coletado via Scrapling: {url}"
    if not caminho:
        return "", ""
    path = Path(caminho)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        extraido = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        return extraido, ""
    return path.read_text(encoding="utf-8").strip(), ""


def extrair_ancoras(texto: str) -> dict:
    numeros = NUMERO.findall(texto)
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+", texto) if f.strip()]
    return Anchors(
        numeros_chave=numeros[:40],
        frases_ancora=frases[:12],
        n_caracteres=len(texto),
        n_frases=len(frases),
    ).model_dump()


def extractor_node(state: ContentState) -> dict:
    texto, aviso = extrair_texto(
        state.get("source_path"),
        state.get("source_text"),
        state.get("source_url"),
        bool(state.get("coletar_noticias")),
    )
    urls: list[str] = []
    if aviso.startswith("noticias automaticas:") and "http" in aviso:
        urls = [p.strip() for p in aviso.split(":", 1)[1].split(",") if p.strip().startswith("http")]
    return {
        "source_text": texto,
        "scrape_aviso": aviso,
        "noticias_urls": urls,
        "anchors": extrair_ancoras(texto),
    }
