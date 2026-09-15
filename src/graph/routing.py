"""Roteamento condicional do reflection loop."""

from __future__ import annotations

from langgraph.graph import END

from graph.state import ContentState


MAX_RETRIES = 2


def route_after_eval(state: ContentState) -> str:
    if state.get("reprocessar") and int(state.get("retries") or 0) < MAX_RETRIES:
        return "adapters"
    return END
