# Laboratorio 2: RAG con Ollama

Un entorno en la nube listo para usar, pensado para el curso de IA/LLM. Cada estudiante
abre un Codespace en el navegador y obtiene Ollama, un modelo pequeño y el laboratorio de
RAG ya instalados: sin instalación local, sin necesidad de GPU.

## Qué incluye

- **Ollama** corriendo en CPU (Codespaces no tiene GPU, lo cual está bien para modelos pequeños)
- **qwen2.5:3b** — el modelo de chat por defecto: pequeño, rápido y predecible
- **nomic-embed-text** — modelo de embeddings para el laboratorio de RAG
- **rag.py** — el script de RAG sin frameworks, listo para ejecutar
- Python 3.12 con `ollama` y `numpy` preinstalados

## Cómo lo inician los estudiantes

1. En la página del repositorio en GitHub: **Code → Codespaces → Create codespace on main**.
2. Esperá ~2 minutos mientras instala Ollama y descarga los modelos (una sola vez).
3. Cuando la terminal esté lista:

   ```bash
   ollama run qwen2.5:3b              # chat interactivo
   python rag.py "tu pregunta"        # el laboratorio de RAG (crea un documento de ejemplo si no hay ninguno)
   ```

Colocá archivos `.txt`/`.md` en una carpeta `docs/` para que RAG pueda recuperarlos.

## Notas

- **Solo CPU:** un modelo de 3B genera texto a unos pocos hasta ~10 tokens/seg. Suficiente para demos.
- **Costo:** el plan gratuito (~120 horas-núcleo al mes por cuenta) cubre aproximadamente
  30 horas en esta máquina de 4 núcleos: normalmente alcanza para el trabajo del curso. Se factura
  solo mientras el Codespace está en ejecución; se suspende automáticamente cuando está inactivo.
- **Cambiar el modelo:** definí un secreto de Codespaces `OLLAMA_MODEL`, o editá
  `CHAT_MODEL` en `rag.py`.
- Para no consumir horas, cerrá la pestaña y usá **Stop** sobre el Codespace desde el
  panel de Codespaces de GitHub cuando termines.

## Estructura del repositorio

```
.
├── .devcontainer/
│   ├── devcontainer.json   # tamaño de la máquina, puertos, hooks de configuración
│   └── setup.sh            # instala Ollama, descarga modelos, instala dependencias
├── rag.py                  # script del laboratorio de RAG
└── docs/                   # (opcional) tus documentos para RAG
```
