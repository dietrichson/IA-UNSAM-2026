"""Modelo simulado para probar el evaluador sin Ollama (`--simulado`). No mide la calidad de ningún modelo real."""
from __future__ import annotations

import hashlib
import re

from servicios.matcher import EvaluacionLLM
from servicios.schemas import Criterio
from servicios.texto import normalizar, palabras


class LLMSimulado:
    def __init__(self):
        self.metricas: list[dict] = []

    def estado(self):
        return True, "Simulado."

    def resumen_metricas(self) -> dict:
        return {"llamadas": len(self.metricas), "segundos": 0.0, "por_tipo": {}}

    @staticmethod
    def _bloque(user: str, etiqueta: str) -> str:
        m = re.search(rf"<{etiqueta}>\n(.*?)\n</{etiqueta}>", user, re.S)
        return m.group(1) if m else ""

    def chat_json(self, system, user, modelo, **kw):
        self.metricas.append({"tipo": "chat_json"})
        if modelo is EvaluacionLLM:
            cv, puesto = self._bloque(user, "cv"), self._bloque(user, "puesto")
            a, b = set(palabras(cv, 5)), set(palabras(puesto, 5))
            p = 20 + int(70 * len(a & b) / max(len(b), 1))
            cita = next((l.strip(" -*#") for l in cv.splitlines() if len(l.strip(" -*#")) > 30), "")
            c = lambda x: Criterio(puntaje=x, evidencia=[cita] if cita else [], comentario="Evaluación simulada.")
            return EvaluacionLLM(experiencia=c(p), formacion=c(p), resumen="Simulado.")
        return modelo()

    def chat_texto(self, system, user, **kw):
        self.metricas.append({"tipo": "chat_texto"})
        cv = self._bloque(user, "cv")
        if "carta de presentación" in system:
            lineas = [l for l in cv.splitlines() if l.strip().startswith("-")][:3]
            return "Estimado equipo de selección:\n\nMe postulo al puesto. " + " ".join(l.strip(" -*") for l in lineas) + "\n\nSaludos."
        return cv

    def embeber(self, textos):
        self.metricas.append({"tipo": "embeddings"})
        salida = []
        for t in textos:
            v = [0.0] * 256
            for w in palabras(t, 4):
                v[int(hashlib.md5(normalizar(w).encode()).hexdigest(), 16) % 256] += 1
            salida.append(v)
        return salida
