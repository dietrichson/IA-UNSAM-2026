# RAG mínimo sobre el calendario académico

## Qué es

Un ejemplo chiquito de **RAG** (*Retrieval-Augmented Generation*, generación
aumentada por recuperación) que contesta preguntas sobre el calendario
académico de la Escuela de Humanidades de la UNSAM.

La idea es sencilla. El modelo de lenguaje no sabe nada del calendario: nunca lo
vio. Entonces, antes de preguntarle, buscamos en el calendario las pocas
entradas que se parecen a tu pregunta y se las pegamos en el prompt. El modelo
lee esos fragmentos en el momento y contesta con eso. Nada más que con eso.

Los cinco pasos, que en el código están numerados `[1]` a `[5]`:

1. Leer el calendario y partirlo en fragmentos.
2. Convertir cada fragmento en un vector (un montón de números que representan
   su significado).
3. Convertir tu pregunta en un vector, con el mismo modelo.
4. Buscar los vectores más parecidos al de la pregunta. Eso es la
   *recuperación*.
5. Pasarle al modelo esos fragmentos y tu pregunta, y pedirle que conteste
   **solamente** con lo que ahí dice.

## Los dos scripts

| Script | Qué hace | Cuándo usarlo |
|---|---|---|
| `consulta-unica.py` | Una pregunta por corrida. Imprime los cinco pasos en orden, con sus números. | Para **leer el código** y ver el mecanismo. Cada corrida arranca de cero, así que ves todo el proceso completo. |
| `chatbot.py` | Vectoriza el calendario una sola vez al arrancar y después te deja preguntar todas las veces que quieras. | Para **jugar y probar preguntas**. Mucho más rápido a partir de la segunda. |

La diferencia no es cosmética. `consulta-unica.py` vuelve a vectorizar los 37
fragmentos cada vez que lo corrés, lo cual es un desperdicio: el calendario no
cambió. `chatbot.py` los calcula una vez y los reusa. Así funciona una
aplicación de RAG de verdad: los vectores del corpus se calculan una vez, se
guardan, y lo único que se calcula por pregunta es el vector de la pregunta.

## Requisitos

- **Ollama** corriendo (`ollama serve`).
- Dos modelos:

```
ollama pull qwen2.5:3b          # el que redacta la respuesta
ollama pull nomic-embed-text    # el que arma los vectores (~274 MB, 768 dimensiones)
```

Son dos modelos distintos porque hacen dos cosas distintas. `nomic-embed-text`
no escribe nada: convierte texto en 768 números. `qwen2.5:3b` no busca nada:
escribe la respuesta.

## Cómo correrlo

### En Codespaces

`.devcontainer/setup.sh` ya instala `ollama` y `numpy` y baja los dos modelos.
No tenés que preparar nada:

```
python3 sasha/calendario-rag/chatbot.py
python3 sasha/calendario-rag/consulta-unica.py "¿Cuándo empieza el segundo cuatrimestre?"
```

### En tu Mac

Si instalaste Python con Homebrew, `pip install` te va a rebotar con un error
que dice `externally-managed-environment`. No está roto: Homebrew protege su
Python para que no le metas paquetes por encima. La forma más corta de
esquivarlo es `uv`, que arma un entorno descartable al vuelo:

```
uv run --with ollama --with numpy python3 sasha/calendario-rag/chatbot.py
```

Si vas a volver seguido, armate un entorno que quede:

```
uv venv
uv pip install ollama numpy
source .venv/bin/activate
python3 sasha/calendario-rag/chatbot.py
```

## Ejemplos de preguntas

| Pregunta | Qué esperar |
|---|---|
| ¿Cuándo empieza el segundo cuatrimestre? | 4 de agosto |
| ¿Cuándo es el receso de invierno? | Del 21 al 27 de julio |
| ¿Cuánto sale la cuota? | «No lo sé, eso no figura en el calendario» |

La tercera es la importante. El calendario no dice absolutamente nada sobre
cuotas, así que la respuesta correcta es **no contestar**. Un modelo suelto,
sin instrucciones, te inventa un número con toda confianza. El *system prompt*
de estos scripts le prohíbe salirse de los fragmentos y le da la frase exacta
para cuando no hay respuesta. Eso es el **anclaje** (*grounding*): atar lo que
el modelo dice a un documento concreto.

Probá otras: preguntale por las equivalencias, por las mesas de suficiencia,
por cuándo termina el primer cuatrimestre. Y probá algo que no esté, como
«¿dónde queda el campus?», para verlo negarse.

