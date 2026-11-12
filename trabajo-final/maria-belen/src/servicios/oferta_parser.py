"""Lectura de una oferta pegada: texto -> datos estructurados (con filtro anti-invención)."""
from __future__ import annotations

from dataclasses import dataclass, field

from servicios.cv_parser import ErrorArchivo, _sin_ruido, _unir, _unir_idiomas, limpiar_texto
from servicios.llm_client import SalidaInvalida
from servicios.prompts import cargar
from servicios.puestos_repo import lineas_con_tipo
from servicios.schemas import OfertaEstructurada
from servicios.texto import delimitar, normalizar, respaldado, truncar
from servicios.vocabulario import herramientas_en_texto, herramientas_unicas, idiomas_en_texto

MAX_CHARS_OFERTA = 4000
MIN_CHARS_OFERTA = 60


@dataclass
class OfertaProcesada:
    texto: str
    recortado: bool
    estructura: OfertaEstructurada
    herramientas: list[str]
    idiomas: list[str]
    palabras_clave: list[str]
    avisos: list[str] = field(default_factory=list)

    @property
    def texto_norm(self) -> str:
        return normalizar(self.texto)


def clasificar_requisitos(texto: str, requisitos: list[str], deseables: list[str]) -> tuple[list[str], list[str]]:
    """Regla por defecto: todo requisito es EXCLUYENTE salvo que el texto de la oferta lo marque expresamente
    como deseable/plus/«se valora». Si el ítem se ubica en el aviso, manda el aviso; si no, queda donde lo puso
    el modelo."""
    lineas = lineas_con_tipo(texto)

    def tipo(item: str) -> bool | None:
        mejor = None
        for linea, des in lineas:
            if respaldado(item, linea, 0.6) or respaldado(linea, item, 0.8):
                if not des:
                    return False  # aparece como requisito sin marca: excluyente
                mejor = True
        return mejor

    exc, des = [], []
    for item in requisitos + deseables:
        t = tipo(item)
        (des if (t is True or (t is None and item in deseables)) else exc).append(item)
    return list(dict.fromkeys(exc)), list(dict.fromkeys(des))


def _es_titulo(item: str, titulo: str) -> bool:
    a, b = normalizar(item).strip(" .:"), normalizar(titulo).strip(" .:")
    if not a or not b:
        return False
    return a == b or (len(b.split()) >= 2 and a in (f"puesto {b}", f"puesto de {b}", f"cargo {b}", f"{b} (puesto)"))


def parsear_oferta(texto: str, llm, vocabulario_extra: list[str] | None = None) -> OfertaProcesada:
    texto = limpiar_texto(texto)
    if len(texto) < MIN_CHARS_OFERTA:
        raise ErrorArchivo("El aviso está vacío o es muy corto. Pegá el texto completo de la oferta.")
    texto, recortado = truncar(texto, MAX_CHARS_OFERTA)
    avisos = []
    if recortado:
        avisos.append(f"El aviso era largo y se usaron solo los primeros {MAX_CHARS_OFERTA} caracteres.")

    try:
        est = llm.chat_json(cargar("oferta_extraer"), delimitar("oferta", texto), OfertaEstructurada,
                            rol="principal", max_tokens=1200)
    except SalidaInvalida:
        est = OfertaEstructurada()
        avisos.append("El modelo no pudo analizar el aviso; sigo con lo que detecto por reglas (puede quedar incompleto).")

    est.requisitos = [r for r in est.requisitos if respaldado(r, texto, umbral=0.6)]
    est.deseables = [r for r in est.deseables if respaldado(r, texto, umbral=0.6)]
    est.requisitos, est.deseables = clasificar_requisitos(texto, est.requisitos, est.deseables)
    if not est.titulo:  # muchos avisos pegados empiezan con el nombre del puesto
        primera = next((l.strip(" #*-") for l in texto.splitlines() if l.strip()), "")
        if 3 <= len(primera) <= 60 and ":" not in primera and not primera.endswith("."):
            est.titulo = primera
    est.herramientas = [h for h in est.herramientas if respaldado(h, texto)]
    est.idiomas = [i for i in est.idiomas if respaldado(i, texto)]
    est.palabras_clave = [k for k in est.palabras_clave if respaldado(k, texto)]
    # el nombre del puesto al que se postula no es un requisito ni una palabra clave que el CV deba "tener"
    est.palabras_clave = [k for k in est.palabras_clave if not _es_titulo(k, est.titulo)]
    est.requisitos = [r for r in est.requisitos if not _es_titulo(r, est.titulo)]
    for campo in ("titulo", "empresa"):
        if getattr(est, campo) and not respaldado(getattr(est, campo), texto):
            setattr(est, campo, "")
    if est.anios_experiencia is not None and not 0 <= est.anios_experiencia <= 40:
        est.anios_experiencia = None

    herramientas = herramientas_unicas(_unir(_sin_ruido(herramientas_en_texto(texto, vocabulario_extra), texto),
                                             est.herramientas))
    idiomas = _unir_idiomas(idiomas_en_texto(texto), est.idiomas)
    palabras = _unir(herramientas, est.palabras_clave)[:25]
    return OfertaProcesada(texto=texto, recortado=recortado, estructura=est, herramientas=herramientas,
                           idiomas=idiomas, palabras_clave=palabras, avisos=avisos)
