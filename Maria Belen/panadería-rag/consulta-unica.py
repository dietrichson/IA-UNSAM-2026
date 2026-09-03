#!/usr/bin/env python3
"""RAG mínimo sobre la info comercial de la panadería Santa Anita.

Qué hace RAG acá: en vez de mandarle al modelo toda la info de la panadería,
buscamos primero las pocas entradas parecidas a la pregunta y le mandamos SOLO
esas. El modelo no "sabe" la info de Santa Anita: la lee en el momento, en el
prompt.

Seamos honestos: esta info entra entera en un prompt, así que acá la búsqueda
no hace falta y se muestra para que se la vea funcionar. RAG se vuelve
necesario con cientos de páginas, cuando ya no entran en la ventana de
contexto (por ejemplo, si esto fuera la carta completa de una cadena con
sucursales, o un catálogo enorme).

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b

Uso:
    python3 consulta-unica.py "¿A qué hora abren los domingos?"
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "panaderia-santa-anita.md"

# Una línea igual a uno de estos abre una sección; las de abajo son sus entradas.
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
    """[1] Un fragmento por entrada, con la sección adelante.

    No usamos ventanas de N palabras: la info entera de la panadería tiene
    pocas líneas, así que ventanas grandes traerían casi todo el documento
    de una. Una entrada por fragmento da más granularidad y ahí sí se ve la
    búsqueda eligiendo. La sección va adelante para que el fragmento se
    entienda solo: "Horarios — Domingo, turno mañana: 08:30 a 14:00 hs".
    """
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
        # Sin sección todavía, la línea es del encabezado del archivo: la salteamos.
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

    Con pocos fragmentos no hace falta ninguna base de datos vectorial:
    normalizar y multiplicar matriz por vector alcanza.
    """
    normalizados = vectores / np.linalg.norm(vectores, axis=1, keepdims=True)
    puntajes = normalizados @ (vector_pregunta / np.linalg.norm(vector_pregunta))
    return np.argsort(puntajes)[::-1][:k], puntajes


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pregunta", help="Lo que le querés preguntar sobre la panadería")
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="qwen2.5:3b", help="Modelo de chat")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo de datos de la panadería")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"No encuentro el archivo de datos en {args.datos}")

    # [1] Leer y partir.
    fragmentos = partir_en_entradas(args.datos.read_text(encoding="utf-8"))
    print(f"[1] Leí los datos y los partí en {len(fragmentos)} fragmentos, uno por entrada.")

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
             "content": f"Fragmentos de la panadería:\n{recuperados}\n\nPregunta: {args.pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(respuesta["message"]["content"].strip())


if __name__ == "__main__":
    main()
