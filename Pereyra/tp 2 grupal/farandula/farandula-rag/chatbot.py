#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"

DATOS = Path(__file__).resolve().parent / "datos" / "farandula.md"

ENCABEZADOS = {
    "LAM",
    "Ángel de Brito",
    "Panelistas",
    "Farándula argentina",
    "Programas de espectáculos",
    "Datos del experimento",
}

SALIDAS = {"salir", "chau", "exit", "quit"}

SISTEMA = (
    "Sos un asistente especializado en farándula argentina y televisión "
    "de espectáculos. Respondé SOLO con la información contenida en los "
    "fragmentos que te paso. No inventes, no supongas y no agregues "
    "información que no aparezca en esos fragmentos. Si la información "
    "necesaria para responder no está en los fragmentos, contestá "
    "exactamente: «No lo sé, esa información no figura en los documentos». "
    "Respondé en castellano rioplatense, de manera clara y natural."
)


def partir_en_entradas(texto):
    """Divide el documento en fragmentos según sus encabezados."""
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
    """Muestra un mensaje comprensible si Ollama falla."""
    if isinstance(error, ollama.ResponseError) and "not found" in str(error).lower():
        print(
            f"\nFalta el modelo «{modelo}». Instalalo con:\n"
            f"    ollama pull {modelo}"
        )
    else:
        print(
            f"\nNo pude hablar con Ollama: {error}\n"
            "¿Está corriendo? Arrancalo en otra terminal con:\n"
            "    ollama serve"
        )

    sys.exit(1)


def vectorizar(textos):
    """Convierte los textos en vectores mediante el modelo de embeddings."""
    try:
        respuesta = ollama.embed(
            model=EMBED_MODEL,
            input=textos
        )
    except Exception as error:
        abortar(error, EMBED_MODEL)

    return np.array(
        respuesta["embeddings"],
        dtype=np.float32
    )


def mas_parecidos(vector_pregunta, vectores, k):
    """Busca los fragmentos más parecidos a la pregunta."""
    normalizados = vectores / np.linalg.norm(
        vectores,
        axis=1,
        keepdims=True
    )

    vector_pregunta = vector_pregunta / np.linalg.norm(vector_pregunta)

    puntajes = normalizados @ vector_pregunta

    return np.argsort(puntajes)[::-1][:k], puntajes


def responder(pregunta, fragmentos, vectores, args):
    """Recupera información relevante y genera una respuesta."""
    vector_pregunta = vectorizar([pregunta])[0]

    indices, puntajes = mas_parecidos(
        vector_pregunta,
        vectores,
        args.top_k
    )

    print(
        f"\nFragmentos recuperados "
        f"(los {args.top_k} más parecidos):"
    )

    for puesto, i in enumerate(indices, 1):
        print(
            f"  {puesto}. "
            f"(similitud {puntajes[i]:.3f}) "
            f"{fragmentos[i]}"
        )

    recuperados = "\n".join(
        f"- {fragmentos[i]}"
        for i in indices
    )

    try:
        respuesta = ollama.chat(
            model=args.modelo,
            messages=[
                {
                    "role": "system",
                    "content": SISTEMA
                },
                {
                    "role": "user",
                    "content": (
                        f"Fragmentos de los documentos:\n"
                        f"{recuperados}\n\n"
                        f"Pregunta: {pregunta}"
                    )
                }
            ]
        )
    except Exception as error:
        abortar(error, args.modelo)

    print(f"\nRespuesta de {args.modelo}:")
    print(f"  {respuesta['message']['content'].strip()}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Cantidad de fragmentos a recuperar"
    )

    parser.add_argument(
        "--modelo",
        default="qwen2.5:3b",
        help="Modelo de chat"
    )

    parser.add_argument(
        "--datos",
        type=Path,
        default=DATOS,
        help="Archivo con los datos"
    )

    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(
            f"No encuentro el archivo de datos en {args.datos}"
        )

    fragmentos = partir_en_entradas(
        args.datos.read_text(encoding="utf-8")
    )

    if not fragmentos:
        sys.exit(
            "No encontré fragmentos en el archivo de datos."
        )

    vectores = vectorizar(fragmentos)

    print(
        f"Documento dividido en {len(fragmentos)} fragmentos."
    )

    print(
        f"Los fragmentos fueron vectorizados con "
        f"{EMBED_MODEL}."
    )

    print(
        'Escribí tu pregunta o "salir" para terminar.'
    )

    while True:
        try:
            pregunta = input(
                '\nPreguntá (o "salir"): '
            ).strip()

        except (EOFError, KeyboardInterrupt):
            break

        if not pregunta:
            continue

        if pregunta.lower() in SALIDAS:
            break

        try:
            responder(
                pregunta,
                fragmentos,
                vectores,
                args
            )

        except KeyboardInterrupt:
            break

    print("\n¡Chau!")


if __name__ == "__main__":
    main()
