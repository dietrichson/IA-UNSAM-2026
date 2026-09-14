# Laboratorio 4: Crear software con agentes

En la clase del 14/09 vimos cómo se construyeron dos videojuegos sin escribir una línea de
código a mano: un párrafo en prosa se convirtió en una especificación, la especificación en
un *brief* para un agente, y el agente en código, tests y un informe. Vimos también que el
trabajo del humano no desapareció: se movió a **decir con precisión qué se quiere** y a
**verificar lo que llegó**.

Ahora te toca a vos. El objetivo no es que el programa sea sofisticado. El objetivo es que el
pedido esté tan bien planteado que un agente, o un compañero, o nosotros en clase, pueda
construirlo sin preguntarte nada.

> **Se evalúa la calidad del pedido y la verificación, no el tamaño del programa.**
> Un juego de diez líneas con un prompt claro, tests y un README vale más que uno de mil
> líneas que nadie puede reproducir ni comprobar.

## Objetivo

- Escribir una especificación en prosa de una pieza de software: qué hace, cómo se usa, qué
  **no** tiene que tener.
- Convertir esa especificación en un prompt que un agente pueda ejecutar de punta a punta.
- Si tenés las herramientas, ejecutarlo, verificar el resultado y subirlo al repo.
- Si no las tenés, dejar el pedido listo para que lo ejecutemos en clase.

## Qué podés construir

Un videojuego clásico es la opción recomendada, porque las reglas ya existen y no hay que
inventarlas: Snake, Pong, Buscaminas, 2048, Simon, Ahorcado, Cuatro en línea. Pero puede ser
cualquier programa chico: un conversor de unidades, un generador de horarios, un
cuestionario, un contador de palabras. Las condiciones son las mismas en todos los casos:

- Corre entero en el navegador, abriendo un `index.html` con doble clic. Sin servidor, sin
  instalar nada.
- Interfaz mínima. Retro está bien. Sin distracciones.
- Código chico y modular: la lógica separada de la interfaz, como `game.js` y `ui.js` en los
  ejemplos de la clase.
- Tests que corran con `node --test`.
- Un `README.md` en español.

Podés usar cualquier técnica de las que vimos en el curso: system prompts, Modelfiles, RAG,
un agente de código. Lo único que queda afuera es *reinforcement learning*, que es el tema de
la próxima clase.

## Qué tenés que hacer

### 1. Escribí la especificación

Media carilla, en prosa. Respondé, como mínimo:

- ¿Qué hace el programa? ¿Cómo se gana, se pierde o se termina?
- ¿Qué ve el usuario y qué puede tocar?
- ¿Qué archivos tiene que producir el agente?
- ¿Qué **no** tiene que hacer? Esta lista es tan importante como la anterior.
- ¿Cómo sabemos que funciona? ¿Qué tests tiene que pasar?

Usá como modelo los briefs que mostramos en clase (están en la
[presentación 7](https://dietrichson.github.io/IA-UNSAM-2026/preso-7-2026-09-14.html)).

### 2. Convertila en un prompt

El prompt es la especificación más las instrucciones de trabajo para el agente: dónde poner
los archivos, en qué idioma escribir los comentarios y el README, y la cláusula de cierre que
le exige correr los tests y mostrar la salida cruda antes de terminar.

### 3. Elegí tu camino

**Camino A: lo construís vos.** Si tenés acceso a un agente de código (Claude Code, Codex,
Cursor, Copilot, o cualquiera de los que vimos), ejecutá el prompt. Después:

1. Abrí el `index.html` y usalo. Anotá lo que no funciona.
2. Corré `node --test` y guardá la salida.
3. Si algo falló, escribí un segundo prompt corrigiéndolo. Guardá ese también.
4. Subí todo al repo en una subcarpeta dentro de tu carpeta, por ejemplo `Tu-Nombre/snake/`,
   y abrí un pull request como en el
   [laboratorio de GitHub](https://dietrichson.github.io/IA-UNSAM-2026/preso-2.html).

**Camino B: lo ejecutamos en clase.** Si no tenés acceso a un agente de código, o no te
alcanza el cupo gratuito, abrí un *issue* en el
[repositorio del curso](https://github.com/dietrichson/IA-UNSAM-2026/issues) con el título
`Pedido de software: <nombre del programa>` y con este contenido:

1. La especificación en prosa.
2. El prompt completo, listo para copiar y pegar.
3. Cómo vamos a verificar que quedó bien: qué tests tiene que pasar y qué tenemos que ver al
   abrirlo.

En la próxima clase vamos a ejecutar algunos de estos pedidos en vivo, con la misma técnica
que usamos con los videojuegos. Un pedido que el agente pueda ejecutar sin preguntarnos nada
es un pedido bien hecho.

### 4. Escribí una nota

Media carilla, en el README (camino A) o en el mismo issue (camino B):

- ¿Qué parte del pedido te costó más escribir? ¿Por qué?
- Si lo ejecutaste: ¿qué hizo el agente que no le pediste? ¿Qué le pediste que no hizo?
- ¿Qué cambiarías del prompt si lo tuvieras que mandar de nuevo?

## Para entregar

- **Camino A**: un pull request con la carpeta del programa. El README tiene que incluir los
  prompts textuales que mandaste, en orden, y la salida de `node --test`. Sin los prompts no
  se corrige: el pedido *es* el trabajo.
- **Camino B**: un issue con los tres puntos de arriba y la nota.

**Fecha límite: 21/09/2026.**

## Notas

- **El error más común es pedir demasiado.** Un Snake sin niveles, sin sonido y sin puntaje
  alto es un buen pedido. Un Snake con todo eso es tres pedidos.
- Los ejemplos completos de la clase están en
  [`sasha/tic-tac-toe/`](../sasha/tic-tac-toe/) y
  [`sasha/space-invaders/`](../sasha/space-invaders/). Copiá la estructura, no el código.
- Si tu programa expone una función `getState()` que devuelve el estado como un objeto,
  igual que los juegos de la clase, nos va a servir para la próxima.
- Si usás un modelo local con Ollama, aclaralo en la nota: los resultados van a ser distintos
  y eso también es un dato.
- Un issue no es un fracaso. Es la mitad del trabajo, hecha bien.
