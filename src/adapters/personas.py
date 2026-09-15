"""Adapters de audiência.

Nesta fase o nó produz rascunhos determinísticos (sem LLM) para o grafo
e a suíte de eval já rodarem. O adapter com LLM entra no próximo ciclo.
"""

from __future__ import annotations

from graph.state import AUDIENCIAS, ContentState


def _rascunho(audiencia: str, fonte: str, falhas: list[str]) -> str:
    trecho = " ".join(fonte.split()[:80])
    feedback = ""
    if falhas:
        feedback = " Ajuste pedido pelo avaliador: " + "; ".join(falhas[:3]) + "."

    if audiencia == "iniciante":
        return (
            "O Banco Central mudou os juros básicos do país. "
            "Isso altera o custo do crédito no dia a dia, como financiamento "
            "e rendimento da poupança. "
            f"Trecho da fonte: {trecho}"
            f"{feedback}"
        )
    if audiencia == "intermediario":
        return (
            "A decisão de política monetária altera a Selic e o CDI, com efeito "
            "sobre alocação em renda fixa e inflação medida pelo IPCA. "
            f"Fonte: {trecho}"
            f"{feedback}"
        )
    return (
        "O comunicado preserva o jargão institucional: forward guidance, "
        "hiato do produto e a curva de juros informam a taxa terminal. "
        "O EBITDA ajustado e covenants permanecem no recorte analítico. "
        f"Fonte: {trecho}"
        f"{feedback}"
    )


def adapters_node(state: ContentState) -> dict:
    fonte = state.get("source_text") or ""
    falhas = state.get("falhas_para_reflexao") or []
    adaptations = {
        audiencia: _rascunho(audiencia, fonte, falhas) for audiencia in AUDIENCIAS
    }
    return {"adaptations": adaptations}
