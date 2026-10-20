#!/usr/bin/env python3
"""Chatbot RAG sobre contaminación del agua y plásticos en el océano.

Es lo mismo que consulta-unica.py, pero conversado. La diferencia que importa:
consulta-unica.py vuelve a vectorizar los fragmentos en cada corrida, y acá
los vectorizamos UNA sola vez al arrancar. Después cada pregunta es sólo
vectorizar esa pregunta y multiplicar. Eso es lo que hace en serio una app de
RAG: los vectores del corpus se calculan una vez y se guardan.

Antes de correrlo (una sola vez):
    pip install ollama numpy
    ollama pull nomic-embed-text
    ollama pull qwen2.5:3b
    # Y crear el modelo de Bob Esponja:
    ollama create agua-rag -f agua-modelfile

Uso:
    python3 chatbot.py
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import ollama

EMBED_MODEL = "nomic-embed-text"
DATOS = Path(__file__).resolve().parent / "datos" / "basura-marina.txt"

# Palabras con las que el usuario corta la charla.
SALIDAS = {"salir", "chau", "exit", "quit", "adiós"}

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
    """Un fragmento por sección del documento, manteniendo el contexto.
    
    El documento tiene ~1500 palabras. Lo partimos en chunks de ~500 palabras
    con un solapamiento de 100 para no perder contexto.
    """
    fragmentos = []
    
    # Primero, separar por párrafos
    parrafos = texto.split('\n\n')
    parrafos = [p.strip() for p in parrafos if p.strip()]
    
    # Juntar párrafos en chunks de tamaño razonable
    chunk_actual = ""
    for parrafo in parrafos:
        if len(chunk_actual) + len(parrafo) < 800:
            chunk_actual += parrafo + "\n\n"
        else:
            if chunk_actual:
                fragmentos.append(chunk_actual.strip())
            chunk_actual = parrafo + "\n\n"
    
    if chunk_actual:
        fragmentos.append(chunk_actual.strip())
    
    # Si hay pocos fragmentos, hacerlos más chicos
    if len(fragmentos) < 5:
        fragmentos = []
        for i in range(0, len(parrafos), 3):
            chunk = "\n\n".join(parrafos[i:i+3])
            if chunk:
                fragmentos.append(chunk)
    
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

    print(f"\n  📄 Fragmentos recuperados (los {args.top_k} más parecidos):")
    for puesto, i in enumerate(indices, 1):
        # Mostrar solo primeras 100 palabras del fragmento
        preview = fragmentos[i][:100] + "..." if len(fragmentos[i]) > 100 else fragmentos[i]
        print(f"    {puesto}. (similitud {puntajes[i]:.3f}) {preview}")

    recuperados = "\n".join(f"- {fragmentos[i]}" for i in indices)
    try:
        respuesta = ollama.chat(model=args.modelo, messages=[
            {"role": "system", "content": SISTEMA},
            {"role": "user",
             "content": f"Fragmentos del documento sobre contaminación marina:\n{recuperados}\n\nPregunta: {pregunta}"},
        ])
    except Exception as error:
        abortar(error, args.modelo)
    print(f"\n  🧽 Respuesta de {args.modelo}:")
    print(f"    {respuesta['message']['content'].strip()}")


def mostrar_banner():
    """Muestra el banner de bienvenida de Bob Esponja."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🧽  ¡BOB ESPONJA - EXPERTO EN CONTAMINACIÓN MARINA!  🧽    ║
║                                                               ║
║   "¡El océano es mi hogar y tenemos que cuidarlo!"          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--top-k", type=int, default=3, help="Fragmentos a recuperar")
    parser.add_argument("--modelo", default="agua-rag", help="Modelo de chat (Bob Esponja)")
    parser.add_argument("--datos", type=Path, default=DATOS, help="Archivo del documento")
    parser.add_argument("--debug", action="store_true", help="Mostrar más información")
    args = parser.parse_args()

    if not args.datos.exists():
        sys.exit(f"❌ No encuentro el documento en {args.datos}")

    # Leer y partir el documento
    texto = args.datos.read_text(encoding="utf-8")
    fragmentos = partir_en_fragmentos(texto)

    if args.debug:
        print(f"📊 Documento partido en {len(fragmentos)} fragmentos.")
        for i, f in enumerate(fragmentos):
            print(f"  Fragmento {i+1}: {len(f)} caracteres")
            print(f"    {f[:100]}...")

    # Vectorizar los fragmentos UNA sola vez
    print(f"🧠 Vectorizando {len(fragmentos)} fragmentos con {EMBED_MODEL}...")
    vectores = vectorizar(fragmentos)
    print(f"✅ ¡Listo! Los vectores están calculados y reusables.")

    mostrar_banner()
    print("📚 Fuente: Argentina.gob.ar - Basura marina y contaminación por plásticos")
    print("💬 Preguntame sobre contaminación del agua, plásticos en el mar,")
    print("   cómo afecta a los animales marinos y qué podemos hacer.")
    print('   Escribí "salir" para terminar.')
    print("")

    while True:
        try:
            pregunta = input('🧑 Preguntá (o "salir"): ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if not pregunta or pregunta.lower() in SALIDAS:
            break
        
        if args.debug:
            print(f"\n🔍 Procesando: '{pregunta}'")
        
        try:
            responder(pregunta, fragmentos, vectores, args)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()

    print("\n🧽 Bob Esponja: ¡Chau, amigo! ¡No olvides reciclar y cuidar el océano! ¡Ja, ja, ja!")


if __name__ == "__main__":
    main()
