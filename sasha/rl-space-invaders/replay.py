"""replay.py — El agente entrenado juega en la pagina real.

Abre index.html en un Chromium sin ventana con Playwright, lee data/q-table.json
y en cada tick elige la mejor accion segun la tabla. Deja el video y una captura
final en plots/.

  python replay.py                                            # el agente de 2 rasgos, que gana
  python replay.py --q-table data/qlearning-q-table.json \\
                   --name replay-qlearning-4rasgos \\
                   --shot plots/replay-final-4rasgos.png      # el de 4 rasgos, que pierde
"""

import argparse
import json
import shutil
from pathlib import Path

from playwright.sync_api import sync_playwright

from env import compact_features
from train_qlearning import table_key

ROOT = Path(__file__).resolve().parent
PAGE = (ROOT.parent / "space-invaders" / "index.html").as_uri()
SEED = 1
MAX_TICKS = 3000


def load_q_table(path):
    """Devuelve la tabla y el modo de estado con el que se entreno."""
    with open(ROOT / path) as f:
        raw = json.load(f)
    q = {tuple(int(n) for n in key.split(",")): v for key, v in raw["q"].items()}
    return q, raw["state"]


def greedy(q, mode, state):
    """Mejor accion aprendida; si el estado nunca se vio, no hacer nada."""
    values = q.get(table_key(compact_features(state), mode))
    return max(range(4), key=lambda a: values[a]) if values else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q-table", default="data/qlearning-aim-q-table.json")
    ap.add_argument("--name", default="replay-qlearning", help="nombre del video en plots/")
    ap.add_argument("--shot", default="plots/replay-final.png")
    args = ap.parse_args()

    q, mode = load_q_table(args.q_table)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(record_video_dir=str(ROOT / "plots"))
        page = context.new_page()
        page.goto(PAGE)
        page.wait_for_function("window.game !== undefined")
        page.evaluate("game.pause()")
        state = page.evaluate("(seed) => game.reset({ seed: seed })", SEED)
        for _ in range(MAX_TICKS):
            result = page.evaluate("(a) => game.step(a)", greedy(q, mode, state))
            state = result["state"]
            page.wait_for_timeout(100)  # 10 ticks por segundo, ritmo humano
            if result["done"]:
                break
        print(f"puntaje final: {state['score']}  vidas: {state['lives']}  "
              f"gano: {bool(state['won'])}  ticks: {state['tick']}")
        page.screenshot(path=str(ROOT / args.shot))
        video = page.video.path()
        context.close()  # el video recien se escribe al cerrar el contexto
        browser.close()
    shutil.move(video, ROOT / "plots" / f"{args.name}.webm")
    print(f"plots/{args.name}.webm, {args.shot}")


if __name__ == "__main__":
    main()
