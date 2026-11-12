"""Cliente de modelo falso para tests de los servicios (sin red ni Ollama)."""
from __future__ import annotations


class LLMFalso:
    def __init__(self, resultado=None, error: Exception | None = None):
        self.resultado, self.error, self.llamadas = resultado, error, []

    def chat_json(self, system, user, modelo, **kw):
        self.llamadas.append({"system": system, "user": user, "modelo": modelo, **kw})
        if self.error:
            raise self.error
        return self.resultado


class LLMGuion:
    """Falso con guion: `textos` se devuelven en orden en chat_texto; `json` en chat_json."""

    def __init__(self, textos=None, json=None, error_json: Exception | None = None):
        self.textos, self.json, self.error_json = list(textos or []), json, error_json
        self.llamadas = []

    def chat_texto(self, system, user, **kw):
        self.llamadas.append({"tipo": "texto", "system": system, "user": user, **kw})
        item = self.textos.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def chat_json(self, system, user, modelo, **kw):
        self.llamadas.append({"tipo": "json", "system": system, "user": user, "modelo": modelo, **kw})
        if self.error_json:
            raise self.error_json
        return self.json


class LLMCompleto:
    """Falso para probar el flujo entero: lee CV, puntúa y genera embeddings (bolsa de palabras)."""

    def __init__(self, puntaje=70, evidencia=("Diseño de piezas gráficas en Canva",), textos=None):
        self.puntaje, self.evidencia, self.llamadas = puntaje, list(evidencia), []
        self.textos = list(textos or [])

    def chat_texto(self, system, user, **kw):
        self.llamadas.append("texto")
        return self.textos.pop(0) if self.textos else "Texto generado sin datos nuevos. " * 5

    def estado(self):
        return True, "Listo."

    def chat_json(self, system, user, modelo, **kw):
        from servicios.matcher import EvaluacionLLM
        from servicios.schemas import Criterio, CVEstructurado, OfertaEstructurada
        self.llamadas.append(modelo.__name__)
        if modelo is EvaluacionLLM:
            c = lambda p: Criterio(puntaje=p, evidencia=self.evidencia, comentario="comentario")
            return EvaluacionLLM(experiencia=c(self.puntaje), formacion=c(self.puntaje),
                                 brechas=[], resumen="Resumen del ajuste.")
        return modelo()

    def embeber(self, textos):
        import hashlib
        from servicios.texto import palabras
        salida = []
        for t in textos:
            v = [0.0] * 256
            for w in palabras(t, 4):
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 256] += 1
            salida.append(v)
        return salida
