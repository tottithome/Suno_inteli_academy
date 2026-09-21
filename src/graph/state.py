"""Estado compartilhado do grafo de adaptação (LangGraph)."""

from __future__ import annotations

from typing import Any, TypedDict

AUDIENCIAS = ("iniciante", "intermediario", "avancado")
FORMATOS = ("artigo", "carrossel", "roteiro")


class ContentState(TypedDict, total=False):
    source_path: str
    source_text: str
    source_url: str
    scrape_aviso: str
    anchors: dict[str, Any]
    adaptations: dict[str, str]
    outputs: dict[str, dict[str, str]]
    eval_reports: dict[str, dict]
    retries: int
    reprocessar: bool
    falhas_para_reflexao: list[str]
    coletar_noticias: bool
    noticias_urls: list[str]
