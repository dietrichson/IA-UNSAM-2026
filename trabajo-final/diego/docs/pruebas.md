# Pruebas

Fecha de las pruebas automáticas: 16 de noviembre de 2026. Se ejecutaron sobre `src/` con el servidor en modo sin IA.

## 1. Pruebas automáticas ejecutadas

| ID | Qué se comprobó | Resultado |
|----|-----------------|-----------|
| A1 | Hay 8 preguntas y cada una tiene exactamente una opción de 2, una de 1 y una de 0 puntos. | Correcto |
| A2 | Diferencia de largo entre las opciones de cada pregunta (caracteres): 4, 4, 10, 8, 7, 2, 3 y 12. | Máximo 12 caracteres sobre unos 120 |
| A3 | Posición de la opción correcta en 5.000 partidas simuladas (arriba, medio, abajo). | 33 %, 33 % y 34 % |
| A4 | Búsqueda RAG: 8 consultas sobre real malicia, Campillay, derecho a la imagen, pérdida de chances, artículo 19, derecho de respuesta, Balbín y fallo de 2025. | La primera sección recuperada fue la esperada en 8 de 8 |
| A5 | Modo sin IA: la respuesta ideal de cada pregunta puntúa 2 y una respuesta sin relación puntúa 0. | 8 de 8 y 8 de 8 |
| A6 | Sentencia sin IA según la solidez: 16/16, 12/16, 6/16 y 0/16. | favorable, favorable, rechazada y rechazada |
| A7 | El navegador pide `/` (juego), `/rubrica.json`, `/servidor.py` y `/corpus/01-hechos-del-caso.md`. | Códigos 200, 404, 404 y 404 (200 para el juego y 404 para lo bloqueado) |
| A8 | Estado del servidor en una máquina sin clave ni Ollama. | `{"ia": false, "modelo": "Ollama: "}` |
| A9 | Sintaxis de `main.js`, `datos.js` y `servidor.py`. | Sin errores |
| A10 | Conexión con Ollama y selección de modelo, con un Ollama simulado (se descartan modelos de embeddings y de personajes). | Elige `qwen2.5:3b` y recibe la respuesta en JSON |

Límite: A10 usó un servidor simulado. La llamada real a Claude **no se pudo probar** en este entorno por falta de clave.

## 2. Pruebas manuales (completar al ejecutarlas en Codespaces)

| ID | Requisito | Pasos | Resultado esperado | Resultado |
|----|-----------|-------|--------------------|-----------|
| M1 | RF1, RF2 | Abrir el juego, elegir modo y presentación, ver los personajes. | Se muestran los 4 personajes y la línea sobre la IA. | ☐ |
| M2 | RF3 | Recorrer el relato animado. | Seis escenas con narración y controles. | ☐ |
| M3 | RF4 | Entrar al juzgado en una pantalla grande. | Jueza, partes, pregunta y respuesta se ven sin desplazarse. | ☐ |
| M4 | RF5, RF10 | Jugar el modo fácil completo. | Las explicaciones aparecen y el resultado muestra solidez y conteo. | ☐ |
| M5 | RF6, RF7, RF8 | Modo difícil con Ollama: responder una pregunta con un buen argumento. | Comentario de la jueza con fuentes consultadas y puntos. Tiempo: ____ s | ☐ |
| M6 | RF6 | Modo difícil: responder con un argumento sin relación. | Comentario crítico y 0 o 1 punto. | ☐ |
| M7 | RF9 | Terminar el modo difícil. | Sentencia fundamentada y consejo. Tiempo: ____ s | ☐ |
| M8 | RF11 | Probar con una clave de Claude (si está disponible). | La línea gris indica Claude y las respuestas llegan. Tiempo: ____ s | ☐ |
| M9 | RF11, RNF4 | Apagar Ollama y repetir una respuesta. | El juego sigue en modo sin IA. | ☐ |
| M10 | RNF6 | Abrir el juego en un celular. | Se puede jugar en una columna. | ☐ |

## 3. Problemas conocidos

- Los textos del corpus son resúmenes didácticos sin revisión jurídica.
- Con modelos locales pequeños la espera es larga y la calidad del comentario varía.
- Un solo caso.
