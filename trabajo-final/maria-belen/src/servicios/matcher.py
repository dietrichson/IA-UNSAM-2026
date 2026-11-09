"""Matcher: puntaje de ajuste entre un CV y cada puesto.

Reparto del puntaje: herramientas 33 %, experiencia 39 %, formación 17 %, otros (idiomas) 11 %
(el diseño original incluía Seniority con 10 %; se eliminó porque lo cubre Experiencia y se repartió su peso).

- Herramientas e idiomas se calculan con reglas (reproducibles y baratas).
- Experiencia y formación los juzga el modelo, un puesto por llamada, y cada
  puntaje alto debe venir con una cita del CV que se verifica; si no, queda limitado a 40.
- Los criterios que el puesto no especifica no se puntúan y su peso se reparte entre los demás.
- Los resultados se guardan en un caché local para no repetir llamadas lentas.
"""
from __future__ import annotations

import json
import re
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

from pydantic import Field

from servicios.config import LOCAL_DIR, Config
from servicios.formacion import carreras_en_texto, es_curso, evaluar_cursos, evaluar_equivalencia, tema_de_curso
from servicios.llm_client import SalidaInvalida
from servicios.prompts import cargar
from servicios.puestos_repo import Puesto, es_deseable, exigencia_experiencia
from servicios.schemas import Base, Criterio
from servicios.texto import delimitar, hash_texto, normalizar, respaldado, truncar
from servicios.vocabulario import (NOMBRE_NIVEL, dominios_en_texto, es_generica, herramienta_cubierta, herramientas_unicas,
                                   herramientas_en_texto, idiomas_en_texto, nivel_idioma, terminos_de_dominio)

PESOS = {"herramientas": 0.31, "experiencia": 0.37, "formacion": 0.16, "cursos": 0.06, "otros": 0.10}
ETIQUETAS = {"herramientas": "Herramientas", "experiencia": "Experiencia", "formacion": "Formación",
             "cursos": "Cursos y certificaciones", "otros": "Idiomas"}
TOPE_SIN_CITA = 40
MAX_CV_PUNTAJE = 4000
MAX_PUESTO_PUNTAJE = 2800


class EvaluacionLLM(Base):
    experiencia: Criterio = Field(default_factory=Criterio)
    formacion: Criterio = Field(default_factory=Criterio)
    brechas: list[str] = Field(default_factory=list)
    resumen: str = ""


@dataclass
class ItemPuntaje:
    clave: str
    etiqueta: str
    puntaje: int | None  # None: no se pudo evaluar
    peso: float = 0.0  # peso efectivo (los de un puesto suman 1)
    evidencia: list[str] = field(default_factory=list)
    comentario: str = ""


@dataclass
class ResultadoPuesto:
    puesto: Puesto
    puntaje: int
    items: list[ItemPuntaje]
    herramientas_cubiertas: list[str] = field(default_factory=list)
    herramientas_faltantes: list[str] = field(default_factory=list)
    brechas_modelo: list[str] = field(default_factory=list)
    brechas_idioma: list[str] = field(default_factory=list)  # idioma que falta o con nivel menor al pedido
    plus: list[str] = field(default_factory=list)  # deseables que el CV cubre (suman puntos extra)
    bonus: int = 0
    deseables_faltantes: list[str] = field(default_factory=list)  # deseables que no figuran: no restan
    resumen: str = ""
    avisos: list[str] = field(default_factory=list)
    parcial: bool = False  # el modelo no pudo evaluar experiencia/formación/seniority
    desde_cache: bool = False

    def item(self, clave: str) -> ItemPuntaje | None:
        return next((i for i in self.items if i.clave == clave), None)

    def a_dict(self) -> dict:
        d = asdict(self)
        d.pop("puesto")
        d.pop("desde_cache")
        return d

    @classmethod
    def desde_dict(cls, d: dict, puesto: Puesto) -> "ResultadoPuesto":
        return cls(puesto=puesto, items=[ItemPuntaje(**i) for i in d["items"]], desde_cache=True,
                   **{k: v for k, v in d.items() if k != "items"})


