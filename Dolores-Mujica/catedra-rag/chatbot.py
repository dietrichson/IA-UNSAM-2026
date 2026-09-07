#!/usr/bin/env python3
"""Chatbot RAG - Asistente de Cátedra."""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
# Apunta al archivo de datos de tu materia
DATOS = Path(__file__).resolve().parent / "datos" / "materia.md"

# Nombres de las secciones de tu texto (para agrupar los fragmentos)
ENCABEZADOS = {
    "Unidad 1", "Unidad 2", "Unidad 3", "Unidad 4",
    "Bibliografía", "Condiciones de Aprobación", "Programa"
}

SALIDAS = {"salir", "chau", "exit", "quit"}

# System Prompt adaptado para Asistente de Cátedra
SISTEMA = (
    "Sos un docente y asistente de cátedra universitario pedagógico y servicial. "
    "Respondé SOLO con la información brindada en los fragmentos del texto académico "
    "que te paso; no inventes ni supongas nada que no esté ahí. Si los "
    "fragmentos no contienen la respuesta, contestá exactamente: "
    "«No lo sé, eso no figura en el material de la materia». Si la contienen, explicá "
    "de forma clara y rigurosa en castellano rioplatense, de vos, sin copiar el "
    "fragmento tal cual."
)


def partir_en_entradas(texto):
    """Segmenta el archivo en fragmentos anteponiendo la unidad o sección."""
    fragmentos = []
    seccion = "General"
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea in ENCABEZADOS or any(linea.startswith(enc) for enc in ENCABEZADOS):
            seccion = linea
        else:
            fragmentos.append(f"{seccion} — {linea}")
    return fragmentos


def abortar(error, modelo):
    """Traduce una falla de Ollama a un mensaje entendible y termina."""
    if isinstance(error, ollama.ResponseError) and "not found" in str(error).lower():
        print(f"\nFalta el modelo «{modelo}». Instalalo con:\n    ollama pull {modelo}")
    else:
        print(f"\nNo pude hablar con Ollama: {error}\n"
              "¿Está corriendo? Arrancalo en otra terminal con:\n    ollama serve")
    sys.exit(1)


def vectorizar(textos):
    """Convierte texto en vectores usando Ollama."""
    try:
        respuesta = ollama.embed(model=EMBED_MODEL, input=textos)
    except Exception as error:
        abortar(error, EMBED_MODEL)
    return np.array(respuesta["embeddings"], dtype=np.float32)


def mas_parecidos(vector_pregunta, vectores, k):
    """Calcula la similitud coseno."""
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def responder(pregunta, fragmentos, vectores, args):
    """Recupera los fragmentos más parecidos y responde."""
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
             "content": f"Fragmentos de la materia:\n{recuperados}\n\nPregunta del alumno: {pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(f"\n  Respuesta del Asistente ({args.modelo}):")
    print(f"    {respuesta['message']['content'].strip()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo de la materia")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro el texto en {args.datos}")

    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    vectores = vectorizar(fragmentos)

    print(f"Texto procesado en {len(fragmentos)} fragmentos.")
    print('Escribí tu pregunta sobre la materia, o "salir" para terminar.')

    while True:
        try:
            pregunta = input('\nPreguntá al asistente (o "salir"): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta or pregunta.lower() in SALIDAS:
            break
        try:
            responder(pregunta, fragmentos, vectores, args)
        except KeyboardInterrupt:
            break

    print("\n¡Chau! Éxitos en el estudio.")


if __name__ == "__main__":
    main()
