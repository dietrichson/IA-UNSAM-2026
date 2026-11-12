"""Flujos completos que usa la pantalla del Sugeridor: buscar puestos y ver brechas de uno."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable

from servicios.brechas import Brecha, FilaAgregada, brechas_de_puesto, resumen_agregado, sugerencia
from servicios.config import Config
from servicios.cv_parser import CVProcesado
from servicios.matcher import CachePuntajes, ResultadoPuesto, puntuar_candidatos, puntuar_puesto
from servicios.oferta_parser import parsear_oferta
from servicios.puestos_repo import Puesto, puesto_desde_oferta
from servicios.recuperador import Recuperador

Progreso = Callable[[str, float], None]


@dataclass
class ResultadoSugeridor:
    cv: CVProcesado
    metodo: str  # "embeddings" | "palabras"
    avisos: list[str]
    resultados: list[ResultadoPuesto]
    sin_puntuar: list[Puesto]
    agregado: list[FilaAgregada]
    n_pedido: int


@dataclass
class DetalleBrechas:
    resultado: ResultadoPuesto
    brechas: list[Brecha]
    sugerencia: str
    avisos: list[str] = field(default_factory=list)


def filtro_puestos(modalidades: set[str] | None = None, excluir_titulo: bool = False) -> Callable[[Puesto], bool]:
    """Los puestos sin dato de modalidad no se descartan (el aviso no lo decía, no es un "no")."""
    def f(p: Puesto) -> bool:
        if modalidades and p.modalidad_tipo not in modalidades and p.modalidad_tipo != "no figura":
            return False
        return not (excluir_titulo and p.requiere_titulo == "sí")
    return f


def buscar_puestos(cv: CVProcesado, llm, cfg: Config, puestos: list[Puesto], n: int,
                   filtro: Callable[[Puesto], bool] | None = None, cache: CachePuntajes | None = None,
                   progreso: Progreso | None = None, indice_dir: Path | str | None = None) -> ResultadoSugeridor:
    avisar = progreso or (lambda etapa, frac: None)
    avisar("Buscando puestos parecidos a tu CV…", 0.02)
    rec = Recuperador(llm, cfg, puestos, indice_dir) if indice_dir else Recuperador(llm, cfg, puestos)
    busq = rec.buscar(cv, k=max(cfg.recuperar_k, n), filtro=filtro,
                      progreso=lambda hecho, total: avisar(
                          f"Preparando el índice de puestos ({hecho} de {total}; solo pasa la primera vez)…",
                          0.02 + 0.2 * hecho / max(total, 1)))
    candidatos = busq.candidatos
    resultados = puntuar_candidatos(
        cv, candidatos, llm, cfg, n=n, cache=cache,
        progreso=lambda i, total, titulo: avisar(f"Puntuando {min(i + 1, total)} de {total}: {titulo}" if titulo else "Listo.",
                                                 0.25 + 0.75 * i / max(total, 1)))
    puntuados = {r.puesto.id for r in resultados}
    return ResultadoSugeridor(cv=cv, metodo=busq.metodo, avisos=[*cv.avisos, *busq.avisos], resultados=resultados,
                              sin_puntuar=[c.puesto for c in candidatos if c.puesto.id not in puntuados],
                              agregado=resumen_agregado(resultados), n_pedido=n)


def evaluar_uno(cv: CVProcesado, puesto: Puesto, llm, cfg: Config, puestos_base: list[Puesto],
                cache: CachePuntajes | None = None) -> DetalleBrechas:
    r = puntuar_puesto(cv, puesto, llm, cfg, cache)
    br = brechas_de_puesto(r, puestos_base)
    return DetalleBrechas(r, br, sugerencia(br, len(puestos_base)), list(r.avisos))


def puesto_desde_texto(texto_oferta: str, llm, vocabulario: list[str] | None = None) -> tuple[Puesto, list[str]]:
    """Convierte una oferta pegada en un Puesto temporal para poder puntuarlo igual que los de la base."""
    oferta = parsear_oferta(texto_oferta, llm, vocabulario)
    est = oferta.estructura.model_copy(update={"herramientas": oferta.herramientas, "idiomas": oferta.idiomas})
    p = puesto_desde_oferta(oferta.texto, est)
    anios = est.anios_experiencia
    # lo que el modelo no informó se conserva de la lectura por reglas del texto (experiencia, formación)
    p = replace(p, seniority=est.seniority or "no figura", experiencia=f"{anios:g} años" if anios else p.experiencia,
                requiere_titulo=est.requiere_titulo if est.requiere_titulo in ("sí", "deseable") else p.requiere_titulo)
    return p, oferta.avisos
