const test = require("node:test");
const assert = require("node:assert/strict");

const { createGame } = require("./game.js");


// 1. Estado inicial
test("estado inicial", () => {
    const game = createGame();

    const state = game.getState();

    assert.equal(state.size, 3);
    assert.equal(state.winLength, 3);
    assert.equal(state.currentPlayer, "X");
    assert.equal(state.gameOver, false);
    assert.equal(state.winner, null);
    assert.equal(state.result, null);

    assert.deepEqual(state.board, [
        null, null, null,
        null, null, null,
        null, null, null
    ]);
});


// 2. Acciones legales iniciales
test("getActions devuelve todas las casillas al comenzar", () => {
    const game = createGame();

    assert.deepEqual(
        game.getActions(),
        [0, 1, 2, 3, 4, 5, 6, 7, 8]
    );
});


// 3. Jugada válida
test("una jugada válida modifica el tablero", () => {
    const game = createGame();

    const result = game.step(4);

    assert.equal(result.valid, true);
    assert.equal(result.reward, 0);
    assert.equal(result.done, false);

    const state = game.getState();

    assert.equal(state.board[4], "X");
    assert.equal(state.currentPlayer, "O");
});


// 4. Acción no entera
test("rechaza una acción que no es un número entero", () => {
    const game = createGame();

    const result = game.step("4");

    assert.equal(result.valid, false);
    assert.equal(result.reason, "invalid_action");
    assert.equal(result.reward, -1);
    assert.equal(result.done, false);
});


// 5. Acción fuera de rango
test("rechaza una acción fuera del tablero", () => {
    const game = createGame();

    const result = game.step(9);

    assert.equal(result.valid, false);
    assert.equal(result.reason, "out_of_range");
    assert.equal(result.reward, -1);
    assert.equal(result.done, false);
});


// 6. Casilla ocupada
test("rechaza una casilla ocupada", () => {
    const game = createGame();

    game.step(0);

    const result = game.step(0);

    assert.equal(result.valid, false);
    assert.equal(result.reason, "occupied");
    assert.equal(result.reward, -1);
    assert.equal(result.done, false);
});


// 7. Victoria horizontal
test("detecta victoria horizontal", () => {
    const game = createGame();

    game.step(0);
    game.step(3);
    game.step(1);
    game.step(4);

    const result = game.step(2);

    assert.equal(result.valid, true);
    assert.equal(result.reward, 1);
    assert.equal(result.opponentReward, -1);
    assert.equal(result.done, true);

    const state = game.getState();

    assert.equal(state.gameOver, true);
    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 8. Victoria vertical
test("detecta victoria vertical", () => {
    const game = createGame();

    game.step(0);
    game.step(1);
    game.step(3);
    game.step(2);

    const result = game.step(6);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    const state = game.getState();

    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 9. Victoria diagonal descendente
test("detecta victoria diagonal descendente", () => {
    const game = createGame();

    game.step(0);
    game.step(1);
    game.step(4);
    game.step(2);

    const result = game.step(8);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    const state = game.getState();

    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 10. Victoria diagonal ascendente
test("detecta victoria diagonal ascendente", () => {
    const game = createGame();

    game.step(6);
    game.step(0);
    game.step(4);
    game.step(1);

    const result = game.step(2);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    const state = game.getState();

    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 11. Empate
test("detecta empate", () => {
    const game = createGame();

    const moves = [
        0, 1,
        2, 4,
        3, 5,
        7, 6,
        8
    ];

    let result;

    for (const move of moves) {
        result = game.step(move);
    }

    assert.equal(result.done, true);
    assert.equal(result.reward, 0);
    assert.equal(result.opponentReward, 0);

    const state = game.getState();

    assert.equal(state.gameOver, true);
    assert.equal(state.winner, null);
    assert.equal(state.result, "draw");
});


// 12. Acciones después de terminar
test("rechaza acciones después de terminar la partida", () => {
    const game = createGame();

    game.step(0);
    game.step(3);
    game.step(1);
    game.step(4);
    game.step(2);

    const result = game.step(5);

    assert.equal(result.valid, false);
    assert.equal(result.reason, "game_over");
    assert.equal(result.reward, -1);
    assert.equal(result.done, true);

    assert.deepEqual(game.getActions(), []);
});


// 13. Reset
test("reset devuelve el tablero al estado inicial", () => {
    const game = createGame();

    game.step(4);
    game.step(0);

    const state = game.reset();

    assert.deepEqual(state.board, [
        null, null, null,
        null, null, null,
        null, null, null
    ]);

    assert.equal(state.currentPlayer, "X");
    assert.equal(state.gameOver, false);
    assert.equal(state.winner, null);
    assert.equal(state.result, null);

    assert.deepEqual(
        game.getActions(),
        [0, 1, 2, 3, 4, 5, 6, 7, 8]
    );
});


// 14. Puntaje
test("getScore registra victoria y derrota", () => {
    const game = createGame();

    game.step(0);
    game.step(3);
    game.step(1);
    game.step(4);
    game.step(2);

    assert.deepEqual(game.getScore(), {
        X: 1,
        O: -1
    });
});


// 15. Tablero 4x4
test("funciona con tablero 4x4", () => {
    const game = createGame({
        size: 4,
        winLength: 3
    });

    const state = game.getState();

    assert.equal(state.size, 4);
    assert.equal(state.winLength, 3);
    assert.equal(state.board.length, 16);

    assert.equal(game.getActions().length, 16);
});


// 16. Victoria en tablero 4x4
test("detecta victoria en tablero 4x4", () => {
    const game = createGame({
        size: 4,
        winLength: 3
    });

    game.step(0);
    game.step(4);
    game.step(1);
    game.step(5);

    const result = game.step(2);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    const state = game.getState();

    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 17. Tablero 5x5
test("funciona con tablero 5x5", () => {
    const game = createGame({
        size: 5,
        winLength: 3
    });

    const state = game.getState();

    assert.equal(state.size, 5);
    assert.equal(state.winLength, 3);
    assert.equal(state.board.length, 25);

    assert.equal(game.getActions().length, 25);
});


// 18. Victoria en tablero 5x5
test("detecta victoria en tablero 5x5", () => {
    const game = createGame({
        size: 5,
        winLength: 3
    });

    game.step(0);
    game.step(5);
    game.step(1);
    game.step(6);

    const result = game.step(2);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    const state = game.getState();

    assert.equal(state.winner, "X");
    assert.equal(state.result, "win");
});


// 19. winLength configurable
test("permite configurar winLength", () => {
    const game = createGame({
        size: 5,
        winLength: 4
    });

    const state = game.getState();

    assert.equal(state.size, 5);
    assert.equal(state.winLength, 4);

    game.step(0);
    game.step(5);
    game.step(1);
    game.step(6);
    game.step(2);
    game.step(7);

    const result = game.step(3);

    assert.equal(result.done, true);
    assert.equal(result.reward, 1);

    assert.equal(game.getState().winner, "X");
});


// 20. Transición completa
test("step devuelve información completa de la transición", () => {
    const game = createGame();

    const result = game.step(0);

    assert.ok(result.state);
    assert.equal(result.action, 0);
    assert.equal(result.player, "X");
    assert.equal(result.valid, true);
    assert.equal(result.reason, null);
    assert.equal(result.reward, 0);
    assert.equal(result.opponentReward, 0);
    assert.equal(result.done, false);
});