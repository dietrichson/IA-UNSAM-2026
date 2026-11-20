# Diseño del proyecto: IA que aprende a jugar al ta-te-ti

## 1. Introducción

El proyecto propone desarrollar un agente de inteligencia artificial capaz de aprender a jugar al ta-te-ti mediante aprendizaje por refuerzo, utilizando el algoritmo Q-learning.

Para su implementación se tomará como base el código proporcionado por el profesor, reutilizando la lógica del juego original y adaptándola al proceso de entrenamiento del agente.

El desarrollo se limitará al tablero clásico de 3 × 3.

## 2. Arquitectura general del sistema

El sistema estará organizado en cuatro componentes principales:

- **Juego:** se utilizará el juego de ta-te-ti existente, desarrollado en JavaScript. Su lógica será ejecutada desde R mediante el paquete V8.
- **Entrenamiento:** el agente aprenderá a elegir sus movimientos mediante Q-learning, jugando como X contra un oponente que realiza movimientos aleatorios como O.
- **Evaluación y registro:** después de cada etapa de entrenamiento, el agente será evaluado mediante partidas en las que utilizará la política aprendida. Se registrarán las victorias, derrotas, empates y otros datos del proceso.
- **Visualización:** se generará un gráfico para representar la evolución del aprendizaje y se utilizará el navegador para mostrar una partida del agente entrenado.

## 3. Funcionamiento del aprendizaje

El entrenamiento se realizará mediante la repetición de múltiples partidas.

En cada partida:

1. El agente observa el estado actual del tablero.
2. Selecciona una casilla disponible para colocar una X.
3. El oponente realiza un movimiento aleatorio y coloca una O.
4. Se observa el nuevo estado del tablero y se determina si hubo una victoria, derrota o empate.
5. El agente recibe una recompensa según el resultado y utiliza esa experiencia para actualizar sus decisiones.

Este proceso se repite durante el entrenamiento, permitiendo que el agente mejore progresivamente la elección de sus movimientos.

## 4. Organización de los archivos

El proyecto se organizará de la siguiente manera:

- `train.R`: ejecuta el entrenamiento del agente y guarda los resultados.
- `plot.R`: procesa los registros del entrenamiento y genera el gráfico de evolución.
- `replay.R`: permite visualizar una partida del agente entrenado en el navegador.
- `data/`: almacena los registros de entrenamiento y el modelo aprendido.
- `plots/`: almacena los gráficos y las capturas de la demostración.

También se reutilizará el archivo `game.js` del juego original proporcionado por el profesor.

## 5. Herramientas y tecnologías

Para desarrollar el proyecto se utilizarán las siguientes herramientas:

- **R:** lenguaje utilizado para el entrenamiento y procesamiento de resultados.
- **V8:** permite ejecutar el código JavaScript del juego desde R.
- **ReinforcementLearning:** se utiliza para implementar el aprendizaje por refuerzo.
- **ggplot2:** permite generar gráficos a partir de los resultados.
- **chromote:** permite interactuar con el navegador para visualizar la partida del agente.
- **GitHub:** permite organizar y documentar el desarrollo del proyecto.

## 6. Evaluación del agente

Para evaluar el desempeño del agente se realizarán partidas de prueba utilizando los movimientos aprendidos, sin actualizar el modelo durante esas partidas.

Se registrarán los siguientes indicadores:

- Cantidad de victorias.
- Cantidad de derrotas.
- Cantidad de empates.
- Porcentaje de victorias.
- Evolución del desempeño a lo largo del entrenamiento.

Estos datos permitirán observar si el agente mejora sus decisiones a medida que acumula experiencia.

## 7. Resultados esperados

Se espera obtener un agente capaz de mejorar su desempeño mediante la práctica y el aprendizaje a partir de los resultados de sus partidas.

Como resultado final, se buscará contar con:

- Un modelo entrenado mediante Q-learning.
- Registros de las partidas de evaluación.
- Estadísticas sobre el desempeño del agente.
- Un gráfico que muestre la evolución del aprendizaje.
- Una demostración del agente jugando al ta-te-ti.

## 8. Alcance del diseño

El diseño contempla únicamente el tablero clásico de 3 × 3 y el entrenamiento del agente como jugador X frente a un oponente aleatorio.

No se incorporarán tableros de mayor tamaño ni funcionalidades adicionales que excedan los objetivos establecidos para el proyecto.
