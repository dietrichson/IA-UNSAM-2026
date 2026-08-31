#!/usr/bin/env bash
PREGUNTA=${1:-"¿De qué trata la materia?"}
python3 "$(dirname "$0")/consulta-unica.py" "$PREGUNTA"
