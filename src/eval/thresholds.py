"""Faixas-alvo de métricas por persona.

Os limiares são o contrato do Eval-Driven Development: o reflection loop
reprocessa o texto se a versão sair da faixa.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudienceThresholds:
    flesch_min: float
    flesch_max: float
    densidade_max: float
    permite_jargao_sem_analogia: bool


THRESHOLDS: dict[str, AudienceThresholds] = {
    "iniciante": AudienceThresholds(
        flesch_min=50.0,
        flesch_max=120.0,
        densidade_max=0.02,
        permite_jargao_sem_analogia=False,
    ),
    "intermediario": AudienceThresholds(
        flesch_min=30.0,
        flesch_max=80.0,
        densidade_max=0.06,
        permite_jargao_sem_analogia=True,
    ),
    "avancado": AudienceThresholds(
        flesch_min=0.0,
        flesch_max=55.0,
        densidade_max=0.12,
        permite_jargao_sem_analogia=True,
    ),
}
