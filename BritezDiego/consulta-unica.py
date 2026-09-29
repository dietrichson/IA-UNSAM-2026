#!/usr/bin/env python3
"""RAG mínimo sobre contaminación del agua y plásticos en el océano.

Qué hace RAG acá: en vez de mandarle al modelo todo el documento, buscamos
primero los fragmentos parecidos a la pregunta y le mandamos SOLO esos. El
modelo no "sabe" el documento: lo lee en el momento, en el prompt.

Este documento tiene ~1500 palabras, así que entra entero en un prompt, pero
lo partimos en fragmentos para mostrar cómo funciona RAG. RAG se vuelve
necesario con cientos de páginas, cuando ya no entran en la ventana de contexto.

Fuente: https://www.argentina.gob.ar/ambiente/basuramarina

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b
    # Y crear el modelo de Bob Esponja:
    ollama create agua-rag -f agua-modelfile

Uso:
    python3 consulta-unica.py "¿Qué es la contaminación por plásticos?"
    python3 consulta-unica.py "¿Cómo afecta la basura a los animales marinos?"
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "basura-marina.txt"

# Palabras que indican secciones importantes en el documento
SECCIONES = {
    "Basura marina", "Contaminación por plásticos", "Ambientes costeros",
    "Fuentes terrestres", "Fuentes marítimas", "Efectos e impacto",
    "Plásticos", "Microplásticos", "Macroplásticos", "Especies afectadas",
    "Ingesta de plásticos", "Enredo", "Medidas de mitigación",
    "Concientización", "Biodiversidad marina"
}

SISTEMA = (
    "Sos Bob Esponja, la esponja marina más feliz de Fondo de Bikini. "
    "Hoy vas a hablar sobre la contaminación del agua y los plásticos en el océano. "
    "Respondé SOLO con lo que digan los fragmentos del documento que te paso; "
    "no inventes ni supongas nada que no esté ahí. "
    "Si los fragmentos no contienen la respuesta, contestá con humor: "
    "«¡Oh, no! No encontré eso en mis documentos. ¡Pero seguro que Arenita sabe!» "
    "Si la contienen, escribí una respuesta como Bob Esponja: alegre, entusiasta, "
    "con tu risa característica (¡Ja, ja, ja!) y siempre dejando un mensaje "
    "positivo sobre cómo cuidar el océano. "
    "Usá tus frases típicas como '¡Oh, sí!', '¡Estoy listo!' o '¡Qué divertido!'."
)


def partir_en_fragmentos(texto):
    """[1] Un fragmento por sección del documento, manteniendo el contexto.
    
    No usamos ventanas de N palabras fijas: el documento tiene secciones
    claras, así que las respetamos. Cada fragmento empieza con el título
    de la sección para que el modelo sepa de qué está hablando.
    """
    fragmentos = []
    seccion_actual = "Introducción"
    texto_actual = []
    
    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        
        # Detectar si es un título de sección (en negrita o con ## en el original)
        es_titulo = False
        for seccion in SECCIONES:
            if seccion.lower() in linea.lower():
                # Guardar el fragmento anterior si tiene contenido
                if texto_actual:
                    fragmentos.append(f"{seccion_actual}\n\n" + "\n".join(texto_actual))
                    texto_actual = []
                seccion_actual = linea
                es_titulo = True
                break
        
        if not es_titulo:
            texto_actual.append(linea)
    
    # Guardar el último fragmento
    if texto_actual:
        fragmentos.append(f"{seccion_actual}\n\n" + "\n".join(texto_actual))
    
    # Si quedó muy grande algún fragmento, partirlo
    fragmentos_finales = []
    for frag in fragmentos:
        if len(frag) > 1000:
            # Partir en chunks más chicos
            partes = [frag[i:i+800] for i in range(0, len(frag), 700)]
            fragmentos_finales.extend(partes)
        else:
            fragmentos_finales.append(frag)
    
    # Si hay muy pocos fragmentos, hacerlos más pequeños
    if len(fragmentos_finales) < 5:
        parrafos = texto.split('\n\n')
        parrafos = [p.strip() for p in parrafos if p.strip()]
        fragmentos_finales = []
        for i in range(0, len(parrafos), 4):
            chunk = "\n\n".join(parrafos[i:i+4])
            if chunk:
                fragmentos_finales.append(chunk)
    
    return fragmentos_finales


def abortar(error, modelo):
    """Traduce una falla de Ollama a un mensaje entendible y termina."""
    if isinstance(error, ollama.ResponseError) and "not found" in str(error).lower():
        print(f"\n❌ Falta el modelo «{modelo}». Instalalo con:\n    ollama pull {modelo}")
    else:
        print(f"\n❌ No pude hablar con Ollama: {error}\n"
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


def mostrar_banner():
    """Muestra el banner de Bob Esponja."""
    print("""
