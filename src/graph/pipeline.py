"""Grafo: extract → adapters → formats → evaluator → (retry | END)."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from adapters.personas import adapters_node
from eval.hybrid import avaliar
from eval.jev import julgar
from extract.anchor import extractor_node
from formats.synthesizers import formats_node
from graph.routing import route_after_eval
from graph.state import AUDIENCIAS, ContentState


def evaluator_node(state: ContentState) -> dict:
    adaptations = state.get("adaptations") or {}
    reports = {}
    falhas: list[str] = []
    for audiencia, texto in adaptations.items():
        veredito = julgar(texto, audiencia, state.get("anchors"))
        relatorio = avaliar(texto, audiencia, jev=veredito)
        reports[audiencia] = {
            "passou": relatorio.passou,
            "score": relatorio.score,
            "flesch_pt": relatorio.flesch_pt,
            "densidade": relatorio.densidade,
            "falhas": list(relatorio.falhas),
            "jev": veredito.model_dump(),
        }
        falhas.extend(f"{audiencia}: {f}" for f in relatorio.falhas)

    retries = int(state.get("retries") or 0)
    precisa_retry = bool(falhas)
    return {
        "eval_reports": reports,
        "falhas_para_reflexao": falhas,
        "reprocessar": precisa_retry,
        "retries": retries + 1 if precisa_retry else retries,
    }


def build_graph():
    builder = StateGraph(ContentState)
    builder.add_node("extract", extractor_node)
    builder.add_node("adapters", adapters_node)
    builder.add_node("formats", formats_node)
    builder.add_node("evaluator", evaluator_node)

    builder.add_edge(START, "extract")
    builder.add_edge("extract", "adapters")
    builder.add_edge("adapters", "formats")
    builder.add_edge("formats", "evaluator")
    builder.add_conditional_edges("evaluator", route_after_eval, {"adapters": "adapters", END: END})
    return builder.compile()


# Usado só para deixar o import de AUDIENCIAS disponível a scripts.
AUDIENCES = AUDIENCIAS
