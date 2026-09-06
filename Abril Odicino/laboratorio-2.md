# Laboratorio 2: RAG con Ollama

## Documento usado como contexto

Para probar el sistema RAG creé un archivo en `docs/apuntes-rag.md` con información breve sobre fotosíntesis y sobre qué es RAG.

## Pregunta realizada

¿Qué es RAG y cuál es su ventaja?

## Fragmentos recuperados

El script cargó 1 archivo y lo dividió en 2 fragmentos. Para la pregunta realizada, recuperó estos fragmentos como los más relevantes:

```text
1. (score 0.690) para responder una pregunta. La ventaja de RAG es que permite que un modelo responda [...]
2. (score 0.637) # Apuntes para probar RAG La fotosíntesis es el proceso por el cual las plantas, [...]
```

## Respuesta del modelo

```text
RAG es un sistema que combina recuperación de información con generación de texto. Su principal ventaja es que permite que un modelo responda usando información externa al modelo.
```

## Reflexión

En esta prueba pude ver que RAG no responde solamente desde el conocimiento interno del modelo, sino que primero busca fragmentos relevantes en documentos y después usa ese contexto para generar la respuesta. La ventaja es que se puede agregar información externa sin reentrenar el modelo.