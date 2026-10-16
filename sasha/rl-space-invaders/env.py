"""env.py — El juego Space Invaders como entorno de aprendizaje por refuerzo.

Habla con bridge/game_bridge.js (un proceso Node) y expone la interfaz de
Gymnasium: reset() / step() / action_space / observation_space. Dos modos de
observacion, elegidos en el constructor:

  obs="compact"  -> 4 numeros, para el Q-learning tabular (train_qlearning.py)
  obs="grid"     -> la grilla 15x20 aplanada, para la red neuronal (train_sb3.py)
"""

import json
import subprocess
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import spaces

BRIDGE = Path(__file__).resolve().parent / "bridge" / "game_bridge.js"
WIDTH, HEIGHT = 20, 15
PLAYER_ROW = HEIGHT - 1  # la nave siempre esta en la fila 14
TOTAL_ALIENS = 24        # 3 filas x 8 columnas
MAX_TICKS = 3000         # tope por episodio: game.js no tiene uno propio


def compact_features(state):
    """Resume el estado del juego en 4 numeros enteros.

    1. x de la nave (0..19)
    2. columna relativa del alien vivo mas cercano, en 5 baldes:
       0 = muy a la izquierda (dx <= -3), 1 = a la izquierda (-2 o -1),
       2 = alineado (dx == 0), 3 = a la derecha (1 o 2), 4 = muy a la derecha (dx >= 3)
    3. hay una bomba en la columna de la nave a 4 filas o menos (0/1)
    4. hay una bala nuestra en vuelo (0/1)
    """
    px = state["player"]["x"]
    alive = [a for a in state["aliens"] if a["alive"]]
    if alive:
        # "Mas cercano" = el que esta mas abajo (el que primero nos alcanza);
        # si hay varios en esa fila, el de la columna mas cercana. Mirar la fila
        # antes que la columna es lo que hace que apuntar sirva.
        bottom = max(a["y"] for a in alive)
        near = min((a for a in alive if a["y"] == bottom), key=lambda a: abs(a["x"] - px))
        dx = near["x"] - px
    else:
        dx = 0
    if dx <= -3:
        col = 0
    elif dx < 0:
        col = 1
    elif dx == 0:
        col = 2
    elif dx <= 2:
        col = 3
    else:
        col = 4
    bomb = int(any(b["x"] == px and 0 <= PLAYER_ROW - b["y"] <= 4 for b in state["bombs"]))
    bullet = int(state["bullet"] is not None)
    return (px, col, bomb, bullet)


class SpaceInvadersEnv(gym.Env):
    """Entorno Gymnasium que envuelve el juego real corriendo en Node."""

    def __init__(self, obs="compact"):
        self.obs_mode = obs
        self.action_space = spaces.Discrete(4)  # 0 nada, 1 izquierda, 2 derecha, 3 disparar
        if obs == "compact":
            self.observation_space = spaces.MultiDiscrete([WIDTH, 5, 2, 2])
        else:
            self.observation_space = spaces.Box(0, 4, shape=(HEIGHT * WIDTH,), dtype=np.float32)
        self.proc = subprocess.Popen(
            ["node", str(BRIDGE)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
        )
        self.episode = 0  # el episodio i usa la semilla i, asi las corridas se repiten
        self.ticks = 0

    def _talk(self, cmd):
        """Manda un comando al proceso Node y espera su respuesta."""
        self.proc.stdin.write(json.dumps(cmd) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("el puente Node se cerro inesperadamente")
        return json.loads(line)

    def _observation(self, state):
        if self.obs_mode == "grid":
            return np.array(state["grid"], dtype=np.float32).reshape(-1)
        return compact_features(state)

    def _info(self, state):
        alive = sum(1 for a in state["aliens"] if a["alive"])
        return {
            "score": state["score"],
            "lives": state["lives"],
            "aliens_killed": TOTAL_ALIENS - alive,
            "won": int(state["won"]),
        }

    def reset(self, seed=None, options=None):
        if seed is None:
            seed = self.episode
        self.episode += 1
        self.ticks = 0
        out = self._talk({"cmd": "reset", "seed": int(seed)})
        return self._observation(out["state"]), self._info(out["state"])

    def step(self, action):
        out = self._talk({"cmd": "step", "action": int(action)})
        state = out["state"]
        self.ticks += 1
        terminated = bool(out["done"])
        truncated = (not terminated) and self.ticks >= MAX_TICKS
        return (
            self._observation(state), float(out["reward"]),
            terminated, truncated, self._info(state),
        )

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            self.proc.wait(timeout=5)