def _dato(valor: str) -> bool:
    return bool(valor) and not normalizar(valor).startswith("no figura")


# --------------------------------------------------------------------- criterios por reglas
def evaluar_herramientas(puesto: Puesto, cv_norm: str) -> tuple[int | None, list[str], list[str]]:
    """Puntaje sobre las herramientas EXCLUYENTES. Las deseables no restan: ver `herramientas_plus`."""
    deseables = puesto.herramientas_deseables()
    pedidas = herramientas_unicas([h for h in puesto.herramientas
                                   if not es_generica(h) and h not in deseables and not idiomas_en_texto(h)])
    if not pedidas:
        return None, [], []
    cubiertas = [h for h in pedidas if herramienta_cubierta(h, cv_norm)]
    faltantes = [h for h in pedidas if h not in cubiertas]
    return round(100 * len(cubiertas) / len(pedidas)), cubiertas, faltantes


def herramientas_plus(puesto: Puesto, cv_norm: str) -> tuple[list[str], list[str]]:
    """(deseables que el CV cubre, deseables que no cubre)."""
    des = herramientas_unicas([h for h in puesto.herramientas if h in puesto.herramientas_deseables()
                               and not es_generica(h) and not idiomas_en_texto(h)])
    cub = [h for h in des if herramienta_cubierta(h, cv_norm)]
    return cub, [h for h in des if h not in cub]


def _comparar_idiomas(puesto: Puesto, cv) -> list[dict]:
    """Un dict por idioma obligatorio: estado 'ok' | 'menor' (nivel del CV por debajo) | 'falta' | 'sin_nivel'."""
    tiene = set(idiomas_en_texto(" ".join(cv.idiomas))) | set(idiomas_en_texto(cv.texto))
    texto_cv = " ; ".join(cv.idiomas) + "\n" + cv.texto
    filas: dict[str, dict] = {}
    deseables = puesto.idiomas_deseables()
    for entrada in puesto.idiomas:
        if es_deseable(entrada):
            continue
        for idioma in idiomas_en_texto(entrada):
            if idioma in deseables:
                continue
            req = nivel_idioma(entrada, idioma, requerido=True)
            if idioma in filas and (req is None or (filas[idioma]["req"] or 0) >= (req or 0)):
                continue
            niv = nivel_idioma(texto_cv, idioma)
            if idioma not in tiene:
                estado = "falta"
            elif req is None or niv is None:
                estado = "ok" if req is None else "sin_nivel"
            else:
                estado = "ok" if niv >= req else "menor"
            filas[idioma] = {"idioma": idioma, "estado": estado, "req": req, "cv": niv}
    return list(filas.values())


def _nombre_nivel(v: float | None) -> str:
    return NOMBRE_NIVEL.get(v, "") if v else ""


def evaluar_idiomas(puesto: Puesto, cv) -> tuple[int | None, str]:
    """Idiomas obligatorios: se compara el nivel cuando ambos lo declaran (avanzado cubre intermedio)."""
    filas = _comparar_idiomas(puesto, cv)
    if not filas:
        return None, ""
    valor = {"ok": 100, "sin_nivel": 100, "menor": 50, "falta": 0}
    textos = []
    for f in filas:
        pide = f" {_nombre_nivel(f['req'])}" if f["req"] else ""
        if f["estado"] == "falta":
            textos.append(f"Pide {f['idioma']}{pide}; no figura en el CV.")
        elif f["estado"] == "menor":
            textos.append(f"Pide {f['idioma']}{pide}; el CV muestra nivel {_nombre_nivel(f['cv'])}.")
        elif f["estado"] == "sin_nivel":
            textos.append(f"Pide {f['idioma']}{pide}; el CV lo menciona sin nivel (no se pudo comparar).")
        else:
            nivel = f" {_nombre_nivel(f['cv'])}" if f["cv"] else ""
            textos.append(f"Pide {f['idioma']}{pide}; el CV muestra {f['idioma']}{nivel}: cumple.")
    return round(sum(valor[f["estado"]] for f in filas) / len(filas)), " ".join(textos)


