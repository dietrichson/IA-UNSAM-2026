# Aprendizaje por refuerzo en R para el ta-te-ti

Un agente que aprende a jugar al ta-te-ti de [`sasha/tic-tac-toe/`](../tic-tac-toe)
con **Q-learning**, escrito en R. El juego no se reescribe: corre el mismo
`game.js` del navegador, pero adentro de R, con el paquete `V8`. Al final, el
agente ya entrenado juega en la página de verdad, con `chromote`.

Lo que se ve en la clase es la **curva de aprendizaje**: cuántas partidas hacen
falta para que el agente gane, y qué pasa cuando el tablero crece.

## Instalación

```r
install.packages(c("V8", "ReinforcementLearning", "chromote", "ggplot2"))
```

Probado con R 4.5.3, `V8` 8.2.0, `ReinforcementLearning` 1.0.5, `chromote` 0.5.1,
`ggplot2` 4.0.3. `chromote` necesita Google Chrome instalado (sólo para
`replay.R`). `hash` viene como dependencia de `ReinforcementLearning`.

## Los archivos

| Archivo | Qué hace |
|---|---|
| `train.R` | Entrena. Escribe `data/log-<tamaño>.csv` y `data/model-<tamaño>.rds`. |
| `plot.R` | Lee todos los CSV y dibuja `plots/learning-curve.png`. |
| `replay.R` | Abre Chrome y hace jugar al agente entrenado en `index.html`. |
| `data/` | Los CSV, los modelos y la salida de consola de cada corrida. |
| `plots/` | El gráfico y la captura del navegador. |

## Los pasos, en el orden del video

### 1. Mirar el juego en el navegador

Abrir `../tic-tac-toe/index.html` y, en la consola, probar `window.game`:

```js
game.reset({ size: 3, opponent: 'random' });
game.step(4);   // X juega el centro y O contesta al azar
```

### 2. El mismo juego, pero en R

```r
library(V8)
ct <- v8()
ct$source("../tic-tac-toe/game.js")
ct$call("TicTacToe.createState", list(size = 3))
```

Mismas reglas, sin navegador y unas cien veces más rápido. Entrenar necesita
cientos de miles de jugadas: en V8 son minutos, en Chrome serían horas.

### 3. Cómo una partida se vuelve tuplas

`train.R` define arriba de `game.js` un objeto `env` con dos funciones,
`env.reset()` y `env.step()`. `env.step()` juega la celda que pide el agente
con X y, si la partida sigue, hace que O conteste al azar. Así el agente sólo
ve turnos de X.

De cada jugada sale una fila `(State, Action, Reward, NextState)`, que es lo
que pide `ReinforcementLearning()`:

- **State**: el tablero aplanado como texto, fila por fila, con `.`, `X` y `O`.
  El tablero inicial de 3x3 es `.........`; después de `X` en el centro y `O`
  arriba a la izquierda, `O...X....`.
- **Action**: el número de celda, como texto (`"0"` … `"8"`).
- **Reward**: la recompensa desde el lado de X **después** de la respuesta de O:
  `+1` si X ganó, `-1` si ganó O, `0` en cualquier otro caso.
- **NextState**: el tablero después de la respuesta de O, o el tablero final.

Una partida de 3x3 da entre 3 y 5 filas. Un lote de 500 partidas da unas 2.100.

### 4. Entrenar el 3x3

```bash
Rscript train.R 3
```

Cada **iteración** es: jugar K partidas con política ε-greedy, pasarle esas
tuplas a `ReinforcementLearning()` para que actualice la misma tabla Q, y
después jugar 1.000 partidas de evaluación con política *greedy* y sin
aprender. Se agrega una fila al CSV al terminar cada iteración, así que el
archivo crece mientras el entrenamiento corre:

```bash
tail -f data/log-3x3.csv
```

### 5. Graficar

```bash
Rscript plot.R
```

Deja `plots/learning-curve.png` e imprime la tabla de resumen: en qué iteración
convergió cada corrida, o qué tope la cortó.

### 6. Repetir con tableros más grandes

```bash
Rscript train.R 4      # 4x4, hay que alinear 4
Rscript train.R 5      # 5x5, hay que alinear 5
Rscript train.R 5 4    # 5x5, pero alcanza con alinear 4
```

Mismo código, sólo cambia el tamaño. Volver a correr `plot.R` y comparar las
curvas: ahí está la clase.

