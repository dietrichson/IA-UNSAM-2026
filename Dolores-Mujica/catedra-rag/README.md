# Asistente de Cátedra - RAG Universitario

## Qué es
Un sistema de RAG (Retrieval-Augmented Generation) diseñado para responder consultas de estudiantes sobre el contenido académico de la asignatura.

## Scripts del proyecto
- consulta-unica.py: Ejecuta el flujo RAG completo para una sola pregunta.
- chatbot.py: Mantiene una conversación continua vectorizando una sola vez.

## Requisitos
- Ollama con modelos nomic-embed-text y qwen2.5:3b.
- Librerías: ollama, numpy.

## Ejecución
- ./run-consulta.sh "tu pregunta"
- ./run-chatbot.sh
