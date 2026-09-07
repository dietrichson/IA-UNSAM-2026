#!/usr/bin/env python3
"""Chatbot RAG sobre la cartelera de estrenos de cine en Argentina."""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "cartelera-estrenos-2026.md"

# Una línea igual a uno de estos abre una sección; las de abajo son sus entradas.
ENCABEZADOS = {
    "Septiembre", "Octubre", "Noviembre", "Diciembre",
    "Sin fecha confirmada", "Complejos",
}

# Palabras con las que el estudiante corta la charla.
SALIDAS = {"salir", "chau", "exit", "quit"}

SISTEMA = (
    "Sos un asistente de la cartelera de estrenos de cine en Argentina. "
    "Respondé SOLO con lo que digan los fragmentos de la cartelera que te "
    "paso; no inventes ni supongas nada que no esté ahí, incluyendo horarios "
    "de funciones, precios de entradas o en qué cine puntual se puede ver "
    "una película, salvo que el fragmento lo diga explícitamente. Si los "
    "fragmentos no contienen la respuesta, contestá exactamente: "
    "«No lo sé, eso no figura en la cartelera». Si la contienen, escribí una "
    "oración completa en castellano rioplatense, de vos, sin copiar el "
    "fragmento tal cual."
)


def partir_en_entradas(texto):
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


def vectorizar(textos):
    try:
        respuesta = ollama.embed(model=EMBED_MODEL, input=textos)
    except Exception as error:
        abortar(error, EMBED_MODEL)
    return np.array(respuesta["embeddings"], dtype=np.float32)


def mas_parecidos(vector_pregunta, vectores, k):
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def responder(pregunta, fragmentos, vectores, args):
    vector_pregunta = vectorizar([pregunta])[0]
    indices, puntajes = mas_parecidos(vector_pregunta, vectores, args.top_k)

    print(f"\n  Fragmentos recuperados (los {args.top_k} más parecidos):")
    for puesto, i in enumerate(indices, 1):
        print(f"    {puesto}. (similitud {puntajes[i]:.3f}) {fragmentos[i]}")

    recuperados = "\n".join(f"- {fragmentos[i]}" for i in indices)
    try:
        respuesta = ollama.chat(model=args.modelo, messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user",
             "content": f"Fragmentos de la cartelera:\n{recuperados}\n\nPregunta: {pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(f"\n  Respuesta de {args.modelo}:")
    print(f"    {respuesta['message']['content'].strip()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo de la cartelera")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro la cartelera en {args.datos}")

    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    vectores = vectorizar(fragmentos)

    print(f"Cartelera partida en {len(fragmentos)} fragmentos, uno por entrada.")
    print(f"Los vectoricé UNA sola vez con {EMBED_MODEL}: las preguntas que vengan "
          "reusan estos vectores.")
    print('Escribí tu pregunta, o "salir" para terminar.')

    while True:
        try:
            pregunta = input('\nPreguntá (o "salir"): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta or pregunta.lower() in SALIDAS:
            break
        try:
            responder(pregunta, fragmentos, vectores, args)
        except KeyboardInterrupt:
            break

    print("\n¡Chau! Que disfrutes el cine.")


if __name__ == "__main__":
    main()