## Los puntajes de similitud

Los scripts te muestran, para cada fragmento recuperado, cuánto se parece a tu
pregunta. Es un número entre 0 y 1 (similitud coseno). Estos son los valores
reales de las tres preguntas de arriba:

| Pregunta | Mejor puntaje | Rango del top-3 |
|---|---:|---|
| ¿Cuándo empieza el segundo cuatrimestre? | 0,645 | 0,617–0,645 |
| ¿Cuándo es el receso de invierno? | 0,660 | 0,560–0,660 |
| ¿Cuánto sale la cuota? | 0,566 | 0,536–0,566 |

Mirá la forma, no la altura. En «receso de invierno» hay un ganador claro:
0,660 contra 0,560, un salto de cien puntos. La búsqueda encontró la entrada y
se nota.

En «cuánto sale la cuota» los tres puntajes son planos y mediocres: 0,566,
0,564, 0,536. Ninguno gana. **Esa chatura es la señal de que no hay nada
relevante.** La búsqueda siempre devuelve sus tres mejores fragmentos, pase lo
que pase: nunca te dice «no encontré nada», porque no sabe hacerlo. Solo ordena
por parecido y te da los de arriba. Aunque todos sean malos, hay tres de arriba.

Por eso el *system prompt* tiene que existir. La recuperación entrega basura
educada y es el prompt el que le enseña al modelo a reconocerla y decir que no
sabe.

## Cómo replicarlo con otros datos

Poné tu archivo en `datos/` y pasáselo con `--datos`:

```
python3 sasha/calendario-rag/chatbot.py --datos sasha/calendario-rag/datos/mi-archivo.md
```

(La ruta de `--datos` se resuelve desde donde estás parado, así que si corrés
desde la raíz del repo, escribila entera como arriba. Sin `--datos`, el script
usa el calendario que tiene al lado, sin importar desde dónde lo llames.)

Lo único que hay que respetar es el formato. El parser lee el archivo línea por
línea: cuando una línea es exactamente el nombre de una sección (acá, un mes:
`Julio`, `Agosto`, `Todo el año`), la toma como encabezado; cada línea que viene
abajo es una entrada, y se convierte en un fragmento con el encabezado adelante
—queda `Julio — 21 al 27 de julio — Receso invernal`—. Así cada fragmento se
entiende solo, sin necesidad de leer los de al lado.

Si tus secciones no son meses, cambiá el conjunto `ENCABEZADOS` arriba de todo
en el script.

## Por qué un fragmento por fecha

La forma habitual de cortar un documento es en ventanas de N palabras. Acá no
sirve. El calendario entero tiene **437 palabras**: con ventanas de 120 te
quedan 4 o 5 fragmentos, y traer los 3 mejores sería traer casi el documento
completo. La recuperación estaría corriendo, sí, pero no se vería hacer nada,
porque devolvería todo siempre.

Un fragmento por entrada da **37**. Ahí sí, pedir los 3 mejores es elegir 3
entre 37, y en pantalla se ve la selección ocurriendo. La forma de cortar
depende del documento, y este documento ya viene cortado en pedacitos con
sentido propio: aprovechémoslo.

## Una advertencia honesta

Este calendario entra entero en la ventana de contexto de cualquier modelo
moderno. Podrías pegarlo completo en el prompt, sin buscar nada, y andaría
igual de bien o mejor. **Acá la recuperación no hace falta.**

Está para que la veas funcionar en algo lo bastante chico como para entenderlo
de punta a punta. RAG se vuelve necesario cuando el corpus son cientos de
páginas, o miles, y ya no hay ventana de contexto que las aguante —ni plata
para pagar los tokens si la hubiera—. El mecanismo es exactamente este; lo que
cambia es la escala.

## Limitación de los datos

`datos/calendario-unsam-2025.md` es el calendario **2025**, y hay que
actualizarlo a mano porque no existe forma de bajarlo con un script.

La página oficial —<https://unsam.edu.ar/escuelas/eh/calendario-academico.php>—
está detrás de un desafío de Cloudflare que bloquea cualquier script. Este
archivo es una captura hecha a mano de una copia guardada en el Wayback Machine,
con fecha **2025-08-07**.

Para actualizarlo hay que abrir la página en el navegador, copiar el texto y
pegarlo respetando el formato descrito arriba. A mano. Es una limitación real y
bastante común: muchísimos datos públicos están detrás de defensas
anti-scraping, y a veces el paso de «conseguir el documento» cuesta más que
todo el sistema de RAG.
