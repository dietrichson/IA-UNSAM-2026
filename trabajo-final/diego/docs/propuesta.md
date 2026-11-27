# Propuesta

## Resumen

Construir un juego web de decisiones legales sobre el caso Salomón contra los medios, en el que una **jueza controlada por IA**, con personalidad propia y conocimiento de las leyes y del caso, evalúa los argumentos de la persona que juega y dicta una sentencia.

## Problema

Los casos sobre libertad de expresión e intimidad se estudian como textos largos y abstractos. Para estudiantes de comunicación es difícil ver cómo pesan, en una decisión concreta, conceptos como interés general, consentimiento o real malicia.

## Para quién

Estudiantes de comunicación y periodismo que quieren entender cómo un tribunal razona un caso de intromisión en la intimidad por parte de un medio.

## Qué vamos a hacer

- Un relato animado que presenta los hechos y los personajes.
- Un juzgado donde se responden 8 preguntas: con opciones (modo fácil) o escribiendo el argumento (modo difícil).
- Una jueza de IA que consulta un corpus mediante RAG, comenta la solidez del caso y dicta la sentencia, con las leyes como base.
- Una pantalla final que compara el resultado con lo que pasó en la realidad.

## Qué no vamos a hacer

- Asesoramiento legal ni un simulador jurídico completo.
- Más de un caso en esta versión.
- Voces ni declaraciones inventadas de las personas reales del caso.

## Herramientas

HTML, CSS y JavaScript en el navegador; un servidor en Python; Claude (SDK de Anthropic) o un modelo local con Ollama; búsqueda BM25 sobre textos en Markdown.

## Relación con el seminario

Aplica un sistema RAG (recuperar información antes de generar), un agente con personalidad definida por un prompt de sistema, y la conexión de una aplicación con un modelo de lenguaje por API o de forma local.

## Riesgos

- La IA puede inventar datos legales: se mitiga con reglas del prompt y con el corpus citado.
- Los textos legales los redactó un asistente de IA y pueden tener errores: se advierte en el juego y deben verificarse con las fuentes.
- Los modelos locales son lentos: se informa la espera y hay un modo sin IA de respaldo.

## Entregables

Código en `src/`, documentación en `docs/`, y un README que explica cómo correrlo.