def brechas_de_idioma(puesto: Puesto, cv) -> list[str]:
    """Solo los idiomas que de verdad faltan o quedan por debajo del nivel pedido."""
    salida = []
    for f in _comparar_idiomas(puesto, cv):
        pide = f" {_nombre_nivel(f['req'])}" if f["req"] else ""
        if f["estado"] == "falta":
            salida.append(f"{f['idioma']}{pide}")
        elif f["estado"] == "menor":
            salida.append(f"{f['idioma']}{pide} (tu CV muestra nivel {_nombre_nivel(f['cv'])})")
    return salida


def brecha_cubierta_por_cv(brecha: str, puesto: Puesto, cv_norm: str, cv) -> bool:
    """¿Esta brecha del modelo habla de algo que el CV ya cubre (herramientas) o que se maneja por reglas (idiomas)?"""
    if idiomas_en_texto(brecha):
        return True  # los idiomas se informan con `brechas_de_idioma`, con el nivel comparado
    herr = herramientas_en_texto(brecha, extra=list(puesto.herramientas))
    herr += [h for h in puesto.herramientas if not es_generica(h) and herramienta_cubierta(h, normalizar(brecha))]
    return bool(herr) and all(herramienta_cubierta(h, cv_norm) for h in herr)


def idiomas_plus(puesto: Puesto, cv) -> tuple[list[str], list[str]]:
    """Idiomas marcados como deseables: (los que el CV menciona, los que no)."""
    des = sorted(puesto.idiomas_deseables())
    tiene = set(idiomas_en_texto(" ".join(cv.idiomas))) | set(idiomas_en_texto(cv.texto))
    return [i for i in des if i in tiene], [i for i in des if i not in tiene]


def formacion_deseable(puesto: Puesto) -> bool:
    return normalizar(puesto.requiere_titulo).startswith("desea") or es_deseable(puesto.titulo_universitario)


def _aplica(puesto: Puesto) -> dict[str, bool]:
    return {"formacion": _dato(puesto.titulo_universitario) or _dato(puesto.requiere_titulo)}


BONUS_POR_PLUS = 3   # puntos que suma cada deseable que el CV cubre
BONUS_MAXIMO = 10    # tope total de puntos extra
PISO_FORMACION = 85          # la carrera y el nivel coinciden
RANGO_PARCIAL = (35, 50)     # la carrera coincide pero el puesto pide título y la persona aún cursa
TOPE_OTRA_CARRERA = 20       # el puesto pide una carrera que el CV no muestra
PISO_DOMINIO = 50  # si el CV muestra experiencia del mismo rubro que el puesto, no queda por debajo de esto
_PALABRAS_EXP = ("experiencia", "seniority", "senior", "junior", "nivel requerido", "trayectoria", "antigüedad")


def _sin_frases_de_experiencia(texto: str) -> str:
    """Saca las oraciones que hablan de experiencia/seniority (cuando el puesto no la exige)."""
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return " ".join(p for p in partes if not any(w in normalizar(p) or w in p.lower() for w in _PALABRAS_EXP)).strip()


def _quitar_frases(texto: str, palabras: tuple[str, ...]) -> str:
    """Saca las oraciones que contienen alguna de las palabras (sin tildes ni mayúsculas)."""
    partes = re.split(r"(?<=[.!?])\s+", texto.strip())
    return " ".join(p for p in partes if not any(w in normalizar(p) for w in palabras)).strip()


def _nota_formacion(eq) -> str:
    if eq is None:
        return ""
    if eq.estado == "no":
        return (f"Pista de formación: el puesto pide estudios en «{eq.pedido}» y el CV NO los muestra. Cursos, talleres y "
                "herramientas no son estudios de grado: la formación NO cumple (puntaje bajo).")
    nivel = {"graduado": "graduado/a", "estudiante": "estudiante"}.get(eq.nivel_cv, "")
    texto = (f"Pista de formación: el CV muestra «{eq.cita}» ({', '.join(eq.carreras)}), que es una de las carreras "
             f"que pide el puesto (Comunicación Social y Ciencias de la Comunicación son la misma carrera)"
             + (f"; nivel: {nivel}." if nivel else "."))
    if eq.estado == "parcial":
        texto += " El puesto pide título completo y la persona aún cursa: NO cumple de sobra, cumple parcialmente (puntaje medio-bajo)."
    return texto


