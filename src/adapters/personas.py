"""Adapters de audiencia: OpenRouter gera; rascunho so se nao houver chave."""

from __future__ import annotations

import json
import time

from config import tem_openrouter
from graph.state import AUDIENCIAS, ContentState

CONTRATO = {
    "iniciante": (
        "Zero jargao sem analogia cotidiana. Foco no impacto no bolso. "
        "Nao so encurte o texto."
    ),
    "intermediario": (
        "Vocabulario de mercado so se o termo aparecer nas ancoras. "
        "Nao invente Selic, CDI, IPCA ou dividendos. Foco em alocacao e tendencia."
    ),
    "avancado": (
        "Tom institucional. Jargao tecnico so se aparecer na fonte. "
        "Nao invente forward guidance, hiato do produto ou EBITDA."
    ),
}

SISTEMA = (
    "Voce e redator financeiro em portugues do Brasil. "
    "Escreva SOMENTE o texto final para o leitor. "
    "Proibido ingles, proibido explicar a tarefa, proibido listar regras, "
    "proibido markdown e proibido inventar numeros."
)

MARCAS_META = (
    "we need to",
    "must use only",
    "must respond",
    "beginner persona",
    "no jargon",
    "everyday analogies",
    "we must",
    "adapted text",
)


def saida_invalida(texto: str) -> bool:
    baixo = texto.casefold()
    return any(marca in baixo for marca in MARCAS_META)


def _rascunho(audiencia: str, fonte: str, falhas: list[str]) -> str:
    trecho = " ".join(fonte.split()[:140])
    feedback = ""
    if falhas:
        feedback = " Ajuste pedido pelo avaliador: " + "; ".join(falhas[:3]) + "."
    abertura = {
        "iniciante": "Em linguagem simples, com impacto no bolso: ",
        "intermediario": "Leitura de mercado (alocacao e tendencia): ",
        "avancado": "Leitura institucional: ",
    }
    return abertura.get(audiencia, "") + trecho + feedback


def _prompt(audiencia: str, fonte: str, anchors: dict, falhas: list[str]) -> tuple[str, str]:
    correcoes = "; ".join(falhas[:8]) or "nenhuma"
    user = (
        f"Persona: {audiencia}\n"
        f"Contrato: {CONTRATO[audiencia]}\n"
        f"Ancoras (so estes fatos): {json.dumps(anchors, ensure_ascii=False)}\n"
        f"Fonte:\n{' '.join(fonte.split()[:500])}\n"
        f"Correcoes do avaliador: {correcoes}\n"
        "Comece ja o texto para o leitor, em portugues. "
        "Termine cada frase. O texto acaba em ponto final."
    )
    return SISTEMA, user


def adaptar(audiencia: str, fonte: str, anchors: dict, falhas: list[str]) -> tuple[str, str]:
    if not tem_openrouter():
        return _rascunho(audiencia, fonte, falhas), "OpenRouter indisponivel; rascunho a partir da fonte"
    try:
        from llm.openrouter import completar

        system, user = _prompt(audiencia, fonte, anchors, falhas)
        texto, modelo = completar(system, user, max_tokens=1800)
        if saida_invalida(texto):
            texto, modelo = completar(
                SISTEMA + " Se voce pensar, pense calado. So imprima o artigo.",
                user,
            )
        aviso = f"ok ({modelo})"
        if saida_invalida(texto):
            aviso += " — recusou raciocinio em ingles"
        return texto, aviso
    except Exception as exc:
        return _rascunho(audiencia, fonte, falhas), f"OpenRouter falhou ({type(exc).__name__})"


def adapters_node(state: ContentState) -> dict:
    fonte = state.get("source_text") or ""
    falhas = state.get("falhas_para_reflexao") or []
    anchors = state.get("anchors") or {}
    adaptations: dict[str, str] = {}
    avisos: list[str] = []
    for i, audiencia in enumerate(AUDIENCIAS):
        if i:
            time.sleep(1.0)
        texto, aviso = adaptar(audiencia, fonte, anchors, falhas)
        if "falhou" in aviso:
            time.sleep(1.5)
            texto, aviso = adaptar(audiencia, fonte, anchors, falhas)
        adaptations[audiencia] = texto
        if aviso:
            avisos.append(f"{audiencia}: {aviso}")
    return {"adaptations": adaptations, "adapter_aviso": " | ".join(avisos)}
