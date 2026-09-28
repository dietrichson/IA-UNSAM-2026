// ui.js — Dibuja el tablero, escucha los clics y publica la API en `window.game`.
// Las reglas están en game.js; acá sólo hay pantalla y entrada.

(function () {
  'use strict';

  const T = TicTacToe;
  const el = (id) => document.getElementById(id);
  const boardEl = el('board'), statusEl = el('status'), scoreEl = el('score');
  const sizeEl = el('size'), opponentEl = el('opponent');

  let state = T.createState({ size: 3 });
  let opponent = 'human';             // 'human' | 'random' | 'none'
  let score = { x: 0, o: 0, draws: 0 };
  let scored = false;                 // para no contar dos veces la misma partida

  function statusText() {
    if (!state.done) return state.player === T.X ? 'Turno: X' : 'Turno: O';
    if (state.winner === T.DRAW) return 'Empate';
    return state.winner === T.X ? 'Gana X' : 'Gana O';
  }

  // Redibuja el tablero entero a partir del estado actual.
  function render() {
    boardEl.style.setProperty('--size', state.size);
    boardEl.innerHTML = '';
    state.board.forEach((mark, i) => {
      const cell = document.createElement('button');
      cell.className = 'cell';
      cell.textContent = mark === T.X ? 'X' : mark === T.O ? 'O' : '';
      cell.disabled = state.done || mark !== T.EMPTY;
      if (state.winningLine && state.winningLine.includes(i)) cell.classList.add('win');
      cell.addEventListener('click', () => step(i));
      boardEl.appendChild(cell);
    });
    statusEl.textContent = statusText();
    scoreEl.textContent = `X: ${score.x}   O: ${score.o}   Empates: ${score.draws}`;
  }

  // Suma el resultado al marcador, una sola vez por partida.
  function recordResult() {
    if (scored || !state.done) return;
    scored = true;
    if (state.winner === T.X) score.x++;
    else if (state.winner === T.O) score.o++;
    else score.draws++;
  }

  // --- La API pública: window.game ---

  // Empieza una partida nueva. Por API el oponente es 'random' si no se aclara.
  function reset(options) {
    const opts = options || {};
    opponent = opts.opponent || 'random';
    state = T.createState({ size: opts.size || state.size, winLength: opts.winLength });
    scored = false;
    sizeEl.value = String(state.size);
    if (opponent !== 'none') opponentEl.value = opponent;
    render();
    return T.clone(state);
  }

  // Juega `action` para quien tiene el turno. Con oponente 'random', O contesta
  // enseguida: así quien llama sólo ve turnos de X o partidas terminadas.
  function step(action) {
    if (!T.applyMove(state, action)) {
      // Jugada inválida: el tablero queda igual y se castiga con -1.
      return { state: T.clone(state), reward: -1, done: state.done, illegal: true };
    }
    if (opponent === 'random' && !state.done) T.applyMove(state, T.randomMove(state));
    recordResult();
    render();
    return { state: T.clone(state), reward: T.reward(state), done: state.done, illegal: false };
  }

  window.game = {
    reset,
    step,
    render,
    getState: () => T.clone(state),
    getScore: () => ({ x: score.x, o: score.o, draws: score.draws }),
    getActions: () => T.legalMoves(state)
  };

  // --- Arranque ---

  const newGame = () => reset({ size: Number(sizeEl.value), opponent: opponentEl.value });
  el('new-game').addEventListener('click', newGame);
  sizeEl.addEventListener('change', newGame);
  opponentEl.addEventListener('change', newGame);

  reset({ size: 3, opponent: 'human' });
})();
