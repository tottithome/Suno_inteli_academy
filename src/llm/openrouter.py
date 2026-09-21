"""Cliente OpenRouter (API estilo OpenAI). So gera texto."""

from __future__ import annotations

import os
import time

from openai import APIStatusError, OpenAI

MODELOS_CANDIDATOS = (
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
)
MODELOS_MORTOS = {
    "meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/free",
}

_modelo_ok: str | None = None


def client() -> OpenAI:
    chave = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not chave:
        raise RuntimeError("OPENROUTER_API_KEY ausente")
    return OpenAI(
        api_key=chave,
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        default_headers={
            "HTTP-Referer": "https://github.com/tottithome/Suno_inteli_academy",
            "X-Title": "Suno Content",
        },
    )


def _eh_retry(exc: Exception) -> bool:
    codigo = getattr(exc, "status_code", None)
    if codigo in {404, 408, 429, 503}:
        return True
    texto = str(exc).lower()
    return (
        "not found" in texto
        or "no endpoints found" in texto
        or "rate limit" in texto
        or "temporar" in texto
    )


def _modelos() -> list[str]:
    preferido = os.getenv("OPENROUTER_MODEL", "").strip()
    fila = []
    if _modelo_ok:
        fila.append(_modelo_ok)
    fila.extend([preferido, *MODELOS_CANDIDATOS])
    vistos: list[str] = []
    for modelo in fila:
        if not modelo or modelo in MODELOS_MORTOS or modelo in vistos:
            continue
        vistos.append(modelo)
    return vistos


def completar(system: str, user: str) -> tuple[str, str]:
    """Devolve (texto, modelo_usado)."""
    global _modelo_ok
    api = client()
    ultimo: Exception | None = None
    for modelo in _modelos():
        try:
            resposta = api.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.3,
                max_tokens=1200,
            )
        except APIStatusError as exc:
            ultimo = exc
            if modelo == _modelo_ok:
                _modelo_ok = None
            if _eh_retry(exc):
                time.sleep(1.2)
                continue
            raise
        except Exception as exc:
            ultimo = exc
            if modelo == _modelo_ok:
                _modelo_ok = None
            if _eh_retry(exc):
                time.sleep(1.2)
                continue
            raise
        texto = (resposta.choices[0].message.content or "").strip()
        if texto:
            _modelo_ok = modelo
            return texto, modelo
        ultimo = RuntimeError(f"OpenRouter devolveu texto vazio ({modelo})")
    raise ultimo or RuntimeError("OpenRouter sem modelo disponivel")
