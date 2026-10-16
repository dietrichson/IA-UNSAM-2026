// game.js — Las reglas del ta-te-ti y nada más.
// No toca la pantalla (acá no hay DOM), así que se puede probar con Node.
// En el navegador queda disponible como la variable global `TicTacToe`.

(function (root) {
  'use strict';

  // Qué puede haber en una celda.
  const EMPTY = 0, X = 1, O = 2;
  const DRAW = 3; // sólo aparece en `winner`, cuando el tablero se llena sin ganador

  // Direcciones donde buscar una línea: →, ↓, ↘, ↙
  const DIRECTIONS = [[0, 1], [1, 0], [1, 1], [1, -1]];

  // Estado inicial. `winLength` por defecto es igual al lado del tablero.
  function createState(options) {
    const opts = options || {};
    const size = opts.size || 3;
    return {
      size,
      winLength: opts.winLength || size,
      board: new Array(size * size).fill(EMPTY),
      player: X, // X siempre empieza
      winner: EMPTY,
      done: false,
      winningLine: null
    };
  }

  // Copia independiente: el estado es JSON puro, así nadie modifica el original.
  function clone(state) {
    return JSON.parse(JSON.stringify(state));
  }

  // Las celdas vacías. Si la partida terminó, no hay jugadas posibles.
  function legalMoves(state) {
    if (state.done) return [];
    const moves = [];
    state.board.forEach((cell, i) => { if (cell === EMPTY) moves.push(i); });
    return moves;
  }

  // ¿Hay `winLength` marcas iguales desde (row, col) yendo hacia (dRow, dCol)?
  // Devuelve las celdas de la línea, o null si no hay.
  function lineFrom(state, row, col, dRow, dCol) {
    const mark = state.board[row * state.size + col];
    if (mark === EMPTY) return null;
    const cells = [];
    for (let k = 0; k < state.winLength; k++) {
      const r = row + dRow * k, c = col + dCol * k;
      if (r < 0 || r >= state.size || c < 0 || c >= state.size) return null;
      if (state.board[r * state.size + c] !== mark) return null;
      cells.push(r * state.size + c);
    }
    return cells;
  }

  // Recorre el tablero entero buscando una línea ganadora.
  function findWin(state) {
    for (let row = 0; row < state.size; row++) {
      for (let col = 0; col < state.size; col++) {
        for (const [dRow, dCol] of DIRECTIONS) {
          const cells = lineFrom(state, row, col, dRow, dCol);
          if (cells) return { player: state.board[row * state.size + col], cells };
        }
      }
    }
    return null;
  }

  // Juega en `index` para quien tiene el turno y modifica `state`.
  // Devuelve true si la jugada era legal; si no, false y el tablero queda igual.
  function applyMove(state, index) {
    if (state.done) return false;
    if (!Number.isInteger(index) || index < 0 || index >= state.board.length) return false;
    if (state.board[index] !== EMPTY) return false;

    state.board[index] = state.player;
    const win = findWin(state);
    if (win) {
      state.winner = win.player;
      state.winningLine = win.cells;
      state.done = true;
    } else if (!state.board.includes(EMPTY)) {
      state.winner = DRAW; // tablero lleno y nadie alineó
      state.done = true;
    } else {
      state.player = state.player === X ? O : X;
    }
    return true;
  }

  // Una jugada legal al azar. `random` permite fijar el azar en las pruebas.
  function randomMove(state, random) {
    const moves = legalMoves(state);
    if (moves.length === 0) return null;
    return moves[Math.floor((random || Math.random)() * moves.length)];
  }

  // La recompensa se mira siempre desde el lado de X.
  function reward(state) {
    if (state.winner === X) return 1;
    if (state.winner === O) return -1;
    return 0;
  }

  const TicTacToe = {
    EMPTY, X, O, DRAW,
    createState, clone, legalMoves, findWin, applyMove, randomMove, reward
  };

  root.TicTacToe = TicTacToe;
  if (typeof module !== 'undefined') module.exports = TicTacToe;
})(typeof globalThis !== 'undefined' ? globalThis : this);
