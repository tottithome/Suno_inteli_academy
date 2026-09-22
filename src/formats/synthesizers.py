"""Sintetizadores de formato: artigo local; carrossel e roteiro via LLM."""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor

from config import tem_openrouter
from graph.state import AUDIENCIAS, FORMATOS, ContentState

SISTEMA = (
    "Voce formata conteudo financeiro em portugues do Brasil. "
    "Nao invente fatos nem numeros. Sem markdown e sem JSON. "
    "Responda exatamente com dois blocos, nesta ordem:\n"
    "===CARROSSEL===\n"
    "Slide 1: ...\n"
    "===ROTEIRO===\n"
    "[0-3s] ..."
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


def _por_linhas(texto: str) -> dict[str, str] | None:
    slides: list[str] = []
    tempos: list[str] = []
    for bruto in texto.splitlines():
        linha = bruto.strip().lstrip("-* ")
        if re.match(r"(?i)^slide\s*\d+", linha):
            slides.append(linha)
        elif re.match(r"^\[\d+", linha):
            tempos.append(linha)
    if len(slides) >= 2 and len(tempos) >= 2:
        return {"carrossel": "\n".join(slides), "roteiro": "\n".join(tempos)}
    return None


def _parse_formatos(bruto: str) -> dict[str, str] | None:
    texto = bruto.strip()
    marcador_c = "===CARROSSEL==="
    marcador_r = "===ROTEIRO==="
    if marcador_c in texto and marcador_r in texto:
        _, resto = texto.split(marcador_c, 1)
        carrossel, roteiro = resto.split(marcador_r, 1)
        carrossel, roteiro = carrossel.strip(), roteiro.strip()
        if carrossel and roteiro:
            return {"carrossel": carrossel, "roteiro": roteiro}
    solto = _por_linhas(texto)
    if solto:
        return solto
    ini, fim = texto.find("{"), texto.rfind("}")
    if ini < 0 or fim <= ini:
        return None
    try:
        dados = json.loads(texto[ini : fim + 1])
    except json.JSONDecodeError:
        return None
    carrossel = str(dados.get("carrossel") or "").strip()
    roteiro = str(dados.get("roteiro") or "").strip()
    if not carrossel or not roteiro:
        return None
    return {"carrossel": carrossel, "roteiro": roteiro}


def _sintetizar_llm(audiencia: str, artigo: str, _anchors: dict) -> dict[str, str] | None:
    from llm.openrouter import completar

    user = (
        f"Persona: {audiencia}\n"
        f"Artigo base:\n{artigo[:900]}\n"
        "Carrossel: ate 6 linhas curtas 'Slide N: ...'. "
        "Roteiro: 4 linhas curtas [0-3s], [3-20s], [20-45s], [45-60s]. "
        "Nao corte frase no meio."
    )
    bruto, _modelo = completar(SISTEMA, user, max_tokens=900)
    return _parse_formatos(bruto)


def _uma_persona(audiencia: str, texto: str, anchors: dict, usar_llm: bool) -> tuple[str, dict[str, str], str]:
    artigo = _artigo(texto, audiencia)
    extra = None
    aviso = ""
    if usar_llm:
        try:
            extra = _sintetizar_llm(audiencia, texto, anchors)
        except Exception as exc:
            aviso = f"{audiencia}: formato LLM falhou ({type(exc).__name__}: {exc})"
    if not extra:
        extra = {
            "carrossel": _carrossel_local(texto, audiencia),
            "roteiro": _roteiro_local(texto, audiencia),
        }
        if usar_llm and not aviso:
            aviso = f"{audiencia}: formato local (resposta sem os blocos)"
    return audiencia, {"artigo": artigo, **extra}, aviso


def formats_node(state: ContentState) -> dict:
    adaptations = state.get("adaptations") or {}
    anchors = state.get("anchors") or {}
    usar_llm = tem_openrouter()
    personas = [(aud, adaptations.get(aud, "")) for aud in AUDIENCIAS]
    if usar_llm:
        with ThreadPoolExecutor(max_workers=3) as pool:
            prontos = list(pool.map(lambda item: _uma_persona(item[0], item[1], anchors, True), personas))
    else:
        prontos = [_uma_persona(aud, texto, anchors, False) for aud, texto in personas]
    outputs = {aud: saida for aud, saida, _aviso in prontos}
    avisos = [aviso for _aud, _saida, aviso in prontos if aviso]
    aviso_atual = state.get("adapter_aviso") or ""
    extra_aviso = " | ".join(avisos)
    juntado = " | ".join(p for p in (aviso_atual, extra_aviso) if p)
    return {"outputs": outputs, "adapter_aviso": juntado}


FORMAT_NAMES = FORMATOS
