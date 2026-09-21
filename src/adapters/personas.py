"""Adapters de audiencia: OpenRouter gera; rascunho so se nao houver chave."""

from __future__ import annotations

import json

from config import tem_openrouter
from graph.state import AUDIENCIAS, ContentState

CONTRATO = {
    "iniciante": (
        "Zero jargao sem analogia cotidiana. Foco no impacto no bolso. "
        "Nao so encurte o texto."
    ),
    "intermediario": (
        "Pode usar Selic, CDI, IPCA, dividendos. Foco em alocacao e tendencia."
    ),
    "avancado": (
        "Preserve jargao institucional (forward guidance, hiato do produto, "
        "curva de juros, EBITDA ajustado, covenants) com foco analitico."
    ),
}

SISTEMA = (
    "Voce adapta documentos financeiros brasileiros. "
    "Use so fatos das ancoras e do trecho da fonte. Nao invente numeros. "
    "Responda em portugues, so o texto da adaptacao, sem markdown."
)


def _rascunho(audiencia: str, fonte: str, falhas: list[str]) -> str:
    trecho = " ".join(fonte.split()[:80])
    feedback = ""
    if falhas:
        feedback = " Ajuste pedido pelo avaliador: " + "; ".join(falhas[:3]) + "."

    if audiencia == "iniciante":
        return (
            "O Banco Central mudou os juros basicos do pais. "
            "Isso altera o custo do credito no dia a dia, como financiamento "
            "e rendimento da poupanca. "
            f"Trecho da fonte: {trecho}"
            f"{feedback}"
        )
    if audiencia == "intermediario":
        return (
            "A decisao de politica monetaria altera a Selic e o CDI, com efeito "
            "sobre alocacao em renda fixa e inflacao medida pelo IPCA. "
            f"Fonte: {trecho}"
            f"{feedback}"
        )
    return (
        "O comunicado preserva o jargao institucional: forward guidance, "
        "hiato do produto e a curva de juros informam a taxa terminal. "
        "O EBITDA ajustado e covenants permanecem no recorte analitico. "
        f"Fonte: {trecho}"
        f"{feedback}"
    )


def _prompt(audiencia: str, fonte: str, anchors: dict, falhas: list[str]) -> tuple[str, str]:
    user = {
        "persona": audiencia,
        "contrato": CONTRATO[audiencia],
        "ancoras": anchors,
        "fonte": " ".join(fonte.split()[:600]),
        "falhas_do_avaliador": falhas[:8],
    }
    return SISTEMA, json.dumps(user, ensure_ascii=False)


def adaptar(audiencia: str, fonte: str, anchors: dict, falhas: list[str]) -> str:
    if not tem_openrouter():
        return _rascunho(audiencia, fonte, falhas)
    try:
        from llm.openrouter import completar

        system, user = _prompt(audiencia, fonte, anchors, falhas)
        return completar(system, user)
    except Exception:
        return _rascunho(audiencia, fonte, falhas)


def adapters_node(state: ContentState) -> dict:
    fonte = state.get("source_text") or ""
    falhas = state.get("falhas_para_reflexao") or []
    anchors = state.get("anchors") or {}
    adaptations = {
        audiencia: adaptar(audiencia, fonte, anchors, falhas) for audiencia in AUDIENCIAS
    }
    return {"adaptations": adaptations}
