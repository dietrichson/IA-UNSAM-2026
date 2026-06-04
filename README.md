# Seminario Experimental de Inteligencia Artificial

Este es el repositorio del **Seminario Experimental de Inteligencia Artificial** (UNSAM).

Acá vas a encontrar todo lo que hagamos en clase: a lo largo del semestre se va a publicar
todo el material del curso, las tareas y trabajos prácticos, y también los aportes de cada
estudiante. La idea es que este repositorio se construya de forma colaborativa, creciendo
clase a clase con lo que vayamos produciendo entre todos.

## Entorno de trabajo (dev container)

El repositorio incluye una definición de **dev container** (`.devcontainer/`) que
arma automáticamente una máquina de trabajo lista para usar. Funciona con
**GitHub Codespaces** y con **Dev Containers**, así que no tenés que instalar nada
en tu propia computadora ni configurar tu entorno a mano.

El contenedor parte de una imagen de Python 3.12 y, al crearse, instala y deja
todo listo:

- **Ollama** ya instalado y corriendo en CPU, con su API expuesta en el puerto
  **11434**.
- El modelo de chat **qwen2.5:3b** y el modelo de embeddings **nomic-embed-text**
  ya descargados.
- Las dependencias de Python (`ollama`, `numpy`) preinstaladas.

La forma más simple de empezar: en la página del repositorio en GitHub,
**Code → Codespaces → Create codespace on main**. En un par de minutos tenés la
terminal lista para los laboratorios, sin instalación local y sin necesidad de GPU.

## Contenido

### Laboratorios

- [Laboratorio 1: LLM local con system prompt](./labs/lab-01-llm-system-prompt.md) — ejecutar un LLM local y darle una instrucción de sistema propia.
- [Laboratorio 2: RAG con Ollama](./labs/lab-02-rag-ollama.md) — recuperación aumentada (RAG) sobre un modelo local.

Se van a ir agregando más laboratorios a medida que avance el seminario.
