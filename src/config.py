"""Carrega .env sem expor chaves. Em pytest nao chama APIs pagas."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def em_teste() -> bool:
    return bool(os.getenv("PYTEST_CURRENT_TEST"))


def tem_openrouter() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY", "").strip()) and not em_teste()


def tem_jev() -> bool:
    return bool(os.getenv("TYPESAFE_API_KEY", "").strip()) and not em_teste()
