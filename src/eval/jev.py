"""Jev (TypeSafe): decisoes tipadas no avaliador hibrido.

Nao gera texto. Recebe estado + perguntas Noul/Choice/Score e devolve
probabilidades. Sem TYPESAFE_API_KEY o no e pulado, nao quebra o grafo.
"""

from __future__ import annotations

import os
from typing import Any

from contracts.models import Anchors, Audiencia, JevVerdict

NOUL_MIN = 0.55


def montar_estado(
    texto: str,
    audiencia: Audiencia,
    anchors: Anchors | dict[str, Any] | None,
) -> dict[str, Any]:
    ancora = anchors if isinstance(anchors, Anchors) else Anchors.model_validate(anchors or {})
    return {
        "audiencia_alvo": audiencia,
        "texto_gerado": texto,
        "numeros_chave": ancora.numeros_chave,
        "frases_ancora": ancora.frases_ancora,
    }


def montar_perguntas(audiencia: Audiencia) -> dict[str, Any]:
    from typesafe_sdk import Choice, Noul, Score

    return {
        "nivel_aparente": Choice(
            instructions=(
                "Qual nivel de sofisticacao financeira deste texto gerado, "
                "dado audiencia_alvo e o jargao usado?"
            ),
            criteria={
                "iniciante": "Analogias do dia a dia; jargao so se explicado; impacto no bolso.",
                "intermediario": "Selic, CDI, IPCA, dividendos; alocacao e tendencia.",
                "avancado": "Forward guidance, hiato do produto, curva de juros, covenants.",
            },
        ),
        "grounding_ok": Noul(
            instructions=(
                "Os fatos e numeros do texto_gerado aparecem em numeros_chave "
                "ou frases_ancora? Nao conte opiniao ou analogia como fato novo."
            ),
        ),
        "trivializou": Score(
            instructions=(
                f"O texto para a persona {audiencia} so encurtou o original "
                "ou perdeu nuance, em vez de adaptar de verdade?"
            ),
            criteria=[
                "Adaptacao genuina do nivel",
                "Simplificou demais em trechos",
                "So cortou frases / infantilizou",
            ],
        ),
    }


def _falhas_do_veredito(veredito: JevVerdict, audiencia: Audiencia) -> list[str]:
    falhas: list[str] = []
    if (
        veredito.nivel_aparente
        and veredito.nivel_aparente != audiencia
        and (veredito.nivel_confianca or 0) >= NOUL_MIN
    ):
        falhas.append(
            f"Jev: nivel aparente {veredito.nivel_aparente} != alvo {audiencia}"
        )
    if veredito.grounding_ok is not None and veredito.grounding_ok < NOUL_MIN:
        falhas.append(f"Jev: grounding baixo ({veredito.grounding_ok:.2f})")
    if veredito.trivializou is not None and veredito.trivializou >= 1.5:
        falhas.append(f"Jev: trivializacao ({veredito.trivializou:.1f})")
    return falhas


def julgar(
    texto: str,
    audiencia: Audiencia,
    anchors: Anchors | dict[str, Any] | None = None,
) -> JevVerdict:
    if not os.getenv("TYPESAFE_API_KEY", "").strip():
        return JevVerdict(pulou=True, motivo_pulo="TYPESAFE_API_KEY ausente")

    from typesafe_sdk import TypeSafeClient

    modelo = os.getenv("JEV_MODEL", "jev-1.13.0")
    estado = montar_estado(texto, audiencia, anchors)
    perguntas = montar_perguntas(audiencia)
    with TypeSafeClient(model=modelo) as client:
        resposta = client.system_one(state=estado, questions=perguntas)

    nivel = resposta.choices["nivel_aparente"]
    noul = resposta.nouls["grounding_ok"]
    score = resposta.scores["trivializou"]
    base = JevVerdict(
        nivel_aparente=nivel.choice,  # type: ignore[arg-type]
        nivel_confianca=getattr(nivel, "confidence", None),
        grounding_ok=float(noul.noul),
        trivializou=float(score.score),
    )
    return base.model_copy(update={"falhas": _falhas_do_veredito(base, audiencia)})
