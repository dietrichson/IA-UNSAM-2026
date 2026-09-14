/*
 * ui.js — Dibujo en canvas, teclado, bucle en tiempo real y la API window.game.
 * Toda la lógica del juego vive en game.js; acá solo se muestra y se controla.
 */

const CELL = 24;      // píxeles por celda de la grilla
const TICK_MS = 100;  // unos 10 ticks por segundo cuando juega una persona
const COLORS = { 1: '#39ff14', 2: '#ffffff', 3: '#ffffff', 4: '#ff5555' };

const core = SpaceInvaders.createGame();
const canvas = document.getElementById('pantalla');
const ctx = canvas.getContext('2d');
const statusLine = document.getElementById('estado');
canvas.width = SpaceInvaders.WIDTH * CELL;
canvas.height = SpaceInvaders.HEIGHT * CELL;

let state = core.getState();
let timer = null;

function drawCell(x, y, kind) {
  ctx.fillStyle = COLORS[kind];
  if (kind === 3 || kind === 4) {
    ctx.fillRect(x * CELL + CELL / 2 - 2, y * CELL + 4, 4, CELL - 8);  // bala o bomba
  } else {
    ctx.fillRect(x * CELL + 3, y * CELL + 3, CELL - 6, CELL - 6);      // alien o nave
  }
}

function draw() {
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (let y = 0; y < state.height; y++) {
    for (let x = 0; x < state.width; x++) {
      if (state.grid[y][x] !== 0) drawCell(x, y, state.grid[y][x]);
    }
  }
  let text = 'Puntos: ' + state.score + '   Vidas: ' + state.lives;
  if (state.done) text += state.won ? '   ¡GANASTE!' : '   FIN DEL JUEGO';
  statusLine.textContent = text;
}

// Teclado: se anotan las teclas apretadas y el bucle las traduce a acciones.
const keys = {};
document.addEventListener('keydown', function (e) {
  if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === ' ') {
    keys[e.key] = true;
    e.preventDefault();
  }
});
document.addEventListener('keyup', function (e) { keys[e.key] = false; });

function humanAction() {
  if (keys[' ']) { keys[' '] = false; return 3; }  // un disparo por pulsación
  if (keys['ArrowLeft']) return 1;
  if (keys['ArrowRight']) return 2;
  return 0;
}

// API interna, pensada para el laboratorio de aprendizaje por refuerzo.
const game = {
  reset: function (options) { game.pause(); state = core.reset(options); draw(); return state; },
  step: function (action) {
    const result = core.step(action);
    state = result.state;
    draw();
    return result;
  },
  getState: function () { return core.getState(); },
  getScore: function () { return core.getScore(); },
  getActions: function () { return core.getActions(); },
  render: function () { state = core.getState(); draw(); },
  play: function () {
    if (timer !== null) return;
    timer = setInterval(function () {
      state = core.step(humanAction()).state;
      draw();
      if (state.done) game.pause();
    }, TICK_MS);
  },
  pause: function () {
    if (timer !== null) { clearInterval(timer); timer = null; }
  },
};

window.game = game;

// Partida nueva con semilla al azar, para que la persona no juegue siempre lo mismo.
function newGame() {
  game.reset({ seed: Math.floor(Math.random() * 1000000) });
  game.play();
}

document.getElementById('nueva').addEventListener('click', newGame);
newGame();