🧽  BOB ESPONJA - EXPERTO EN CONTAMINACIÓN MARINA  🧽
📚 Fuente: Argentina.gob.ar - Basura marina y plásticos
""")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pregunta", help="Lo que le querés preguntar a Bob Esponja")
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="agua-rag", help="Modelo de chat (Bob Esponja)")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo del documento")
    parser.add_argument("--verbose", action="store_true", help="Mostrar pasos detallados")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"❌ No encuentro el documento en {args.datos}")

    # [1] Leer y partir.
    texto = args.datos.read_text(encoding="utf-8")
    fragmentos = partir_en_fragmentos(texto)
    
    if args.verbose:
        print(f"[1] 📄 Leí el documento y lo partí en {len(fragmentos)} fragmentos.")
        for i, f in enumerate(fragmentos[:3]):
            print(f"    Fragmento {i+1}: {len(f)} caracteres")
            print(f"    {f[:100]}...")
        if len(fragmentos) > 3:
            print(f"    ... y {len(fragmentos)-3} fragmentos más.")

    # [2] Vectorizar el corpus. En una app real esto se guardaría en disco.
    if args.verbose:
        print(f"[2] 🧠 Convierto los {len(fragmentos)} fragmentos en vectores con {EMBED_MODEL}...")
    vectores = vectorizar(fragmentos)

    # [3] Vectorizar la pregunta con EL MISMO modelo: eso es lo que hace que
    #     "el vector más cercano" signifique "el texto más parecido".
    if args.verbose:
        print(f"[3] 🔍 Convierto la pregunta en un vector con el mismo modelo: {args.pregunta!r}")
    vector_pregunta = vectorizar([args.pregunta])[0]

    # [4] Recuperar. Esto es lo que hay que mirar: qué eligió y con qué puntaje.
    indices, puntajes = mas_parecidos(vector_pregunta, vectores, args.top_k)
    
    if args.verbose:
        print(f"\n[4] 🎯 Los {args.top_k} fragmentos más parecidos a la pregunta:")
        for puesto, i in enumerate(indices, 1):
            preview = fragmentos[i][:80] + "..." if len(fragmentos[i]) > 80 else fragmentos[i]
            print(f"    {puesto}. (similitud {puntajes[i]:.3f}) {preview}")
        print("")

    # [5] Responder usando SOLO esos fragmentos.
    recuperados = "\n".join(f"- {fragmentos[i]}" for i in indices)
    if args.verbose:
        print(f"[5] 💬 Le paso esos {args.top_k} fragmentos a {args.modelo}:\n")
    
    try:
        respuesta = ollama.chat(model=args.modelo, messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user",
             "content": f"Fragmentos del documento sobre contaminación marina:\n{recuperados}\n\nPregunta: {args.pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    
    mostrar_banner()
    print(f"\n🧽 Bob Esponja responde:")
    print(respuesta["message"]["content"].strip())
    print("\n🌊 ¡Cuidemos el océano! 🌊")


if __name__ == "__main__":
    main()
