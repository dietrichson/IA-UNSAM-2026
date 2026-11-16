Aprendizaje por refuerzo en R para el ta-te-ti

Un agente que aprende a jugar al ta-te-ti clásico (tablero 3x3) mediante Q-learning, un método de aprendizaje por refuerzo. El proyecto está desarrollado en R y utiliza el mismo motor del juego original (game.js), ejecutado dentro de R mediante el paquete V8.

El objetivo es entrenar un agente que mejore progresivamente sus decisiones a partir de la experiencia de juego y observar su rendimiento mediante estadísticas y una curva de aprendizaje.

Instalación

Para instalar las dependencias necesarias, ejecutar en R:

install.packages(c("V8", "ReinforcementLearning", "chromote", "ggplot2"))

chromote necesita Google Chrome instalado para ejecutar la demostración del agente en el navegador.

Los archivos del proyecto

Archivo

Función

train.R

Entrena al agente mediante Q-learning.

plot.R

Genera el gráfico de la curva de aprendizaje.

replay.R

Ejecuta una partida del agente entrenado en el navegador.

data/

Contiene los registros del entrenamiento y el modelo aprendido.

plots/

Guarda los gráficos y la captura de la demostración.

¿Cómo funciona el proyecto?

1. El entorno de juego

El proyecto utiliza el motor original del ta-te-ti, escrito en JavaScript. En lugar de crear nuevamente las reglas, se ejecuta ese mismo código dentro de R mediante la biblioteca V8.

De esta manera, el agente puede jugar numerosas partidas sin necesidad de abrir el navegador durante el entrenamiento.

2. Aprendizaje por refuerzo y Q-learning

El agente aprende mediante la experiencia. En cada partida observa el estado del tablero, selecciona una acción y recibe una recompensa según el resultado.

El sistema utiliza una tabla Q para registrar el valor estimado de las distintas acciones en cada estado del juego.

Las recompensas se definen desde la perspectiva del jugador X:

+1: cuando X gana.

-1: cuando gana O.

0: cuando la partida termina en empate o continúa sin resultado final.

El agente juega como X, mientras que su oponente realiza movimientos aleatorios.

3. Entrenamiento del agente

Para iniciar el entrenamiento se ejecuta:

Rscript train.R 3

El entrenamiento se organiza en iteraciones. En cada una, el agente juega partidas de práctica utilizando una política ε-greedy: combina movimientos exploratorios con decisiones basadas en lo aprendido.

Luego, se actualiza la tabla Q y se realizan 1.000 partidas de evaluación sin aprendizaje, utilizando la política greedy.

Los resultados de cada iteración se guardan en:

data/log-3x3.csv

4. Visualización del aprendizaje

Para generar el gráfico se ejecuta:

Rscript plot.R

El resultado se guarda en:

plots/learning-curve.png

La curva permite observar cómo evoluciona el rendimiento del agente a medida que aumenta la cantidad de partidas de entrenamiento.



5. Demostración en el navegador

Una vez entrenado el agente, se puede observar cómo juega en la página original mediante:

Rscript replay.R

El programa utiliza chromote para abrir Chrome, cargar el modelo entrenado y ejecutar una partida con la política greedy.

La captura del tablero final se guarda en:

plots/replay-3x3.png



Parámetros del entrenamiento

Parámetro

Valor

Descripción

Alpha (α)

0,2

Tasa de aprendizaje.

Gamma (γ)

0,9

Factor de descuento de recompensas futuras.

Epsilon (ε)

De 1,0 a 0,1

Controla la exploración de movimientos.

Partidas por iteración

500

Cantidad de partidas de entrenamiento por iteración.

Partidas de evaluación

1.000

Partidas utilizadas para medir el rendimiento.

Máximo de partidas

200.000

Límite de entrenamiento.

Tiempo máximo

45 minutos

Límite de duración del entrenamiento.

Resultados del entrenamiento

En la ejecución realizada se obtuvieron los siguientes resultados:

Indicador

Resultado

Iteraciones completadas

400

Partidas de entrenamiento

200.000

Estados registrados en la tabla Q

2.423

Tasa de victoria final

99,1 %

Tiempo total

1.411,19 segundos

Tiempo aproximado

23 minutos y 31 segundos

La tasa de victoria corresponde a la evaluación de la última iteración, realizada sobre 1.000 partidas contra un oponente aleatorio.

El agente alcanzó un rendimiento elevado y logró mantener una tasa de victoria cercana al 99 % al finalizar el entrenamiento.

Criterio de convergencia

Para analizar si el agente alcanzó un rendimiento estable, se utiliza una media móvil de la tasa de victoria de tres iteraciones consecutivas.

Se considera que el agente converge cuando esa media alcanza o supera el 90 %.

Este criterio permite observar la evolución del aprendizaje sin depender únicamente del resultado de una iteración aislada.

Notas y limitaciones

El agente juega como X, que es el jugador que comienza la partida.

El oponente realiza movimientos aleatorios.

La evaluación no modifica la tabla Q: solamente mide el rendimiento del agente.

La tasa de victoria obtenida corresponde a un oponente aleatorio y no significa que el agente sea invencible.

Los resultados pueden variar ligeramente entre ejecuciones debido al componente aleatorio del juego.

Conclusión

El proyecto permite observar cómo un agente puede aprender a tomar decisiones a partir de la experiencia, sin recibir instrucciones específicas para cada situación del tablero.

Mediante Q-learning, el sistema registra y actualiza el valor de sus acciones, mejorando progresivamente su desempeño.

Los resultados muestran que, para el ta-te-ti clásico de 3x3, el agente logra alcanzar una tasa de victoria del 99,1 % frente a un oponente aleatorio. La curva de aprendizaje y la demostración en el navegador permiten visualizar tanto el proceso de entrenamiento como el resultado obtenido.