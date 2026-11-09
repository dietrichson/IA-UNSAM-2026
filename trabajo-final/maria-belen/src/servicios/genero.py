"""Género gramatical de la persona (para redactar en primera persona sin «o/a» ni «(a)»).

Se infiere del CV por reglas (título, cargos, participios) y la persona puede elegirlo a mano.
Valores: "f" (femenino), "m" (masculino), "n" (neutro: se evitan adjetivos con género) o None (no se pudo inferir).
"""
from __future__ import annotations

import re

from servicios.texto import normalizar

GENEROS = {"auto": "Detectar del CV", "f": "Femenino", "m": "Masculino", "n": "Neutro (sin marcar género)"}

# raíz + terminación o/a (se cuenta cada variante en el CV)
_RAICES = ["licenciad", "graduad", "egresad", "titulad", "comunicador", "diseñador", "disenador", "redactor", "editor",
           "coordinador", "creador", "analista de datos", "productor", "estudiante avanzad", "estudiante recién graduad",
           "tecnic", "técnic", "periodista", "apasionad", "motivad", "interesad", "entusiasmad", "comprometid",
           "responsable", "organizad", "autodidact", "proactiv", "capacitad", "especializad", "bilingu", "bilingü",
           "colaborador", "emprendedor", "fotograf", "publicist", "asistente", "director", "gerent", "jefe", "jefa"]
_F = re.compile(r"\b(licenciada|graduada|egresada|titulada|comunicadora|diseñadora|disenadora|redactora|editora|coordinadora|"
                r"creadora|productora|estudiante avanzada|técnica|tecnica|apasionada|motivada|interesada|entusiasmada|"
                r"comprometida|organizada|capacitada|especializada|colaboradora|emprendedora|directora|gerenta|jefa|"
                r"practicante|pasante)\b", re.I)
_M = re.compile(r"\b(licenciado|graduado|egresado|titulado|comunicador|diseñador|disenador|redactor|editor|coordinador|"
                r"creador|productor|estudiante avanzado|técnico|tecnico|apasionado|motivado|interesado|entusiasmado|"
                r"comprometido|organizado|capacitado|especializado|colaborador|emprendedor|director|gerente|jefe)\b", re.I)
_F_ESTRICTO = re.compile(r"\b(licenciada|graduada|egresada|titulada|comunicadora|diseñadora|redactora|editora|coordinadora|"
                         r"estudiante avanzada|apasionada|motivada|interesada|entusiasmada|comprometida)\b", re.I)


def inferir_genero(cv_texto: str) -> str | None:
    """'f' / 'm' si el CV lo marca de forma consistente; None si no hay señales o se contradicen."""
    f = len(_F_ESTRICTO.findall(cv_texto)) + len(re.findall(r"\b(licenciada|estudiante avanzada)\b", cv_texto, re.I))
    m = len(_M.findall(cv_texto))
    if f and not m:
        return "f"
    if m and not f:
        return "m"
    if f and m:
        return "f" if f >= 2 * m else ("m" if m >= 2 * f else None)
    return None


def resolver_genero(preferencia: str | None, cv_texto: str) -> str:
    """'auto'/None -> se infiere; si no se puede, 'n' (neutro)."""
    if preferencia in ("f", "m", "n"):
        return preferencia
    return inferir_genero(cv_texto) or "n"


def instruccion_genero(genero: str) -> str:
    base = ("Nunca uses marcas como «o/a», «a/o», «(a)», «@», «x» ni «e» para el género: escribí una sola forma. ")
    if genero == "f":
        return ("\nGénero: la persona es mujer. Escribí en primera persona en femenino (por ejemplo «emocionada», "
                "«interesada», «graduada»). " + base)
    if genero == "m":
        return ("\nGénero: la persona es varón. Escribí en primera persona en masculino (por ejemplo «emocionado», "
                "«interesado», «graduado»). " + base)
    return ("\nGénero: no se conoce. Evitá adjetivos y participios que marquen género en primera persona: usá "
            "construcciones neutras («me entusiasma», «tengo interés en», «cuento con»), no «emocionado» ni «emocionada». "
            + base)


_PARES = [  # (patrón sobre la palabra con ambas formas, raíz con grupo 1)
    re.compile(r"\b(\w+?)o/a\b", re.I), re.compile(r"\b(\w+?)a/o\b", re.I),
    re.compile(r"\b(\w+?)o\s?\(a\)", re.I), re.compile(r"\b(\w+?)a\s?\(o\)", re.I),
    re.compile(r"\b(\w+?)o/as?\b", re.I),
]
_EXCEPCIONES = {"el": "ella", "los": "las"}


def resolver_marcas(texto: str, genero: str) -> str:
    """Reemplaza «emocionado/a», «emocionado(a)», «Estimado/a» por una sola forma según el género.
    En neutro no se toca (lo marca el verificador)."""
    # «Estimado/a equipo»: «equipo» es masculino, el saludo no depende del género de quien escribe
    texto = re.sub(r"\bEstimad[oa]s?\s*(?:/\s*[oa]s?|\(\w\))?\s+(equipo|equipos|comité|comite)\b", r"Estimado \1", texto,
                   flags=re.I)
    if genero not in ("f", "m"):
        return texto
    fin = "a" if genero == "f" else "o"

    def sub(m):
        raiz = m.group(1)
        return raiz + fin if raiz else m.group(0)

    for pat in _PARES:
        texto = pat.sub(sub, texto)
    texto = re.sub(r"\b(\w+?)\(a\)", lambda m: m.group(1) + ("a" if genero == "f" else ""), texto) if genero == "f" else texto
    texto = re.sub(r"\b(\w+?)\(o\)", lambda m: m.group(1) + "o", texto) if genero == "m" else texto
    return texto


_ADJETIVOS = ("emocionad", "interesad", "motivad", "entusiasmad", "orgullos", "agradecid", "convencid", "comprometid",
              "apasionad", "capacitad", "preparad", "encantad", "contentos", "content", "seguro", "segura")
_RE_ADJ = re.compile(r"\b(?:estoy|me siento|me encuentro|soy|estaría|estaria|quedo|quedaría)\s+(?:muy\s+|más\s+|bastante\s+)?"
                     r"(\w+?)(o|a)\b", re.I)


def marcas_de_genero(texto: str, genero: str) -> list[tuple[str, str]]:
    """[(fragmento, motivo)] de lo que rompe la concordancia: «o/a»/«(a)» o un adjetivo del género contrario
    (o con género, si se pidió neutro)."""
    salida: list[tuple[str, str]] = []
    for m in re.finditer(r"\b\w+(?:o/a|a/o|o\s?\(a\)|a\s?\(o\)|\(a\)|\(o\)|o/as|@)(?=\W|$)", texto, re.I):
        salida.append((m.group(), "Marca de género doble («o/a», «(a)»): la carta debe usar una sola forma."))
    for m in _RE_ADJ.finditer(texto):
        raiz, fin = m.group(1).lower(), m.group(2).lower()
        if not any(raiz.startswith(a.rstrip("o")) or raiz + fin == a for a in _ADJETIVOS):
            continue
        if genero == "f" and fin == "o":
            salida.append((m.group(), "La persona es mujer: debería concordar en femenino."))
        elif genero == "m" and fin == "a":
            salida.append((m.group(), "La persona es varón: debería concordar en masculino."))
        elif genero == "n":
            salida.append((m.group(), "Género desconocido: conviene una redacción neutra (p. ej. «me entusiasma»)."))
    return salida
