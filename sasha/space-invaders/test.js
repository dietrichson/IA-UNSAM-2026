// Tests de game.js. Se corren con:  node --test test.js
const test = require('node:test');
const assert = require('node:assert');
const SpaceInvaders = require('./game.js');

// Partida "de laboratorio": los aliens no se mueven y no hay bombas,
// así cada test controla una sola cosa por vez.
const QUIET = { seed: 1, alienSpeed: 100000, bombChance: 0 };

function newGame(options) {
  const g = SpaceInvaders.createGame();
  g.reset(options);
  return g;
}

/** Dispara y avanza hasta que cambie el puntaje. Devuelve la recompensa del impacto. */
function fireAndWait(g) {
  let reward = g.step(3).reward;
  for (let i = 0; i < 20 && reward === 0; i++) reward = g.step(0).reward;
  return reward;
}

test('reset devuelve 24 aliens, la nave en el centro y 3 vidas', () => {
  const s = newGame(QUIET).getState();
  assert.strictEqual(s.aliens.length, 24);
  assert.strictEqual(s.aliens.filter((a) => a.alive).length, 24);
  assert.strictEqual(s.player.x, 10);
  assert.strictEqual(s.lives, 3);
  assert.strictEqual(s.score, 0);
  assert.strictEqual(s.tick, 0);
  assert.strictEqual(s.done, false);
  assert.strictEqual(s.width, 20);
  assert.strictEqual(s.height, 15);
  assert.strictEqual(s.grid.length, 15);
  assert.strictEqual(s.grid[0].length, 20);
});

test('la misma semilla produce estados idénticos tras 50 pasos', () => {
  const options = { seed: 42, bombChance: 0.5 };
  const rnd = SpaceInvaders.makeRandom(7);
  const actions = [];
  for (let i = 0; i < 50; i++) actions.push(Math.floor(rnd() * 4));

  const a = newGame(options);
  const b = newGame(options);
  let last = null;
  for (const action of actions) {
    last = a.step(action);
    assert.deepStrictEqual(last, b.step(action));
  }
  assert.ok(last.state.tick === 50 || last.state.done);
});

test('una semilla distinta produce otra partida', () => {
  const a = newGame({ seed: 1, bombChance: 0.5 });
  const b = newGame({ seed: 2, bombChance: 0.5 });
  for (let i = 0; i < 50; i++) { a.step(0); b.step(0); }
  assert.notDeepStrictEqual(a.getState().bombs, b.getState().bombs);
});

test('el movimiento se frena en los bordes', () => {
  const g = newGame(QUIET);
  for (let i = 0; i < 15; i++) g.step(1);
  assert.strictEqual(g.getState().player.x, 0);
  for (let i = 0; i < 25; i++) g.step(2);
  assert.strictEqual(g.getState().player.x, 19);
});

test('solo hay una bala a la vez', () => {
  const g = newGame(QUIET);
  assert.strictEqual(g.step(3).state.bullet.y, 13);
  const s = g.step(3).state;          // el segundo disparo se ignora
  assert.strictEqual(s.bullet.y, 12); // la bala original siguió subiendo
});

test('se puede volver a disparar cuando la bala sale de la grilla', () => {
  const g = newGame(QUIET);
  g.step(3);
  for (let i = 0; i < 14; i++) g.step(0);
  assert.strictEqual(g.getState().bullet, null);
  assert.strictEqual(g.step(3).state.bullet.y, 13);
});

test('la bala elimina un alien y suma según la fila', () => {
  const g = newGame(QUIET);           // la nave en x=10 está bajo una columna de aliens
  assert.strictEqual(fireAndWait(g), 10);   // fila de abajo
  assert.strictEqual(g.getScore(), 10);
  assert.strictEqual(fireAndWait(g), 20);   // fila del medio
  assert.strictEqual(fireAndWait(g), 30);   // fila de arriba
  assert.strictEqual(g.getScore(), 60);
  const s = g.getState();
  assert.strictEqual(s.aliens.filter((a) => a.alive).length, 21);
  assert.strictEqual(s.aliens.filter((a) => a.x === 10 && a.alive).length, 0);
});