### 7. El agente juega en la página real

```bash
Rscript replay.R
```

`chromote` abre Chrome con `index.html`, carga `data/model-3x3.rds` y juega la
política greedy jugada por jugada, con una pausa para que se vea. Guarda una
captura del tablero final en `plots/replay-3x3.png`.

## Los parámetros

| Parámetro | Valor | Dónde |
|---|---|---|
| `alpha` (tasa de aprendizaje) | 0,2 | `CONTROL` en `train.R` |
| `gamma` (descuento) | 0,9 | `CONTROL` en `train.R` |
| `epsilon` | baja de 1,0 a 0,1 | `epsilon_at()` en `train.R` |
| K (partidas por iteración) | 500 en 3x3, 2.000 en 4x4 y 5x5 | `K` en `train.R` |
| Partidas de evaluación | 1.000 por iteración | `EVAL_GAMES` |
| Tope de partidas | 200.000 | `MAX_EPISODES` |
| Tope de tiempo | 45 minutos | `MAX_SECONDS` |

**El esquema de epsilon**: baja en línea recta de 1,0 a 0,1 a lo largo de
`MAX_ITER = 200.000 / K` iteraciones (400 para el 3x3, 100 para los demás), y
se queda en 0,1 de ahí en adelante:

```
epsilon(i) = max(0,1 ;  1,0 - 0,9 * (i - 1) / (MAX_ITER - 1))
```

Que epsilon quede alto durante casi toda la corrida no arruina el aprendizaje:
Q-learning es *off-policy*, así que aprende la política óptima aunque explore
mucho, y la evaluación siempre es greedy. En los tableros grandes la corrida se
corta por tiempo mucho antes de que epsilon llegue a 0,1, y eso también se ve
en el CSV.

**Los topes**: una corrida termina cuando llega a 200.000 partidas de
entrenamiento o cuando se acaban los 45 minutos, lo que pase primero. El tiempo
se mira antes de empezar cada iteración: si la iteración que viene no entra en
el presupuesto (usando lo que tardó la anterior como estimación), se corta ahí.

## El CSV

Una fila por iteración, en `data/log-<tamaño>.csv`:

| Columna | Qué es |
|---|---|
| `iteration` | Número de iteración, desde 1. |
| `episodes_cumulative` | Partidas de **entrenamiento** acumuladas (no cuenta las de evaluación). |
| `epsilon` | El epsilon que se usó para explorar en esa iteración. |
| `wins` / `draws` / `losses` | Resultados de las 1.000 partidas de evaluación, desde el lado de X. |
| `win_rate` | `wins / 1000`. |
| `mean_reward` | Recompensa promedio de la evaluación (`(wins - losses) / 1000`). |
| `q_table_size` | Cuántos estados distintos tiene la tabla Q. |
| `wall_time_s` | Segundos desde que arrancó la corrida. |

## El criterio de convergencia

> Convergió en la primera iteración en la que la **media móvil de `win_rate`
> sobre 3 iteraciones** llega a 0,90 o más.

La media móvil es para no declarar victoria por una iteración con suerte: 1.000
partidas contra un oponente al azar tienen un ruido de ±1,5 puntos. `plot.R`
calcula eso y reporta la iteración y las partidas acumuladas en ese punto.

## Resultados

Cuatro corridas en un Mac con 48 GB de RAM y R 4.5.3, una detrás de la otra.

| Corrida | Iteraciones | Partidas | Tiempo | Estados en Q | `win_rate` final | Tope que cortó | ¿Convergió? |
|---|---:|---:|---:|---:|---:|---|---|
| 3x3 | 400 | 200.000 | 5,8 min | 2.423 | **0,997** | partidas | **sí: iteración 10, 5.000 partidas** |
| 4x4 | 100 | 200.000 | 40,7 min | 544.921 | 0,812 | partidas | no |
| 5x5 (`winLength` 5) | 51 | 102.000 | 44,5 min | 982.721 | 0,426 | tiempo | no |
| 5x5 (`winLength` 4) | 68 | 136.000 | 45,0 min | 937.245 | 0,862 | tiempo | no |

Lo que se ve en `plots/learning-curve.png` (el eje x está en escala
logarítmica, si no las tres corridas grandes quedan aplastadas contra el
margen):

