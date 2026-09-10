# Información técnica y laboratorios

En este seminario trabajamos sobre GitHub. El primer paso es hacer un **fork** de este repositorio a tu propia cuenta de GitHub, así tenés tu propia copia para trabajar. Sobre esa copia vas a ir haciendo los laboratorios y sumando tus aportes a lo largo del semestre.

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
- [Laboratorio 3: Silicon sampling](./labs/lab-03-silicon-sampling.md) — generar una muestra sintética con un LLM y analizar dónde y por qué falla frente a datos reales.

Se van a ir agregando más laboratorios a medida que avance el seminario (que todavía no empezó).
