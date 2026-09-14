// test.js — Pruebas de game.js. Se corren con:  node --test test.js
// Sólo usa el runner que viene con Node: no hay dependencias que instalar.

const test = require('node:test');
const assert = require('node:assert');
const T = require('./game.js');

// Juega una lista de celdas, alternando X y O automáticamente.
function play(state, moves) {
  for (const move of moves) T.applyMove(state, move);
  return state;
}

test('el estado inicial usa winLength igual al tamaño y arranca X', () => {
  const state = T.createState({ size: 4 });
  assert.strictEqual(state.size, 4);
  assert.strictEqual(state.winLength, 4);
  assert.strictEqual(state.board.length, 16);
  assert.strictEqual(state.player, T.X);
  assert.strictEqual(state.done, false);
  assert.deepStrictEqual(state.board, new Array(16).fill(0));
});

test('X gana en una fila (3x3)', () => {
  const state = play(T.createState({ size: 3 }), [0, 3, 1, 4, 2]);
  assert.strictEqual(state.winner, T.X);
  assert.strictEqual(state.done, true);
  assert.deepStrictEqual(state.winningLine, [0, 1, 2]);
  assert.strictEqual(T.reward(state), 1);
});

test('O gana en una columna (3x3)', () => {
  const state = play(T.createState({ size: 3 }), [0, 1, 2, 4, 3, 7]);
  assert.strictEqual(state.winner, T.O);
  assert.strictEqual(state.done, true);
  assert.deepStrictEqual(state.winningLine, [1, 4, 7]);
  assert.strictEqual(T.reward(state), -1);
});

test('X gana en la diagonal (4x4)', () => {
  const state = play(T.createState({ size: 4 }), [0, 1, 5, 2, 10, 3, 15]);
  assert.strictEqual(state.winner, T.X);
  assert.deepStrictEqual(state.winningLine, [0, 5, 10, 15]);
});

test('X gana en la antidiagonal (4x4)', () => {
  const state = play(T.createState({ size: 4 }), [3, 0, 6, 1, 9, 2, 12]);
  assert.strictEqual(state.winner, T.X);
  assert.deepStrictEqual(state.winningLine, [3, 6, 9, 12]);
});

test('X gana en la diagonal (5x5)', () => {
  const state = play(T.createState({ size: 5 }), [0, 1, 6, 2, 12, 3, 18, 4, 24]);
  assert.strictEqual(state.winner, T.X);
  assert.deepStrictEqual(state.winningLine, [0, 6, 12, 18, 24]);
});

test('X gana en la antidiagonal (5x5)', () => {
  const state = play(T.createState({ size: 5 }), [4, 0, 8, 1, 12, 2, 16, 3, 20]);
  assert.strictEqual(state.winner, T.X);
  assert.deepStrictEqual(state.winningLine, [4, 8, 12, 16, 20]);
});

test('winLength menor que el tamaño: 4 en línea alcanza en un 5x5', () => {
  const state = T.createState({ size: 5, winLength: 4 });
  assert.strictEqual(state.winLength, 4);
  play(state, [0, 5, 1, 6, 2, 7, 3]);
  assert.strictEqual(state.winner, T.X);
  assert.deepStrictEqual(state.winningLine, [0, 1, 2, 3]);
});

test('tres en línea no alcanza cuando winLength es 4 (5x5)', () => {
  const state = play(T.createState({ size: 5, winLength: 4 }), [0, 5, 1, 6, 2]);
  assert.strictEqual(state.winner, T.EMPTY);
  assert.strictEqual(state.done, false);
});

test('empate: tablero lleno sin ganador (3x3)', () => {
  const state = play(T.createState({ size: 3 }), [0, 1, 2, 4, 3, 5, 7, 6, 8]);
  assert.strictEqual(state.done, true);
  assert.strictEqual(state.winner, T.DRAW);
  assert.strictEqual(state.winningLine, null);
  assert.strictEqual(T.reward(state), 0);
  assert.ok(state.board.every((cell) => cell !== T.EMPTY));
});

test('jugadas inválidas: celda ocupada, fuera de rango y partida terminada', () => {
  const state = T.createState({ size: 3 });
  T.applyMove(state, 0);
  const before = T.clone(state);

  assert.strictEqual(T.applyMove(state, 0), false, 'celda ocupada');
  assert.strictEqual(T.applyMove(state, -1), false, 'índice negativo');
  assert.strictEqual(T.applyMove(state, 9), false, 'índice fuera del tablero');
  assert.strictEqual(T.applyMove(state, 1.5), false, 'índice no entero');
  assert.deepStrictEqual(state, before, 'el estado no cambia');

  const finished = play(T.createState({ size: 3 }), [0, 3, 1, 4, 2]);
  assert.strictEqual(T.applyMove(finished, 5), false, 'la partida ya terminó');
  assert.strictEqual(finished.board[5], T.EMPTY);
});

test('legalMoves devuelve las celdas vacías y nada cuando terminó', () => {
  const state = T.createState({ size: 3 });
  assert.deepStrictEqual(T.legalMoves(state), [0, 1, 2, 3, 4, 5, 6, 7, 8]);

  play(state, [4, 0]);
  assert.deepStrictEqual(T.legalMoves(state), [1, 2, 3, 5, 6, 7, 8]);

  const finished = play(T.createState({ size: 3 }), [0, 3, 1, 4, 2]);
  assert.deepStrictEqual(T.legalMoves(finished), []);
});

test('randomMove sólo elige jugadas legales y la partida siempre termina', () => {
  for (let game = 0; game < 200; game++) {
    const size = 3 + (game % 3); // alterna 3x3, 4x4 y 5x5
    const state = T.createState({ size });
    let turns = 0;

    while (!state.done) {
      const legal = T.legalMoves(state);
      const move = T.randomMove(state);
      assert.ok(legal.includes(move), 'la jugada elegida está entre las legales');
      assert.strictEqual(state.board[move], T.EMPTY, 'no pisa una celda ocupada');
      assert.strictEqual(T.applyMove(state, move), true);
      turns++;
      assert.ok(turns <= size * size, 'no juega más veces que celdas hay');
    }

    assert.ok([T.X, T.O, T.DRAW].includes(state.winner));
    assert.strictEqual(T.randomMove(state), null, 'sin jugadas cuando terminó');
  }
});

test('clone devuelve una copia independiente', () => {
  const state = play(T.createState({ size: 3 }), [4]);
  const copy = T.clone(state);
  copy.board[0] = T.O;
  assert.strictEqual(state.board[0], T.EMPTY);
});
