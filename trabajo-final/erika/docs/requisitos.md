# Requisitos del proyecto: IA que aprende a jugar al ta-te-ti

## 1. Descripción general

El proyecto consiste en desarrollar una inteligencia artificial capaz de aprender a jugar al ta-te-ti mediante aprendizaje por refuerzo (Q-learning).

Para su desarrollo se utilizará como base el código proporcionado por el profesor, adaptándolo para entrenar un agente que aprenda a tomar decisiones a partir de los resultados de sus partidas.

El proyecto se limitará al tablero clásico de 3 × 3.

## 2. Objetivo general

Desarrollar y entrenar un agente de inteligencia artificial que mejore progresivamente su desempeño en el juego del ta-te-ti mediante la experiencia acumulada durante múltiples partidas.

## 3. Requisitos funcionales

El sistema deberá:

1. Utilizar un tablero de ta-te-ti de 3 × 3.
2. Permitir que el agente de inteligencia artificial juegue como X.
3. Utilizar un oponente que realice movimientos aleatorios como O.
4. Entrenar al agente mediante el algoritmo Q-learning.
5. Registrar los resultados de las partidas de evaluación, diferenciando victorias, derrotas y empates.
6. Generar estadísticas que permitan observar la evolución del aprendizaje.
7. Generar un gráfico que represente el desempeño del agente durante el entrenamiento.
8. Permitir visualizar una partida realizada por el agente una vez finalizado el entrenamiento.

## 4. Requisitos no funcionales

- **Claridad:** el código y la documentación deberán estar organizados para facilitar su comprensión.
- **Reproducibilidad:** el proceso de entrenamiento deberá poder ejecutarse nuevamente siguiendo las instrucciones del proyecto.
- **Registro:** los resultados del entrenamiento deberán almacenarse en archivos para su posterior análisis.
- **Visualización:** los resultados deberán presentarse mediante estadísticas y un gráfico de evolución.
- **Alcance:** el desarrollo se limitará al juego clásico de ta-te-ti, sin incorporar tableros de mayor tamaño ni funcionalidades adicionales.

## 5. Herramientas y tecnologías

Para el desarrollo se utilizarán:

- **R:** lenguaje de programación utilizado para el entrenamiento y análisis de resultados.
- **RStudio:** entorno de desarrollo para trabajar con el código en R, si resulta necesario.
- **V8:** paquete que permite ejecutar JavaScript desde R y reutilizar la lógica del juego original.
- **ReinforcementLearning:** paquete utilizado para implementar el aprendizaje por refuerzo.
- **ggplot2:** paquete utilizado para generar gráficos.
- **chromote:** paquete utilizado para visualizar la partida del agente en el navegador.
- **GitHub:** plataforma para organizar, documentar y entregar el proyecto.

## 6. Resultados esperados

Se espera obtener un agente capaz de mejorar su desempeño a medida que acumula experiencia jugando al ta-te-ti.

Además, se buscará analizar su evolución a través de los resultados de las partidas de evaluación, las estadísticas obtenidas y el gráfico de aprendizaje.

Finalmente, se realizará una demostración del agente entrenado jugando una partida.

## 7. Criterios de aceptación

Se considerará cumplida esta etapa cuando:

- Los requisitos funcionales y no funcionales estén definidos.
- El alcance del proyecto esté delimitado al tablero clásico de 3 × 3.
- Las herramientas necesarias para el desarrollo estén identificadas.
- Los resultados esperados estén establecidos.
- La documentación permita comprender qué se busca desarrollar y cómo se evaluará su funcionamiento.
