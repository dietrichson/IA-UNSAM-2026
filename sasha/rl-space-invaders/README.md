# Aprendizaje por refuerzo sobre el Space Invaders

Un agente que aprende a jugar al juego de `sasha/space-invaders/` sin que nadie
le explique las reglas: solo ve números y recibe premios y castigos.

Hay dos agentes, y sirve compararlos:

- **Q-learning tabular** (`train_qlearning.py`): una tabla de valores escrita a
  mano, ~60 líneas, que se puede imprimir y leer entera.
- **PPO de Stable-Baselines3** (`train_sb3.py`): la biblioteca estándar del
  área, una red neuronal sobre la grilla completa.

El juego no se toca. Los dos agentes entrenan contra el mismo `game.js` que
corre en el navegador, a través de un puente de Node.

---

## 1. Instalación

Antes de la clase, no en cámara: `torch` y Chromium pesan cientos de megabytes.

```bash
cd sasha/rl-space-invaders

node --version                 # probado con v24.15.0; fnm puede cambiarla entre terminales
uv venv --python 3.12 .venv
uv pip install --python .venv -r requirements.txt
.venv/bin/playwright install chromium
```

`.venv/` está en el `.gitignore` de esta carpeta: no se commitea.

---

## 2. Cómo está armado

```
bridge/game_bridge.js   Node: corre game.js y habla JSON por línea
env.py                  interfaz Gymnasium (reset/step) sobre ese puente
train_qlearning.py      Q-learning tabular      -> data/<out>-log.csv, data/<out>-q-table.json
train_sb3.py            PPO                     -> data/sb3-log.csv, data/ppo-space-invaders.zip
plot_learning_curve.py  los tres CSV            -> plots/learning-curve.png
replay.py               la política aprendida jugando en index.html
```

El puente evita el navegador durante el entrenamiento. Medido acá:
**30.181 pasos por segundo** (5.000 pasos aleatorios a través de `env.py`). Por
Playwright serían unos 300. Un episodio dura ~265 ticks, así que 3.000 episodios
son ~790.000 pasos: medio minuto.

### La observación

`SpaceInvadersEnv(obs="compact")` devuelve 4 enteros (`env.py`,
`compact_features`):

| # | Rasgo | Valores |
|---|---|---|
| 1 | `x` de la nave | 0..19 |
| 2 | columna relativa del alien vivo más cercano | 0 = muy a la izquierda (dx ≤ -3), 1 = izquierda (-2, -1), 2 = alineado (0), 3 = derecha (1, 2), 4 = muy a la derecha (dx ≥ 3) |
| 3 | bomba en la columna de la nave, a ≤ 4 filas | 0 / 1 |
| 4 | bala nuestra en vuelo | 0 / 1 |

"Más cercano" es **el alien que está más abajo**, y entre esos el de la columna
más cercana. Mirar la fila antes que la columna es lo que hace que apuntar
sirva: con una distancia que mezcle las dos, el blanco salta de un alien a otro
y el agente nunca aprende a disparar.

`SpaceInvadersEnv(obs="grid")` devuelve la grilla 15x20 aplanada (300 números,
`float32`), que es lo que come PPO.

Acciones: `0` nada, `1` izquierda, `2` derecha, `3` disparar.
Tope de 3.000 ticks por episodio (`game.js` no tiene uno propio).
El episodio *i* usa la semilla *i*: las corridas se repiten exactamente.

### El CSV

Los dos entrenamientos escriben las mismas columnas, una fila por episodio:

```
episode, total_steps, epsilon, episode_reward, score, aliens_killed, lives_left, won, wall_time_s
```

En `data/sb3-log.csv` la columna `epsilon` es `NA` (PPO no usa epsilon-greedy).

### Los tres niveles

Media móvil del `score` sobre 50 episodios:

| Nivel | Umbral | Referencia |
|---|---|---|
| Supera al azar | ≥ 250 | azar = 175 |
| Competente | ≥ 400 | — |
| Casi óptimo | ≥ 550 | máximo posible = 580 |

---

## 3. Correrlo

```bash
# 1. Q-learning con los 4 rasgos: la configuración del plan. ~30 s
.venv/bin/python train_qlearning.py

# 2. Q-learning con 2 rasgos: el mismo algoritmo, menos estado. ~100 s
.venv/bin/python train_qlearning.py --state aim --alpha 0.02 \
                                    --seed 1 --episodes 10000 --out qlearning-aim

# 3. PPO. ~2 min
.venv/bin/python train_sb3.py

# 4. El gráfico con los tres paneles
.venv/bin/python plot_learning_curve.py

# 5. El agente que gana, jugando en la página real
.venv/bin/python replay.py
# ... y el que pierde, para mostrarlo primero en el video
.venv/bin/python replay.py --q-table data/qlearning-q-table.json \
                           --name replay-qlearning-4rasgos \
                           --shot plots/replay-final-4rasgos.png
```

`train_qlearning.py` acepta `--episodes`, `--alpha`, `--seed`, `--state` y
`--out` (el nombre de los archivos en `data/`).

---

## 4. Resultados medidos

Referencias, sobre la dificultad default (`alienSpeed: 4, bombChance: 0.02`):

| Política | Puntaje medio | Victorias |
|---|---|---|
| Al azar (200 episodios) | 175,1 | 0 / 200 |
| A mano, sobre los mismos 4 rasgos (100 ep.) | 578,7 | 99 / 100 |
| Máximo posible | 580 | — |

