
# Propuesta · Copiloto de búsqueda laboral para Comunicación

**Autora:** María Belén Martínez Contardi · Trabajo final del seminario de IA (UNSAM, 2026)

## ¿Qué vamos a construir?

Una aplicación web que corre en la computadora de la persona y la ayuda a buscar trabajo en Comunicación con dos herramientas: un **sugeridor de puestos**, que compara su CV con una base de 40 avisos y explica qué le falta para cada uno, y un **adaptador de CV y carta**, que reescribe su CV y redacta una carta para una oferta concreta usando solo lo que ya figura en el CV.

## ¿Para quién es y qué problema resuelve?

Es para **estudiantes avanzados y graduados de Comunicación** que buscan su primer trabajo o quieren cambiar de puesto. Resuelve tres problemas concretos:

- Los roles del rubro tienen nombres difusos (community manager, prensa, comunicación interna, contenidos…) y cuesta saber cuáles encajan con la formación y la experiencia propias.
- Se envía el mismo CV a todas las ofertas, sin usar el vocabulario de cada aviso.
- No es claro qué herramientas o requisitos faltan para un puesto ni cuáles conviene aprender primero.

## ¿Qué parte de IA tiene?

- **RAG** en el sugeridor: el CV y los puestos se convierten en vectores (embeddings con `bge-m3`), se recuperan los más cercanos y recién ahí un LLM los puntúa.
- **LLM con system prompt** (`qwen2.5:3b` en Ollama) para extraer datos de ofertas y CV, puntuar, adaptar el CV y escribir la carta. Los prompts son archivos de texto versionados.
- **Reglas y verificación alrededor del modelo:** como el modelo es chico, el puntaje combina lo que dice el LLM con reglas escritas a mano, y un verificador revisa que la salida no agregue datos que no están en el CV.

## ¿Qué del seminario ya sabemos usar y qué nos falta aprender?

**Ya sabemos usar:** un RAG armado con Ollama (embeddings, búsqueda por similitud), prompts con instrucciones de sistema y modelos locales.

**Nos falta aprender (y fue lo que más costó):** pedir salidas en JSON y validarlas; evitar que un modelo de 3.000 millones de parámetros invente datos; combinar el modelo con reglas; defenderse de instrucciones escondidas en el CV o la oferta (*prompt injection*); armar una interfaz con Streamlit; y medir la calidad con casos de prueba en lugar de confiar en la primera impresión.

## ¿Cómo sería la versión mínima que funciona?

Con el CV pegado y una oferta pegada, la app devuelve (1) las palabras clave que el CV tiene y las que no, (2) un CV adaptado y una carta, ambos revisados por el verificador, y (3) una lista de puestos de la base ordenada por coincidencia con los motivos y las brechas de cada uno. Todo funciona sin cuentas ni claves, con Ollama y 8 GB de RAM. Fuera de la versión mínima quedan, por decisión propia, el envío automático de postulaciones, el rastreo de portales de empleo y el seguimiento de postulaciones.
