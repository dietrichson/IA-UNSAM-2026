"""Cálculo de las métricas de evaluación (funciones puras, sin modelo ni red)."""
from __future__ import annotations

from servicios.config import PROMPTS_DIR
from servicios.texto import hash_texto, normalizar


def version_prompts() -> str:
    """Identificador corto del conjunto de prompts: cambia si se edita cualquier archivo de `prompts/`."""
    contenido = "".join(p.name + p.read_text(encoding="utf-8") for p in sorted(PROMPTS_DIR.glob("*.txt")))
    return hash_texto(contenido)[:8]


def acierta_alguno(esperados: list[str], obtenidos: list[str]) -> bool | None:
    """¿Al menos uno de los puestos elegidos por la persona del rubro está entre los obtenidos? None si no hay esperados."""
    if not esperados:
        return None
    return any(e in set(obtenidos) for e in esperados)


def acierta_todos(esperados: list[str], obtenidos: list[str]) -> bool | None:
    if not esperados:
        return None
    return all(e in set(obtenidos) for e in esperados)


def jaccard(a: list[str], b: list[str]) -> float:
    ca, cb = {normalizar(x) for x in a if normalizar(x)}, {normalizar(x) for x in b if normalizar(x)}
    if not ca and not cb:
        return 1.0
    return len(ca & cb) / len(ca | cb)


def comparar_faltantes(esperado: list[str] | None, obtenido: list[str], umbral: float = 0.8) -> dict | None:
    """Compara la lista de faltantes hecha a mano con la de la herramienta. Coincide si el solapamiento es >= umbral."""
    if esperado is None:
        return None
    j = jaccard(esperado, obtenido)
    exacta = {normalizar(x) for x in esperado} == {normalizar(x) for x in obtenido}
    return {"jaccard": round(j, 3), "exacta": exacta, "coincide": j >= umbral}


def tasa(valores: list[bool | None]) -> dict:
    """Porcentaje de aciertos ignorando los casos sin datos (None)."""
    validos = [v for v in valores if v is not None]
    return {"casos": len(validos), "sin_datos": len(valores) - len(validos), "aciertos": sum(validos),
            "porcentaje": round(100 * sum(validos) / len(validos), 1) if validos else None}


UMBRALES = {"veracidad": 100.0, "palabras": 80.0, "ranking": 70.0, "recuperacion": 90.0, "brechas": 80.0}


def estado(clave: str, t: dict) -> str:
    if t["porcentaje"] is None:
        return "Sin datos (completar evaluacion/casos/esperados.json)" if clave != "veracidad" else "Sin datos"
    return "Cumple" if t["porcentaje"] >= UMBRALES[clave] else "No cumple"
