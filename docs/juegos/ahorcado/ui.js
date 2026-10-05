const { createGame, getState, guess } = window.HangmanGame;

const WORDS = ["MATE", "BOSQUE", "LUNA", "FUTBOL", "CAMINO", "PERRO"];
const LETTERS = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".split("");

const wordElement = document.querySelector("#word");
const messageElement = document.querySelector("#message");
const errorsElement = document.querySelector("#errors");
const wrongLettersElement = document.querySelector("#wrong-letters");
const keyboardElement = document.querySelector("#keyboard");
const newGameButton = document.querySelector("#new-game");

let game;

function pickWord() {
  return WORDS[Math.floor(Math.random() * WORDS.length)];
}

function messageFor(state) {
  if (state.status === "won") return "Ganaste.";
  if (state.status === "lost") return "Perdiste. La palabra era visible.";
  if (state.lastResult === "duplicate") return "Esa letra ya fue elegida.";
  if (state.lastResult === "wrong") return "Esa letra no está.";
  if (state.lastResult === "correct") return "Bien.";
  return "Elegí una letra.";
}

function render() {
  const state = getState(game);
  wordElement.textContent = state.maskedWord;
  messageElement.textContent = messageFor(state);
  errorsElement.textContent = `${state.errors} / ${state.maxErrors}`;
  wrongLettersElement.textContent = state.wrongLetters.join(" - ") || "-";
  document.querySelector("#drawing").dataset.errors = String(state.errors);

  for (const button of keyboardElement.querySelectorAll("button")) {
    const alreadyUsed = state.correctLetters.includes(button.value) || state.wrongLetters.includes(button.value);
    button.disabled = alreadyUsed || state.status !== "playing";
  }
}

function play(letter) {
  game = guess(game, letter);
  render();
}

function startGame() {
  game = createGame(pickWord());
  render();
}

for (const letter of LETTERS) {
  const button = document.createElement("button");
  button.type = "button";
  button.value = letter;
  button.textContent = letter;
  button.addEventListener("click", () => play(letter));
  keyboardElement.append(button);
}

window.addEventListener("keydown", (event) => {
  if (!event.ctrlKey && !event.metaKey && !event.altKey) {
    play(event.key);
  }
});

newGameButton.addEventListener("click", startGame);
startGame();
