"""Carga de los prompts (archivos de texto en `prompts/`, editables sin tocar el código)."""
from __future__ import annotations

from functools import lru_cache

from servicios.config import PROMPTS_DIR


@lru_cache(maxsize=None)
def cargar(nombre: str) -> str:
    return (PROMPTS_DIR / f"{nombre}.txt").read_text(encoding="utf-8").strip()
