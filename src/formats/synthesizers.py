"""Sintetizadores de formato: artigo, carrossel e roteiro de até 60s."""

from __future__ import annotations

from graph.state import AUDIENCIAS, FORMATOS, ContentState


def _artigo(texto: str, audiencia: str) -> str:
    return f"# Versão {audiencia}\n\n{texto}\n"


def _carrossel(texto: str, audiencia: str) -> str:
    frases = [s.strip() for s in texto.split(". ") if s.strip()][:5]
    slides = [f"Slide {i}: {frase.rstrip('.')}" for i, frase in enumerate(frases, start=1)]
    if not slides:
        slides = [f"Slide 1: versão {audiencia}"]
    return "\n".join(["Gancho: o que muda agora", *slides, "Conclusão: impacto prático"])


def _roteiro(texto: str, audiencia: str) -> str:
    return (
        f"[0–3s] Gancho visual — {audiencia}\n"
        f"[3–20s] {texto[:220]}\n"
        f"[20–45s] Números-chave da fonte\n"
        f"[45–60s] Fechamento e CTA\n"
    )


def formats_node(state: ContentState) -> dict:
    adaptations = state.get("adaptations") or {}
    outputs: dict[str, dict[str, str]] = {}
    for audiencia in AUDIENCIAS:
        texto = adaptations.get(audiencia, "")
        outputs[audiencia] = {
            "artigo": _artigo(texto, audiencia),
            "carrossel": _carrossel(texto, audiencia),
            "roteiro": _roteiro(texto, audiencia),
        }
    return {"outputs": outputs}


FORMAT_NAMES = FORMATOS
