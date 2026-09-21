"""Coleta automatica de noticias publicas (BCB/CVM) via Scrapling."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

from scraping.fetch import coletar_url

FONTES = (
    "https://www.gov.br/cvm/pt-br/assuntos/noticias",
    "https://www.bcb.gov.br/noticias",
)

BLOQUEIOS = (
    "/atas-de-comites",
    "/centrais-de-conteudo",
    "/acesso-a-informacao",
    "/servicos",
    "javascript:",
)

LIXO = (
    "seu navegador não pode executar javascript",
    "carregando conteúdo da aba",
    "abrir menu principal",
    "ir para o conteúdo",
    "aguarde.",
)


@dataclass(frozen=True)
class Noticia:
    titulo: str
    url: str
    resumo: str
    texto: str

    def as_dict(self) -> dict:
        return asdict(self)


def url_parece_artigo(url: str) -> bool:
    baixo = url.lower()
    if any(b in baixo for b in BLOQUEIOS):
        return False
    if "detalhenoticia" in baixo:
        return True
    partes = [p for p in urlparse(url).path.rstrip("/").split("/") if p]
    if not partes:
        return False
    ultimo = partes[-1]
    if ultimo.isdigit() and len(ultimo) <= 4:
        return False
    if "noticias" not in baixo and "comunicado" not in baixo and "copom" not in baixo:
        return False
    return "-" in ultimo or len(ultimo) > 24


def texto_parece_artigo(texto: str) -> bool:
    if len(texto) < 350:
        return False
    baixo = texto.casefold()
    return not any(marca in baixo for marca in LIXO)


def _pagina(url: str, timeout: int = 30):
    from scrapling.fetchers import Fetcher

    if hasattr(Fetcher, "get"):
        return Fetcher.get(url, timeout=timeout)
    return Fetcher.fetch(url, timeout=timeout)


def _titulo_de(texto: str, fallback: str) -> str:
    linha = next((ln.strip() for ln in texto.splitlines() if ln.strip()), fallback)
    return linha[:180]


def listar_noticias(max_itens: int = 8, timeout: int = 30) -> list[Noticia]:
    """Lista artigos reais (nao paginas de menu) com titulo e texto."""
    candidatos: list[str] = []
    for fonte in FONTES:
        try:
            page = _pagina(fonte, timeout=timeout)
        except Exception:
            continue
        try:
            hrefs = list(page.css("a::attr(href)"))
        except Exception:
            html = str(getattr(page, "html_content", "") or "")
            hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
        for href in hrefs:
            full = urljoin(fonte, str(href)).split("#")[0].rstrip("/")
            if url_parece_artigo(full) and full not in candidatos:
                candidatos.append(full)

    noticias: list[Noticia] = []
    for link in candidatos:
        if len(noticias) >= max_itens:
            break
        try:
            texto = coletar_url(link, timeout=timeout)
        except Exception:
            continue
        if not texto_parece_artigo(texto):
            continue
        titulo = _titulo_de(texto, link)
        resumo = " ".join(texto.split()[:40])
        noticias.append(Noticia(titulo=titulo, url=link, resumo=resumo, texto=texto))
    return noticias
