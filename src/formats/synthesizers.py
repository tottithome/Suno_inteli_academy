"""Sintetizadores de formato: artigo local; carrossel e roteiro via LLM."""

from __future__ import annotations

import json
import time

from config import tem_openrouter
from graph.state import AUDIENCIAS, FORMATOS, ContentState

SISTEMA = (
    "Voce formata conteudo financeiro em portugues do Brasil. "
    "Responda SOMENTE um JSON com as chaves carrossel e roteiro. "
    "Nao invente fatos nem numeros. Sem markdown."
)


def _artigo(texto: str, audiencia: str) -> str:
    return f"# Versao {audiencia}\n\n{texto}\n"


def _carrossel_local(texto: str, audiencia: str) -> str:
    frases = [s.strip() for s in texto.split(". ") if s.strip()][:5]
    slides = [f"Slide {i}: {frase.rstrip('.')}" for i, frase in enumerate(frases, start=1)]
    if not slides:
        slides = [f"Slide 1: versao {audiencia}"]
    return "\n".join(["Gancho: o que muda agora", *slides, "Conclusao: impacto pratico"])


def _roteiro_local(texto: str, audiencia: str) -> str:
    return (
        f"[0-3s] Gancho visual — {audiencia}\n"
        f"[3-20s] {texto[:220]}\n"
        f"[20-45s] Fatos da fonte, sem inventar numero\n"
        f"[45-60s] Fechamento e CTA\n"
    )


def _parse_formatos(bruto: str) -> dict[str, str] | None:
    ini, fim = bruto.find("{"), bruto.rfind("}")
    if ini < 0 or fim <= ini:
        return None
    try:
        dados = json.loads(bruto[ini : fim + 1])
    except json.JSONDecodeError:
        return None
    carrossel = str(dados.get("carrossel") or "").strip()
    roteiro = str(dados.get("roteiro") or "").strip()
    if not carrossel or not roteiro:
        return None
    return {"carrossel": carrossel, "roteiro": roteiro}


def _sintetizar_llm(audiencia: str, artigo: str, anchors: dict) -> dict[str, str] | None:
    from llm.openrouter import completar

    user = (
        f"Persona: {audiencia}\n"
        f"Artigo base:\n{artigo[:2500]}\n"
        f"Ancoras permitidas: {json.dumps(anchors, ensure_ascii=False)}\n"
        "carrossel: 6 linhas no maximo, cada uma 'Slide N: ...', "
        "com gancho no 1, corpo e conclusao no ultimo.\n"
        "roteiro: exatamente 60s, linhas [0-3s], [3-20s], [20-45s], [45-60s], "
        "com gancho visual e fala."
    )
    bruto, _modelo = completar(SISTEMA, user)
    return _parse_formatos(bruto)


def formats_node(state: ContentState) -> dict:
    adaptations = state.get("adaptations") or {}
    anchors = state.get("anchors") or {}
    outputs: dict[str, dict[str, str]] = {}
    avisos: list[str] = []
    usar_llm = tem_openrouter()
    for i, audiencia in enumerate(AUDIENCIAS):
        texto = adaptations.get(audiencia, "")
        artigo = _artigo(texto, audiencia)
        extra = None
        if usar_llm:
            if i:
                time.sleep(0.8)
            try:
                extra = _sintetizar_llm(audiencia, texto, anchors)
            except Exception as exc:
                avisos.append(f"{audiencia}: formato LLM falhou ({type(exc).__name__})")
        if extra:
            outputs[audiencia] = {
                "artigo": artigo,
                "carrossel": extra["carrossel"],
                "roteiro": extra["roteiro"],
            }
        else:
            outputs[audiencia] = {
                "artigo": artigo,
                "carrossel": _carrossel_local(texto, audiencia),
                "roteiro": _roteiro_local(texto, audiencia),
            }
            if usar_llm and not any(audiencia in a for a in avisos):
                avisos.append(f"{audiencia}: formato local (JSON invalido)")
    aviso_atual = state.get("adapter_aviso") or ""
    extra_aviso = " | ".join(avisos)
    juntado = " | ".join(p for p in (aviso_atual, extra_aviso) if p)
    return {"outputs": outputs, "adapter_aviso": juntado}


FORMAT_NAMES = FORMATOS
