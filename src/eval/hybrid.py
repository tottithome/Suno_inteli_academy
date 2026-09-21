"""Avaliador híbrido: métricas determinísticas + score composto.

O juiz LLM estruturado entra depois; esta camada já rejeita versões que
apenas encurtam o texto ou violam o contrato da persona.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from eval.readability import flesch_portugues
from eval.term_density import densidade_terminologica
from eval.thresholds import THRESHOLDS
from contracts.models import JevVerdict
from adapters.personas import saida_invalida


@dataclass(frozen=True)
class HybridReport:
    audiencia: str
    passou: bool
    score: float
    flesch_pt: float
    densidade: float
    falhas: tuple[str, ...]
    detalhes: dict


def _clip(valor: float, minimo: float, maximo: float) -> float:
    if maximo == minimo:
        return 1.0
    return max(0.0, min(1.0, (valor - minimo) / (maximo - minimo)))


def avaliar(
    texto: str,
    audiencia: str,
    jev: JevVerdict | None = None,
) -> HybridReport:
    limiar = THRESHOLDS[audiencia]
    leitura = flesch_portugues(texto)
    termos = densidade_terminologica(texto, audiencia)
    falhas: list[str] = []

    if leitura.flesch_pt < limiar.flesch_min:
        falhas.append(
            f"legibilidade baixa ({leitura.flesch_pt} < {limiar.flesch_min})"
        )
    if leitura.flesch_pt > limiar.flesch_max:
        falhas.append(
            f"legibilidade alta demais para o nível ({leitura.flesch_pt} > {limiar.flesch_max})"
        )
    if termos.densidade > limiar.densidade_max:
        falhas.append(
            f"densidade de jargão excessiva ({termos.densidade} > {limiar.densidade_max})"
        )
    if not limiar.permite_jargao_sem_analogia and termos.jargao_sem_analogia:
        falhas.append(
            "jargão sem analogia: " + ", ".join(termos.jargao_sem_analogia)
        )
    if termos.termos_acima_do_nivel and audiencia == "iniciante":
        falhas.append(
            "termos acima do nível: " + ", ".join(termos.termos_acima_do_nivel)
        )
    if saida_invalida(texto):
        falhas.append("saida meta/ingles em vez do texto para o leitor")
    if jev and not jev.pulou:
        falhas.extend(jev.falhas)

    # Score 1.0 quando está no centro da faixa de Flesch e sem violações de jargão.
    flesch_score = 1.0 - abs(
        _clip(leitura.flesch_pt, limiar.flesch_min, limiar.flesch_max) - 0.5
    ) * 2
    jargao_score = 1.0 if not falhas else max(0.0, 1.0 - 0.25 * len(falhas))
    score = round(0.6 * max(flesch_score, 0.0) + 0.4 * jargao_score, 3)

    return HybridReport(
        audiencia=audiencia,
        passou=not falhas,
        score=score,
        flesch_pt=leitura.flesch_pt,
        densidade=termos.densidade,
        falhas=tuple(falhas),
        detalhes={
            "readability": asdict(leitura),
            "term_density": asdict(termos),
            "jev": jev.model_dump() if jev else None,
        },
    )