test('el bloque rebota y baja al llegar al borde', () => {
  const g = newGame({ seed: 1, alienSpeed: 1, bombChance: 0 });
  for (let i = 0; i < 3; i++) g.step(0);       // tres pasos hacia la derecha
  let a0 = g.getState().aliens[0];
  assert.deepStrictEqual({ x: a0.x, y: a0.y }, { x: 5, y: 1 });
  g.step(0);                                    // el borde: baja y cambia de sentido
  a0 = g.getState().aliens[0];
  assert.deepStrictEqual({ x: a0.x, y: a0.y }, { x: 5, y: 2 });
  g.step(0);                                    // ahora va hacia la izquierda
  a0 = g.getState().aliens[0];
  assert.deepStrictEqual({ x: a0.x, y: a0.y }, { x: 4, y: 2 });
});

test('se pierde la partida si un alien llega a la fila de la nave', () => {
  const g = newGame({ seed: 1, alienSpeed: 1, bombChance: 0 });
  let last = null;
  for (let i = 0; i < 400 && !(last && last.done); i++) last = g.step(0);
  assert.strictEqual(last.done, true);
  assert.strictEqual(last.state.won, false);
  assert.strictEqual(last.reward, -100);
  assert.ok(last.state.aliens.some((a) => a.alive && a.y >= 14));
});

test('una bomba quita una vida y da -50; a las 3 se pierde con -150', () => {
  const g = newGame({ seed: 3, alienSpeed: 100000, bombChance: 1 });
  const penalties = [];
  let last = null;
  for (let i = 0; i < 1000 && !(last && last.done); i++) {
    last = g.step(0);                       // la nave se queda quieta y come bombas
    if (last.reward !== 0) penalties.push(last.reward);
  }
  assert.deepStrictEqual(penalties, [-50, -50, -150]);
  assert.strictEqual(last.state.lives, 0);
  assert.strictEqual(last.state.done, true);
  assert.strictEqual(last.state.won, false);
});

test('se gana al eliminar a todos los aliens, con bonus de 100', () => {
  const g = newGame(QUIET);
  let s = g.getState();
  for (let i = 0; i < 5000 && !s.done; i++) {
    const target = s.aliens.find((a) => a.alive);
    let action = 0;
    if (s.player.x < target.x) action = 2;
    else if (s.player.x > target.x) action = 1;
    else if (s.bullet === null) action = 3;
    s = g.step(action).state;
  }
  assert.strictEqual(s.done, true);
  assert.strictEqual(s.won, true);
  assert.strictEqual(s.lives, 3);
  assert.strictEqual(s.score, 8 * (30 + 20 + 10) + 100);
  assert.strictEqual(g.getScore(), 580);
});

test('grid codifica lo mismo que los campos del estado', () => {
  const g = newGame({ seed: 5, alienSpeed: 100000, bombChance: 1 });
  g.step(3);
  for (let i = 0; i < 6; i++) g.step(0);
  const s = g.getState();
  assert.strictEqual(s.grid[14][s.player.x], 2);
  assert.strictEqual(s.grid[s.bullet.y][s.bullet.x], 3);
  assert.ok(s.bombs.length > 0);
  s.bombs.forEach((b) => assert.strictEqual(s.grid[b.y][b.x], 4));
  const aliveInGrid = s.grid.flat().filter((cell) => cell === 1).length;
  assert.strictEqual(aliveInGrid, s.aliens.filter((a) => a.alive).length);
});

test('getActions siempre devuelve [0, 1, 2, 3]', () => {
  assert.deepStrictEqual(newGame(QUIET).getActions(), [0, 1, 2, 3]);
});

test('step() después de done no cambia nada', () => {
  const g = newGame({ seed: 3, alienSpeed: 100000, bombChance: 1 });
  let last = null;
  for (let i = 0; i < 1000 && !(last && last.done); i++) last = g.step(0);
  const before = g.getState();
  const after = g.step(3);
  assert.strictEqual(after.reward, 0);
  assert.strictEqual(after.done, true);
  assert.deepStrictEqual(after.state, before);
});
