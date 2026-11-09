"""Verificador anti-invención.

Compara un texto generado (CV adaptado o carta) con el CV original y marca lo que no está
respaldado: cifras, herramientas, nombres propios (empleadores, instituciones) y títulos.
Son reglas simples y reproducibles; no reemplazan la lectura de la persona, la ayudan.
Pueden dar falsos positivos (se prefiere avisar de más antes que dejar pasar una invención).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from servicios.cv_parser import _sin_ruido
from servicios.texto import contiene_termino, normalizar
from servicios.genero import marcas_de_genero
from servicios.vocabulario import (ALIAS_CATEGORIA, categoria_herramienta, herramienta_cubierta,
                                   herramientas_en_texto)

PALABRAS_NUMERO = {"un": 1, "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
                   "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12}
TITULOS = {"graduado", "graduada", "egresado", "egresada", "licenciado", "licenciada", "magister", "maestria",
           "master", "posgrado", "doctorado", "doctor", "doctora", "diplomatura", "tecnicatura"}
CONECTORES = {"de", "del", "la", "las", "los", "y", "e", "da", "do", "von", "van"}
# Palabras con mayúscula que son normales en un CV o una carta y no son nombres propios inventados.
NO_PROPIOS = set("""perfil experiencia profesional formacion educacion herramientas idiomas objetivo resumen habilidades
competencias logros estudios contacto referencias cursos certificaciones proyectos datos personales laboral academica
academico tecnicas destacadas adicional adicionales conocimientos informaticos informatica estimado estimada estimados
hola saludos atentamente cordialmente cordial buenos dias tardes noches equipo seleccion recursos humanos gracias quedo
disposicion muchas att postulacion carta presentacion cv ia pyme pymes argentina buenos aires caba gba enero febrero
marzo abril mayo junio julio agosto septiembre setiembre octubre noviembre diciembre lunes martes miercoles jueves
viernes sabado domingo en curso actualidad remoto hibrido presencial nivel intermedio avanzado basico nativo""".split())

_RE_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_RE_TOKEN = re.compile(r"\w+(?:[&'’.-]\w+)*")


@dataclass
class Hallazgo:
    tipo: str  # "cifra" | "herramienta" | "categoría" | "género" | "nombre propio" | "título"
    fragmento: str  # texto exacto dentro del generado, para resaltarlo
    contexto: str
    motivo: str


def _norm_num(s: str) -> str:
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        return s.replace(".", "")
    return s.replace(",", ".")


def _numeros(texto: str) -> set[str]:
    salida = {_norm_num(m) for m in _RE_NUM.findall(texto)}
    for m in re.finditer(r"\b(" + "|".join(PALABRAS_NUMERO) + r")\s+(?:años|año|meses|mes)\b", texto, re.I):
        salida.add(str(PALABRAS_NUMERO[m.group(1).lower()]))
    return salida


def _limpiar_markdown(texto: str) -> str:
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"(?m)^\s*(?:[-*+>#]+|\d+[.)])\s+", "", texto)
    return re.sub(r"[*_`]+", "", texto)


def _contexto(texto: str, ini: int, largo: int) -> str:
    return texto[max(0, ini - 45): ini + largo + 45].replace("\n", " ").strip()


def _palabras_permitidas(*textos: str) -> set[str]:
    return {p for t in textos for p in normalizar(t).split()} | NO_PROPIOS


_RE_CATEGORIA = re.compile(r"(?:herramientas|plataformas|programas|softwares?|tecnolog[ií]as|recursos)\s+de\s+"
                           r"(?P<cat>[A-Za-zÁÉÍÓÚáéíóúñ ]{2,30}?)\s*(?:como|tales como|:|,\s*como|\(como)\s+"
                           r"(?P<lista>[^.;\n]{3,140})", re.I)


def verificar(generado: str, cv_texto: str, oferta_texto: str = "", vocabulario_extra: list[str] | None = None,
              genero: str | None = None) -> list[Hallazgo]:
    """Devuelve lo que el texto generado dice y el CV no respalda (lista vacía = nada que marcar)."""
    hallazgos: list[Hallazgo] = []
    vistos: set[tuple[str, str]] = set()

    def agregar(tipo: str, frag: str, ini: int, motivo: str):
        if (tipo, frag.lower()) not in vistos:
            vistos.add((tipo, frag.lower()))
            hallazgos.append(Hallazgo(tipo, frag, _contexto(generado, ini, len(frag)), motivo))

    cv_norm = normalizar(cv_texto)

    # 1) cifras y años
    del_cv = _numeros(cv_texto)
    for m in _RE_NUM.finditer(generado):
        linea_ini = generado.rfind("\n", 0, m.start()) + 1
        if re.fullmatch(r"\s*\d+[.)]\s*", generado[linea_ini:m.end()]):
            continue  # numeración de lista
        if _norm_num(m.group()) not in del_cv:
            agregar("cifra", m.group(), m.start(), f"La cifra «{m.group()}» no figura en el CV.")
    for m in re.finditer(r"\b(" + "|".join(PALABRAS_NUMERO) + r")\s+(?:años|año|meses|mes)\b", generado, re.I):
        if str(PALABRAS_NUMERO[m.group(1).lower()]) not in del_cv:
            agregar("cifra", m.group(), m.start(), f"«{m.group()}» no figura en el CV.")

    # 2) herramientas
    for h in _sin_ruido(herramientas_en_texto(generado, vocabulario_extra), generado):
        if not herramienta_cubierta(h, cv_norm):
            m = re.search(rf"(?<!\w){re.escape(h)}(?!\w)", generado, re.I)
            if m:
                agregar("herramienta", m.group(), m.start(), f"La herramienta «{h}» no figura en el CV.")

    # 2b) categoría equivocada: «herramientas de IA como Meta Ads y Excel»
    for m in _RE_CATEGORIA.finditer(generado):
        cat = ALIAS_CATEGORIA.get(normalizar(m.group("cat")))
        if not cat:
            continue
        lista = re.split(r"\s+(?:y\s+)?(?:en\s+)?(?:herramientas|plataformas|programas|softwares?)\b", m.group("lista"))[0]
        for h in herramientas_en_texto(lista, vocabulario_extra):
            real = categoria_herramienta(h)
            if real and real != cat:
                ini = generado.find(h, m.start())
                agregar("categoría", h, ini if ini >= 0 else m.start(),
                        f"«{h}» no es una herramienta de {cat} (es de {real}).")

    # 2c) género gramatical
    for frag, motivo in marcas_de_genero(generado, genero or "?"):
        agregar("género", frag, max(generado.find(frag), 0), motivo)

    # 3) títulos y estudios
    for m in _RE_TOKEN.finditer(generado):
        n = normalizar(m.group())
        if n in TITULOS and not contiene_termino(cv_norm, n):
            agregar("título", m.group(), m.start(), f"«{m.group()}» no figura en el CV (¿estudios o título que no tenés?).")

    # 4) nombres propios (empleadores, instituciones, marcas)
    limpio = _limpiar_markdown(generado)
    permitidas = _palabras_permitidas(cv_texto, oferta_texto)
    tokens = list(_RE_TOKEN.finditer(limpio))
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if not (t.group()[0].isupper() and not t.group().isdigit()):
            i += 1
            continue
        run = [t]
        j = i + 1
        while j < len(tokens) and limpio[tokens[j - 1].end():tokens[j].start()].strip() == "":
            if tokens[j].group()[0].isupper():
                run.append(tokens[j]); j += 1
            elif (tokens[j].group().lower() in CONECTORES and j + 1 < len(tokens)
                  and tokens[j + 1].group()[0].isupper()
                  and limpio[tokens[j].end():tokens[j + 1].start()].strip() == ""):
                run += [tokens[j], tokens[j + 1]]; j += 2
            else:
                break
        i = j
        previo = limpio[:run[0].start()].rstrip(" \t")
        inicio_oracion = not previo or previo[-1] in ".!?:\n¡¿"
        if len(run) == 1 and inicio_oracion:
            continue
        frag = limpio[run[0].start():run[-1].end()]
        if herramientas_en_texto(frag, vocabulario_extra):
            continue  # ya lo cubre el control de herramientas
        palabras = [w for r in run for w in normalizar(r.group()).split() if w not in CONECTORES]
        if any(p not in permitidas for p in palabras):
            ini = generado.find(frag)
            agregar("nombre propio", frag, ini if ini >= 0 else 0, f"«{frag}» no figura en el CV ni en la oferta.")
    return hallazgos
