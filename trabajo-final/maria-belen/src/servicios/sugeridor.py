"""Sugeridor de puestos: recuperar -> puntuar -> resumir brechas, listo para usar desde la interfaz."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from servicios import config as _config
from servicios.brechas import (Brecha, FilaAgregada, FilaHerramienta, brechas_de_puesto, herramientas_mas_pedidas,
                               resumen_agregado, sugerencia)
from servicios.config import Config
from servicios.cv_parser import CVProcesado
from servicios.matcher import CachePuntajes, ResultadoPuesto, puntuar_candidatos, puntuar_puesto
from servicios.puestos_repo import Puesto
from servicios.recuperador import Recuperador, ResultadoBusqueda

# etapa ("indice" | "buscar" | "puntuar" | "listo"), avance, total, detalle
Progreso = Callable[[str, int, int, str], None]


@dataclass
class Sugerencia:
    busqueda: ResultadoBusqueda
    resultados: list[ResultadoPuesto]
    agregado: list[FilaAgregada]
    herramientas: list[FilaHerramienta]
    avisos: list[str] = field(default_factory=list)


@dataclass
class AnalisisPuesto:
    resultado: ResultadoPuesto
    brechas: list[Brecha]
    sugerencia: str


def sugerir(cv: CVProcesado, llm, cfg: Config, puestos: list[Puesto], n: int | None = None,
            filtro: Callable[[Puesto], bool] | None = None, cache: CachePuntajes | None = None,
            progreso: Progreso | None = None, indice_dir: Path | str | None = None) -> Sugerencia:
    avisar = progreso or (lambda *a: None)
    rec = Recuperador(llm, cfg, puestos, indice_dir or _config.INDICE_DIR)
    avisar("buscar", 0, 1, "Buscando los puestos más parecidos")
    busqueda = rec.buscar(cv, k=max(n or cfg.puntuar_n, cfg.recuperar_k), filtro=filtro,
                          progreso=lambda i, t: avisar("indice", i, t, "Preparando la base de puestos (solo la primera vez)"))
    resultados = puntuar_candidatos(cv, busqueda.candidatos, llm, cfg, n=n, cache=cache,
                                    progreso=lambda i, t, titulo: avisar("puntuar", i, t, titulo))
    avisar("listo", 1, 1, "")
    avisos = [*cv.avisos, *busqueda.avisos]
    return Sugerencia(busqueda, resultados, resumen_agregado(resultados), herramientas_mas_pedidas(cv, puestos), avisos)


def analizar_puesto(cv: CVProcesado, puesto: Puesto, llm, cfg: Config, puestos_base: list[Puesto],
                    cache: CachePuntajes | None = None) -> AnalisisPuesto:
    """Qué le falta al CV para un puesto elegido (de la base o armado a partir de una oferta pegada)."""
    res = puntuar_puesto(cv, puesto, llm, cfg, cache)
    br = brechas_de_puesto(res, puestos_base)
    return AnalisisPuesto(res, br, sugerencia(br, len(puestos_base)))
