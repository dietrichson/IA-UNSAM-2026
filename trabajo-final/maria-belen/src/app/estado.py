"""Piezas compartidas por las pantallas: servicios cacheados, estado de sesión y borrado de datos locales."""
from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
for ruta in (str(RAIZ), str(RAIZ / "app")):
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from servicios.config import INDICE_DIR, LOCAL_DIR, Config, cargar_config  # noqa: E402
from servicios.cv_parser import CVProcesado, parsear_cv  # noqa: E402
from servicios.llm_client import LLMClient  # noqa: E402
from servicios.puestos_repo import Puesto, cargar_puestos  # noqa: E402
from servicios.texto import hash_texto  # noqa: E402
from servicios.vocabulario import vocabulario_desde_puestos  # noqa: E402


@dataclass
class Servicios:
    cfg: Config
    llm: LLMClient
    puestos: list[Puesto]
    vocabulario: list[str]


@st.cache_resource(show_spinner=False)
def servicios() -> Servicios:
    """Configuración, cliente del modelo y base de puestos: se crean una vez por servidor."""
    cfg = cargar_config()
    puestos = cargar_puestos()
    return Servicios(cfg, LLMClient(cfg), puestos, vocabulario_desde_puestos(puestos))


def aviso_aceptado() -> bool:
    return bool(st.session_state.get("aviso_ok"))


def aceptar_aviso() -> None:
    st.session_state["aviso_ok"] = True


def borrar_datos_locales() -> int:
    """Borra el caché de puntajes y el CV guardado (`data/local/`) y limpia la sesión. Devuelve cuántos archivos borró."""
    n = 0
    if LOCAL_DIR.exists():
        n = sum(1 for p in LOCAL_DIR.rglob("*") if p.is_file())
        shutil.rmtree(LOCAL_DIR, ignore_errors=True)
    for clave in ("cv_texto", "cv_procesado", "resultados_sugeridor", "oferta_texto", "adaptacion"):
        st.session_state.pop(clave, None)
    return n


# ---------------------------------------------------------------- CV
def _ruta_cv() -> Path:
    return LOCAL_DIR / "cv_guardado.txt"


def guardar_cv(texto: str) -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    _ruta_cv().write_text(texto, encoding="utf-8")


def cv_guardado() -> str | None:
    try:
        return _ruta_cv().read_text(encoding="utf-8") or None
    except OSError:
        return None


def cv_procesado(texto: str, S: Servicios) -> CVProcesado:
    """Lee el CV con el modelo una sola vez por texto (se guarda en la sesión)."""
    clave = hash_texto(f"{texto}|{S.cfg.modelo_principal}")
    guardado = st.session_state.get("cv_procesado")
    if guardado and guardado[0] == clave:
        return guardado[1]
    cv = parsear_cv(texto, S.llm, S.cfg, S.vocabulario)
    st.session_state["cv_procesado"] = (clave, cv)
    return cv


# ---------------------------------------------------------------- CV recordado (opcional, solo en esta computadora)
def _ruta_cv() -> Path:
    return LOCAL_DIR / "cv.txt"


def guardar_cv(texto: str) -> None:
    _ruta_cv().parent.mkdir(parents=True, exist_ok=True)
    _ruta_cv().write_text(texto, encoding="utf-8")


def leer_cv_guardado() -> str | None:
    try:
        return _ruta_cv().read_text(encoding="utf-8") or None
    except OSError:
        return None


def borrar_cv_guardado() -> None:
    _ruta_cv().unlink(missing_ok=True)
