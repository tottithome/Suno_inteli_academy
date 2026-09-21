"""Cliente OpenRouter (API estilo OpenAI). So gera texto."""

from __future__ import annotations

import os

from openai import OpenAI


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


def completar(system: str, user: str) -> str:
    modelo = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    resposta = client().chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=700,
    )
    texto = (resposta.choices[0].message.content or "").strip()
    if not texto:
        raise RuntimeError("OpenRouter devolveu texto vazio")
    return texto
