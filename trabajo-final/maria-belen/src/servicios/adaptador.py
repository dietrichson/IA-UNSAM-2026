"""Adaptador: palabras clave presentes/faltantes, CV adaptado y carta (A3 a A8).

Flujo: comparar palabras clave (reglas + confirmación del modelo para los casos dudosos) ->
generar CV o carta usando solo el CV original -> verificar -> si hay datos no respaldados,
regenerar UNA vez -> lo que persista se devuelve marcado para que la persona lo revise.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from pydantic import Field

from servicios.config import Config
from servicios.llm_client import LLMError, SalidaInvalida
from servicios.oferta_parser import OfertaProcesada
from servicios.prompts import cargar
from servicios.schemas import Base
from servicios.texto import contiene_termino, delimitar, normalizar, respaldado, truncar
from servicios.formacion import evaluar_equivalencia, evaluar_nivel
from servicios.puestos_repo import Puesto, es_clausula_formacion, lineas_con_tipo
from servicios.genero import instruccion_genero, resolver_genero, resolver_marcas
from servicios.vocabulario import grupo_de, herramientas_por_categoria
from servicios.verificador import Hallazgo, verificar

TONOS = {
    "formal": "Tono formal y profesional: tratamiento de usted, frases claras, sin coloquialismos.",
    "cercano": "Tono cercano y cordial: natural y amable, en primera persona, sin perder profesionalismo.",
    "creativo": "Tono creativo: abrí con una frase original que muestre personalidad, pero sin exagerar ni inventar.",
}
MAX_DUDOSAS = 8
MAX_CV_ADAPTAR = 4000
MAX_OFERTA_RESUMEN = 1500


class Confirmacion(Base):
    palabra: str = ""
    cita: str = ""


class Confirmaciones(Base):
    confirmadas: list[Confirmacion] = Field(default_factory=list)


@dataclass
class PalabraPresente:
    palabra: str
    via: str  # "exacta" | "sinónimo" | "confirmada por el modelo"
    cita: str = ""


@dataclass
class AnalisisPalabras:
    presentes: list[PalabraPresente] = field(default_factory=list)
    faltantes: list[str] = field(default_factory=list)
    no_cubiertos: list[str] = field(default_factory=list)  # requisitos del aviso que el CV no permite cubrir (A7)
    avisos: list[str] = field(default_factory=list)


@dataclass
class Generado:
    texto: str
    hallazgos: list[Hallazgo] = field(default_factory=list)  # lo que sigue sin respaldo después de regenerar
    regenerado: bool = False
    avisos: list[str] = field(default_factory=list)


def _raices(texto: str) -> set[str]:
    return {t[:5] for t in normalizar(texto).split() if len(t) >= 5}


def _esta(palabra: str, cv_norm: str) -> str | None:
    if contiene_termino(cv_norm, palabra):
        return "exacta"
    if any(contiene_termino(cv_norm, s) for s in grupo_de(normalizar(palabra)) if s != normalizar(palabra)):
        return "sinónimo"
    return None


def _equivalencia(texto: str, cv):
    """Si `texto` es un requisito de formación que nombra carreras: Equivalencia del CV; si no, None."""
    if not es_clausula_formacion(texto):
        return None
    eq = evaluar_equivalencia(Puesto(id="req", titulo="", cuerpo="", titulo_universitario=texto), cv.texto)
    return eq if eq is not None else evaluar_nivel(texto, cv.texto)  # «Estudiante avanzado» a secas: se mira el nivel


def _experiencia_deseable(oferta_texto: str) -> bool:
    """¿Los años de experiencia figuran solo como deseables («deseable 1 año de experiencia»)?"""
    cl = [(c, d) for c, d in lineas_con_tipo(oferta_texto) if "experiencia" in normalizar(c)]
    return bool(cl) and all(d for _, d in cl)


def analizar_palabras(cv, oferta: OfertaProcesada, llm=None) -> AnalisisPalabras:
    cv_norm, raices_cv = cv.texto_norm, _raices(cv.texto)
    res = AnalisisPalabras()
    dudosas: list[str] = []
    for k in oferta.palabras_clave:
        eq = _equivalencia(k, cv)
        if eq is not None and eq.estado == "cumple":  # «Estudiante avanzado de Licenciatura en Comunicación o afines»
            res.presentes.append(PalabraPresente(k, "equivalencia de carrera", eq.cita))
            continue
        if eq is not None:
            res.faltantes.append(k)
            continue
        via = _esta(k, cv_norm)
        if via:
            res.presentes.append(PalabraPresente(k, via))
        elif _raices(k) & raices_cv:
            dudosas.append(k)
        else:
            res.faltantes.append(k)

    if dudosas and llm is not None:
        confirmadas: dict[str, str] = {}
        try:
            r = llm.chat_json(cargar("confirmar_palabras"),
                              delimitar("cv", truncar(cv.texto, MAX_CV_ADAPTAR)[0]) + "\n\n"
                              + delimitar("palabras", "\n".join(f"- {d}" for d in dudosas[:MAX_DUDOSAS])),
                              Confirmaciones, rol="liviano", max_tokens=500)
            for c in r.confirmadas:
                match = next((d for d in dudosas if normalizar(d) == normalizar(c.palabra)), None)
                if match and respaldado(c.cita, cv.texto, 0.7):  # sin cita verificable no se acepta
                    confirmadas[match] = c.cita
        except SalidaInvalida:
            res.avisos.append("No pude confirmar con el modelo algunas palabras dudosas; las tomé como faltantes.")
        for d in dudosas:
            if d in confirmadas:
                res.presentes.append(PalabraPresente(d, "confirmada por el modelo", confirmadas[d]))
            else:
                res.faltantes.append(d)
    else:
        res.faltantes += dudosas

    est = oferta.estructura
    for req in est.requisitos:
        eq = _equivalencia(req, cv)
        if eq is not None:  # la formación se compara por carrera equivalente, no por palabras sueltas
            if eq.estado in ("no", "parcial"):  # otra carrera, o se pide título y la persona aún cursa
                res.no_cubiertos.append(req)
            continue
        raices = _raices(req)
        if raices and len(raices & raices_cv) / len(raices) <= 0.5 and not any(
                normalizar(p.palabra) in normalizar(req) for p in res.presentes):
            res.no_cubiertos.append(req)
    pedidos, tiene = est.anios_experiencia, cv.estructura.anios_experiencia
    if pedidos and (tiene is None or tiene < pedidos) and not _experiencia_deseable(oferta.texto):
        res.no_cubiertos.append(f"Pide {pedidos:g} años de experiencia; el CV no permite confirmarlos.")
    return res


# ------------------------------------------------------------------ generación
def _resumen_oferta(oferta: OfertaProcesada) -> str:
    e = oferta.estructura
    partes = []
    if e.titulo:
        partes.append(f"Puesto: {e.titulo}")
    if e.empresa:
        partes.append(f"Empresa: {e.empresa}")
    if e.requisitos:
        partes.append("Requisitos:\n" + "\n".join(f"- {r}" for r in e.requisitos[:8]))
    if e.deseables:
        partes.append("Deseables:\n" + "\n".join(f"- {r}" for r in e.deseables[:5]))
    texto = "\n".join(partes)
    if len(texto) < 120:  # el modelo no estructuró casi nada: se usa el aviso tal cual
        texto = truncar(oferta.texto, MAX_OFERTA_RESUMEN)[0]
    return truncar(texto, MAX_OFERTA_RESUMEN)[0]


def _pedido(cv, oferta: OfertaProcesada, analisis: AnalisisPalabras, correccion: str = "") -> str:
    presentes = ", ".join(p.palabra for p in analisis.presentes) or "(ninguna)"
    no_cubiertas = ", ".join(analisis.faltantes) or "(ninguna)"
    cats = herramientas_por_categoria(cv.herramientas)
    por_cat = "; ".join(f"{c}: {', '.join(hs)}" for c, hs in cats.items()) or "(ninguna reconocida)"
    texto = (delimitar("cv", truncar(cv.texto, MAX_CV_ADAPTAR)[0]) + "\n\n"
             + delimitar("oferta", _resumen_oferta(oferta)) + f"\n\nPalabras clave presentes: {presentes}"
             + f"\nPalabras clave no cubiertas: {no_cubiertas}"
             + f"\nHerramientas del CV por categoría: {por_cat}")
    if correccion:
        texto += "\n\n" + correccion
    return texto


def _limpiar_salida(texto: str) -> str:
    t = texto.strip()
    m = re.match(r"^```(?:markdown|md|text)?\s*\n(.*?)\n```$", t, re.S | re.I)
    return (m.group(1) if m else t).strip()


_SEPARADOR = re.compile(r"^\s*([-_*=]{3,}|```)\s*$")


def quitar_repeticiones(texto: str) -> tuple[str, bool]:
    """Los modelos chicos a veces repiten el documento entero (o párrafos) varias veces.
    1) Si el texto vuelve a empezar con su primera línea y repite el mismo contenido, se corta ahí.
    2) Se quitan líneas largas repetidas y los títulos que quedan sin contenido.
    Devuelve (texto sin repeticiones, si se quitó algo)."""
    lineas = texto.splitlines()
    original = list(lineas)
    util = [i for i, l in enumerate(lineas) if l.strip() and not _SEPARADOR.match(l)]
    if len(util) >= 4:
        primera = normalizar(lineas[util[0]])
        for pos in util[1:]:
            if normalizar(lineas[pos]) != primera:
                continue
            resto = [normalizar(l) for l in lineas[pos:] if l.strip() and not _SEPARADOR.match(l)]
            inicio = [normalizar(l) for l in lineas[util[0]:] if l.strip() and not _SEPARADOR.match(l)]
            m = min(len(resto), 5)
            if m >= 2 and resto[:m] == inicio[:m]:
                lineas = lineas[:pos]
                while lineas and (not lineas[-1].strip() or _SEPARADOR.match(lineas[-1])):
                    lineas.pop()
                break
    vistas: set[str] = set()
    salida: list[str] = []
    for l in lineas:
        k = normalizar(re.sub(r"^\s*([-*+•]|\d+[.)])\s+", "", l))
        if len(k) >= 25 and not l.lstrip().startswith("#"):
            if k in vistas:
                continue
            vistas.add(k)
        salida.append(l)
    limpio: list[str] = []  # títulos sin contenido: se quitan
    for i, l in enumerate(salida):
        if l.lstrip().startswith("#") and l is not salida[0]:
            sig = next((x for x in salida[i + 1:] if x.strip()), "")
            if not sig or sig.lstrip().startswith("#"):
                if any(normalizar(l) == normalizar(o) for o in original if o is not l) or not sig:
                    continue
        limpio.append(l)
    res = re.sub(r"\n{3,}", "\n\n", "\n".join(limpio)).strip()
    return res, normalizar(res) != normalizar(texto.strip())


def _generar(sistema: str, cv, oferta, analisis, llm, cfg: Config, extra_sistema: str, max_tokens: int,
             vocabulario_extra, genero: str = "auto") -> Generado:
    genero = resolver_genero(genero, cv.texto)
    repeticion = [False]

    def una_vez(correccion: str = "") -> str:
        texto = _limpiar_salida(llm.chat_texto(sistema + extra_sistema + instruccion_genero(genero),
                                               _pedido(cv, oferta, analisis, correccion),
                                               rol="principal", temperatura=0.4, max_tokens=max_tokens))
        texto = re.sub(r"\b([Oo])fim[áa]tic([ao]s?)\b",
                       lambda m: ("I" if m.group(1) == "O" else "i") + "nform" + "át" + "ic" + m.group(2), texto)  # vocabulario local
        texto, quitado = quitar_repeticiones(texto)
        if quitado:
            repeticion[0] = True
        texto = resolver_marcas(texto, genero)  # «emocionado/a» -> una sola forma
        if len(texto) < 80:
            raise SalidaInvalida("El modelo devolvió un texto vacío o demasiado corto.")
        return texto

    aviso = "El modelo repitió partes del texto; se quitaron las repeticiones."
    texto = una_vez()
    hallazgos = verificar(texto, cv.texto, oferta.texto, vocabulario_extra, genero)
    if not hallazgos:
        return Generado(texto, avisos=[aviso] if repeticion[0] else [])
    lista = "; ".join(f"«{h.fragmento}» ({h.tipo})" for h in hallazgos[:10])
    correccion = (f"CORRECCIÓN: tu versión anterior incluyó datos que NO están en el CV: {lista}. "
                  "Escribila de nuevo sin esos datos ni ninguno otro que el CV no contenga.")
    try:
        texto2 = una_vez(correccion)
    except (SalidaInvalida, LLMError):
        return Generado(texto, hallazgos, regenerado=False, avisos=[aviso] if repeticion[0] else [])
    hallazgos2 = verificar(texto2, cv.texto, oferta.texto, vocabulario_extra, genero)
    if len(hallazgos2) <= len(hallazgos):
        return Generado(texto2, hallazgos2, regenerado=True, avisos=[aviso] if repeticion[0] else [])
    return Generado(texto, hallazgos, regenerado=True, avisos=[aviso] if repeticion[0] else [])  # la segunda versión empeoró: se conserva la primera


def adaptar_cv(cv, oferta: OfertaProcesada, analisis: AnalisisPalabras, llm, cfg: Config,
               vocabulario_extra: list[str] | None = None, genero: str = "auto") -> Generado:
    return _generar(cargar("adaptar_cv"), cv, oferta, analisis, llm, cfg, "", 1300, vocabulario_extra, genero)


def redactar_carta(cv, oferta: OfertaProcesada, analisis: AnalisisPalabras, llm, cfg: Config, tono: str = "cercano",
                   vocabulario_extra: list[str] | None = None, genero: str = "auto") -> Generado:
    if tono not in TONOS:
        raise ValueError(f"Tono desconocido: {tono}. Opciones: {', '.join(TONOS)}")
    return _generar(cargar("adaptar_carta"), cv, oferta, analisis, llm, cfg, "\n" + TONOS[tono], 700, vocabulario_extra, genero)
