# Requisitos: Ta-te-ti con comentarista deportivo

**Autora:** Lucia Ruiz Serman

**Seminario Experimental de Inteligencia Artificial (UNSAM)**

Cada requisito se puede comprobar con un sí o un no. Los resultados de esas comprobaciones van a estar en `docs/pruebas.md`.

## Requisitos imprescindibles (versión mínima)

**R1.** El juego se puede jugar en el navegador: hay un tablero de 3x3 donde la persona juega como X contra un rival que elige sus jugadas al azar.

**R2.** El juego no permite jugar en una casilla ocupada, y detecta correctamente las victorias (filas, columnas y diagonales) y los empates.

**R3.** Después de cada jugada, tanto de la persona como del rival, el programa le envía a la LLM el estado real del tablero y la jugada hecha, y muestra en pantalla el relato que devuelve.

**R4.** La LLM usa un *system prompt* que la define como relator de fútbol y le indica que cuente únicamente lo que ocurrió.

**R5.** Cada relato tiene una o dos oraciones.

**R6.** En al menos el 90% de las jugadas revisadas, el relato menciona correctamente quién jugó y en qué casilla.

**R7.** En al menos 9 de las 10 partidas de prueba, el relato anuncia correctamente el final (victoria o empate) y no lo anuncia antes de que ocurra.

**R8.** Se juegan 10 partidas completas y se revisa a mano cada relato, anotando en una tabla la jugada, el relato, si fue fiel (sí o no) y qué tipo de error tuvo, si lo hubo.

**R9.** El proyecto se puede correr en mi computadora con un modelo de lenguaje chico, siguiendo instrucciones escritas en el `README.md`.

## Requisitos "si llegamos"

**R10.** La persona puede elegir entre un relator de fútbol y uno de hockey, y el estilo del relato cambia según la elección.

**R11.** Se comparan dos versiones del *system prompt* jugando las mismas partidas, y se informa cuál tiene menos errores.

**R12.** Hay un botón para empezar una nueva partida sin recargar la página.

## Fuera de alcance

Estas cosas se decidió no hacerlas:

- Entrenar o ajustar un modelo de lenguaje. Solo se usa uno ya existente.
- Que la IA juegue al ta-te-ti. El rival es aleatorio y las reglas las resuelve el programa.
- Tableros más grandes que 3x3 o variantes de las reglas.
- Partidas entre dos personas o juego en línea.
- Narración con voz o con imágenes.
- Publicar el juego en internet.
- Evaluar el comentarista con otras personas (las pruebas las hago yo).
