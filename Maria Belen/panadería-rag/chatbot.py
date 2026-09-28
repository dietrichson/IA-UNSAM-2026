#!/usr/bin/env python3
"""Chatbot sobre la info comercial de la panadería Santa Anita.

Misma lógica de RAG que consulta-unica.py, pero acá los fragmentos se
vectorizan UNA sola vez al arrancar y se reusan para todas las preguntas.
Eso es lo que hace una aplicación de RAG de verdad: los vectores del corpus
se calculan una vez, se guardan en memoria (o en disco), y lo único que se
calcula por pregunta es el vector de la pregunta.

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b

Uso:
    python3 chatbot.py
    python3 chatbot.py --top-k 5 --datos datos/otro-archivo.md
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "panaderia-santa-anita.md"

ENCABEZADOS = {
    "Horarios", "Dirección", "Cómo llegar", "Productos", "Delivery", "Formas de pago",
}

SISTEMA = (
    "Sos un asistente de la panadería Santa Anita, en Lanús Oeste. Respondé "
    "SOLO con lo que digan los fragmentos de información que te paso; no "
    "inventes ni supongas nada que no esté ahí (ni precios, ni horarios, ni "
    "productos que no figuren). Si los fragmentos no contienen la respuesta, "
    "contestá exactamente: «No lo sé, esa información no está en los datos "
    "de la panadería». Si la contienen, escribí una oración completa en "
    "castellano rioplatense, de vos, sin copiar el fragmento tal cual."
)


def partir_en_entradas(texto):
    """Un fragmento por entrada, con la sección adelante (ver consulta-unica.py)."""
    fragmentos = []
    seccion = None
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea in ENCABEZADOS:
            seccion = linea
        elif seccion:
            fragmentos.append(f"{seccion} — {linea}")
    return fragmentos


def abortar(error, modelo):
    if isinstance(error, ollama.ResponseError) and "not found" in str(error).lower():
        print(f"\nFalta el modelo «{modelo}». Instalalo con:\n    ollama pull {modelo}")
    else:
        print(f"\nNo pude hablar con Ollama: {error}\n"
              "¿Está corriendo? Arrancalo en otra terminal con:\n    ollama serve")
    sys.exit(1)


def vectorizar(textos, modelo=EMBED_MODEL):
    try:
        respuesta = ollama.embed(model=modelo, input=textos)
    except Exception as error:
        abortar(error, modelo)
    return np.array(respuesta["embeddings"], dtype=np.float32)


def mas_parecidos(vector_pregunta, vectores, k):
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo de datos de la panadería")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro el archivo de datos en {args.datos}")

    print(f"Leyendo y vectorizando {args.datos.name}...")
    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    vectores = vectorizar(fragmentos)
    print(f"Listo: {len(fragmentos)} fragmentos vectorizados. Preguntá lo que quieras (Ctrl+C para salir).\n")

    while True:
        try:
            pregunta = input("Vos: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nChau!")
            break
        if not pregunta:
            continue

        vector_pregunta = vectorizar([pregunta])[0]
        indices, puntajes = mas_parecidos(vector_pregunta, vectores, args.top_k)
        for i in indices:
            print(f"    (similitud {puntajes[i]:.3f}) {fragmentos[i]}")

        recuperados = "\n".join(f"- {fragmentos[i]}" for i in indices)
        try:
            respuesta = ollama.chat(model=args.modelo, messages=[
                {"role": "system", "content": SISTEMA},
                {"role": "user",
                 "content": f"Fragmentos de la panadería:\n{recuperados}\n\nPregunta: {pregunta}"},
            ])
        except Exception as error:
            abortar(error, args.modelo)
        print("Bot:", respuesta["message"]["content"].strip(), "\n")


if __name__ == "__main__":
    main()
