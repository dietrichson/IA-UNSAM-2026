# RAG mínimo — Panadería Santa Anita

Adaptado del ejemplo `sasha/calendario-rag` (IA-UNSAM-2026), mismo mecanismo
pero apuntando a la info comercial de la panadería en vez del calendario
académico.

## Qué es

El modelo de lenguaje no sabe nada de Santa Anita. Antes de preguntarle,
buscamos en `datos/panaderia-santa-anita.md` las entradas que se parecen a
la pregunta y se las pasamos en el prompt. El modelo contesta solo con eso.

Los 5 pasos (numerados en el código como `[1]` a `[5]` en `consulta-unica.py`):

1. Leer `datos/panaderia-santa-anita.md` y partirlo en fragmentos (uno por
   línea, con el encabezado de sección adelante — ej. "Horarios — Lunes:
   cerrado todo el día").
2. Convertir cada fragmento en un vector con `nomic-embed-text`.
3. Convertir la pregunta en un vector, con el mismo modelo.
4. Buscar los vectores más parecidos al de la pregunta (similitud coseno).
5. Pasarle esos fragmentos + la pregunta a `qwen2.5:3b`, pidiéndole que
   conteste solo con lo que ahí dice.

## Los dos scripts

| Script | Qué hace | Cuándo usarlo |
|---|---|---|
| `consulta-unica.py` | Una pregunta por corrida, imprime los 5 pasos. | Para ver el mecanismo completo. |
| `chatbot.py` | Vectoriza una sola vez y deja preguntar en loop. | Para jugar y probar preguntas. |

## Requisitos

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
pip install ollama numpy
```

## Cómo correrlo

```bash
python3 chatbot.py
python3 consulta-unica.py "¿A qué hora abren los domingos?"
```

## Ejemplos de preguntas

| Pregunta | Qué esperar |
|---|---|
| ¿A qué hora abren los domingos? | 08:30 a 14:00 y 16:30 a 19:00 |
| ¿Hacen delivery? | Sí, por la app V-go, solo línea vegana |
| ¿Cuánto sale el kilo de pan? | "No lo sé, esa información no está en los datos de la panadería." |

La tercera pregunta es la importante: el archivo de datos no tiene precios,
así que la respuesta correcta es que el bot lo reconozca y no invente un
número. Eso es el **anclaje (grounding)**: atar lo que dice el modelo a un
documento concreto.

## Cómo agregar más datos

Editá `datos/panaderia-santa-anita.md` respetando el formato: una línea con
el nombre exacto de una sección (debe estar en el set `ENCABEZADOS`, que
está duplicado arriba de `consulta-unica.py` y de `chatbot.py` — si agregás
una sección nueva, actualizalo en los dos) y, debajo, una entrada por línea.

O usá otro archivo con `--datos`:

```bash
python3 chatbot.py --datos datos/otro-archivo.md
```

## Por qué no hay un módulo compartido

`consulta-unica.py` y `chatbot.py` repiten el código de parseo/vectorización
a propósito, calcando la estructura del ejemplo original: cada script es
autónomo y se lee de punta a punta sin saltar a otro archivo. La diferencia
entre uno y otro no es solo estética: `consulta-unica.py` vectoriza todo de
cero en cada corrida (para ver el proceso completo), mientras que
`chatbot.py` lo hace una sola vez y reusa los vectores en cada pregunta.
