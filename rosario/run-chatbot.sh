#!/usr/bin/env bash
# Chatbot RAG conversacional sobre la cartelera de estrenos de cine en Argentina.
# Uso:  ./run-chatbot.sh
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
