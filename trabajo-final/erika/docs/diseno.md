# Diseño del proyecto

## 1. Arquitectura general

El proyecto se organiza en tres scripts principales desarrollados en R, que permiten entrenar al agente, analizar los resultados y visualizar una partida.

La lógica original del ta-te-ti se encuentra en la carpeta `sasha/tic-tac-toe/`. Se utiliza como base para ejecutar el juego sin modificar sus archivos originales.

## 2. Funcionamiento del agente

El agente utiliza el algoritmo **Q-learning**, perteneciente al aprendizaje por refuerzo.

Este método permite aprender a partir de la experiencia: durante las partidas, el agente observa el estado del tablero, selecciona un movimiento y recibe una recompensa según el resultado obtenido.

La información aprendida se almacena en una tabla Q, que relaciona los estados del juego con las acciones posibles.

## 3. Estados, acciones y recompensas

- **Estados:** representan las distintas configuraciones posibles del tablero 3x3.
- **Acciones:** corresponden a los movimientos legales que puede realizar el agente.
- **Recompensas:** se utilizan para orientar el aprendizaje. Desde la perspectiva de X, ganar otorga una recompensa positiva (+1), perder una negativa (-1) y empatar una recompensa neutra (0).

El agente juega como X, mientras que el oponente juega como O y selecciona sus movimientos de manera aleatoria.

## 4. Estrategia de aprendizaje

Para seleccionar sus movimientos se utiliza una estrategia epsilon-greedy.

Esta estrategia combina dos posibilidades:

- **Exploración:** probar movimientos diferentes para obtener nueva experiencia.
- **Explotación:** elegir movimientos que, según la tabla Q, ofrecen mejores resultados.

Durante el entrenamiento, el valor de epsilon disminuye progresivamente, reduciendo la exploración y favoreciendo el uso de lo aprendido.

Los valores de aprendizaje utilizados incluyen una tasa de aprendizaje (alpha) de 0.2 y un factor de descuento (gamma) de 0.9.

## 5. Etapas del procesamiento

### Entrenamiento: `train.R`

Ejecuta las partidas de entrenamiento, actualiza la tabla Q y registra los resultados obtenidos. Al finalizar, guarda el modelo aprendido y los datos del proceso en `src/data/`.

### Visualización de resultados: `plot.R`

Lee los datos registrados durante el entrenamiento y genera un gráfico de la curva de aprendizaje. La imagen se guarda en `src/plots/`.

### Reproducción: `replay.R`

Carga el modelo entrenado y permite visualizar una partida del agente en la página original del juego. Para esta etapa se utiliza `chromote`.

## 6. Organización de archivos

La estructura del proyecto separa la documentación, los scripts y los resultados:

- `docs/`: contiene la propuesta, los requisitos, el diseño y las pruebas.
- `src/`: contiene los scripts desarrollados en R.
- `src/data/`: almacena el registro del entrenamiento y el modelo aprendido.
- `src/plots/`: contiene los gráficos y las capturas generadas.

## 7. Flujo de trabajo

El funcionamiento general del proyecto sigue esta secuencia:

1. Se carga la lógica original del juego.
2. El agente comienza a jugar y explorar movimientos.
3. Se actualiza la tabla Q a partir de las recompensas.
4. Se guardan los datos y el modelo entrenado.
5. Se evalúa el desempeño del agente.
6. Se genera la curva de aprendizaje.
7. Se reproduce una partida para observar el comportamiento del agente.