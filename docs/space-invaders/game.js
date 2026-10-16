/*
 * game.js — Lógica pura del juego, sobre una grilla discreta de 20 x 15.
 * No toca el DOM, ni el canvas, ni temporizadores: solo calcula estados. Por eso
 * funciona igual en el navegador (window.SpaceInvaders) que en Node (module.exports).
 */

const WIDTH = 20;                     // columnas de la grilla
const HEIGHT = 15;                    // filas de la grilla
const PLAYER_ROW = HEIGHT - 1;        // la nave siempre está en la fila 14
const ALIEN_ROWS = 3, ALIEN_COLS = 8; // el bloque de aliens
const ALIEN_X0 = 2, ALIEN_Y0 = 1;     // celda del primer alien
const ALIEN_GAP = 2;                  // separación horizontal entre aliens
const ROW_POINTS = [30, 20, 10];      // puntos según la fila del alien (0 = la de arriba)
const PENALTY_LIFE = -50;             // castigo por perder una vida
const PENALTY_LOSS = -100;            // castigo por perder la partida
const BONUS_WIN = 100;                // premio por eliminar a todos los aliens
const START_LIVES = 3;
const DEFAULTS = { seed: 1, alienSpeed: 4, bombChance: 0.02 };

/** Generador pseudoaleatorio con semilla (mulberry32): misma semilla, misma partida. */
function makeRandom(seed) {
  let a = seed >>> 0;
  return function random() {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Crea una partida independiente, con su propio estado interno. */
function createGame() {
  let s = null;    // estado interno (mutable)
  let rng = null;  // generador aleatorio de esta partida

  /** Empieza un episodio nuevo y devuelve el estado inicial. */
  function reset(options) {
    const o = Object.assign({}, DEFAULTS, options || {});
    rng = makeRandom(o.seed);
    s = {
      tick: 0, score: 0, lives: START_LIVES, done: false, won: false,
      playerX: Math.floor(WIDTH / 2),
      aliens: [], bullet: null, bombs: [],
      dir: 1,        // 1 = el bloque va a la derecha, -1 = a la izquierda
      moveTimer: 0,  // ticks acumulados desde el último movimiento del bloque
      alienSpeed: o.alienSpeed, bombChance: o.bombChance,
    };
    for (let row = 0; row < ALIEN_ROWS; row++) {
      for (let col = 0; col < ALIEN_COLS; col++) {
        s.aliens.push({ x: ALIEN_X0 + col * ALIEN_GAP, y: ALIEN_Y0 + row, row: row, alive: true });
      }
    }
    return getState();
  }

  /** Avanza el mundo un tick. action: 0 = nada, 1 = izquierda, 2 = derecha, 3 = disparar. */
  function step(action) {
    if (s.done) return { state: getState(), reward: 0, done: true };
    let reward = 0;
    if (action === 1) s.playerX = Math.max(0, s.playerX - 1);
    else if (action === 2) s.playerX = Math.min(WIDTH - 1, s.playerX + 1);
    else if (action === 3 && s.bullet === null) s.bullet = { x: s.playerX, y: PLAYER_ROW };
    reward += moveBullet();
    moveAliens();
    dropBomb();
    reward += moveBombs();
    if (!s.done && livingAliens().length === 0) {          // no queda ningún alien
      s.done = true; s.won = true; s.score += BONUS_WIN; reward += BONUS_WIN;
    } else if (!s.done && livingAliens().some((a) => a.y >= PLAYER_ROW)) {
      s.done = true; reward += PENALTY_LOSS;               // un alien llegó a la fila de la nave
    }
    s.tick++;
    return { state: getState(), reward: reward, done: s.done };
  }

  /** Sube la bala una fila y resuelve el impacto. Devuelve los puntos ganados. */
  function moveBullet() {
    if (s.bullet === null) return 0;
    s.bullet.y -= 1;
    if (s.bullet.y < 0) { s.bullet = null; return 0; }
    const hit = s.aliens.find((a) => a.alive && a.x === s.bullet.x && a.y === s.bullet.y);
    if (!hit) return 0;
    hit.alive = false;
    s.bullet = null;
    s.score += ROW_POINTS[hit.row];
    return ROW_POINTS[hit.row];
  }

  /** Cada alienSpeed ticks el bloque se corre una celda; en el borde baja y cambia de sentido. */
  function moveAliens() {
    s.moveTimer++;
    if (s.moveTimer < s.alienSpeed) return;
    s.moveTimer = 0;
    const alive = livingAliens();
    if (alive.length === 0) return;
    const minX = Math.min.apply(null, alive.map((a) => a.x));
    const maxX = Math.max.apply(null, alive.map((a) => a.x));
    if ((s.dir === 1 && maxX + 1 > WIDTH - 1) || (s.dir === -1 && minX - 1 < 0)) {
      s.dir = -s.dir;                            // en el borde: baja y cambia de sentido
      alive.forEach((a) => { a.y += 1; });
    } else alive.forEach((a) => { a.x += s.dir; });
  }

  /** Con probabilidad bombChance, uno de los aliens más bajos de su columna tira una bomba. */
  function dropBomb() {
    if (rng() >= s.bombChance) return;
    const lowest = {};  // por columna, el alien vivo que está más abajo
    livingAliens().forEach((a) => { if (!lowest[a.x] || a.y > lowest[a.x].y) lowest[a.x] = a; });
    const shooters = Object.keys(lowest).map((x) => lowest[x]);
    if (shooters.length === 0) return;
    const shooter = shooters[Math.floor(rng() * shooters.length)];
    s.bombs.push({ x: shooter.x, y: shooter.y });
  }

  /** Baja las bombas una fila y resuelve el choque con la nave. Devuelve el castigo. */
  function moveBombs() {
    let reward = 0;
    const surviving = [];
    for (const b of s.bombs) {
      b.y += 1;
      if (b.y > PLAYER_ROW) continue;                  // se fue de la grilla
      if (b.y === PLAYER_ROW && b.x === s.playerX) {   // le pegó a la nave
        s.lives -= 1;
        reward += PENALTY_LIFE;
        if (s.lives <= 0) { s.done = true; reward += PENALTY_LOSS; }
        continue;
      }
      surviving.push(b);
    }
    s.bombs = surviving;
    return reward;
  }

  function livingAliens() { return s.aliens.filter((a) => a.alive); }

  /** Copia nueva del estado, lista para convertir a JSON. */
  function getState() {
    const state = {
      width: WIDTH, height: HEIGHT, tick: s.tick,
      player: { x: s.playerX },
      aliens: s.aliens.map((a) => ({ x: a.x, y: a.y, row: a.row, alive: a.alive })),
      bullet: s.bullet ? { x: s.bullet.x, y: s.bullet.y } : null,
      bombs: s.bombs.map((b) => ({ x: b.x, y: b.y })),
      score: s.score, lives: s.lives, done: s.done, won: s.won,
    };
    state.grid = buildGrid(state);
    return state;
  }

  /** Vuelca el estado en una matriz: 0 vacío, 1 alien, 2 nave, 3 bala, 4 bomba. */
  function buildGrid(state) {
    const grid = [];
    for (let y = 0; y < HEIGHT; y++) grid.push(new Array(WIDTH).fill(0));
    state.aliens.forEach((a) => { if (a.alive) grid[a.y][a.x] = 1; });
    grid[PLAYER_ROW][state.player.x] = 2;
    if (state.bullet) grid[state.bullet.y][state.bullet.x] = 3;
    state.bombs.forEach((b) => { grid[b.y][b.x] = 4; });
    return grid;
  }

  reset();
  return { reset, step, getState, getScore: () => s.score, getActions: () => [0, 1, 2, 3] };
}

const SpaceInvaders = { createGame, makeRandom, WIDTH, HEIGHT, ROW_POINTS, DEFAULTS };
if (typeof window !== 'undefined') window.SpaceInvaders = SpaceInvaders;
if (typeof module !== 'undefined') module.exports = SpaceInvaders;
