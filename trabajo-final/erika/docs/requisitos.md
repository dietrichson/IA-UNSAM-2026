# Requisitos del proyecto

## 1. Objetivo

Desarrollar un agente de inteligencia artificial capaz de aprender a jugar al ta-te-ti clásico, utilizando un tablero de 3x3 y el método de aprendizaje por refuerzo Q-learning.

El agente debe mejorar sus decisiones a partir de la experiencia obtenida en partidas sucesivas, buscando ganar, evitar perder y reconocer situaciones que pueden terminar en empate.

## 2. Requisitos funcionales

- **RF1. Representación del juego:** utilizar un tablero de ta-te-ti de 3x3 y reconocer los movimientos legales.
- **RF2. Interacción con el juego:** utilizar la lógica del juego original, ubicada en `sasha/tic-tac-toe/`, sin modificar sus archivos.
- **RF3. Entrenamiento del agente:** permitir que el agente aprenda mediante partidas repetidas contra un oponente que realiza movimientos aleatorios.
- **RF4. Aprendizaje:** implementar Q-learning para que el agente actualice sus valores según las recompensas obtenidas durante las partidas.
- **RF5. Selección de movimientos:** utilizar una estrategia epsilon-greedy que combine exploración de movimientos y aprovechamiento de lo aprendido.
- **RF6. Evaluación:** evaluar el desempeño del agente utilizando una política greedy, sin modificar la tabla Q durante la evaluación.
- **RF7. Registro de resultados:** guardar los datos del entrenamiento y el modelo aprendido.
- **RF8. Visualización:** generar un gráfico que permita observar la evolución del aprendizaje.
- **RF9. Reproducción:** permitir visualizar una partida del agente entrenado en la página del juego y guardar una captura del resultado.

## 3. Requisitos no funcionales y técnicos

- El proyecto debe estar desarrollado en R.
- Se utilizan los paquetes `V8`, `ReinforcementLearning`, `ggplot2` y `chromote`.
- Se requiere Google Chrome para ejecutar la reproducción visual mediante `chromote`.
- Los scripts deben estar organizados dentro de la carpeta `src/`.
- Los datos del entrenamiento deben guardarse en `src/data/` y los gráficos y capturas en `src/plots/`.
- Los nombres de archivos y carpetas deben ser claros y mantener una organización consistente.
- El proyecto debe conservar los archivos originales del juego sin modificarlos.

## 4. Criterios de aceptación

Se considera que el proyecto cumple con sus requisitos cuando:

- El agente puede entrenarse para jugar al ta-te-ti 3x3.
- El entrenamiento registra los resultados obtenidos.
- La tabla Q aprendida queda guardada en un archivo.
- Se puede evaluar el desempeño del agente frente a un oponente aleatorio.
- Se genera un gráfico de la curva de aprendizaje.
- Se puede visualizar una partida del agente entrenado.
- Los resultados obtenidos pueden consultarse a través de los archivos y gráficos generados.

## 5. Alcance y limitaciones

El desarrollo se concentra en el ta-te-ti clásico de 3x3. El agente se entrena para jugar como X frente a un oponente que realiza movimientos aleatorios como O.

El desempeño obtenido corresponde a las condiciones de entrenamiento y evaluación utilizadas en este proyecto. Por lo tanto, los resultados no garantizan que el agente tenga el mismo rendimiento frente a cualquier tipo de oponente.