def _nota_experiencia(exigencia: str, puesto: Puesto, cv_texto: str) -> str:
    """Instrucciones que se agregan al pedido del modelo sobre cómo juzgar la experiencia."""
    if exigencia == "si":
        lineas = ["Exigencia de experiencia: SÍ. Juzgá la experiencia por el tipo de tareas, no solo por el cargo."]
        comunes = [d for d in dominios_en_texto(cv_texto) if d in dominios_en_texto(puesto.cuerpo + " " + puesto.titulo)]
        for d in comunes[:3]:
            lineas.append(f"Pista: el CV menciona {', '.join(terminos_de_dominio(cv_texto, d)) or d}, "
                          f"que cuenta como experiencia en {d}, rubro que el puesto pide.")
        return "\n".join(lineas)
    if exigencia == "deseable":
        return "Exigencia de experiencia: DESEABLE (no obligatoria). No digas que falta experiencia ni que el nivel no coincide."
    return ("Exigencia de experiencia: NO. El puesto no pide experiencia previa. No menciones falta de experiencia "
            "ni de seniority ni como brecha ni en el resumen; evaluá solo formación y los demás datos.")


# --------------------------------------------------------------------- caché
class CachePuntajes:
    def __init__(self, ruta: Path | str | None = None, maximo: int = 500):
        self.ruta = Path(ruta) if ruta else LOCAL_DIR / "cache_puntajes.json"
        self.maximo = maximo
        try:
            self._datos: dict = json.loads(self.ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._datos = {}

    def get(self, clave: str) -> dict | None:
        return self._datos.get(clave)

    def set(self, clave: str, valor: dict) -> None:
        self._datos.pop(clave, None)
        self._datos[clave] = valor
        while len(self._datos) > self.maximo:
            self._datos.pop(next(iter(self._datos)))
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.ruta.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._datos, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.ruta)

    def vaciar(self) -> None:
        self._datos = {}
        self.ruta.unlink(missing_ok=True)


# --------------------------------------------------------------------- puntaje de un puesto
def _limitar(c: Criterio, cv_texto: str) -> ItemPuntaje | None:
    evidencia = [q for q in c.evidencia if respaldado(q, cv_texto, 0.7)]
    puntaje, comentario = c.puntaje, c.comentario
    if puntaje > TOPE_SIN_CITA and not evidencia:
        puntaje = TOPE_SIN_CITA
        comentario = (comentario + " " if comentario else "") + "(Sin cita verificable en el CV: puntaje limitado.)"
    return puntaje, evidencia, comentario  # type: ignore[return-value]


