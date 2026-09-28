export class Input {
  constructor(game) {
    this.game = game;
    window.addEventListener('keydown', (e) => this._tecla(e));
    window.addEventListener('touchstart', (e) => this._touch(e), { passive: true });
  }

  _tecla(e) {
    const g = this.game;
    if (!g.activo) {
      if (e.code === 'Space') g.reintentar();
      return;
    }
    switch (e.code) {
      case 'ArrowLeft': case 'KeyA': g.player.moverIzquierda(); break;
      case 'ArrowRight': case 'KeyD': g.player.moverDerecha(); break;
      case 'ArrowUp': case 'KeyW': case 'Space': g.player.saltar(); break;
    }
  }

  _touch(e) {
    if (!this.game.activo) { this.game.reintentar(); return; }
    const t = e.changedTouches[0];
    const x = t.clientX, y = t.clientY;
    const cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    if (Math.abs(x - cx) > Math.abs(y - cy)) {
      x < cx ? this.game.player.moverIzquierda() : this.game.player.moverDerecha();
    } else {
      this.game.player.saltar();
    }
  }
}