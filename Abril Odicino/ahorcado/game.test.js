const test = require("node:test");
const assert = require("node:assert/strict");

const { createGame, getState, guess } = require("./game.js");

test("una partida nueva oculta todas las letras", () => {
  const state = getState(createGame("MATE"));

  assert.equal(state.maskedWord, "_ _ _ _");
  assert.equal(state.errors, 0);
  assert.equal(state.status, "playing");
});

test("una letra correcta se revela sin sumar errores", () => {
  const state = getState(guess(createGame("MATE"), "a"));

  assert.equal(state.maskedWord, "_ A _ _");
  assert.equal(state.errors, 0);
  assert.deepEqual(state.correctLetters, ["A"]);
});

test("una letra incorrecta suma un solo error y no se repite", () => {
  let game = guess(createGame("MATE"), "z");
  game = guess(game, "z");
  const state = getState(game);

  assert.equal(state.errors, 1);
  assert.deepEqual(state.wrongLetters, ["Z"]);
  assert.equal(state.lastResult, "duplicate");
});

test("la partida termina al encontrar todas las letras", () => {
  let game = createGame("SOL");
  for (const letter of ["s", "o", "l"]) {
    game = guess(game, letter);
  }

  const state = getState(game);
  assert.equal(state.status, "won");
  assert.equal(state.maskedWord, "S O L");
});

test("la partida termina al llegar al máximo de errores", () => {
  let game = createGame("SOL", 2);
  game = guess(game, "a");
  game = guess(game, "b");

  const state = getState(game);
  assert.equal(state.status, "lost");
  assert.equal(state.errors, 2);
  assert.equal(state.maskedWord, "S O L");
});
