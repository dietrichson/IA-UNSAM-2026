# Propuesta: Ta-te-ti con comentarista deportivo

**Autora:** Lucia Ruiz Serman

**Seminario Experimental de Inteligencia Artificial (UNSAM)**

## ¿Qué vamos a construir?

Un ta-te-ti de 3x3 que se juega en el navegador, con un comentarista hecho con inteligencia artificial. Después de cada jugada, una LLM (un modelo de lenguaje) la narra como si fuera un relator deportivo de fútbol o de hockey, por ejemplo: "¡Toma el centro y se queda con la pelota!". El juego usa reglas comunes y un rival que juega al azar. La IA no juega: solo cuenta lo que pasó.

## ¿Para quién es y qué problema resuelve?

Es para cualquier persona que quiera jugar un juego conocido y simple de una forma más entretenida, y también para quienes quieran ver cómo se comporta una LLM en una tarea concreta.

El problema de fondo es que las LLM suenan muy convincentes, pero a veces **inventan o se equivocan** (dicen que ganó alguien que no ganó, mencionan una casilla que no se jugó). Este proyecto pone a prueba ese límite: además de hacer el comentarista, voy a comprobar qué tan fiel es el relato a lo que realmente pasó en la partida.

## ¿Qué parte de IA tiene?

Una **LLM con *system prompt***. El system prompt le indica que es un relator deportivo, qué estilo usar y que debe contar únicamente lo que ocurrió. En cada jugada, el programa le pasa a la LLM el estado real del tablero y la jugada hecha, y ella devuelve el relato. Las reglas del juego (quién gana, si hay empate) las resuelve el programa, no la IA, para que no haya errores en eso.

## ¿Qué de lo visto en el seminario ya sabemos usar y qué nos falta aprender?

**Ya sabemos:**
- Qué es una LLM y para qué sirve un *system prompt*.
- Cómo se organiza un juego para que otro programa lo use (reiniciar la partida, jugar un turno, consultar el estado), como se vio en el ejemplo del ta-te-ti de clase.
- Cómo trabajar con un asistente de IA para que escriba el código y explique cómo correrlo.

**Nos falta aprender:**
- Cómo correr una LLM (por ejemplo, un modelo chico con Ollama) y conectarla con el juego.
- Cómo escribir un buen *system prompt* para que el relato sea fiel y mantenga el estilo.
- Cómo evaluar las respuestas de una LLM de forma ordenada.

## ¿Cómo sería la versión mínima que funciona?

- Un ta-te-ti de 3x3 en una página web, contra un rival que juega al azar.
- Una llamada a la LLM después de cada jugada, con un solo estilo (relator de fútbol).
- Una prueba de 10 partidas (unas 50 jugadas narradas), revisando a mano cada relato y anotando si fue fiel a lo que pasó.
- Una tabla con los resultados: cuántos relatos fueron correctos y qué errores aparecieron.

**Si llegamos:** elegir entre fútbol y hockey, y comparar dos versiones del *system prompt* para ver cuál se equivoca menos.

## Limitaciones previstas

Mi computadora tiene recursos limitados, así que voy a usar un modelo chico y partidas cortas. El proyecto no entrena ningún modelo.