- **3x3 converge enseguida.** A las 5.000 partidas ya pasa 0,90, y de ahí en
  adelante se queda arriba de 0,98. La tabla Q se estanca en 2.423 estados: de
  los 5.478 estados posibles del 3x3, esos son los que se alcanzan jugando
  contra un oponente aleatorio. La tabla **alcanza**, y se nota.
- **4x4 aprende pero no termina.** Sube de 0,37 a 0,81 en 200.000 partidas y
  todavía venía subiendo cuando se acabó el presupuesto. La tabla Q llegó a
  544.921 estados y sigue creciendo ~1.000 por iteración: cada partida nueva
  sigue trayendo posiciones que nunca vio.
- **5x5 con `winLength` 5 es el caso perdido.** 0,43 después de 102.000
  partidas, con casi un millón de estados en la tabla y creciendo ~18.000 por
  iteración. Ahí no hay tabla que alcance: el agente está, en la práctica,
  jugando casi siempre en posiciones nuevas. Fijarse en la columna `draws`: el
  5x5 empata mucho (425 de 1.000 en la última iteración), porque alinear 5 en
  un tablero de 25 casillas es difícil para los dos.
- **5x5 con `winLength` 4 es el contraejemplo útil.** Mismo tablero, misma
  cantidad de estados, pero como las partidas terminan antes y ganar es más
  fácil, la curva sube hasta 0,86 y casi llega al umbral. No cambió el tamaño
  del problema: cambió cuánto tarda en llegar la recompensa.

La moraleja de la clase: el 3x3 se resuelve con una tabla; el 4x4 ya está en el
límite; el 5x5 no. Para eso hacen falta métodos que **generalicen** entre
estados parecidos en vez de guardar uno por uno.

### Velocidad

Medido en la primera iteración del 3x3: **2.179 partidas por segundo** jugando
contra `game.js` en V8, y **13.176 filas por segundo** en el ajuste (después
sube a ~2.600 y ~16.500, cuando R ya calentó). Jugar no es nunca el problema.
El cuello de botella es `ReinforcementLearning()`, y empeora a medida que crece
la tabla:

| Corrida | Estados en Q | Jugar 2.000 partidas | Ajustar el lote |
|---|---:|---:|---:|
| 4x4 (iteración 1) | 10.897 | 1,4 s | 3,8 s |
| 4x4 (iteración 100) | 544.921 | 3,4 s | 36,4 s |
| 5x5 (iteración 51) | 982.721 | 5,2 s | 72,8 s |

El ajuste tarda más o menos en proporción a cuántos estados tiene ya la tabla,
porque el paquete rearma la matriz Q completa en cada llamada. Con 900.000
estados el proceso de R usa unos 15 GB. Es un límite del paquete, no del
método; acá se deja así a propósito, porque es parte de lo que muestra el
ejemplo.

## Notas y límites

- **Lo que se guarda en `model-<tamaño>.rds` es la tabla Q**, una matriz con los
  estados en las filas y las celdas del tablero en las columnas. No se guarda el
  objeto entero que devuelve `ReinforcementLearning()`: ese objeto guarda Q
  *además* como un hash de hashes, y serializar medio millón de entornos de R
  tarda más de media hora y deja archivos de varios GB. La misma tabla, como
  matriz, ocupa 3 MB y se guarda en segundos.
- **El azar de JavaScript no se puede fijar.** `game.js` usa `Math.random()`, así
  que dos corridas del mismo comando no dan números idénticos. `set.seed(42)`
  fija el lado de R (la exploración ε-greedy), no el oponente aleatorio. Las
  curvas se parecen, los números exactos no se repiten.
- **Estados nuevos se juegan al azar.** Si el agente llega a una posición que no
  está en la tabla Q, elige una celda libre al azar. En el 3x3 casi no pasa; en
  el 5x5 pasa casi siempre, y por eso la curva se parece tanto a la de un
  jugador aleatorio.
- **Sólo se juega como X**, que es quien empieza. El oponente es siempre el
  aleatorio del juego: ganarle a un oponente al azar no es lo mismo que jugar
  bien.
- **La evaluación no aprende y no cuenta** para `episodes_cumulative`: las 1.000
  partidas de evaluación por iteración son aparte de las K de entrenamiento.
- Los archivos `data/train-<tamaño>.out` son la salida de consola de cada
  corrida, con el detalle por iteración (tiempo de juego, tiempo de ajuste,
  partidas por segundo).
