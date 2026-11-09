"""Cliente de modelos de lenguaje con un único punto de entrada.

El resto del código llama solo a `chat_texto`, `chat_json` y `embeber`; no sabe qué
proveedor hay detrás. Por defecto es Ollama local (gratis, los datos no salen de la compu).
Gemini y Claude son opcionales y se activan por `.env`. Solo usa la biblioteca estándar.
"""
from __future__ import annotations

import contextlib
import json
import re
import time
import urllib.error
import urllib.request
from typing import Callable, TypeVar

from pydantic import BaseModel, ValidationError

from servicios.config import Config

T = TypeVar("T", bound=BaseModel)

CARACTERES_POR_TOKEN = 3.2  # estimación conservadora para español con modelos tipo Qwen


class LLMError(Exception):
    """Error al hablar con el modelo; el mensaje está escrito para mostrárselo a la persona."""


class ModeloNoDisponible(LLMError):
    pass


class ContextoExcedido(LLMError):
    pass


class SalidaInvalida(LLMError):
    pass


def estimar_tokens(texto: str) -> int:
    return int(len(texto) / CARACTERES_POR_TOKEN) + 1


def extraer_json(texto: str) -> str:
    """Saca el JSON de una respuesta que puede traer ```json ... ``` o texto alrededor."""
    t = texto.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S | re.I)
    if m:
        t = m.group(1).strip()
    ini, fin = t.find("{"), t.rfind("}")
    return t[ini:fin + 1] if ini != -1 and fin > ini else t


Http = Callable[[str, dict | None, dict, int], dict]


def _http_urllib(url: str, payload: dict | None, headers: dict, timeout: int) -> dict:
    datos = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=datos, headers={"Content-Type": "application/json", **headers},
                                 method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", "replace")[:400]
        raise LLMError(f"HTTP {e.code} desde {url.split('?')[0]}: {cuerpo}") from e
    except urllib.error.URLError as e:
        raise LLMError(f"No se pudo conectar a {url.split('?')[0]} ({e.reason}).") from e
    except TimeoutError as e:
        raise LLMError(f"El modelo tardó más de {timeout} s en responder. Probá con menos puestos o un texto más corto.") from e
    except json.JSONDecodeError as e:
        raise LLMError("La respuesta del servidor no era JSON válido.") from e


