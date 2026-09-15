"""Flesch Reading Ease adaptado ao português (Martins, 1996).

ILE = 248.835 − 1.015 × (palavras/frases) − 84.6 × (sílabas/palavras)

Valores mais altos = texto mais fácil. Faixas usadas pelo avaliador híbrido
são definidas em `eval.thresholds`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

VOGAIS = set("aeiouáéíóúâêôãõàü")


@dataclass(frozen=True)
class ReadabilityScore:
    flesch_pt: float
    palavras: int
    frases: int
    silabas: int
    palavras_por_frase: float
    silabas_por_palavra: float


def _conta_silabas(palavra: str) -> int:
    letras = re.sub(r"[^a-záéíóúâêôãõàü]", "", palavra.casefold())
    if not letras:
        return 0
    grupos = 0
    anterior_vogal = False
    for ch in letras:
        vogal = ch in VOGAIS
        if vogal and not anterior_vogal:
            grupos += 1
        anterior_vogal = vogal
    return max(grupos, 1)


def _frases(texto: str) -> list[str]:
    partes = re.split(r"[.!?;:\n]+", texto)
    return [p.strip() for p in partes if p.strip()]


def _palavras(texto: str) -> list[str]:
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+", texto)


def flesch_portugues(texto: str) -> ReadabilityScore:
    frases = _frases(texto)
    palavras = _palavras(texto)
    n_frases = max(len(frases), 1)
    n_palavras = max(len(palavras), 1)
    n_silabas = sum(_conta_silabas(p) for p in palavras) or 1
    asl = n_palavras / n_frases
    asw = n_silabas / n_palavras
    ile = 248.835 - (1.015 * asl) - (84.6 * asw)
    return ReadabilityScore(
        flesch_pt=round(ile, 2),
        palavras=len(palavras),
        frases=len(frases),
        silabas=n_silabas,
        palavras_por_frase=round(asl, 2),
        silabas_por_palavra=round(asw, 2),
    )
