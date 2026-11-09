"""Configuración del proyecto.

Lee el archivo `.env` (si existe) y las variables de entorno. Las variables de
entorno ya definidas tienen prioridad sobre el `.env`. Las claves de API se
leen solo de acá y nunca se guardan en el código ni llegan al navegador.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PUESTOS_DIR = RAIZ / "data" / "puestos"
EJEMPLOS_DIR = RAIZ / "data" / "ejemplos"
INDICE_DIR = RAIZ / "data" / "indice"
LOCAL_DIR = RAIZ / "data" / "local"  # CV guardado y caché: queda en tu compu, fuera del repositorio
PROMPTS_DIR = RAIZ / "prompts"

# Modelos por defecto según el proveedor (⚠️ confirmar nombres vigentes en cada proveedor).
MODELOS_POR_DEFECTO = {
    "ollama": {"principal": "qwen2.5:3b", "liviano": None, "embeddings": "bge-m3"},
    "gemini": {"principal": "gemini-2.5-flash", "liviano": "gemini-2.5-flash-lite", "embeddings": "gemini-embedding-001"},
    "claude": {"principal": "claude-sonnet-5-5", "liviano": "claude-haiku-5-5", "embeddings": None},
}
PROVEEDORES = tuple(MODELOS_POR_DEFECTO)


@dataclass(frozen=True)
class Config:
    provider: str = "ollama"
    modelo_principal: str = "qwen2.5:3b"
    modelo_liviano: str = "qwen2.5:3b"
    modelo_embeddings: str = "bge-m3"
    embeddings_provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    num_ctx: int = 4096
    timeout_s: int = 900
    recuperar_k: int = 10
    puntuar_n: int = 5
    max_cv_chars: int = 5000
    max_cv_chars_embedding: int = 4000
    min_intervalo_s: float = 0.0
    gemini_api_key: str = ""
    anthropic_api_key: str = ""

    @property
    def es_local(self) -> bool:
        return self.provider == "ollama" and self.embeddings_provider == "ollama"


def _leer_env(ruta: Path) -> dict[str, str]:
    valores: dict[str, str] = {}
    if not ruta.is_file():
        return valores
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, _, valor = linea.partition("=")
        valor = valor.split(" #")[0].strip().strip('"').strip("'")
        valores[clave.strip()] = valor
    return valores


def _entero(valor: str | None, defecto: int) -> int:
    try:
        return int(valor) if valor not in (None, "") else defecto
    except ValueError:
        return defecto


def cargar_config(env: dict[str, str] | None = None) -> Config:
    """Arma la configuración. `env` permite inyectar valores en los tests."""
    if env is None:
        archivo = _leer_env(RAIZ / ".env")
        env = {**archivo, **os.environ}
    provider = (env.get("LLM_PROVIDER") or "ollama").strip().lower()
    if provider not in PROVEEDORES:
        raise ValueError(f"LLM_PROVIDER='{provider}' no es válido. Opciones: {', '.join(PROVEEDORES)}")
    d = MODELOS_POR_DEFECTO[provider]
    principal = env.get("LLM_MODELO_PRINCIPAL") or d["principal"]
    liviano = env.get("LLM_MODELO_LIVIANO") or d["liviano"] or principal
    emb_provider = (env.get("EMBEDDINGS_PROVIDER") or ("ollama" if provider == "claude" else provider)).strip().lower()
    if emb_provider not in ("ollama", "gemini"):
        raise ValueError("EMBEDDINGS_PROVIDER debe ser 'ollama' o 'gemini' (Claude no ofrece embeddings).")
    emb_modelo = env.get("EMBEDDINGS_MODELO") or MODELOS_POR_DEFECTO[emb_provider]["embeddings"]
    return Config(
        provider=provider,
        modelo_principal=principal,
        modelo_liviano=liviano,
        modelo_embeddings=emb_modelo,
        embeddings_provider=emb_provider,
        ollama_url=(env.get("OLLAMA_URL") or "http://localhost:11434").rstrip("/"),
        num_ctx=_entero(env.get("OLLAMA_NUM_CTX"), 4096),
        timeout_s=_entero(env.get("LLM_TIMEOUT_S"), 900),
        recuperar_k=_entero(env.get("RECUPERAR_K"), 10),
        puntuar_n=_entero(env.get("PUNTUAR_N"), 5),
        max_cv_chars=_entero(env.get("MAX_CV_CHARS"), 5000),
        min_intervalo_s=float(env.get("LLM_MIN_INTERVALO_S") or (6 if provider == "gemini" else 0)),
        gemini_api_key=env.get("GEMINI_API_KEY", ""),
        anthropic_api_key=env.get("ANTHROPIC_API_KEY", ""),
    )