class LLMClient:
    def __init__(self, config: Config, http: Http | None = None):
        self.cfg = config
        self._http = http or _http_urllib
        self._ultima_llamada = 0.0
        self.metricas: list[dict] = []  # una fila por llamada: tipo, modelo, segundos, ok (nunca guarda el contenido)

    # ------------------------------------------------------------- API pública
    def chat_texto(self, system: str, user: str, rol: str = "principal", temperatura: float = 0.3,
                   max_tokens: int = 1200) -> str:
        return self._chat([{"role": "system", "content": system}, {"role": "user", "content": user}],
                          rol, temperatura, max_tokens, esquema=None)

    def chat_json(self, system: str, user: str, modelo: type[T], rol: str = "principal",
                  temperatura: float = 0.1, max_tokens: int = 1200) -> T:
        """Pide JSON y lo valida con `modelo`. Si falla, reintenta una vez diciéndole el error."""
        esquema = modelo.model_json_schema()
        mensajes = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        ultimo_error = ""
        for intento in range(2):
            crudo = self._chat(mensajes, rol, temperatura, max_tokens, esquema=esquema)
            try:
                return modelo.model_validate_json(extraer_json(crudo))
            except (ValidationError, ValueError) as e:
                ultimo_error = str(e).splitlines()[0][:200] if str(e) else "JSON inválido"
                mensajes = mensajes + [
                    {"role": "assistant", "content": crudo[:1500]},
                    {"role": "user", "content": "Tu respuesta no es un JSON válido para el esquema pedido "
                                                f"({ultimo_error}). Respondé de nuevo solo con el JSON corregido."},
                ]
        raise SalidaInvalida(f"El modelo no devolvió un JSON válido después de reintentar ({ultimo_error}).")

    def embeber(self, textos: list[str]) -> list[list[float]]:
        if not textos:
            return []
        with self._medir("embeddings", self.cfg.modelo_embeddings):
            if self.cfg.embeddings_provider == "gemini":
                return self._embeber_gemini(textos)
            return self._embeber_ollama(textos)

    def resumen_metricas(self) -> dict:
        """Cantidad de llamadas y tiempo, total y por tipo (para la evaluación). No incluye texto de CV ni de ofertas."""
        por_tipo: dict[str, dict] = {}
        for m in self.metricas:
            t = por_tipo.setdefault(m["tipo"], {"llamadas": 0, "segundos": 0.0, "errores": 0})
            t["llamadas"] += 1
            t["segundos"] = round(t["segundos"] + m["segundos"], 3)
            t["errores"] += 0 if m["ok"] else 1
        return {"llamadas": len(self.metricas), "segundos": round(sum(m["segundos"] for m in self.metricas), 3),
                "por_tipo": por_tipo}

    def estado(self) -> tuple[bool, str]:
        """Chequeo rápido para mostrar en la interfaz. Devuelve (ok, mensaje)."""
        if self.cfg.provider == "ollama" or self.cfg.embeddings_provider == "ollama":
            try:
                datos = self._http(f"{self.cfg.ollama_url}/api/tags", None, {}, 5)
            except LLMError:
                return False, (f"No encuentro Ollama en {self.cfg.ollama_url}. Abrí la aplicación de Ollama "
                               "(o ejecutá `ollama serve`) y recargá la página.")
            instalados = {m.get("name", "") for m in datos.get("models", [])}
            pedidos = []
            if self.cfg.provider == "ollama":
                pedidos += [self.cfg.modelo_principal, self.cfg.modelo_liviano]
            if self.cfg.embeddings_provider == "ollama":
                pedidos.append(self.cfg.modelo_embeddings)
            faltan = [m for m in dict.fromkeys(pedidos) if not self._instalado(m, instalados)]
            if faltan:
                return False, "Falta descargar: " + ", ".join(f"`ollama pull {m}`" for m in faltan)
        if self.cfg.provider == "gemini" and not self.cfg.gemini_api_key:
            return False, "Falta GEMINI_API_KEY en el archivo .env."
        if self.cfg.provider == "claude" and not self.cfg.anthropic_api_key:
            return False, "Falta ANTHROPIC_API_KEY en el archivo .env."
        return True, "Listo."

    # ------------------------------------------------------------- internos
    @staticmethod
    def _instalado(modelo: str, instalados: set[str]) -> bool:
        return modelo in instalados or (":" not in modelo and f"{modelo}:latest" in instalados)

    def _modelo(self, rol: str) -> str:
        return self.cfg.modelo_liviano if rol == "liviano" else self.cfg.modelo_principal

    def _esperar(self):
        falta = self.cfg.min_intervalo_s - (time.monotonic() - self._ultima_llamada)
        if falta > 0:
            time.sleep(falta)
        self._ultima_llamada = time.monotonic()

    @contextlib.contextmanager
    def _medir(self, tipo: str, modelo: str):
        t0, ok = time.monotonic(), False
        try:
            yield
            ok = True
        finally:
            self.metricas.append({"tipo": tipo, "modelo": modelo, "segundos": round(time.monotonic() - t0, 3), "ok": ok})

    def _chat(self, mensajes: list[dict], rol: str, temperatura: float, max_tokens: int, esquema: dict | None) -> str:
        with self._medir("chat_json" if esquema is not None else "chat_texto", self._modelo(rol)):
            return self._chat_directo(mensajes, rol, temperatura, max_tokens, esquema)

    def _chat_directo(self, mensajes: list[dict], rol: str, temperatura: float, max_tokens: int, esquema: dict | None) -> str:
        self._esperar()
        modelo = self._modelo(rol)
        if self.cfg.provider == "ollama":
            return self._chat_ollama(modelo, mensajes, temperatura, max_tokens, esquema)
        if esquema is not None:  # proveedores en la nube: el esquema va en el prompt
            mensajes = [dict(m) for m in mensajes]
            mensajes[0]["content"] += ("\n\nRespondé únicamente con un objeto JSON que cumpla este esquema:\n"
                                       + json.dumps(esquema, ensure_ascii=False))
        if self.cfg.provider == "gemini":
            return self._chat_gemini(modelo, mensajes, temperatura, max_tokens, esquema is not None)
        return self._chat_claude(modelo, mensajes, temperatura, max_tokens)

    # --- Ollama
    def _chat_ollama(self, modelo, mensajes, temperatura, max_tokens, esquema) -> str:
        entrada = sum(estimar_tokens(m["content"]) for m in mensajes)
        if entrada + max_tokens > self.cfg.num_ctx:
            raise ContextoExcedido(
                f"El pedido es demasiado largo para el modelo (~{entrada} tokens de entrada y hasta {max_tokens} de "
                f"respuesta, con un límite de {self.cfg.num_ctx}). Acortá el CV o la oferta.")
        cuerpo = {"model": modelo, "messages": mensajes, "stream": False, "keep_alive": "10m",
                  "options": {"temperature": temperatura, "num_ctx": self.cfg.num_ctx, "num_predict": max_tokens}}
        if esquema is not None:
            cuerpo["format"] = esquema
        try:
            r = self._http(f"{self.cfg.ollama_url}/api/chat", cuerpo, {}, self.cfg.timeout_s)
        except LLMError as e:
            raise self._traducir_ollama(e, modelo) from e
        contenido = (r.get("message") or {}).get("content")
        if contenido is None:
            raise LLMError("Ollama respondió sin contenido.")
        return contenido

    def _embeber_ollama(self, textos: list[str]) -> list[list[float]]:
        try:
            r = self._http(f"{self.cfg.ollama_url}/api/embed",
                           {"model": self.cfg.modelo_embeddings, "input": textos, "keep_alive": "10m"}, {},
                           self.cfg.timeout_s)
        except LLMError as e:
            raise self._traducir_ollama(e, self.cfg.modelo_embeddings) from e
        vectores = r.get("embeddings")
        if not vectores or len(vectores) != len(textos):
            raise LLMError("Ollama no devolvió los embeddings esperados.")
        return vectores

    def _traducir_ollama(self, e: LLMError, modelo: str) -> LLMError:
        msg = str(e)
        if "HTTP 404" in msg and "not found" in msg.lower():
            return ModeloNoDisponible(f"El modelo `{modelo}` no está descargado. Ejecutá: ollama pull {modelo}")
        if "No se pudo conectar" in msg:
            return LLMError(f"No encuentro Ollama en {self.cfg.ollama_url}. Abrilo (o ejecutá `ollama serve`) y reintentá.")
        return e

    # --- Gemini (opcional; sin probar contra la API real)
    def _chat_gemini(self, modelo, mensajes, temperatura, max_tokens, como_json) -> str:
        sistema = "\n".join(m["content"] for m in mensajes if m["role"] == "system")
        contenidos = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                      for m in mensajes if m["role"] != "system"]
        gen = {"temperature": temperatura, "maxOutputTokens": max_tokens}
        if como_json:
            gen["responseMimeType"] = "application/json"
        cuerpo = {"contents": contenidos, "generationConfig": gen, "systemInstruction": {"parts": [{"text": sistema}]}}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        r = self._http(url, cuerpo, {"x-goog-api-key": self.cfg.gemini_api_key}, self.cfg.timeout_s)
        try:
            return "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"])
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError("Gemini no devolvió texto (¿bloqueado por filtros o sin cuota?).") from e

    def _embeber_gemini(self, textos: list[str]) -> list[list[float]]:
        modelo = self.cfg.modelo_embeddings
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:batchEmbedContents"
        cuerpo = {"requests": [{"model": f"models/{modelo}", "content": {"parts": [{"text": t}]}} for t in textos]}
        r = self._http(url, cuerpo, {"x-goog-api-key": self.cfg.gemini_api_key}, self.cfg.timeout_s)
        try:
            return [e["values"] for e in r["embeddings"]]
        except (KeyError, TypeError) as e:
            raise LLMError("Gemini no devolvió los embeddings esperados.") from e

    # --- Claude (opcional; sin probar contra la API real)
    def _chat_claude(self, modelo, mensajes, temperatura, max_tokens) -> str:
        sistema = "\n".join(m["content"] for m in mensajes if m["role"] == "system")
        resto = [m for m in mensajes if m["role"] != "system"]
        cuerpo = {"model": modelo, "system": sistema, "messages": resto, "max_tokens": max_tokens,
                  "temperature": temperatura}
        r = self._http("https://api.anthropic.com/v1/messages", cuerpo,
                       {"x-api-key": self.cfg.anthropic_api_key, "anthropic-version": "2023-06-01"},
                       self.cfg.timeout_s)
        try:
            return "".join(b.get("text", "") for b in r["content"] if b.get("type") == "text")
        except (KeyError, TypeError) as e:
            raise LLMError("Claude no devolvió texto.") from e
