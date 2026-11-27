# El caso Salomón: juego de decisiones legales con una jueza de IA

Trabajo final del seminario de IA (UNSAM). Autor: Diego.

## Qué es

Un juego web en el que la persona defiende a la actora en un juicio real y conocido: el caso de Beatriz Salomón contra los medios que emitieron y repitieron una cámara oculta sobre su esposo (2004). Primero se presentan los personajes y se ve un relato animado de lo ocurrido; después el juego pasa a un juzgado, donde una **jueza controlada por IA** hace preguntas, comenta qué tan sólido está el caso y dicta una sentencia al final.

La jueza no responde "de memoria": **busca en un corpus** (hechos del caso, Constitución y tratados, Código Civil, doctrina) con un sistema RAG y muestra qué material consultó.

Es una reconstrucción educativa basada en la sentencia de la Cámara Civil (2018) y en notas periodísticas. Las voces del juzgado son ficticias. No es asesoramiento legal.

## Cómo correrlo (Codespaces)

1. Abrir el repositorio en un Codespace.
2. En la terminal:

       bash trabajo-final/diego/src/iniciar.sh

3. En la pestaña **Puertos**, abrir el puerto 8000.

La línea gris de la pantalla de inicio indica con qué IA trabaja la jueza.

## Con qué IA trabaja la jueza

El servidor elige solo, en este orden:

1. **Claude** (SDK de Anthropic), si existe la variable de entorno `ANTHROPIC_API_KEY`. Modelo por defecto: `claude-haiku-5-5`; se cambia con `MODELO_JUEZA`.
2. **Ollama** (modelo local y gratuito), si está encendido. Usa el primer modelo que conversa (por ejemplo `qwen2.5:3b`); se elige con `OLLAMA_MODELO`.
3. **Modo sin IA**: criterios locales fijos, para que el juego nunca se rompa.

La clave nunca se escribe en el código ni se sube al repositorio. En Codespaces se guarda como secreto (Settings → Codespaces → Secrets).

## Cómo se juega

- **Fácil:** 8 preguntas con tres opciones (muy buena, parcial, débil).
- **Difícil:** las mismas 8 preguntas, pero el argumento se escribe y lo evalúa la jueza (IA).
- En ambos modos se ve primero el relato inicial y al final hay una pantalla con "qué pasó en la realidad".

## Estructura

    trabajo-final/diego/
    ├── README.md
    ├── docs/
    │   ├── propuesta.md
    │   ├── requisitos.md
    │   ├── diseno.md
    │   └── pruebas.md
    └── src/
        ├── index.html, estilos.css, main.js   (juego en el navegador)
        ├── datos.js                           (personajes, relato, preguntas)
        ├── servidor.py                        (servidor, RAG y conexión con la IA)
        ├── rubrica.json                       (criterio ideal de cada pregunta)
        ├── corpus/                            (textos que consulta la jueza)
        ├── iniciar.sh, requirements.txt

## Limitaciones

- Los textos de `src/corpus/` son resúmenes didácticos y **no fueron revisados por un abogado**: deben verificarse con las fuentes oficiales.
- Los modelos locales pequeños son más lentos y menos precisos que Claude.
- Un solo caso (Salomón). El selector de casos queda como trabajo futuro.

## Fuentes

Sentencia de la Cámara Civil, Sala B (24/05/2018, "Salomón, Beatriz Raquel y otros c/ Rial, Jorge y otros s/ daños y perjuicios"); nota de La Nación (02/07/2025); comentario de elDial sobre el fallo.
