"""Coleta automatica de noticias publicas (BCB/CVM) via Scrapling."""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

from scraping.fetch import coletar_url

FONTES = (
    "https://www.bcb.gov.br/noticias",
    "https://www.gov.br/cvm/pt-br/assuntos/noticias",
)

HINTS = (
    "noticia",
    "noticias",
    "comunicado",
    "copom",
    "ata",
    "fato-relevante",
    "release",
)


def _pagina(url: str, timeout: int = 30):
    from scrapling.fetchers import Fetcher

    if hasattr(Fetcher, "get"):
        return Fetcher.get(url, timeout=timeout)
    return Fetcher.fetch(url, timeout=timeout)


def _links_listagem(url: str, timeout: int = 30) -> list[str]:
    dominio = urlparse(url).netloc
    vistos: set[str] = set()
    saida: list[str] = []
    try:
        page = _pagina(url, timeout=timeout)
    except Exception:
        return []
    hrefs = []
    try:
        hrefs = list(page.css("a::attr(href)"))
    except Exception:
        html = str(getattr(page, "html_content", "") or "")
        hrefs = []
        if html:
            import re

            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    for href in hrefs:
        full = urljoin(url, str(href)).split("#")[0].rstrip("/")
        if not full or full in vistos:
            continue
        parsed = urlparse(full)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc != dominio:
            continue
        baixo = full.lower()
        if any(h in baixo for h in HINTS) and baixo != url.rstrip("/").lower():
            vistos.add(full)
            saida.append(full)
    return saida


def coletar_noticias(max_itens: int = 3, timeout: int = 30) -> tuple[str, list[str]]:
    """Baixa as listagens oficiais e devolve texto concatenado + URLs usadas."""
    urls: list[str] = []
    for fonte in FONTES:
        for link in _links_listagem(fonte, timeout=timeout):
            if link not in urls:
                urls.append(link)
            if len(urls) >= max_itens:
                break
        if len(urls) >= max_itens:
            break

    partes: list[str] = []
    usadas: list[str] = []
    for link in urls[:max_itens]:
        try:
            texto = coletar_url(link, timeout=timeout)
        except Exception:
            texto = ""
        if texto:
            partes.append(f"# Fonte: {link}\n{texto}")
            usadas.append(link)
    return "\n\n".join(partes).strip(), usadas
