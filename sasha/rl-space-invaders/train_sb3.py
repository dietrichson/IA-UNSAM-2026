"""train_sb3.py — La misma tarea con la biblioteca estandar del area.

PPO (Stable-Baselines3) sobre la grilla completa 15x20, en vez de Q-learning
tabular sobre 4 rasgos. Mismo entorno, misma dificultad, y al final el mismo CSV
que train_qlearning.py para poder comparar las dos curvas en un solo grafico.

  python train_sb3.py
"""

import csv

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from env import SpaceInvadersEnv
from train_qlearning import COLUMNS

TOTAL_TIMESTEPS = 500_000
MONITOR_PATH = "data/sb3-monitor"


def monitor_to_csv():
    """Traduce el CSV del wrapper Monitor al mismo formato que el log tabular."""
    with open(MONITOR_PATH + ".monitor.csv") as f:
        next(f)  # la primera linea es un comentario JSON con metadatos
        rows = list(csv.DictReader(f))
    total_steps = 0
    with open("data/sb3-log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for episode, row in enumerate(rows):
            total_steps += int(row["l"])
            writer.writerow([episode, total_steps, "NA", row["r"], row["score"],
                             row["aliens_killed"], row["lives"], row["won"], row["t"]])
    print(f"data/sb3-log.csv: {len(rows)} episodios")


def main():
    env = Monitor(
        SpaceInvadersEnv(obs="grid"), MONITOR_PATH,
        info_keywords=("score", "aliens_killed", "lives", "won"),
    )
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    model.save("data/ppo-space-invaders")
    env.close()
    monitor_to_csv()


if __name__ == "__main__":
    main()
