"""Ollama falso mínimo para probar el cliente sin Ollama instalado (solo para tests)."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class OllamaFalso:
    def __init__(self):
        self.modelos = ["qwen2.5:3b", "bge-m3:latest"]
        self.respuestas: list[str] = []  # contenidos que devolverá /api/chat, en orden
        self.pedidos: list[dict] = []
        self.url = ""


@pytest.fixture
def ollama_falso():
    estado = OllamaFalso()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _responder(self, codigo, datos):
            cuerpo = json.dumps(datos).encode()
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)

        def do_GET(self):
            self._responder(200, {"models": [{"name": m} for m in estado.modelos]})

        def do_POST(self):
            datos = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            estado.pedidos.append({"ruta": self.path, **datos})
            if datos["model"] not in estado.modelos and f"{datos['model']}:latest" not in estado.modelos:
                return self._responder(404, {"error": f"model '{datos['model']}' not found"})
            if self.path == "/api/embed":
                return self._responder(200, {"embeddings": [[float(len(t)), 1.0] for t in datos["input"]]})
            contenido = estado.respuestas.pop(0) if estado.respuestas else "{}"
            self._responder(200, {"message": {"role": "assistant", "content": contenido}})

    servidor = HTTPServer(("127.0.0.1", 0), H)
    estado.url = f"http://127.0.0.1:{servidor.server_port}"
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield estado
    servidor.shutdown()
