#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────
#  Models. qwen2.5:3b is the default teaching model: small, fast on CPU, and
#  it never emits reasoning traces (no thinking-toggle headaches).
#  nomic-embed-text is the embedding model the RAG lab needs.
#  Confirm current tags at https://ollama.com/library
# ─────────────────────────────────────────────────────────────────────────
CHAT_MODEL="${OLLAMA_MODEL:-qwen2.5:3b}"
EMBED_MODEL="nomic-embed-text"

echo "==> Installing Ollama (Linux build bundles the engine)..."
curl -fsSL https://ollama.com/install.sh | sh

echo "==> Starting Ollama server in the background..."
# Codespaces containers have no systemd, so run the server directly.
nohup ollama serve > /tmp/ollama.log 2>&1 &

echo "==> Waiting for the Ollama API to come up..."
for _ in $(seq 1 30); do
  if curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then break; fi
  sleep 1
done

echo "==> Pulling ${CHAT_MODEL} (chat) and ${EMBED_MODEL} (embeddings)..."
ollama pull "${CHAT_MODEL}"
ollama pull "${EMBED_MODEL}"

echo "==> Installing Python deps for the RAG lab..."
pip install --quiet ollama numpy

cat <<MSG

✅ Setup complete.

   Chat in the terminal:   ollama run ${CHAT_MODEL}
   Run the RAG lab:        python rag.py "What is this about?"
   Hit the API:            curl http://localhost:11434/api/generate \\
                             -d '{"model":"${CHAT_MODEL}","prompt":"Hello!","stream":false}'

MSG
