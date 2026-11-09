"""Equivalencias de carreras y nivel de estudios (reglas, sin modelo).

«Licenciado en Comunicación Social» y «Ciencias de la Comunicación» son la misma carrera; «afines» abarca las
carreras vecinas del rubro. El resultado sirve para dar una pista al modelo y para que la formación no quede
injustamente baja cuando el CV sí cumple.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from servicios.texto import contiene_termino, normalizar

CARRERAS: dict[str, list[str]] = {
    "comunicación": ["comunicacion", "comunicacion social", "ciencias de la comunicacion", "comunicador", "comunicadora",
                     "licenciatura en comunicacion", "comunicacion institucional", "comunicacion digital",
                     "comunicacion y medios", "ciencias de la informacion", "comunicaciones"],
    "marketing": ["marketing", "marketing digital", "mercadotecnia", "comercializacion"],
    "publicidad": ["publicidad", "publicista", "creatividad publicitaria"],
    "periodismo": ["periodismo", "periodista", "periodismo digital"],
    "relaciones públicas": ["relaciones publicas", "relaciones institucionales", "ceremonial y protocolo"],
    "fotografía": ["fotografia", "imagen fotografica", "fotografo", "fotografa", "fotografico", "imagen"],
    "audiovisual": ["comunicacion audiovisual", "audiovisual", "produccion audiovisual", "cine", "realizacion audiovisual"],
    "diseño": ["diseno grafico", "diseno multimedia", "diseno visual", "diseno", "diseno de imagen y sonido",
               "diseno de comunicacion visual"],
    "letras": ["letras", "literatura", "lengua y literatura"],
    "recursos humanos": ["recursos humanos", "relaciones laborales", "rrhh"],
    "ciencias políticas": ["ciencias politicas", "ciencia politica", "politologia"],
    "relaciones internacionales": ["relaciones internacionales"],
    "administración": ["administracion", "administracion de empresas", "ade", "negocios", "ciencias economicas",
                       "economia"],
    "contabilidad": ["contador publico", "contador", "contadora", "contabilidad", "contaduria"],
    "derecho": ["abogacia", "abogado", "abogada", "derecho"],
    "psicología": ["psicologia", "psicologo", "psicologa"],
    "sociología": ["sociologia", "sociologo", "sociologa", "trabajo social"],
    "educación": ["ciencias de la educacion", "profesorado", "docente", "pedagogia", "psicopedagogia"],
    "arquitectura": ["arquitectura", "arquitecto", "arquitecta"],
    "ingeniería": ["ingenieria", "ingeniero", "ingeniera"],
    "salud": ["medicina", "veterinaria", "enfermeria", "odontologia", "kinesiologia", "nutricion", "farmacia", "biologia"],
    "sistemas": ["ciencias de la computacion", "ingenieria de software", "sistemas", "computacion", "informatica"],
}
# Carreras vecinas del rubro: si el puesto dice «afines», cualquiera de ellas cuenta.
RUBRO = {"comunicación", "marketing", "publicidad", "periodismo", "relaciones públicas", "audiovisual", "diseño", "letras", "fotografía"}
_PALABRAS_ESTUDIO = re.compile(r"licenciad|licenciatura|tecnicatura|tecnico|\bgrado\b|carrera|estudiante|graduad|egresad|"
                               r"cursando|\bcursa\b|titulo|posgrado|maestria|ingenier|profesorado")
_ESTUDIANTE = re.compile(r"estudiante|cursando|\bcursa\b|en curso|\d\w* ano de la carrera|\d(?:er|do|ro|to)? ano|materias")
# «Licenciado/a», «graduado/a», «egresado/a», «título»: título completo. Un año suelto NO prueba que se haya graduado.
_GRADUADO = re.compile(r"licenciado|licenciada|graduad|egresad|titulad|tecnico |tecnica |titulo|magister|"
                       r"\b(19|20)\d\d\s*(-|–|a)\s*(19|20)\d\d\b")
# Cursos, talleres y certificados no son estudios de grado ni tecnicaturas.
_CURSO = re.compile(r"\b(cursos?|talleres?|capacitacion(es)?|seminarios?|certificacion(es)?|certificados?|diplomaturas?|"
                    r"bootcamp|workshops?|webinars?|autodidacta)\b")
_STOP = {"de", "en", "la", "el", "los", "las", "del", "y", "o", "u", "afines", "afin", "carreras", "carrera", "superior",
         "universitario", "universitaria", "licenciatura", "licenciado", "licenciada", "tecnicatura", "estudiante",
         "graduado", "graduada", "titulo", "avanzado", "avanzada", "con", "para", "area", "areas", "similares", "similar"}


def carreras_en_texto(texto: str) -> set[str]:
    n = normalizar(texto)
    return {c for c, ts in CARRERAS.items() if any(contiene_termino(n, t) for t in ts)}


def _nivel_pedido(texto: str) -> str | None:
    """'estudiante' (alcanza con estar cursando) | 'graduado' | None (no lo dice)."""
    n = normalizar(texto)
    if re.search(r"estudiante|estudios avanzados|estudiante avanzad|cursando|en curso|proximo a finalizar|avanzado de", n):
        return "estudiante"
    if re.search(r"graduad|titulo|licenciatura|licenciad|universitario completo|titulad|tecnicatura|grado\b", n):
        return "graduado"
    return None


@dataclass
class Equivalencia:
    estado: str  # "cumple" | "parcial" (es estudiante y se pide graduado) | "no" (otra carrera)
    carreras: list[str]  # carreras del CV que coinciden con lo que pide el puesto
    cita: str = ""  # línea del CV que lo muestra
    nivel_cv: str = ""
    nivel_pedido: str = ""
    pedido: str = ""  # qué carrera pide el puesto (para explicar la brecha)


def texto_formacion_puesto(puesto) -> str:
    """Lo que el puesto pide de formación. Si el encabezado lo informa, solo eso (el cuerpo de una oferta pegada
    trae todo el aviso y mezclaría otras frases)."""
    base = puesto.titulo_universitario if normalizar(puesto.titulo_universitario) not in ("", "no figura") else ""
    if base:
        return base.strip()
    extra = [l for l in puesto.cuerpo.splitlines()
             if re.search(r"formacion|titulo|licenciatura|carrera|estudiante|graduad", normalizar(l))]
    return " ".join(extra).strip()


def _lineas_de_estudio(cv_texto: str):
    """(línea, normalizada, nivel) de las líneas del CV que hablan de estudios formales (no cursos)."""
    for linea in cv_texto.splitlines():
        ln = normalizar(linea)
        if not _PALABRAS_ESTUDIO.search(ln) or _CURSO.search(ln.replace("en curso", "")):
            continue
        nivel = "estudiante" if _ESTUDIANTE.search(ln) else ("graduado" if _GRADUADO.search(ln) else "")
        yield linea.strip(" -*#\t"), ln, nivel


def _carrera_literal(pedido: str) -> list[str]:
    """Raíces de las palabras de la carrera pedida, cuando no está en el diccionario
    («Estudiante de Contador Público» -> ['conta', 'publi'])."""
    m = re.search(r"(?:estudiante|licenciad[oa]|graduad[oa]|titulad[oa]|tecnicatura(?: superior)?|ingenier[oa]|t[ií]tulo)"
                  r"(?: avanzad[oa])?\s+(?:de|en)\s+([^,;.()]{3,70})", pedido, re.I)
    if not m:
        return []
    frase = re.split(r"\s+(?:o|u|y)\s+|\bafines\b", m.group(1))[0]
    return [t[:5] for t in normalizar(frase).split() if len(t) >= 4 and t not in _STOP]


def evaluar_equivalencia(puesto, cv_texto: str) -> Equivalencia | None:
    """None si no se puede determinar la carrera pedida (decide el modelo)."""
    pedido = texto_formacion_puesto(puesto)
    if not pedido:
        return None
    nivel_pedido = _nivel_pedido(pedido) or ""
    pide = carreras_en_texto(pedido)
    if not pide:
        raices = _carrera_literal(pedido)  # carrera fuera del diccionario: se busca literalmente en los estudios del CV
        if not raices:
            return None
        for linea, ln, nivel in _lineas_de_estudio(cv_texto):
            if any(t.startswith(r) for r in raices for t in ln.split()):
                estado = "parcial" if (nivel_pedido == "graduado" and nivel == "estudiante") else "cumple"
                return Equivalencia(estado, [], linea, nivel, nivel_pedido, pedido)
        return Equivalencia("no", [], "", "", nivel_pedido, pedido)
    if re.search(r"afin|similar|areas|otras carreras", normalizar(pedido)) and pide & RUBRO:
        pide |= RUBRO
    mejor: tuple[int, str, str, list[str]] | None = None
    for linea, ln, nivel in _lineas_de_estudio(cv_texto):
        coinciden = sorted(carreras_en_texto(linea) & pide)
        if not coinciden:
            continue
        rango = {"graduado": 2, "": 1, "estudiante": 0}[nivel]
        if mejor is None or rango > mejor[0]:
            mejor = (rango, nivel, linea, coinciden)
    if mejor is None:
        return Equivalencia("no", [], "", "", nivel_pedido, pedido)
    _, nivel, cita, coinciden = mejor
    estado = "parcial" if (nivel_pedido == "graduado" and nivel == "estudiante") else "cumple"
    return Equivalencia(estado, coinciden, cita, nivel, nivel_pedido, pedido)


_PALABRAS_NIVEL = {"estudiante", "estudiantes", "avanzado", "avanzada", "avanzados", "graduado", "graduada", "licenciado",
                   "licenciada", "titulo", "universitario", "universitaria", "terciario", "terciaria", "tecnico", "tecnica",
                   "recien", "egresado", "egresada", "titulado", "titulada", "en", "curso", "de", "o", "u", "y", "con",
                   "estudios", "superiores", "completos", "completo", "afines", "carrera", "grado", "a", "o", "as", "os", "a/o"}


def evaluar_nivel(texto: str, cv_texto: str) -> Equivalencia | None:
    """Requisito de formación que dice solo el NIVEL, sin carrera («Estudiante avanzado», «Graduado/a»).
    Se compara con el mejor nivel de estudios formales del CV. None si el texto nombra algo más."""
    palabras = normalizar(texto).replace("/", " ").split()
    if not palabras or any(p.strip(".,;:()") not in _PALABRAS_NIVEL for p in palabras):
        return None
    pedido = _nivel_pedido(texto) or ""
    mejor: tuple[int, str, str] | None = None
    for linea, _ln, nivel in _lineas_de_estudio(cv_texto):
        rango = {"graduado": 2, "": 1, "estudiante": 0}[nivel]
        if mejor is None or rango > mejor[0]:
            mejor = (rango, nivel, linea)
    if mejor is None:
        return Equivalencia("no", [], "", "", pedido, texto)
    _, nivel, cita = mejor
    estado = "parcial" if (pedido == "graduado" and nivel == "estudiante") else "cumple"
    return Equivalencia(estado, [], cita, nivel, pedido, texto)


# ----------------------------------------------------------------------------- cursos y certificaciones
# Curso, diplomatura, certificación, capacitación y taller se consideran equivalentes entre sí.
_RE_CURSO_PEDIDO = re.compile(r"\b(cursos?|diplomaturas?|diplomados?|certificacion(?:es)?|capacitacion(?:es)?|talleres?|"
                              r"bootcamp|seminarios?|workshops?|formacion complementaria)\b")
_OFRECE = re.compile(r"ofrecemos|brindamos|te damos|beneficios?|plan de|oportunidad|incluye|posibilidad|acceso a|constantes|"
                     r"te capacitamos|capacitacion continua|capacitacion interna")
_PALABRAS_CURSO = {"curso", "cursos", "diplomatura", "diplomaturas", "diplomado", "diplomados", "certificacion", "certificaciones",
                   "capacitacion", "capacitaciones", "taller", "talleres", "bootcamp", "seminario", "seminarios", "workshop",
                   "workshops", "formacion", "complementaria", "de", "en", "sobre", "con", "y", "o", "u", "el", "la", "los", "las",
                   "del", "al", "un", "una", "basico", "basica", "intermedio", "avanzado", "avanzada", "minimo", "previo", "previa",
                   "realizado", "realizada", "completo", "completa", "afines", "afin", "requisito", "requisitos",
                   "requiere", "requerido", "excluyente", "deseable", "valora", "suma", "plus"}


def es_curso(texto: str) -> bool:
    n = normalizar(texto)
    return bool(_RE_CURSO_PEDIDO.search(n)) and not _OFRECE.search(n) and not re.search(r"\bestudiante|licenciad|tecnicatura", n)


def tema_de_curso(texto: str) -> list[str]:
    return _tema(texto)


def _tema(texto: str) -> list[str]:
    return [t[:5] for t in re.findall(r"[a-z0-9]+", normalizar(texto)) if len(t) >= 3 and t not in _PALABRAS_CURSO]


@dataclass
class ResultadoCurso:
    puntaje: int
    cita: str
    pedido: str


def evaluar_cursos(pedidos: list[str], cv_texto: str) -> ResultadoCurso | None:
    """Puntaje (0-100) de cuánto del tema pedido aparece en un curso/diplomatura/certificación (o estudio) del CV."""
    if not pedidos:
        return None
    lineas = []
    for linea in cv_texto.splitlines():
        ln = normalizar(linea)
        if not ln.strip():
            continue
        if _RE_CURSO_PEDIDO.search(ln.replace("en curso", "")) or _PALABRAS_ESTUDIO.search(ln):
            lineas.append((linea.strip(" -*#\t"), ln.split()))
    total, citas = [], []
    for pedido in pedidos:
        tema = _tema(pedido)
        mejor, cita = 0.0, ""
        for linea, palabras in lineas:
            if not tema:
                frac = 1.0 if _RE_CURSO_PEDIDO.search(" ".join(palabras).replace("en curso", "")) else 0.0
            else:
                frac = sum(any(w.startswith(r) for w in palabras) for r in tema) / len(tema)
            if frac > mejor:
                mejor, cita = frac, linea
        total.append(mejor)
        if cita and mejor > 0:
            citas.append(cita)
    return ResultadoCurso(round(100 * sum(total) / len(total)), " | ".join(dict.fromkeys(citas))[:300], "; ".join(pedidos))
