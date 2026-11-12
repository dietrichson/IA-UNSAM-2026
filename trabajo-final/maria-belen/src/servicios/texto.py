"""Utilidades de texto: normalización, búsqueda de términos y comprobación de citas."""
from __future__ import annotations

import hashlib
import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes ni signos; solo letras, números y espacios simples."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c)).lower()
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def contiene_termino(texto_norm: str, termino: str) -> bool:
    """¿Aparece el término (como palabra o frase completa) en un texto ya normalizado?"""
    t = normalizar(termino)
    if not t:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", texto_norm) is not None


def palabras(texto: str, minimo: int = 3) -> list[str]:
    return [p for p in normalizar(texto).split() if len(p) >= minimo]


def respaldado(fragmento: str, texto: str, umbral: float = 0.8) -> bool:
    """¿El fragmento está en el texto? Acepta coincidencia literal (sin tildes ni mayúsculas)
    o casi literal: la mayoría de sus palabras significativas aparecen en el texto."""
    frag = normalizar(fragmento)
    if len(frag) < 3:
        return False
    base = normalizar(texto)
    if frag in base:
        return True
    toks = [t for t in frag.split() if len(t) >= 4]
    if len(toks) < 3:
        return False
    conjunto = set(base.split())
    return sum(t in conjunto for t in toks) / len(toks) >= umbral


def truncar(texto: str, maximo: int) -> tuple[str, bool]:
    """Corta en un salto de línea o espacio cercano. Devuelve (texto, fue_recortado)."""
    if len(texto) <= maximo:
        return texto, False
    corte = texto.rfind("\n", 0, maximo)
    if corte < maximo * 0.7:
        corte = texto.rfind(" ", 0, maximo)
    if corte < maximo * 0.7:
        corte = maximo
    return texto[:corte].rstrip(), True


def hash_texto(texto: str) -> str:
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:16]


def delimitar(etiqueta: str, texto: str) -> str:
    """Encierra un texto entre etiquetas y neutraliza etiquetas de cierre internas
    (defensa básica ante prompt injection: el contenido es dato, no instrucciones)."""
    limpio = re.sub(rf"</?\s*{re.escape(etiqueta)}\s*>", "", texto, flags=re.I)
    return f"<{etiqueta}>\n{limpio.strip()}\n</{etiqueta}>"
