"""plot_learning_curve.py — La curva de aprendizaje y los episodios hasta cada nivel.

Lee data/qlearning-log.csv (y data/sb3-log.csv si existe), dibuja el puntaje por
episodio con su media movil, y dice en que episodio la media movil cruzo cada
umbral de habilidad.

  python plot_learning_curve.py
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")  # sin ventana: guardamos el PNG y listo
import matplotlib.pyplot as plt
import numpy as np

WINDOW = 50  # episodios de la media movil
THRESHOLDS = [(250, "supera al azar"), (400, "competente"), (550, "casi optimo")]
RUNS = [
    ("data/qlearning-log.csv", "Q-learning, 4 rasgos"),
    ("data/qlearning-aim-log.csv", "Q-learning, 2 rasgos (columna, bala)"),
    ("data/sb3-log.csv", "PPO (SB3)"),
]


def load_scores(path):
    with open(path) as f:
        return [float(row["score"]) for row in csv.DictReader(f)]


def rolling_mean(scores, window=WINDOW):
    """Media movil simple; los primeros episodios promedian lo que hay."""
    return np.array([np.mean(scores[max(0, i - window + 1):i + 1]) for i in range(len(scores))])


def main():
    runs = [(path, label) for path, label in RUNS if os.path.exists(path)]
    fig, axes = plt.subplots(1, len(runs), figsize=(6 * len(runs), 5), sharey=True, squeeze=False)
    for ax, (path, label) in zip(axes[0], runs):
        scores = load_scores(path)
        mean = rolling_mean(scores)
        episodes = np.arange(len(scores))
        ax.plot(episodes, scores, color="tab:blue", alpha=0.15, linewidth=0.8, label="puntaje crudo")
        ax.plot(episodes, mean, color="tab:blue", linewidth=2, label=f"media movil ({WINDOW})")
        print(f"\n{label}  ({len(scores)} episodios, mejor media movil {mean.max():.1f})")
        for value, name in THRESHOLDS:
            ax.axhline(value, linestyle="--", color="gray", linewidth=1)
            ax.text(len(scores) * 0.99, value + 6, f"{name} ({value})", fontsize=8,
                    color="gray", ha="right")
            crossed = np.flatnonzero(mean >= value)
            first = int(crossed[0]) if crossed.size else None
            print(f"  {name:>16} (>= {value}): "
                  + (f"episodio {first}" if first is not None else "no alcanzado"))
        ax.set_title(label)
        ax.set_xlabel("episodio")
        ax.legend(loc="lower right", fontsize=8)
    axes[0][0].set_ylabel("puntaje")
    fig.suptitle("Space Invaders — curva de aprendizaje")
    fig.tight_layout()
    fig.savefig("plots/learning-curve.png", dpi=150)
    print("\nplots/learning-curve.png")


if __name__ == "__main__":
    main()
