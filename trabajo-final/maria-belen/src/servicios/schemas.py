"""Esquemas de las salidas estructuradas (JSON) que se le piden al modelo.

Están pensados para un modelo chico (qwen2.5:3b): todos los campos tienen valor por
defecto y se corrigen los errores típicos (null en lugar de lista, "3 años" en lugar de 3).
Lo que falte o sobre no rompe la validación; lo que cambie el sentido sí la rompe.
"""
from __future__ import annotations

import re
import types
import typing

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _es_lista(anotacion) -> bool:
    return typing.get_origin(anotacion) is list


def _es_opcional_numero(anotacion) -> bool:
    return typing.get_origin(anotacion) in (typing.Union, types.UnionType) and float in typing.get_args(anotacion)


class Base(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    @model_validator(mode="before")
    @classmethod
    def _arreglar(cls, datos):
        if not isinstance(datos, dict):
            return datos
        datos = dict(datos)
        for nombre, campo in cls.model_fields.items():
            valor = datos.get(nombre)
            if _es_lista(campo.annotation):
                if valor is None:
                    datos[nombre] = []
                elif isinstance(valor, (str, dict)):
                    datos[nombre] = [valor]
            elif campo.annotation is str and valor is None:
                datos[nombre] = ""
            elif _es_opcional_numero(campo.annotation) and isinstance(valor, str):
                m = re.search(r"\d+(?:[.,]\d+)?", valor)
                datos[nombre] = float(m.group().replace(",", ".")) if m else None
        return datos

    @field_validator("*", mode="after")
    @classmethod
    def _limpiar_listas(cls, v):
        if isinstance(v, list) and all(isinstance(x, str) for x in v):
            return [x.strip() for x in v if x and x.strip()]
        return v


# ---------------------------------------------------------------- CV y oferta
class Experiencia(Base):
    puesto: str = ""
    organizacion: str = ""
    periodo: str = ""
    logros: list[str] = Field(default_factory=list)


class CVEstructurado(Base):
    titulo_objetivo: str = ""
    formacion: list[str] = Field(default_factory=list)
    experiencias: list[Experiencia] = Field(default_factory=list)
    herramientas: list[str] = Field(default_factory=list)
    idiomas: list[str] = Field(default_factory=list)
    anios_experiencia: float | None = None


class OfertaEstructurada(Base):
    titulo: str = ""
    empresa: str = ""
    requisitos: list[str] = Field(default_factory=list)
    deseables: list[str] = Field(default_factory=list)
    herramientas: list[str] = Field(default_factory=list)
    idiomas: list[str] = Field(default_factory=list)
    palabras_clave: list[str] = Field(default_factory=list)
    seniority: str = ""
    anios_experiencia: float | None = None
    requiere_titulo: str = ""


# ---------------------------------------------------------------- puntaje
class Criterio(Base):
    puntaje: int = Field(default=0, ge=0, le=100)
    evidencia: list[str] = Field(default_factory=list)  # citas textuales del CV
    comentario: str = ""

    @field_validator("puntaje", mode="before")
    @classmethod
    def _acotar(cls, v):
        try:
            return max(0, min(100, int(round(float(v)))))
        except (TypeError, ValueError):
            return 0


class EvaluacionPuesto(Base):
    experiencia: Criterio = Field(default_factory=Criterio)
    formacion: Criterio = Field(default_factory=Criterio)
    seniority: Criterio = Field(default_factory=Criterio)
    otros: Criterio = Field(default_factory=Criterio)
    resumen: str = ""


# ---------------------------------------------------------------- adaptación
class Adaptado(Base):
    cv_markdown: str = ""
    carta: str = ""
    cambios: list[str] = Field(default_factory=list)
