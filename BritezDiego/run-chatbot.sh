#!/usr/bin/env bash
# Chatbot RAG sobre contaminación del agua y plásticos en el océano.
# Usá a Bob Esponja para consultar sobre basura marina y sus efectos.
#
# Uso:  ./run-chatbot.sh            (modo interactivo)
#       ./run-chatbot.sh --top-k 5  (usar 5 fragmentos en lugar de 3)
#       ./run-chatbot.sh --help     (mostrar ayuda)
#       ./run-chatbot.sh --debug    (modo debug con más información)

set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"

# Colores
ROJO='\033[0;31m'
VERDE='\033[0;32m'
AMARILLO='\033[1;33m'
AZUL='\033[0;34m'
RESET='\033[0m'

# Función de ayuda
mostrar_ayuda() {
    cat << EOF
🧽 BOB ESPONJA - CHATBOT RAG

Un chatbot interactivo que usa RAG (Retrieval-Augmented Generation)
para responder preguntas sobre contaminación del agua y plásticos.

USO:
    ./run-chatbot.sh [OPCIONES]

OPCIONES:
    --top-k N      Usar N fragmentos para responder (default: 3)
    --modelo NOM   Usar otro modelo de Ollama (default: agua-rag)
    --debug        Mostrar información detallada del proceso
    --help         Mostrar esta ayuda

EJEMPLOS:
    ./run-chatbot.sh
    ./run-chatbot.sh --top-k 5
    ./run-chatbot.sh --modelo qwen2.5:3b
    ./run-chatbot.sh --debug

PREGUNTAS DE EJEMPLO:
    - ¿Qué es la contaminación por plásticos?
    - ¿Cómo afecta la basura a los animales marinos?
    - ¿Qué porcentaje de plásticos viene de tierra?
    - ¿Cuántas especies están afectadas en Argentina?
    - ¿Qué son los microplásticos?

FUENTE:
    Argentina.gob.ar - Basura marina y contaminación por plásticos
    https://www.argentina.gob.ar/ambiente/basuramarina
EOF
}

# Verificar si piden ayuda
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]; then
    mostrar_ayuda
    exit 0
fi

echo -e "${AZUL}🧽  BOB ESPONJA - CHATBOT RAG  🧽${RESET}"
echo -e "${AZUL}📚  Contaminación del agua y plásticos en el océano${RESET}"
echo ""

# 1. Verificar que el modelo existe
if ! ollama list 2>/dev/null | grep -q "agua-rag"; then
    echo -e "${ROJO}❌ El modelo 'agua-rag' no existe.${RESET}"
    echo -e "${AMARILLO}   Creálo con: ./create-agua.sh${RESET}"
    exit 1
fi
echo -e "${VERDE}✓ Modelo 'agua-rag' encontrado${RESET}"

# 2. Verificar que el archivo de datos existe
if [ ! -f "$AQUI/datos/basura-marina.txt" ]; then
    echo -e "${ROJO}❌ No encuentro el archivo de datos: datos/basura-marina.txt${RESET}"
    echo -e "${AMARILLO}   Asegurate de tener el documento en la carpeta datos/${RESET}"
    exit 1
fi
echo -e "${VERDE}✓ Archivo de datos encontrado: datos/basura-marina.txt${RESET}"

# 3. Verificar que Ollama está corriendo
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${ROJO}❌ Ollama no está corriendo.${RESET}"
    echo -e "${AMARILLO}   Arrancalo en otra terminal con: ollama serve${RESET}"
    exit 1
fi
echo -e "${VERDE}✓ Ollama está corriendo${RESET}"

# 4. Verificar dependencias de Python
echo -e "${AMARILLO}📦 Verificando dependencias...${RESET}"
if python3 -c "import ollama, numpy" 2>/dev/null; then
    echo -e "${VERDE}✓ Dependencias encontradas${RESET}"
    echo ""
    echo -e "${VERDE}¡Estoy listo! ¡Estoy listo! ¡Estoy listo! 🧽${RESET}"
    echo ""
    exec python3 "$AQUI/chatbot.py" "$@"
elif command -v uv >/dev/null 2>&1; then
    echo -e "${VERDE}✓ Usando uv para ejecutar${RESET}"
    echo ""
    echo -e "${VERDE}¡Estoy listo! ¡Estoy listo! ¡Estoy listo! 🧽${RESET}"
    echo ""
    exec uv run --with ollama --with numpy python3 "$AQUI/chatbot.py" "$@"
else
    echo -e "${ROJO}❌ Faltan las librerías 'ollama' y 'numpy', y no encontré uv.${RESET}" >&2
    echo -e "${AMARILLO}   Instalá uv (https://docs.astral.sh/uv/) o corré:${RESET}" >&2
    echo "     pip install ollama numpy" >&2
    exit 1
fi
