"""Lectura del CV: archivo -> texto limpio -> datos estructurados.

Combina reglas (vocabulario de herramientas, idiomas) con el modelo, y descarta todo
lo que el modelo "extraiga" pero no esté realmente escrito en el CV (anti-invención).
"""
from __future__ import annotations

import html
import io
import re
import zipfile
from dataclasses import dataclass, field

from servicios.config import Config
from servicios.llm_client import SalidaInvalida
from servicios.prompts import cargar
from servicios.schemas import CVEstructurado
from servicios.texto import delimitar, normalizar, respaldado, truncar
from servicios.vocabulario import es_ruidosa, herramientas_en_texto, idiomas_en_texto

MIN_CHARS = 80


class ErrorArchivo(ValueError):
    """Problema con el archivo o el texto; el mensaje se le muestra a la persona."""


@dataclass
class CVProcesado:
    texto: str
    recortado: bool
    estructura: CVEstructurado
    herramientas: list[str]
    idiomas: list[str]
    avisos: list[str] = field(default_factory=list)

    @property
    def texto_norm(self) -> str:
        return normalizar(self.texto)


def limpiar_texto(texto: str) -> str:
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", texto)
    texto = re.sub(r"[ \t]+\n", "\n", texto)
    return re.sub(r"\n{3,}", "\n\n", texto).strip()


def leer_archivo(nombre: str, contenido: bytes) -> str:
    """Devuelve el texto de un .txt, .md, .docx o .pdf."""
    ext = nombre.lower().rsplit(".", 1)[-1] if "." in nombre else ""
    if ext in ("txt", "md"):
        for cod in ("utf-8", "latin-1"):
            try:
                return limpiar_texto(contenido.decode(cod))
            except UnicodeDecodeError:
                continue
    if ext == "docx":
        try:
            with zipfile.ZipFile(io.BytesIO(contenido)) as z:
                xml = z.read("word/document.xml").decode("utf-8")
        except (zipfile.BadZipFile, KeyError) as e:
            raise ErrorArchivo("No pude abrir el .docx. Probá guardarlo de nuevo o pegá el texto.") from e
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<w:(?:tab|br)\s*/>", " ", xml)
        return limpiar_texto(html.unescape(re.sub(r"<[^>]+>", "", xml)))
    if ext == "pdf":
        try:
            from pypdf import PdfReader
        except ImportError as e:
            raise ErrorArchivo("Para leer PDF hace falta `pip install pypdf`. También podés pegar el texto del CV.") from e
        try:
            texto = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(contenido)).pages)
        except Exception as e:  # pypdf lanza varios tipos de error según el archivo
            raise ErrorArchivo("No pude leer el PDF. Pegá el texto del CV.") from e
        if len(texto.strip()) < MIN_CHARS:
            raise ErrorArchivo("El PDF no tiene texto seleccionable (¿es una imagen escaneada?). Pegá el texto del CV.")
        return limpiar_texto(texto)
    raise ErrorArchivo(f"Formato no soportado (`.{ext}`). Usá .txt, .md, .docx o .pdf, o pegá el texto.")


def _sin_ruido(nombres: list[str], texto: str) -> list[str]:
    """Palabras ambiguas (Make, Teams, Word...) solo cuentan si están escritas con su mayúscula."""
    return [n for n in nombres if not es_ruidosa(n) or re.search(rf"\b{re.escape(n)}\b", texto)]


def _unir(*listas: list[str]) -> list[str]:
    vistos, salida = set(), []
    for lista in listas:
        for x in lista:
            k = normalizar(x)
            if k and k not in vistos:
                vistos.add(k)
                salida.append(x.strip())
    return salida


def _unir_idiomas(detectados: list[str], del_modelo: list[str]) -> list[str]:
    """Prefiere la versión del modelo (con nivel, p. ej. "Inglés intermedio (B1)") si menciona el idioma."""
    salida = []
    for nombre in detectados:
        con_nivel = next((m for m in del_modelo if normalizar(nombre) in normalizar(m)), None)
        salida.append(con_nivel or nombre)
    return _unir(salida, del_modelo)


def parsear_cv(texto: str, llm, cfg: Config, vocabulario_extra: list[str] | None = None) -> CVProcesado:
    texto = limpiar_texto(texto)
    if len(texto) < MIN_CHARS:
        raise ErrorArchivo("El CV está vacío o es muy corto. Pegá el texto completo.")
    texto, recortado = truncar(texto, cfg.max_cv_chars)
    avisos = []
    if recortado:
        avisos.append(f"El CV era largo y se usaron solo los primeros {cfg.max_cv_chars} caracteres.")

    try:
        est = llm.chat_json(cargar("cv_extraer"), delimitar("cv", texto), CVEstructurado, rol="principal",
                            max_tokens=1200)
    except SalidaInvalida:
        est = CVEstructurado()
        avisos.append("El modelo no pudo estructurar el CV; sigo con lo que detecto por reglas (puede quedar incompleto).")

    # Lo que el modelo dice pero el CV no contiene, se descarta.
    est.herramientas = [h for h in est.herramientas if respaldado(h, texto)]
    est.idiomas = [i for i in est.idiomas if respaldado(i, texto)]
    for e in est.experiencias:
        e.logros = [x for x in e.logros if respaldado(x, texto, umbral=0.6)]
    if est.anios_experiencia is not None and not 0 <= est.anios_experiencia <= 40:
        est.anios_experiencia = None

    herramientas = _unir(_sin_ruido(herramientas_en_texto(texto, vocabulario_extra), texto), est.herramientas)
    idiomas = _unir_idiomas(idiomas_en_texto(texto), est.idiomas)
    return CVProcesado(texto=texto, recortado=recortado, estructura=est, herramientas=herramientas,
                       idiomas=idiomas, avisos=avisos)
