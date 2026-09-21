"""Contrato dos dados: o que o pipeline pode devolver."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Audiencia = Literal["iniciante", "intermediario", "avancado"]
Formato = Literal["artigo", "carrossel", "roteiro"]


class Anchors(BaseModel):
    numeros_chave: list[str] = Field(default_factory=list)
    frases_ancora: list[str] = Field(default_factory=list)
    n_caracteres: int = 0
    n_frases: int = 0


class JevVerdict(BaseModel):
    nivel_aparente: Audiencia | None = None
    nivel_confianca: float | None = None
    grounding_ok: float | None = None
    trivializou: float | None = None
    pulou: bool = False
    motivo_pulo: str | None = None
    falhas: list[str] = Field(default_factory=list)
