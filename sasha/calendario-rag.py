#!/usr/bin/env python3
"""RAG mínimo sobre el calendario académico de la Escuela de Humanidades.

Qué hace RAG acá: en vez de mandarle al modelo todo el calendario, buscamos
primero las pocas entradas parecidas a la pregunta y le mandamos SOLO esas. El
modelo no "sabe" el calendario: lo lee en el momento, en el prompt.

Seamos honestos: este calendario entra entero en un prompt, así que acá la
búsqueda no hace falta y se muestra para que se la vea funcionar. RAG se vuelve
necesario con cientos de páginas, cuando ya no entran en la ventana de contexto.

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b

Uso:
    python3 sasha/calendario-rag.py "¿Cuándo empieza el segundo cuatrimestre?"
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).parent / "docs" / "calendario-unsam-2025.md"

# Una línea igual a uno de estos abre un mes; las de abajo son sus entradas.
ENCABEZADOS = {
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre", "Todo el año",
}

SISTEMA = (
    "Sos un asistente del calendario académico de la Escuela de Humanidades "
    "de la UNSAM. Respondé SOLO con lo que digan los fragmentos del calendario "
    "que te paso; no inventes ni supongas nada que no esté ahí. Si los "
    "fragmentos no contienen la respuesta, contestá exactamente: "
    "«No lo sé, eso no figura en el calendario». Si la contienen, escribí una "
    "oración completa en castellano rioplatense, de vos, sin copiar el "
    "fragmento tal cual."
)


def partir_en_entradas(texto):
    """[1] Un fragmento por entrada del calendario, con el mes adelante.

    No usamos ventanas de N palabras como rag.py: el calendario entero tiene
    ~437 palabras, así que ventanas de 120 darían 4 fragmentos y traer 3 sería
    traer casi todo. Una entrada por fragmento da 37 y ahí sí se ve la
    búsqueda eligiendo. El mes va adelante para que el fragmento se entienda
    solo: "Julio — 21 al 27 de julio — Receso invernal".
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
    """[4] Similitud coseno: qué fragmentos apuntan para el mismo lado.

    Con 37 fragmentos no hace falta ninguna base de datos vectorial: normalizar
    y multiplicar matriz por vector alcanza.
    """
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
             "content": f"Fragmentos del calendario:\n{recuperados}\n\nPregunta: {args.pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(respuesta["message"]["content"].strip())


if __name__ == "__main__":
    main()
