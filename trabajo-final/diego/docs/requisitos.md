# Requisitos

## Requisitos funcionales

| ID | Requisito |
|----|-----------|
| RF1 | La pantalla de inicio permite elegir la presentación (abogada o abogado) y la dificultad (fácil o difícil). |
| RF2 | Antes de jugar se presentan los personajes y el contexto del caso. |
| RF3 | Un relato animado de seis escenas explica los hechos, solo con narración (sin voces ni frases inventadas de personas reales). |
| RF4 | El juzgado muestra en una sola pantalla a la jueza, a las partes, la pregunta y el espacio de respuesta. |
| RF5 | Modo fácil: 8 preguntas con tres opciones (muy buena, parcial, débil) de largo parecido y posición aleatoria; tras responder se explica la opción. |
| RF6 | Modo difícil: 8 preguntas con respuesta escrita; la jueza (IA) comenta la solidez del argumento sin decir "correcto" o "incorrecto" y le da de 0 a 2 puntos. |
| RF7 | La jueza consulta un corpus (RAG) con los hechos del caso, la Constitución y tratados, el Código Civil y doctrina, y muestra el material consultado. |
| RF8 | La jueza tiene una personalidad definida (formal, exigente, imparcial) y reglas: fundar solo en el material recuperado, citar fuentes y no inventar. |
| RF9 | Al final se dicta una sentencia fundamentada según todas las respuestas, con un consejo para mejorar. |
| RF10 | La pantalla final muestra la solidez del caso en porcentaje, el conteo de respuestas por tipo, el resultado por pregunta y "qué pasó en la realidad". |
| RF11 | La jueza funciona con Claude (SDK), con Ollama local o, si no hay ninguno, en modo sin IA. |
| RF12 | El juego avisa que es una reconstrucción educativa y que no es asesoramiento legal. |

## Requisitos no funcionales

| ID | Requisito |
|----|-----------|
| RNF1 | Se inicia con un solo comando en Codespaces. |
| RNF2 | Ninguna clave se escribe en el código ni se sube al repositorio; se lee de una variable de entorno. |
| RNF3 | El navegador no puede descargar la rúbrica, el corpus ni el código del servidor. |
| RNF4 | Si la IA falla o no está disponible, el juego sigue funcionando en modo sin IA. |
| RNF5 | Con IA local, la pantalla informa que la jueza está deliberando; se mide el tiempo de respuesta en las pruebas. |
| RNF6 | La interfaz se adapta a pantallas grandes y a celulares. |
| RNF7 | La estética es sobria (estilo juzgado) y legible. |

## Criterios para considerar el proyecto terminado

- Todos los requisitos están comprobados en `docs/pruebas.md`.
- El README explica cómo correrlo y qué limitaciones tiene.
- No hay claves ni archivos grandes en el repositorio.
- Las etapas fueron aprobadas en sus tickets.
