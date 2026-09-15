"""Domain Term Density Score e checagem de jargão por persona."""

from __future__ import annotations

from dataclasses import dataclass

from glossary.finance_terms import analogia_presente, termos_no_texto


@dataclass(frozen=True)
class TermDensityScore:
    densidade: float
    termos_encontrados: tuple[str, ...]
    jargao_sem_analogia: tuple[str, ...]
    termos_acima_do_nivel: tuple[str, ...]


_ORDEM = {"iniciante": 0, "intermediario": 1, "avancado": 2}


def densidade_terminologica(texto: str, audiencia: str) -> TermDensityScore:
    palavras = max(len(texto.split()), 1)
    encontrados = termos_no_texto(texto)
    nivel = _ORDEM[audiencia]

    sem_analogia: list[str] = []
    acima: list[str] = []
    for termo in encontrados:
        if _ORDEM[termo.nivel_minimo] > nivel:
            acima.append(termo.canonical)
        if audiencia == "iniciante" and not analogia_presente(texto, termo):
            sem_analogia.append(termo.canonical)

    densidade = len(encontrados) / palavras
    return TermDensityScore(
        densidade=round(densidade, 4),
        termos_encontrados=tuple(t.canonical for t in encontrados),
        jargao_sem_analogia=tuple(sem_analogia),
        termos_acima_do_nivel=tuple(acima),
    )
