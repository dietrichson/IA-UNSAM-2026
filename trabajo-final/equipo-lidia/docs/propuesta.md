# Propuesta: El Profe Histérico

**Equipo Lidia – Trabajo final**

## ¿Qué vamos a construir?

Vamos a desarrollar *El Profe Histérico*, un juego web de cultura general argentina en el que el jugador compite contra un profesor de historia con una personalidad exagerada y humorística. A través de preguntas, apuestas y comodines, el objetivo es sumar puntos, superar al profesor y aprender de una manera entretenida.

## ¿Para quién es y qué problema resuelve?

El juego está dirigido a estudiantes y a cualquier persona interesada en poner a prueba sus conocimientos sobre historia y cultura general argentina.

Buscamos ofrecer una alternativa a los cuestionarios tradicionales, combinando el aprendizaje con el entretenimiento y la competencia. La idea es que los jugadores puedan aprender de sus errores a través de explicaciones breves y de las reacciones humorísticas del profesor.

## ¿Qué parte de inteligencia artificial tiene?

La inteligencia artificial se utiliza principalmente para darle personalidad al profesor mediante un modelo de lenguaje (LLM).

A través de un *system prompt*, se define su comportamiento para que genere comentarios humorísticos y exagerados según las respuestas del jugador. De esta manera, el profesor puede reaccionar de distintas formas durante la partida, haciendo que la experiencia sea más dinámica.

Las respuestas del profesor a las preguntas se determinan mediante probabilidades de acierto, mientras que el LLM se encarga de generar sus comentarios.

## ¿Qué sabemos usar de lo visto en el seminario y qué nos falta aprender?

A partir de lo trabajado en el seminario, sabemos utilizar modelos de lenguaje (LLM) y elaborar prompts para orientar sus respuestas. También aprendimos a trabajar con Ollama para ejecutar modelos de inteligencia artificial y con sistemas RAG para recuperar información de distintas fuentes.

Estos conocimientos nos permiten comprender cómo incorporar herramientas de IA al juego y definir el comportamiento del profesor.

Lo que nos falta es seguir profundizando en la integración de estas herramientas dentro de una aplicación web, especialmente en la optimización de los tiempos de respuesta, el manejo de posibles errores y la protección de las claves de acceso. También buscamos mejorar los prompts para conseguir comentarios más variados y coherentes con la personalidad del personaje.

## ¿Cómo sería la versión mínima que funciona?

La versión mínima permitirá jugar una partida completa de 10 preguntas de cultura general argentina, seleccionadas aleatoriamente de un banco de preguntas.

El jugador podrá personalizar su personaje, elegir cuánto apostar antes de responder y utilizar comodines durante la partida. El profesor también responderá las preguntas y reaccionará a los resultados con comentarios generados mediante inteligencia artificial.

Al finalizar, se mostrará un boletín con los aciertos, los puntajes y la nota obtenida, junto con la posibilidad de comenzar una nueva partida.

El juego funcionará directamente desde un navegador web, sin necesidad de registrarse ni instalar ninguna aplicación.