def puntuar_puesto(cv, puesto: Puesto, llm, cfg: Config, cache: CachePuntajes | None = None) -> ResultadoPuesto:
    cv_texto, _ = truncar(cv.texto, MAX_CV_PUNTAJE)
    sistema = cargar("puntuar_puesto")
    texto_puesto = puesto.para_prompt(MAX_PUESTO_PUNTAJE)
    clave = hash_texto(f"v4|{cv_texto}|{puesto.id}|{texto_puesto}|{cfg.modelo_principal}|{sistema}")
    if cache and (hit := cache.get(clave)):
        return ResultadoPuesto.desde_dict(hit, puesto)

    avisos: list[str] = []
    items: dict[str, ItemPuntaje] = {}
    cv_norm = normalizar(cv.texto)

    p_herr, cubiertas, faltantes = evaluar_herramientas(puesto, cv_norm)
    plus: list[str] = []
    des_falt: list[str] = []
    h_cub, h_falt = herramientas_plus(puesto, cv_norm)
    plus += h_cub
    des_falt += h_falt
    i_cub, i_falt = idiomas_plus(puesto, cv)
    plus += [f"{i} (idioma)" for i in i_cub]
    des_falt += [f"{i} (idioma)" for i in i_falt]
    if p_herr is not None:
        items["herramientas"] = ItemPuntaje("herramientas", ETIQUETAS["herramientas"], p_herr,
                                            comentario=f"Cubre {len(cubiertas)} de {len(cubiertas) + len(faltantes)} (excluyentes).")
    exc_l0, des_l0 = puesto.requisitos_por_tipo()
    def _cursos(lineas):
        limpias = (re.sub(r"^(?:(?:requisitos?|requerimientos?|se requiere|se valora(?:n)?|suma(?:n)?|plus|deseables?|opcional|"
                          r"excluyente)\s*[:\-]?\s*)+", "", c.strip(), flags=re.I)
                   for c in lineas if es_curso(c))
        vistos: dict[str, str] = {}
        for c in limpias:  # el mismo curso puede venir de la lista de requisitos y del texto original
            vistos.setdefault(" ".join(sorted(set(tema_de_curso(c)))) or normalizar(c), c)
        return list(vistos.values())
    cursos_exc, cursos_des = _cursos(exc_l0), _cursos(des_l0)
    brecha_curso = ""
    rc = evaluar_cursos(cursos_exc, cv.texto)
    if rc is not None:  # curso/diplomatura obligatorio: pesa menos que una carrera, pero cuenta
        items["cursos"] = ItemPuntaje("cursos", ETIQUETAS["cursos"], rc.puntaje, evidencia=[rc.cita] if rc.cita else [],
                                      comentario=("El CV muestra un curso o certificación afín al tema pedido (curso, diplomatura y "
                                                  "certificación se consideran equivalentes)." if rc.puntaje >= 100 else
                                                  "El CV no muestra (o solo muestra en parte) el curso o certificación pedido."))
        if rc.puntaje < 100:
            brecha_curso = f"Curso o certificación: {rc.pedido}"
    rd = evaluar_cursos(cursos_des, cv.texto)
    if rd is not None:
        (plus if rd.puntaje >= 100 else des_falt).append(f"Curso: {rd.pedido}")
    p_idi, texto_idi = evaluar_idiomas(puesto, cv)
    if p_idi is not None:
        items["otros"] = ItemPuntaje("otros", ETIQUETAS["otros"], p_idi, comentario=texto_idi)

    aplica = _aplica(puesto)
    exigencia = exigencia_experiencia(puesto)
    equiv = evaluar_equivalencia(puesto, cv.texto)
    parcial, brechas, resumen = False, [], ""
    try:
        ev = llm.chat_json(sistema, delimitar("cv", cv_texto) + "\n\n" + delimitar("puesto", texto_puesto)
                           + "\n\n" + _nota_experiencia(exigencia, puesto, cv.texto)
                           + (("\n" + _nota_formacion(equiv)) if _nota_formacion(equiv) else "")
                           + "\n\nEvaluá el ajuste del CV con el puesto.", EvaluacionLLM, rol="principal",
                           max_tokens=700)
        for clave_c in ("experiencia", "formacion"):
            if clave_c == "experiencia" and exigencia == "deseable":
                bueno = getattr(ev, "experiencia").puntaje >= 70 and any(
                    respaldado(q, cv.texto, 0.7) for q in getattr(ev, "experiencia").evidencia)
                (plus if bueno else des_falt).append("Experiencia")
            if clave_c == "experiencia" and exigencia != "si":
                texto_exp = ("El puesto no exige experiencia previa: no suma ni resta." if exigencia == "no" else
                             "La experiencia es deseable en este puesto: no resta, suma si la tenés.")
                items[clave_c] = ItemPuntaje(clave_c, ETIQUETAS[clave_c], None, comentario=texto_exp)
                continue
            if clave_c != "experiencia" and not aplica[clave_c]:
                continue  # el puesto no lo especifica: no se puntúa
            puntaje, evidencia, comentario = _limitar(getattr(ev, clave_c), cv.texto)
            if clave_c == "formacion" and equiv is not None:
                if equiv.estado == "cumple":
                    if puntaje < PISO_FORMACION:
                        puntaje = PISO_FORMACION
                        comentario = (comentario + " " if comentario else "") + (
                            f"(Ajustado: «{equiv.cita}» equivale a la carrera que pide el puesto.)")
                    if not evidencia and equiv.cita:
                        evidencia = [equiv.cita]
                elif equiv.estado == "parcial":
                    puntaje = min(max(puntaje, RANGO_PARCIAL[0]), RANGO_PARCIAL[1])
                    evidencia = [equiv.cita] if equiv.cita else evidencia
                    comentario = "Cumple parcialmente: el puesto pide título y el CV muestra estudios en curso."
                else:  # otra carrera: cursos, herramientas o talleres no cuentan como estudios
                    puntaje = min(puntaje, TOPE_OTRA_CARRERA)
                    evidencia = []
                    comentario = f"Los estudios del CV no coinciden con lo que pide el puesto ({equiv.pedido})."
            if clave_c == "formacion" and formacion_deseable(puesto):
                if puntaje >= 70 and evidencia:
                    plus.append("Formación")
                else:
                    des_falt.append("Formación")
                items[clave_c] = ItemPuntaje(clave_c, ETIQUETAS[clave_c], None, evidencia=evidencia,
                                             comentario="La formación es deseable en este puesto: no resta, suma si la tenés.")
                continue
            if clave_c == "experiencia" and puntaje < PISO_DOMINIO:
                comunes = [d for d in dominios_en_texto(cv.texto) if d in dominios_en_texto(puesto.cuerpo + " " + puesto.titulo)]
                if comunes:
                    puntaje = PISO_DOMINIO
                    comentario = (comentario + " " if comentario else "") + (
                        f"(Ajustado: el CV muestra experiencia en {comunes[0]}, rubro que pide el puesto.)")
            items[clave_c] = ItemPuntaje(clave_c, ETIQUETAS[clave_c], puntaje, evidencia=evidencia, comentario=comentario)
        brechas = [b for b in ev.brechas if respaldado(b, puesto.cuerpo + " " + texto_puesto, 0.6)][:5]
        exc_l, des_l = puesto.requisitos_por_tipo()
        txt_des, txt_exc = " ".join(des_l), " ".join(exc_l)
        es_des = lambda b: bool(txt_des) and respaldado(b, txt_des, 0.6) and not respaldado(b, txt_exc, 0.6)  # noqa: E731
        # una brecha sobre algo que el CV ya cubre (herramienta) o sobre idiomas (se informan aparte) se descarta
        brechas = [b for b in brechas if not brecha_cubierta_por_cv(b, puesto, cv_norm, cv)]
        if equiv is not None and equiv.estado == "cumple":  # la carrera ya coincide: no es brecha
            brechas = [b for b in brechas if not (carreras_en_texto(b) & set(equiv.carreras))
                       and not re.search(r"\b(titulo|licenciatura|carrera|estudios)\b", normalizar(b))]
        des_falt += [b for b in brechas if es_des(b)]
        brechas = [b for b in brechas if not es_des(b)]
        resumen = ev.resumen
        if rc is not None and rc.puntaje >= 100:  # el curso ya está en el CV: ninguna brecha puede pedirlo
            brechas = [b for b in brechas if not es_curso(b)]
        if brecha_curso:
            brechas.append(brecha_curso)
        if exigencia != "si":
            brechas = [b for b in brechas if not any(w in normalizar(b) for w in ("experiencia", "seniority", "anos"))]
            resumen = _sin_frases_de_experiencia(resumen) or "Ajuste calculado con herramientas, formación e idiomas."
        if equiv is not None and equiv.estado in ("parcial", "no") and "formacion" in items:
            # el resumen del modelo no puede decir que la formación cumple si no cumple
            resumen = _quitar_frases(resumen, ("formacion", "estudios", "titulo", "carrera", "licenciatura")) or ""
            resumen = (resumen + " " if resumen else "") + (
                "La formación cumple solo parcialmente: el puesto pide título y el CV muestra estudios en curso."
                if equiv.estado == "parcial" else
                f"La formación no coincide con lo que pide el puesto ({equiv.pedido}).")
            brechas = [b for b in brechas if not re.search(r"\b(formacion|titulo|licenciatura|carrera|estudios)\b", normalizar(b))]
            brechas.insert(0, "Título de grado (el CV muestra estudios en curso)" if equiv.estado == "parcial"
                           else f"Formación: {equiv.pedido}")
        # coherencia: las brechas y el resumen no pueden contradecir lo que el puntaje ya reconoce
        exp_item = items.get("experiencia")
        if exigencia == "si" and exp_item is not None and exp_item.puntaje is not None and exp_item.puntaje >= PISO_DOMINIO:
            doms_cv = set(dominios_en_texto(cv.texto))

            def _contradice_experiencia(b: str) -> bool:
                if not re.search(r"experiencia|trayectoria|\banos?\b", normalizar(b)):
                    return False
                doms_b = set(dominios_en_texto(b))
                return exp_item.puntaje >= 70 or (bool(doms_b) and doms_b <= doms_cv)
            brechas = [b for b in brechas if not _contradice_experiencia(b)]
        herr_item = items.get("herramientas")
        if herr_item is not None and herr_item.puntaje == 100:  # cubre todas las excluyentes
            resumen = _quitar_frases(resumen, ("herramienta", "software", "programa", "conocimientos en", "manejo de",
                                               "carece")) or "Ajuste calculado a partir de las herramientas, la experiencia y la formación."
    except SalidaInvalida:
        parcial = True
        avisos.append("El modelo no pudo evaluar este puesto (respuesta inválida). "
                      "El puntaje usa solo herramientas e idiomas y no es comparable.")
        items["experiencia"] = ItemPuntaje("experiencia", ETIQUETAS["experiencia"], None, comentario="No evaluado.")

    activos = {k: i for k, i in items.items() if i.puntaje is not None}
    suma = sum(PESOS[k] for k in activos) or 1.0
    for k, i in activos.items():
        i.peso = PESOS[k] / suma
    base = round(sum(i.peso * i.puntaje for i in activos.values())) if activos else 0
    plus = list(dict.fromkeys(plus))
    bonus = min(BONUS_MAXIMO, BONUS_POR_PLUS * len(plus)) if activos else 0
    total = min(100, base + bonus)
    orden = list(PESOS)
    res = ResultadoPuesto(puesto=puesto, puntaje=total, items=sorted(items.values(), key=lambda i: orden.index(i.clave)),
                          herramientas_cubiertas=cubiertas, herramientas_faltantes=faltantes,
                          brechas_modelo=brechas, brechas_idioma=brechas_de_idioma(puesto, cv), plus=plus, bonus=total - base,
                          deseables_faltantes=list(dict.fromkeys(des_falt)), resumen=resumen, avisos=avisos, parcial=parcial)
    if cache and not parcial:
        cache.set(clave, res.a_dict())
    return res


def puntuar_candidatos(cv, candidatos, llm, cfg: Config, n: int | None = None, cache: CachePuntajes | None = None,
                       progreso: Callable[[int, int, str], None] | None = None) -> list[ResultadoPuesto]:
    """Puntúa los primeros `n` candidatos (Candidato o Puesto) y los ordena de mayor a menor."""
    puestos = [getattr(c, "puesto", c) for c in candidatos][: (n or cfg.puntuar_n)]
    resultados = []
    for i, p in enumerate(puestos):
        if progreso:
            progreso(i, len(puestos), p.titulo)
        resultados.append(puntuar_puesto(cv, p, llm, cfg, cache))
    if progreso:
        progreso(len(puestos), len(puestos), "")
    return sorted(resultados, key=lambda r: (r.parcial, -r.puntaje))
