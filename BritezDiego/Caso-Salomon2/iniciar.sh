#!/usr/bin/env bash
# iniciar.sh — instala lo necesario y abre el juego con la jueza (un solo comando)
cd "$(dirname "$0")" || exit 1
pip install -q anthropic
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo ">> Aviso: no hay ANTHROPIC_API_KEY. La jueza va a funcionar en modo sin IA."
fi
python3 servidor.py
