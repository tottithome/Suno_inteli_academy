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


_SLOTS = ("[0-3s]", "[3-20s]", "[20-45s]", "[45-60s]")


def _limpa_linha(bruto: str) -> str:
    return bruto.strip().lstrip("-*#> ").strip()


def _roteiro_dos_slides(slides: list[str]) -> list[str]:
    miolos = []
    for slide in slides:
        miolo = re.sub(r"(?i)^slide\s*\d+\s*[:.\-]\s*", "", slide).strip()
        if miolo:
            miolos.append(miolo)
    if not miolos:
        miolos = ["Fechamento"]
    while len(miolos) < len(_SLOTS):
        miolos.append(miolos[-1])
    return [f"{slot} {miolo}" for slot, miolo in zip(_SLOTS, miolos, strict=False)]


def _slides_dos_tempos(tempos: list[str]) -> list[str]:
    slides = []
    for i, tempo in enumerate(tempos, start=1):
        miolo = re.sub(r"^\[\d+[^\]]*\]\s*", "", tempo).strip()
        slides.append(f"Slide {i}: {miolo or 'ponto da noticia'}")
    return slides


def _montar(slides: list[str], tempos: list[str]) -> dict[str, str] | None:
    if len(slides) >= 2 and len(tempos) < 2:
        tempos = _roteiro_dos_slides(slides)
    elif len(tempos) >= 2 and len(slides) < 2:
        slides = _slides_dos_tempos(tempos)
    if len(slides) >= 2 and len(tempos) >= 2:
        return {"carrossel": "\n".join(slides), "roteiro": "\n".join(tempos)}
    return None


def _por_linhas(texto: str) -> dict[str, str] | None:
    slides: list[str] = []
    tempos: list[str] = []
    for bruto in texto.splitlines():
        linha = _limpa_linha(bruto)
        if not linha:
            continue
        if re.match(r"(?i)^slide\s*\d+", linha):
            slides.append(linha)
        elif re.match(r"^\[\d+", linha):
            tempos.append(linha)
        elif re.match(r"^\d+[\.\)]\s+\S", linha) and len(linha.split()) <= 24:
            slides.append(f"Slide {linha.split(maxsplit=1)[0].rstrip('.)')}: {linha.split(maxsplit=1)[1]}")
    return _montar(slides, tempos)


def _parse_formatos(bruto: str) -> dict[str, str] | None:
    texto = bruto.strip()
    marcador_c = "===CARROSSEL==="
    marcador_r = "===ROTEIRO==="
    if marcador_c in texto and marcador_r in texto:
        _, resto = texto.split(marcador_c, 1)
        carrossel, roteiro = resto.split(marcador_r, 1)
        carrossel, roteiro = carrossel.strip(), roteiro.strip()
        pronto = _montar(carrossel.splitlines(), roteiro.splitlines()) if carrossel or roteiro else None
        if pronto:
            return pronto
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
        f"Artigo base:\n{artigo[:500]}\n"
        "Carrossel: 6 linhas, cada uma com no maximo 14 palavras, no formato 'Slide N: ...'. "
        "Roteiro: exatamente 4 linhas [0-3s], [3-20s], [20-45s], [45-60s]. "
        "Nao copie o artigo. Nao corte frase no meio."
    )
    bruto, _modelo = completar(SISTEMA, user, max_tokens=500)
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
