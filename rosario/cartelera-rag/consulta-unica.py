#!/usr/bin/env python3
"""RAG mínimo sobre la cartelera de estrenos de cine en Argentina."""

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
    """[1] Un fragmento por entrada de la cartelera, con la sección adelante."""
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
    parser.add_argument("pregunta", help="Lo que le querés preguntar a la cartelera")
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo de la cartelera")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro la cartelera en {args.datos}")

    # [1] Leer y partir.
    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    print(f"[1] Leí la cartelera y la partí en {len(fragmentos)} fragmentos, uno por entrada.")

    # [2] Vectorizar el corpus. En una app real esto se guardaría en disco.
    print(f"[2] Convierto los {len(fragmentos)} fragmentos en vectores con {EMBED_MODEL}...")
    vectores = vectorizar(fragmentos)

    # [3] Vectorizar la pregunta con EL MISMO modelo: eso es lo que hace que
    #     "el vector más cercano" signifique "el texto más parecido".
    print(f"[3] Convierto la pregunta en un vector con el mismo modelo: {args.pregunta!r}")
    vector_pregunta = vectorizar([args.pregunta])[0]

    # [4] Recuperar. Esto es lo que hay que mirar: qué eligió y con qué puntaje.
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
             "content": f"Fragmentos de la cartelera:\n{recuperados}\n\nPregunta: {args.pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(respuesta["message"]["content"].strip())


if __name__ == "__main__":
    main()
