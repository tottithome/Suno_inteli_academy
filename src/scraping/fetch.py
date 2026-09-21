"""Baixa HTML publico com Scrapling e limpa com trafilatura."""

from __future__ import annotations

import io
from urllib.parse import urlparse

import trafilatura


def _html_com_scrapling(url: str, timeout: int = 30) -> str:
    from scrapling.fetchers import Fetcher

    if hasattr(Fetcher, "get"):
        page = Fetcher.get(url, timeout=timeout)
    else:
        page = Fetcher.fetch(url, timeout=timeout)
    html = getattr(page, "html_content", None) or getattr(page, "body", None) or ""
    return str(html)


def _texto_pdf_bytes(dados: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(dados))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def coletar_url(url: str, timeout: int = 30) -> str:
    """Devolve texto limpo de uma URL publica (HTML ou PDF)."""
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL precisa ser http(s)")

    if parsed.path.lower().endswith(".pdf"):
        import urllib.request

        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return _texto_pdf_bytes(resp.read())

    html = _html_com_scrapling(url, timeout=timeout)
    texto = trafilatura.extract(html, url=url, favor_recall=True)
    return (texto or "").strip()
