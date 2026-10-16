"""train_qlearning.py — Q-learning tabular contra el Space Invaders.

La tabla Q es un diccionario: estado -> valor de cada una de las 4 acciones. No
hay red neuronal ni nada que no se pueda imprimir en pantalla.

  python train_qlearning.py                          # la configuracion del plan
  python train_qlearning.py --state aim --alpha 0.02 --out qlearning-aim

Sobre --state: ver la seccion "Lo que no funciono" del README. Con los 4 rasgos
la tabla tiene 400 casilleros y el agente se queda en ~250 puntos; con solo
(columna, bala) tiene 10 y a veces llega a 576.
"""

import argparse
import csv
import json
import random
import time
from collections import defaultdict, deque

from env import SpaceInvadersEnv

GAMMA = 0.95       # cuanto pesa el futuro frente al premio inmediato
EPS_FINAL = 0.05   # exploracion que queda al final
COLUMNS = ["episode", "total_steps", "epsilon", "episode_reward", "score",
           "aliens_killed", "lives_left", "won", "wall_time_s"]


def table_key(obs, mode):
    """Que parte de la observacion entra en la tabla. 'full' = los 4 rasgos."""
    return obs if mode == "full" else (obs[1], obs[3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=3000)
    ap.add_argument("--alpha", type=float, default=0.1, help="cuanto se corrige el valor viejo")
    ap.add_argument("--state", choices=["full", "aim"], default="full")
    ap.add_argument("--seed", type=int, default=0, help="semilla de la exploracion")
    ap.add_argument("--out", default="qlearning", help="nombre de los archivos en data/")
    args = ap.parse_args()

    random.seed(args.seed)
    env = SpaceInvadersEnv(obs="compact")
    q = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    decay_until = max(1, int(0.8 * args.episodes))  # epsilon baja durante el 80% inicial
    recent = deque(maxlen=100)
    total_steps = 0
    t0 = time.time()

    with open(f"data/{args.out}-log.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        for episode in range(args.episodes):
            epsilon = max(EPS_FINAL, 1.0 - (1.0 - EPS_FINAL) * episode / decay_until)
            obs, info = env.reset(seed=episode)
            state = table_key(obs, args.state)
            episode_reward, done = 0.0, False
            while not done:
                if random.random() < epsilon:
                    action = random.randrange(4)
                else:
                    action = max(range(4), key=lambda a: q[state][a])
                obs, reward, terminated, truncated, info = env.step(action)
                nxt = table_key(obs, args.state)
                # Regla de Q-learning: acercar Q(s,a) al premio mas el mejor futuro.
                target = reward if terminated else reward + GAMMA * max(q[nxt])
                q[state][action] += args.alpha * (target - q[state][action])
                state = nxt
                episode_reward += reward
                total_steps += 1
                done = terminated or truncated
            recent.append(info["score"])
            writer.writerow([episode, total_steps, round(epsilon, 4), round(episode_reward, 1),
                             info["score"], info["aliens_killed"], info["lives"], info["won"],
                             round(time.time() - t0, 2)])
            f.flush()  # el CSV crece en vivo: se puede graficar mientras entrena
            if episode % 100 == 0:
                print(f"episodio {episode:5d}  epsilon {epsilon:.2f}  "
                      f"puntaje medio (100) {sum(recent) / len(recent):6.1f}  "
                      f"estados {len(q):4d}  {time.time() - t0:6.1f}s", flush=True)

    with open(f"data/{args.out}-q-table.json", "w") as f:
        json.dump({"state": args.state,
                   "q": {",".join(map(str, k)): v for k, v in q.items()}}, f)
    env.close()
    print(f"listo: {args.episodes} episodios, {total_steps} pasos, "
          f"{time.time() - t0:.1f}s, {len(q)} estados visitados")


if __name__ == "__main__":
    main()
