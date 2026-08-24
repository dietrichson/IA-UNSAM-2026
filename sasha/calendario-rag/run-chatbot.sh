#!/usr/bin/env bash
# Chatbot RAG sobre el calendario académico de la Escuela de Humanidades.
# Uso:  ./run-chatbot.sh            (o pasale opciones: ./run-chatbot.sh --top-k 5)
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"

if python3 -c "import ollama, numpy" 2>/dev/null; then
    exec python3 "$AQUI/chatbot.py" "$@"
elif command -v uv >/dev/null 2>&1; then
    exec uv run --with ollama --with numpy python3 "$AQUI/chatbot.py" "$@"
else
    echo "Faltan las librerías 'ollama' y 'numpy', y no encontré uv." >&2
    echo "Instalá uv (https://docs.astral.sh/uv/) o corré: pip install ollama numpy" >&2
    exit 1
fi
