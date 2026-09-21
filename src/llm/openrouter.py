"""Cliente OpenRouter (API estilo OpenAI). So gera texto."""

from __future__ import annotations

import os

from openai import OpenAI, NotFoundError

MODELOS_CANDIDATOS = (
    "openrouter/free",
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
)


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


def _modelos() -> list[str]:
    preferido = os.getenv("OPENROUTER_MODEL", MODELOS_CANDIDATOS[0]).strip()
    fila = [preferido, *MODELOS_CANDIDATOS]
    vistos: list[str] = []
    for modelo in fila:
        if modelo and modelo not in vistos:
            vistos.append(modelo)
    return vistos


def completar(system: str, user: str) -> str:
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
                max_tokens=700,
            )
        except NotFoundError as exc:
            ultimo = exc
            continue
        texto = (resposta.choices[0].message.content or "").strip()
        if texto:
            return texto
        ultimo = RuntimeError(f"OpenRouter devolveu texto vazio ({modelo})")
    raise ultimo or RuntimeError("OpenRouter sem modelo disponivel")
