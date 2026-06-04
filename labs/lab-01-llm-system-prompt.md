# Laboratorio 1: Ejecutar un LLM local con un system prompt propio

Tu primer contacto con un modelo de lenguaje (LLM) corriendo de forma **local**,
dentro del entorno del seminario. La idea es simple: levantar el modelo en la
máquina del curso y darle una **instrucción de sistema** (un *system prompt*)
para moldear su comportamiento.

Acá **no** hay RAG, ni embeddings, ni recuperación de documentos. Eso llega en el
[Laboratorio 2](./lab-02-rag-ollama.md). Por ahora, solo el modelo y vos.

## Objetivo

- Ejecutar un LLM local con **Ollama**, la misma herramienta que ya trae el entorno.
- Entender qué es un **system prompt** y cómo cambia las respuestas del modelo.
- Definir tu propia instrucción de sistema y comprobar el efecto.

## El entorno

El repositorio incluye una definición de **dev container** que arma una máquina
de trabajo lista para usar. Cada estudiante abre un **Codespace** en el navegador
y obtiene Ollama ya instalado, junto con un modelo pequeño descargado. Sin
instalación local, sin necesidad de GPU.

Lo que ya está disponible cuando arranca la terminal:

- **Ollama** corriendo en CPU (Codespaces no tiene GPU, lo cual está bien para
  modelos pequeños). Su API queda expuesta en el puerto **11434**.
- **qwen2.5:3b** — el modelo de chat por defecto: pequeño, rápido y predecible.
- Python 3.12 con el paquete `ollama` preinstalado (lo vamos a usar más adelante).

### Cómo lo iniciás

1. En la página del repositorio en GitHub: **Code → Codespaces → Create codespace on main**.
2. Esperá ~2 minutos la primera vez, mientras instala Ollama y descarga el modelo.
3. Cuando la terminal esté lista, ya podés hablar con el modelo.

Para confirmar que el servidor está arriba:

```bash
curl http://localhost:11434/api/tags
```

## Parte 1 — Hablar con el modelo, sin instrucciones

Primero, el modelo "tal cual viene". Abrí un chat interactivo:

```bash
ollama run qwen2.5:3b
```

Probá un par de preguntas y observá el tono y el estilo por defecto. Por ejemplo:

```
>>> ¿Qué es la fotosíntesis?
>>> Contame un chiste.
```

Para salir del chat interactivo, escribí `/bye`.

## Parte 2 — Pasar un system prompt en una sola corrida

El **system prompt** es una instrucción que se le da al modelo *antes* que la
consulta del usuario, y define cómo se tiene que comportar: su rol, su tono, sus
reglas. No es la pregunta; es el "personaje" y las reglas del juego.

Con Ollama podés fijar la instrucción de sistema con la opción `--system` y
mandar una única consulta así:

```bash
ollama run qwen2.5:3b --system "Sos un asistente que responde siempre en una sola oración, de forma muy concisa." "¿Qué es la fotosíntesis?"
```

Compará la respuesta con la de la Parte 1: misma pregunta, comportamiento
distinto. Eso es el system prompt en acción.

Probá variantes y observá el cambio:

```bash
ollama run qwen2.5:3b --system "Sos un profesor de biología paciente. Explicá con una analogía cotidiana." "¿Qué es la fotosíntesis?"
```

```bash
ollama run qwen2.5:3b --system "Respondé siempre en formato de lista con viñetas, sin texto introductorio." "Dame ideas para estudiar mejor."
```

## Parte 3 — Guardar tu instrucción en un Modelfile

Pasar `--system` en cada corrida funciona, pero si querés *tu propio modelo* con
una personalidad fija, conviene un **Modelfile**. Es un archivo de texto donde
declarás de qué modelo base partís y qué system prompt lleva incorporado.

Creá un archivo llamado `Modelfile` (sin extensión) con este contenido:

```dockerfile
FROM qwen2.5:3b

# Tu instrucción de sistema: cambiá este texto a gusto.
SYSTEM """
Sos "Tutor UNSAM", un asistente del Seminario Experimental de Inteligencia
Artificial. Respondés en español rioplatense, usás voseo y sos breve y claro.
Si no sabés algo, lo decís en vez de inventar.
"""

# Opcional: parámetros de generación. temperature baja = respuestas más estables.
PARAMETER temperature 0.4
```

Construí tu modelo a partir de ese Modelfile (le ponemos el nombre `tutor-unsam`):

```bash
ollama create tutor-unsam -f Modelfile
```

Ahora corré *tu* modelo. Ya lleva el system prompt adentro, no hace falta repetirlo:

```bash
ollama run tutor-unsam "Presentate y decime en qué me podés ayudar."
```

Probá también una consulta donde el modelo debería admitir que no sabe, para ver
que respeta la regla del Modelfile:

```bash
ollama run tutor-unsam "¿Cuál es la nota exacta que me saqué en el último parcial?"
```

## Parte 4 (opcional) — El system prompt desde la API

El mismo system prompt se puede mandar por la API HTTP de Ollama (la del puerto
11434). Esto es lo que vas a usar cuando programes, en vez de la terminal:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "stream": false,
  "messages": [
    { "role": "system", "content": "Sos un asistente que responde solo con emojis." },
    { "role": "user",   "content": "Hola, ¿cómo estás?" }
  ]
}'
```

Fijate que el mensaje con `"role": "system"` es exactamente el system prompt:
lo mismo que `--system` en la terminal, pero desde código.

## Para entregar / discutir

1. Una instrucción de sistema propia (en un `Modelfile` o con `--system`) que le
   dé al modelo un rol o estilo claro.
2. Dos ejemplos de la **misma** pregunta: uno sin system prompt y otro con el
   tuyo, mostrando la diferencia.
3. Una frase corta: ¿qué pudiste cambiar con el system prompt y qué **no**?

## Notas

- **Solo CPU:** un modelo de 3B genera texto a unos pocos hasta ~10 tokens/seg.
  Suficiente para esta práctica.
- **System prompt ≠ pregunta:** el system prompt fija el comportamiento; la
  pregunta del usuario va aparte. Si mezclás todo en un solo mensaje, perdés esa
  separación.
- **Cambiar el modelo base:** definí un secreto de Codespaces `OLLAMA_MODEL`, o
  cambiá la línea `FROM` de tu `Modelfile`.
- Para no consumir horas, cerrá la pestaña y usá **Stop** sobre el Codespace
  desde el panel de Codespaces de GitHub cuando termines.
