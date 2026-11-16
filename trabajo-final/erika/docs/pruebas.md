# Pruebas y resultados

## 1. Objetivo de las pruebas

Verificar el funcionamiento del agente de ta-te-ti 3x3, observar su aprendizaje y comprobar que los resultados del entrenamiento puedan visualizarse y guardarse correctamente.

## 2. Prueba de entrenamiento

Se realizó el entrenamiento del agente utilizando Q-learning durante 400 iteraciones, con un total de 200.000 partidas.

Los resultados obtenidos fueron:

- Iteraciones: 400.
- Partidas de entrenamiento: 200.000.
- Estados registrados en la tabla Q: 2.423.
- Tiempo de entrenamiento: aproximadamente 23,5 minutos.
- Tasa de victorias final: 99,1 % frente a un oponente aleatorio.

La convergencia se identificó en la iteración 6, luego de 3.000 partidas, considerando como criterio una media móvil de tres iteraciones con una tasa de victorias igual o superior al 90 %.

## 3. Prueba de generación del gráfico

Se ejecutó el script `plot.R` desde la carpeta del proyecto final.

El script procesó los datos registrados durante el entrenamiento y generó correctamente el gráfico de la curva de aprendizaje.

**Archivo generado:** `src/plots/learning-curve.png`.

## 4. Prueba de reproducción

El proyecto incluye el script `replay.R`, diseñado para cargar el modelo entrenado y reproducir una partida en la página original del ta-te-ti.

También se incluye una captura de la reproducción:

**Archivo:** `src/plots/replay-3x3.png`.

## 5. Archivos de resultados

Los principales archivos generados y utilizados son:

- `src/data/log-3x3.csv`: registro de los resultados del entrenamiento.
- `src/data/model-3x3.rds`: tabla Q correspondiente al modelo aprendido.
- `src/plots/learning-curve.png`: gráfico de evolución del aprendizaje.
- `src/plots/replay-3x3.png`: captura de la reproducción de una partida.

## 6. Resultado general

Las pruebas realizadas muestran que el agente pudo aprender a jugar al ta-te-ti 3x3 mediante aprendizaje por refuerzo y alcanzar un alto porcentaje de victorias frente a un oponente aleatorio.

Además, se comprobó la generación del gráfico de aprendizaje desde la carpeta oficial del proyecto. La reproducción visual está documentada mediante la captura incluida.

## 7. Conclusión

El desarrollo permitió observar cómo un agente puede mejorar su comportamiento a partir de la experiencia y la retroalimentación obtenida durante las partidas.

Los resultados muestran un desempeño satisfactorio dentro de las condiciones de entrenamiento y evaluación utilizadas. Como limitación, el agente fue evaluado frente a un oponente aleatorio, por lo que no se puede asegurar el mismo rendimiento frente a jugadores con estrategias diferentes.