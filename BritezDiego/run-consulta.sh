#!/usr/bin/env bash
# Una consulta RAG sobre contaminación del agua y plásticos en el océano.
# Uso:  ./run-consulta.sh "¿Qué es la contaminación por plásticos?"

set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"

if [ "$#" -eq 0 ]; then
    echo "🧽 ¡Oh, no! No me preguntaste nada."
    echo ""
    echo "Uso: ./run-consulta.sh \"tu pregunta\""
    echo ""
    echo "Ejemplos:"
    echo '  ./run-consulta.sh "¿Qué es la contaminación por plásticos?"'
    echo '  ./run-consulta.sh "¿Cómo afecta la basura a los animales marinos?"'
    echo '  ./run-consulta.sh "¿Qué porcentaje de plásticos viene de tierra?"'
    echo '  ./run-consulta.sh "¿Cuántas especies están afectadas en Argentina?"'
    exit 1
fi

# Verificar que el modelo existe
if ! ollama list 2>/dev/null | grep -q "agua-rag"; then
    echo "❌ El modelo 'agua-rag' no existe." >&2
    echo "   Creálo con: ./create-agua.sh" >&2
    exit 1
fi

# Verificar que el archivo de datos existe
if [ ! -f "$AQUI/datos/basura-marina.txt" ]; then
    echo "❌ No encuentro datos/basura-marina.txt" >&2
    echo "   Asegurate de tener el documento en la carpeta datos/" >&2
    exit 1
fi

echo "🧽 ¡Estoy listo! ¡Estoy listo! ¡Estoy listo!"
echo ""

if python3 -c "import ollama, numpy" 2>/dev/null; then
    exec python3 "$AQUI/consulta-unica.py" "$@"
elif command -v uv >/dev/null 2>&1; then
    exec uv run --with ollama --with numpy python3 "$AQUI/consulta-unica.py" "$@"
else
    echo "❌ Faltan las librerías 'ollama' y 'numpy', y no encontré uv." >&2
    echo "   Instalá uv (https://docs.astral.sh/uv/) o corré: pip install ollama numpy" >&2
    exit 1
fi
