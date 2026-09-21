"""Extração de âncoras factuais do documento fonte."""

from __future__ import annotations

import re
from pathlib import Path

from graph.state import ContentState
from contracts.models import Anchors


NUMERO = re.compile(
    r"(?<!\w)(\d{1,3}(?:\.\d{3})*(?:,\d+)?%?|\d+(?:,\d+)?%)(?!\w)"
)


def extrair_texto(caminho: str | None, texto: str | None) -> str:
    if texto and texto.strip():
        return texto.strip()
    if not caminho:
        return ""
    path = Path(caminho)
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    return path.read_text(encoding="utf-8").strip()


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
    texto = extrair_texto(state.get("source_path"), state.get("source_text"))
    return {
        "source_text": texto,
        "anchors": extrair_ancoras(texto),
    }
