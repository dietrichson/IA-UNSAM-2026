#!/usr/bin/env bash
# Una consulta RAG sobre la cartelera de estrenos de cine en Argentina.
# Uso:  ./run-consulta.sh "¿Quién dirige DIGGER?"
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
if [ "$#" -eq 0 ]; then
    echo "Falta la pregunta. Uso: ./run-consulta.sh \"tu pregunta\"" >&2
    exit 1
fi
if python3 -c "import ollama, numpy" 2>/dev/null; then
    exec python3 "$AQUI/consulta-unica.py" "$@"
elif command -v uv >/dev/null 2>&1; then
    exec uv run --with ollama --with numpy python3 "$AQUI/consulta-unica.py" "$@"
else
    echo "Faltan las librerías 'ollama' y 'numpy', y no encontré uv." >&2
    echo "Instalá uv (https://docs.astral.sh/uv/) o corré: pip install ollama numpy" >&2
    exit 1
fi
