((root, factory) => {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  root.HangmanGame = api;
})(typeof window === "undefined" ? globalThis : window, () => {
  const MAX_ERRORS = 6;

  function normalizeWord(word) {
    if (typeof word !== "string") {
      throw new TypeError("La palabra debe ser texto.");
    }

    const normalized = word.trim().toUpperCase();
    if (!/^[A-ZÑ]+$/.test(normalized)) {
      throw new Error("La palabra solo puede contener letras.");
    }

    return normalized;
  }

  function normalizeLetter(letter) {
    if (typeof letter !== "string") {
      return null;
    }

    const normalized = letter.trim().toUpperCase();
    return /^[A-ZÑ]$/.test(normalized) ? normalized : null;
  }

  function nextStatus(word, guessedLetters, errors, maxErrors) {
    const allLettersFound = [...new Set(word)].every((letter) => guessedLetters.includes(letter));
    if (allLettersFound) {
      return "won";
    }

    return errors >= maxErrors ? "lost" : "playing";
  }

  function createGame(word, maxErrors = MAX_ERRORS) {
    const normalizedWord = normalizeWord(word);
    if (!Number.isInteger(maxErrors) || maxErrors < 1) {
      throw new Error("El máximo de errores debe ser un entero positivo.");
    }

    return {
      word: normalizedWord,
      guessedLetters: [],
      errors: 0,
      maxErrors,
      status: "playing",
      lastResult: "new",
    };
  }

  function guess(game, letter) {
    const normalizedLetter = normalizeLetter(letter);
    if (!normalizedLetter) {
      return { ...game, lastResult: "invalid" };
    }

    if (game.status !== "playing") {
      return { ...game, lastResult: "finished" };
    }

    if (game.guessedLetters.includes(normalizedLetter)) {
      return { ...game, lastResult: "duplicate" };
    }

    const guessedLetters = [...game.guessedLetters, normalizedLetter];
    const isCorrect = game.word.includes(normalizedLetter);
    const errors = isCorrect ? game.errors : game.errors + 1;

    return {
      ...game,
      guessedLetters,
      errors,
      status: nextStatus(game.word, guessedLetters, errors, game.maxErrors),
      lastResult: isCorrect ? "correct" : "wrong",
    };
  }

  function getState(game) {
    const correctLetters = game.guessedLetters.filter((letter) => game.word.includes(letter));
    const wrongLetters = game.guessedLetters.filter((letter) => !game.word.includes(letter));
    const maskedWord = [...game.word]
      .map((letter) => (correctLetters.includes(letter) || game.status === "lost" ? letter : "_"))
      .join(" ");

    return {
      maskedWord,
      correctLetters,
      wrongLetters,
      errors: game.errors,
      maxErrors: game.maxErrors,
      status: game.status,
      lastResult: game.lastResult,
    };
  }

  return { MAX_ERRORS, createGame, guess, getState };
});
