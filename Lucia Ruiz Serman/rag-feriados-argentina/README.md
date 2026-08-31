# RAG mínimo sobre feriados y fechas conmemorativas de Argentina

Basado en el ejemplo `sasha/calendario-rag` del profesor, con un documento
de datos propio: los feriados nacionales 2026 de Argentina (Ley 27.399) más
algunas fechas conmemorativas no feriado (Día de la Madre, Día del Maestro,
Día de la Tradición, etc.).

El mecanismo es el mismo: partir el documento en fragmentos, convertirlos en
vectores, buscar los más parecidos a la pregunta y pedirle al modelo que
conteste **solo** con eso. Si la pregunta no tiene respuesta en el documento
(por ejemplo, "¿qué feriados hay en 2027?"), el modelo tiene que decir que no
lo sabe en vez de inventar.

## Requisitos

- Ollama corriendo (`ollama serve`)
- Dos modelos:

ollama pull qwen2.5:3b
ollama pull nomic-embed-text


## Cómo correrlo

./run-chatbot.sh
./run-consulta.sh "¿Cuándo es el Día de la Independencia?"


## Ejemplos de preguntas

| Pregunta | Qué esperar |
|---|---|
| ¿Cuándo es el Día de la Independencia? | 9 de julio |
| ¿El 20 de junio es feriado? | Sí, pero cae sábado y no da día libre extra |
| ¿Cuánto sale viajar en el feriado de agosto? | «No lo sé, eso no figura en el calendario» — el documento no tiene precios |

## Fuente de los datos

`datos/feriados-argentina-2026.md`, armado a partir del calendario oficial
publicado por la Jefatura de Gabinete de Ministros
(argentina.gob.ar/jefatura/feriados-nacionales-2026), capturado el
25/08/2026.
