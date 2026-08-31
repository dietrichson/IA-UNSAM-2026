"""
Minimal RAG against a local Ollama model — no frameworks, on purpose.

The whole point of this script is that you can SEE every step of retrieval-
augmented generation. There are exactly five moves, marked [1]..[5] below.

Prereqs (run once in your terminal):
    pip install ollama numpy
    ollama pull qwen3:4b            # the chat model
    ollama pull nomic-embed-text    # the embedding model (small, ~275MB)

Then drop some .txt or .md files into a ./docs folder and run:
    python rag.py "your question here"

If ./docs is empty, the script writes a tiny sample corpus so it runs anyway.
"""

import os
import sys
import glob
import textwrap

import numpy as np
import ollama

# ─────────────────────────────────────────────────────────────────────────
#  The knobs. In a real system you'd tune these. For an intro course, treat
#  them as given and point at them as "things that matter in production."
# ─────────────────────────────────────────────────────────────────────────
CHAT_MODEL = "qwen2.5:3b"
EMBED_MODEL = "nomic-embed-text"
CHUNK_WORDS = 120      # how many words per chunk
CHUNK_OVERLAP = 20     # words shared between neighboring chunks
TOP_K = 3              # how many chunks to retrieve and feed to the model
DOCS_DIR = "docs"


def load_documents(folder):
    """Read every .txt/.md file in `folder` into one big string per file."""
    paths = glob.glob(os.path.join(folder, "*.txt")) + \
            glob.glob(os.path.join(folder, "*.md"))
    if not paths:
        return _write_sample_docs(folder)
    texts = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            texts.append(f.read())
    return texts


def chunk(text, size=CHUNK_WORDS, overlap=CHUNK_OVERLAP):
    """Split text into overlapping windows of words.

    Overlap matters: it keeps a sentence that straddles a boundary from being
    cut in half and lost. This is the single most common RAG gotcha.
    """
    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        window = words[start:start + size]
        if window:
            chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks


def embed(texts):
    """[2] Turn text into vectors. Ollama batches a list in one call."""
    resp = ollama.embed(model=EMBED_MODEL, input=texts)
    return np.array(resp["embeddings"], dtype=np.float32)


def cosine_top_k(query_vec, doc_vecs, k):
    """[4] Rank chunks by cosine similarity to the query, return top-k indices.

    Cosine = dot product of L2-normalized vectors. We normalize, then it's just
    a matrix-vector multiply. No vector database needed for a few hundred chunks.
    """
    doc_norm = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
    q_norm = query_vec / np.linalg.norm(query_vec)
    scores = doc_norm @ q_norm
    return np.argsort(scores)[::-1][:k], scores


def main():
    question = " ".join(sys.argv[1:]) or "What is this collection of notes about?"

    # [1] Load + chunk the corpus
    docs = load_documents(DOCS_DIR)
    chunks = [c for doc in docs for c in chunk(doc)]
    print(f"Loaded {len(docs)} file(s) -> {len(chunks)} chunks.\n")

    # [2] Embed every chunk (once; in a real app you'd cache these)
    chunk_vecs = embed(chunks)

    # [3] Embed the question the SAME way as the chunks — this is what makes
    #     "closest vector" mean "most relevant text."
    query_vec = embed([question])[0]

    # [4] Retrieve the most similar chunks
    idx, scores = cosine_top_k(query_vec, chunk_vecs, TOP_K)
    retrieved = [chunks[i] for i in idx]

    print("Retrieved chunks (highest similarity first):")
    for rank, i in enumerate(idx, 1):
        preview = textwrap.shorten(chunks[i], width=90)
        print(f"  {rank}. (score {scores[i]:.3f}) {preview}")
    print()

    # [5] Stuff the retrieved chunks into the prompt as context, then generate.
    #     The instruction to say "I don't know" is what reins in hallucination.
    context = "\n\n---\n\n".join(retrieved)
    prompt = (
        "Answer the question using ONLY the context below. "
        "If the answer isn't in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}"
    )

    resp = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    print("Answer:\n" + resp["message"]["content"])


def _write_sample_docs(folder):
    """Create a tiny corpus so the script runs with zero setup."""
    os.makedirs(folder, exist_ok=True)
    sample = (
        "The course meets on Tuesdays and Thursdays at 10am in Room 214.\n\n"
        "The final project is a small RAG application and is worth 40% of the grade.\n\n"
        "Office hours are Wednesdays 2-4pm. Late work loses 10% per day.\n\n"
        "Students may use any local model via Ollama; cloud APIs are not required."
    )
    path = os.path.join(folder, "syllabus.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(sample)
    print(f"(No docs found — wrote a sample corpus to {path})\n")
    return [sample]


if __name__ == "__main__":
    main()
