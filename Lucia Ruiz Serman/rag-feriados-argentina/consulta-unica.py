#!/usr/bin/env python3
"""RAG mínimo sobre los feriados y fechas conmemorativas de Argentina.

Qué hace RAG acá: en vez de mandarle al modelo todo el calendario de
feriados, buscamos primero las pocas entradas parecidas a la pregunta y le
mandamos SOLO esas. El modelo no "sabe" el calendario de feriados: lo lee en
el momento, en el prompt.

Este ejemplo está basado en sasha/calendario-rag del profesor, cambiando el
documento de datos por uno propio: feriados nacionales 2026 de Argentina.

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b

Uso:
    python3 consulta-unica.py "¿Cuándo es el Día de la Independencia?"
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
    """[1] Un fragmento por entrada del calendario, con el mes adelante.

    Igual que en el ejemplo del profesor: una entrada por fragmento (en vez
    de ventanas de N palabras) hace que la búsqueda se note eligiendo entre
    varias opciones. El mes va adelante para que el fragmento se entienda
    solo: "Julio — 9 de julio (jueves) — Día de la Independencia...".
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
    """[2] y [3] Convierte texto en vectores. Ollama acepta una lista entera."""
    try:
        respuesta = ollama.embed(model=EMBED_MODEL, input=textos)
    except Exception as error:
        abortar(error, EMBED_MODEL)
    return np.array(respuesta["embeddings"], dtype=np.float32)


def mas_parecidos(vector_pregunta, vectores, k):
    """[4] Similitud coseno: qué fragmentos apuntan para el mismo lado."""
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pregunta", help="Lo que le querés preguntar al calendario")
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo del calendario")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro el calendario en {args.datos}")

    # [1] Leer y partir.
    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    print(f"[1] Leí el calendario y lo partí en {len(fragmentos)} fragmentos, uno por entrada.")

    # [2] Vectorizar el corpus.
    print(f"[2] Convierto los {len(fragmentos)} fragmentos en vectores con {EMBED_MODEL}...")
    vectores = vectorizar(fragmentos)

    # [3] Vectorizar la pregunta con EL MISMO modelo.
    print(f"[3] Convierto la pregunta en un vector con el mismo modelo: {args.pregunta!r}")
    vector_pregunta = vectorizar([args.pregunta])[0]

    # [4] Recuperar.
    indices, puntajes = mas_parecidos(vector_pregunta, vectores, args.top_k)
    print(f"\n[4] Los {args.top_k} fragmentos más parecidos a la pregunta:")
    for puesto, i in enumerate(indices, 1):
        print(f"    {puesto}. (similitud {puntajes[i]:.3f}) {fragmentos[i]}")

    # [5] Responder usando SOLO esos fragmentos.
    recuperados = "\n".join(f"- {fragmentos[i]}" for i in indices)
    print(f"\n[5] Le paso esos {args.top_k} fragmentos y la pregunta a {args.modelo}:\n")
    try:
        respuesta = ollama.chat(model=args.modelo, messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user",
             "content": f"Fragmentos del calendario:\n{recuperados}\n\nPregunta: {args.pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(respuesta["message"]["content"].strip())


if __name__ == "__main__":
    main()