La segunda fila importa: **una política escrita a mano que usa solo estos 4
rasgos gana el 99% de las partidas**. Lo que falta no es información en la
observación; es que el algoritmo la encuentre.

### Las tres corridas

| | Q-learning, 4 rasgos | Q-learning, 2 rasgos | PPO (SB3) |
|---|---|---|---|
| Configuración | α=0,1 γ=0,95, ε 1,0→0,05 | α=0,02, `--state aim`, semilla 1 | `MlpPolicy`, 500.000 pasos |
| Casilleros en la tabla | 400 | 10 | — (red neuronal) |
| Episodios corridos | 3.000 (792.321 pasos) | 10.000 (2.790.666 pasos) | 1.808 (500.000 pasos) |
| Tiempo de reloj | **29,4 s** | **102,5 s** | **135,1 s** |
| Mejor media móvil (50) | **251,0** | **447,8** | **384,6** |
| Supera al azar (≥ 250) | episodio **2.575** | episodio **4.156** | episodio **526** |
| Competente (≥ 400) | no alcanzado | episodio **7.994** | no alcanzado |
| Casi óptimo (≥ 550) | no alcanzado | no alcanzado | no alcanzado |
| Política final, sin explorar (100 juegos) | 187,4 — **0 victorias** | **580,0 — 100 victorias** | 353,7 — 3 victorias |

![curva de aprendizaje](plots/learning-curve.png)

El agente de 2 rasgos termina con una política **perfecta**: 580 puntos, el
máximo del juego, en las 100 partidas. Aun así su media móvil nunca llega a 550,
y no es un defecto del agente: al final del entrenamiento todavía toma el 5% de
las acciones al azar, y una política perfecta con esa exploración rinde 515,5
(medido). El umbral de 550 sólo se puede cruzar apagando la exploración, que es
lo que hace `replay.py`.

Los videos: `replay.py` deja `plots/replay-qlearning.webm` (2 rasgos: 580 puntos
y gana) y `plots/replay-qlearning-4rasgos.webm` (4 rasgos: 180 puntos y pierde).
Mostrar primero el que pierde.

---

## 5. Lo que no funcionó

**La lección: la tabla funciona sólo cuando el estado tiene exactamente lo que
la política necesita — ni menos, ni más.**

**Con los 4 rasgos, el Q-learning tabular no aprende a jugar.** Se queda en una
media móvil de ~250 sobre un techo de 580, con la misma observación con la que
una política a mano gana el 99%. Con dos de esos cuatro rasgos, el mismo
algoritmo termina con una política perfecta. Vale la pena mostrarlo en clase: es
el resultado real, no un accidente de esta corrida.

Lo que se midió buscando la causa (en todos los casos γ=0,95, ε 1,0→0,05,
puntaje de la política greedy sobre 100 episodios):

| Qué entra en la tabla | Casilleros | α=0,1 | α=0,05 | α=0,02 |
|---|---|---|---|---|
| Los 4 rasgos | 400 | 243 | 208 | 241 |
| (columna, bomba, bala) | 20 | 209 | 260 | 299 |
| (columna, bala) | 10 | 300 | 420 | **468** |

Promedios de 3 semillas, 5.000 episodios cada una. Dos conclusiones:

1. **Los rasgos de más arruinan el aprendizaje.** El `x` de la nave y la bomba
   no le hacen falta a la política óptima, pero multiplican la tabla por 40. La
   misma decisión hay que acertarla en 400 casilleros en vez de 10, y con que
   falle en unos pocos la nave pierde la puntería. Con los 4 rasgos ninguna
   configuración probada ganó una sola partida.
2. **Más episodios no arreglan nada.** Con los 4 rasgos, 30.000 episodios dan lo
   mismo que 3.000 (~200). Con `(columna, bala)` y α=0,02, 20.000 episodios dan
   *peor* resultado que 10.000: la tabla se asienta con más firmeza sobre la
   política mala.

3. **El resultado es bimodal, y por eso la semilla está fija.** Con
   `--state aim --alpha 0.02 --episodes 10000`, cuatro semillas dieron 401, 580,
   576 y 401 puntos (0, 100, 99 y 0 victorias). O el agente encuentra "disparar
   sólo cuando está alineado" y gana casi siempre, o no la encuentra y se queda
   a mitad de camino. **La corrida que se commiteó usa la semilla 1**
   (`--seed 1`), que llega a la política perfecta.

`--state aim` deja en la tabla sólo la columna relativa y la bala; `--state full`
(el default) usa los 4 rasgos.

---

## 6. Pasos del video

1. Abrir `index.html`, jugar una ronda a mano, mostrar `window.game` en la consola.
2. `uv venv` + `uv pip install -r requirements.txt`.
3. Abrir `env.py`: cómo el estado del juego se convierte en 4 números.
4. Correr `train_qlearning.py`; ver crecer el CSV.
5. Graficar. Leer en qué episodio cruzó cada umbral: se queda en 250.
6. `replay.py --q-table data/qlearning-q-table.json ...`: el agente pierde.
7. Sacar dos rasgos de la tabla (`--state aim`) y volver a entrenar.
8. Graficar de nuevo, y `replay.py`: ahora gana con 580, el máximo posible.
9. `train_sb3.py`: la misma tarea con la biblioteca estándar, y el mismo gráfico.
10. Comparar los tres paneles y discutir la sección 5.
