"""Brechas: qué le falta al CV para un puesto, y qué se repite entre los mejores puestos.

Todo se calcula con reglas sobre los resultados del matcher y la base de puestos, así que es
reproducible. La importancia de una herramienta es en cuántos de los puestos de la base se pide.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from servicios.matcher import ETIQUETAS, ResultadoPuesto
from servicios.puestos_repo import Puesto
from servicios.texto import normalizar
from servicios.vocabulario import alternativas, es_generica, grupo_de, herramienta_cubierta, herramientas_unicas

UMBRAL_DEBIL = 50


def clave_herramienta(item: str) -> str:
    """Identificador estable: "Google Analytics 4 (GA4)" y "GA4" dan la misma clave."""
    alts = alternativas(item)
    return min(grupo_de(alts[0])) if alts else normalizar(item)


def _etiqueta(item: str) -> str:
    return re.sub(r"\s*\(.*?\)", "", item).strip() or item


@dataclass
class Brecha:
    texto: str
    tipo: str  # "herramienta" | "requisito"
    frecuencia: int = 0  # en cuántos puestos de la base se pide (herramientas)


@dataclass
class FilaHerramienta:
    herramienta: str
    puestos: int
    porcentaje: int
    la_tengo: bool


@dataclass
class FilaAgregada:
    texto: str
    veces: int
    de: int
    tipo: str  # "herramienta" | "criterio"


def frecuencias_herramientas(puestos: list[Puesto]) -> tuple[Counter, dict[str, str]]:
    """(cuántos puestos piden cada herramienta, etiqueta más común de cada una)."""
    cuenta: Counter = Counter()
    etiquetas: dict[str, Counter] = {}
    for p in puestos:
        vistas = set()
        for item in herramientas_unicas([h for h in p.herramientas if not es_generica(h)]):
            k = clave_herramienta(item)
            etiquetas.setdefault(k, Counter())[_etiqueta(item)] += 1
            vistas.add(k)
        cuenta.update(vistas)
    return cuenta, {k: c.most_common(1)[0][0] for k, c in etiquetas.items()}


def herramientas_mas_pedidas(cv, puestos: list[Puesto], top: int = 10) -> list[FilaHerramienta]:
    cuenta, etiquetas = frecuencias_herramientas(puestos)
    con_dato = sum(1 for p in puestos if any(not es_generica(h) for h in p.herramientas)) or 1
    cv_norm = normalizar(cv.texto)
    filas = [FilaHerramienta(etiquetas[k], n, round(100 * n / con_dato), herramienta_cubierta(etiquetas[k], cv_norm))
             for k, n in cuenta.most_common()]
    return filas[:top]


def _habla_de_cubiertas(brecha: str, cubiertas: list[str], res: ResultadoPuesto) -> bool:
    """Una herramienta cubierta nunca puede figurar como brecha (ni como «por dónde empezar»)."""
    n = normalizar(brecha)
    mencionadas = [h for h in res.puesto.herramientas if herramienta_cubierta(h, n)]
    return bool(mencionadas) and all(h in cubiertas for h in mencionadas)


def brechas_de_puesto(res: ResultadoPuesto, puestos_base: list[Puesto]) -> list[Brecha]:
    """Herramientas faltantes (las más pedidas primero) y requisitos que el modelo no encontró en el CV."""
    cuenta, _ = frecuencias_herramientas(puestos_base)
    herr = sorted((Brecha(_etiqueta(h), "herramienta", cuenta[clave_herramienta(h)]) for h in res.herramientas_faltantes),
                  key=lambda b: -b.frecuencia)
    cubiertas = list(res.herramientas_cubiertas)
    reqs = [Brecha(b, "requisito") for b in res.brechas_modelo if not _habla_de_cubiertas(b, cubiertas, res)]
    reqs += [Brecha(i, "idioma") for i in res.brechas_idioma]
    opcionales = [Brecha(d, "deseable") for d in res.deseables_faltantes]  # no restan: se listan aparte
    return herr + reqs + opcionales


def sugerencia(brechas: list[Brecha], total_puestos: int) -> str:
    opcionales = [b for b in brechas if b.tipo == "deseable"]
    brechas = [b for b in brechas if b.tipo != "deseable"]
    herr = [b for b in brechas if b.tipo == "herramienta"]
    if herr:
        b = herr[0]
        extra = f" (se pide en {b.frecuencia} de los {total_puestos} puestos de la base)" if b.frecuencia > 1 else ""
        return f"Por dónde empezar: {b.texto}{extra}."
    idi = [b for b in brechas if b.tipo == "idioma"]
    if idi:
        return f"Por dónde empezar: {idi[0].texto}."
    if brechas and brechas[0].tipo == "idioma":
        return f"Por dónde empezar: {brechas[0].texto}. Si ya lo tenés, indicá el nivel en tu CV."
    if brechas and brechas[0].texto.startswith("Curso o certificación"):
        return f"Por dónde empezar: sumar o mostrar en tu CV el curso pedido ({brechas[0].texto.split(': ', 1)[1]})."
    if brechas:
        return f"Por dónde empezar: mostrar en tu CV experiencia concreta en «{brechas[0].texto}»."
    if opcionales:
        return f"No detecté brechas obligatorias. Si querés sumar puntos extra: {opcionales[0].texto}."
    return "No detecté brechas claras para este puesto."


def resumen_agregado(resultados: list[ResultadoPuesto], top: int = 8) -> list[FilaAgregada]:
    """Qué falta con más frecuencia entre los mejores puestos ("lo que más conviene aprender")."""
    validos = [r for r in resultados if not r.parcial] or resultados
    n = len(validos)
    herr: Counter = Counter()
    nombres: dict[str, Counter] = {}
    debiles: Counter = Counter()
    for r in validos:
        for h in {clave_herramienta(x): x for x in r.herramientas_faltantes}.items():
            herr[h[0]] += 1
            nombres.setdefault(h[0], Counter())[_etiqueta(h[1])] += 1
        for i in r.items:
            if i.clave in ("experiencia", "formacion", "cursos") and i.puntaje is not None and i.puntaje < UMBRAL_DEBIL:
                debiles[i.clave] += 1
    filas = [FilaAgregada(nombres[k].most_common(1)[0][0], v, n, "herramienta") for k, v in herr.items()]
    filas += [FilaAgregada(f"{ETIQUETAS[k]} por debajo de {UMBRAL_DEBIL}", v, n, "criterio") for k, v in debiles.items()]
    return sorted(filas, key=lambda f: (-f.veces, f.tipo, f.texto))[:top]
