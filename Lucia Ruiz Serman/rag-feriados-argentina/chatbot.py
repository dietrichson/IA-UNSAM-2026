#!/usr/bin/env python3
"""Chatbot RAG sobre los feriados y fechas conmemorativas de Argentina.

Es lo mismo que consulta-unica.py, pero conversado. La diferencia que
importa: consulta-unica.py vuelve a vectorizar los fragmentos en cada
corrida, y acá los vectorizamos UNA sola vez al arrancar. Después cada
pregunta es sólo vectorizar esa pregunta y multiplicar. Eso es lo que hace
en serio una app de RAG: los vectores del corpus se calculan una vez y se
guardan.

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b

Uso:
    python3 chatbot.py
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "feriados-argentina-2026.md"

# Una línea igual a uno de estos abre un mes; las de abajo son sus entradas.
ENCABEZADOS = {
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre", "Todo el año",
}

# Palabras con las que se corta la charla.
SALIDAS = {"salir", "chau", "exit", "quit"}

SISTEMA = (
    "Sos un asistente sobre los feriados y fechas conmemorativas de "
    "Argentina. Respondé SOLO con lo que digan los fragmentos del "
    "calendario que te paso; no inventes ni supongas nada que no esté ahí. "
    "Si los fragmentos no contienen la respuesta, contestá exactamente: "
    "«No lo sé, eso no figura en el calendario». Si la contienen, escribí "
    "una oración completa en castellano rioplatense, de vos, sin copiar el "
    "fragmento tal cual."
)


def partir_en_entradas(texto):
    """Un fragmento por entrada del calendario, con el mes adelante.

    Una entrada por fragmento (en vez de ventanas de N palabras) hace que la
    búsqueda se note eligiendo entre varias opciones. El mes va adelante
    para que el fragmento se entienda solo: "Julio — 9 de julio (jueves) —
    Día de la Independencia...".
    """
    fragmentos = []
    mes = None
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        if linea in ENCABEZADOS:
            mes = linea
        elif mes:
            fragmentos.append(f"{mes} — {linea}")
        # Sin mes todavía, la línea es del encabezado del archivo: la salteamos.
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
    """Convierte texto en vectores. Ollama acepta una lista entera."""
    try:
        respuesta = ollama.embed(model=EMBED_MODEL, input=textos)
    except Exception as error:
        abortar(error, EMBED_MODEL)
    return np.array(respuesta["embeddings"], dtype=np.float32)


def mas_parecidos(vector_pregunta, vectores, k):
    """Similitud coseno: qué fragmentos apuntan para el mismo lado."""
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def responder(pregunta, fragmentos, vectores, args):
    """Recupera los k fragmentos más parecidos y contesta con SOLO esos."""
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
             "content": f"Fragmentos del calendario:\n{recuperados}\n\nPregunta: {pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(f"\n  Respuesta de {args.modelo}:")
    print(f"    {respuesta['message']['content'].strip()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo del calendario")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro el calendario en {args.datos}")

    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    vectores = vectorizar(fragmentos)

    print(f"Calendario partido en {len(fragmentos)} fragmentos, uno por entrada.")
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

    print("\n¡Chau!")


if __name__ == "__main__":
    main()
