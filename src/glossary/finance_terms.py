"""Glossario financeiro usado pelo Domain Term Density Score.

Cada termo traz analogias aceitas para o nivel iniciante. Se o termo aparecer
sem analogia nesse nivel, o avaliador marca violacao de jargao.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FinanceTerm:
    canonical: str
    aliases: tuple[str, ...]
    analogias: tuple[str, ...]
    nivel_minimo: str  # iniciante | intermediario | avancado


FINANCE_GLOSSARY: tuple[FinanceTerm, ...] = (
    FinanceTerm(
        canonical="selic",
        aliases=("taxa selic", "selic"),
        analogias=("juros basico do pais", "juros basico do brasil", "taxa basica de juros"),
        nivel_minimo="intermediario",
    ),
    FinanceTerm(
        canonical="ipca",
        aliases=("ipca", "indice de precos ao consumidor amplo"),
        analogias=("inflacao oficial", "custo de vida"),
        nivel_minimo="intermediario",
    ),
    FinanceTerm(
        canonical="cdi",
        aliases=("cdi", "certificado de deposito interbancario"),
        analogias=("rendimento de referencia", "juro do dinheiro entre bancos"),
        nivel_minimo="intermediario",
    ),
    FinanceTerm(
        canonical="forward guidance",
        aliases=("forward guidance", "sinalizacao futura"),
        analogias=("o que o banco central indica que fara com os juros",),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="hiato do produto",
        aliases=("hiato do produto", "output gap"),
        analogias=("economia aquecida ou ociosa demais em relacao ao potencial",),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="curva de juros",
        aliases=("curva de juros", "yield curve"),
        analogias=("preco do dinheiro no tempo", "juros para prazos diferentes"),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="ebitda ajustado",
        aliases=("ebitda ajustado", "ebitda"),
        analogias=("lucro operacional antes de juros, impostos e depreciacao",),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="covenant",
        aliases=("covenant", "covenants"),
        analogias=("clausula de protecao no contrato de divida",),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="taxa terminal",
        aliases=("taxa terminal", "terminal rate"),
        analogias=("patamar final esperado dos juros",),
        nivel_minimo="avancado",
    ),
    FinanceTerm(
        canonical="dividendos",
        aliases=("dividendo", "dividendos"),
        analogias=("parte do lucro distribuida ao acionista",),
        nivel_minimo="intermediario",
    ),
)


def _normaliza(texto: str) -> str:
    return re.sub(r"\s+", " ", texto.casefold()).strip()


def termos_no_texto(texto: str) -> list[FinanceTerm]:
    normalizado = _normaliza(texto)
    encontrados: list[FinanceTerm] = []
    for termo in FINANCE_GLOSSARY:
        if any(alias in normalizado for alias in termo.aliases):
            encontrados.append(termo)
    return encontrados


def analogia_presente(texto: str, termo: FinanceTerm) -> bool:
    normalizado = _normaliza(texto)
    return any(analogia in normalizado for analogia in termo.analogias)
