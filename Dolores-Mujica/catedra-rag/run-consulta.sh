#!/usr/bin/env bash
# Consulta única de RAG sobre el material del Asistente de Cátedra.
# Uso: ./run-consulta.sh "¿Qué es el signo lingüístico?"
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"

if python3 -c "import ollama, numpy" 2>/dev/null; then
    exec python3 "$AQUI/consulta-unica.py" "$@"
elif command -v uv >/dev/null 2>&1; then
    exec uv run --with ollama --with numpy python3 "$AQUI/consulta-unica.py" "$@"
else
    echo "Faltan las librerías 'ollama' y 'numpy', y no encontré uv." >&2
    echo "Instalá uv (https://docs.astral.sh/uv/) o corré: pip install ollama numpy" >&2
    exit 1
fi
