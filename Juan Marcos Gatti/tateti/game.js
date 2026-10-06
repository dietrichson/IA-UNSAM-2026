function createGame(options = {}) {
    const size = options.size || 3;
    const winLength = options.winLength || 3;

    if (![3, 4, 5].includes(size)) {
        throw new Error("El tamaño del tablero debe ser 3, 4 o 5.");
    }

    if (winLength < 3 || winLength > size) {
        throw new Error(
            "winLength debe ser como mínimo 3 y no puede superar el tamaño del tablero."
        );
    }

    let score = {
        X: 0,
        O: 0
    };

    let state = createInitialState();

    function createInitialState() {
        return {
            board: new Array(size * size).fill(null),
            size: size,
            winLength: winLength,
            currentPlayer: "X",
            gameOver: false,
            winner: null,
            result: null
        };
    }

    function reset() {
        state = createInitialState();
        return getState();
    }

    function getState() {
        return {
            ...state,
            board: [...state.board]
        };
    }

    function getActions() {
        if (state.gameOver) {
            return [];
        }

        const actions = [];

        for (let i = 0; i < state.board.length; i++) {
            if (state.board[i] === null) {
                actions.push(i);
            }
        }

        return actions;
    }

    function isBoardFull() {
        return state.board.every(function (cell) {
            return cell !== null;
        });
    }

    function checkWinner(player) {
        const board = state.board;

        // Filas
        for (let row = 0; row < size; row++) {
            let count = 0;

            for (let col = 0; col < size; col++) {
                const index = row * size + col;

                if (board[index] === player) {
                    count++;
                } else {
                    count = 0;
                }

                if (count >= winLength) {
                    return true;
                }
            }
        }

        // Columnas
        for (let col = 0; col < size; col++) {
            let count = 0;

            for (let row = 0; row < size; row++) {
                const index = row * size + col;

                if (board[index] === player) {
                    count++;
                } else {
                    count = 0;
                }

                if (count >= winLength) {
                    return true;
                }
            }
        }

        // Diagonales descendentes
        for (let row = 0; row <= size - winLength; row++) {
            for (let col = 0; col <= size - winLength; col++) {
                let count = 0;

                for (let i = 0; i < winLength; i++) {
                    const currentRow = row + i;
                    const currentCol = col + i;
                    const index = currentRow * size + currentCol;

                    if (board[index] === player) {
                        count++;
                    } else {
                        break;
                    }
                }

                if (count >= winLength) {
                    return true;
                }
            }
        }

        // Diagonales ascendentes
        for (let row = winLength - 1; row < size; row++) {
            for (let col = 0; col <= size - winLength; col++) {
                let count = 0;

                for (let i = 0; i < winLength; i++) {
                    const currentRow = row - i;
                    const currentCol = col + i;
                    const index = currentRow * size + currentCol;

                    if (board[index] === player) {
                        count++;
                    } else {
                        break;
                    }
                }

                if (count >= winLength) {
                    return true;
                }
            }
        }

        return false;
    }

    function step(action) {
        // El juego ya terminó
        if (state.gameOver) {
            return {
                state: getState(),
                action: action,
                player: state.currentPlayer,
                valid: false,
                reason: "game_over",
                reward: -1,
                opponentReward: 0,
                done: true
            };
        }

        // Acción no entera
        if (!Number.isInteger(action)) {
            return {
                state: getState(),
                action: action,
                player: state.currentPlayer,
                valid: false,
                reason: "invalid_action",
                reward: -1,
                opponentReward: 0,
                done: false
            };
        }

        // Acción fuera del tablero
        if (action < 0 || action >= state.board.length) {
            return {
                state: getState(),
                action: action,
                player: state.currentPlayer,
                valid: false,
                reason: "out_of_range",
                reward: -1,
                opponentReward: 0,
                done: false
            };
        }

        // Casilla ocupada
        if (state.board[action] !== null) {
            return {
                state: getState(),
                action: action,
                player: state.currentPlayer,
                valid: false,
                reason: "occupied",
                reward: -1,
                opponentReward: 0,
                done: false
            };
        }

        const player = state.currentPlayer;
        const opponent = player === "X" ? "O" : "X";

        // Realizar jugada
        state.board[action] = player;

        // Victoria
        if (checkWinner(player)) {
            state.gameOver = true;
            state.winner = player;
            state.result = "win";

            score[player] += 1;
            score[opponent] -= 1;

            return {
                state: getState(),
                action: action,
                player: player,
                valid: true,
                reason: null,
                reward: 1,
                opponentReward: -1,
                done: true
            };
        }

        // Empate
        if (isBoardFull()) {
            state.gameOver = true;
            state.winner = null;
            state.result = "draw";

            return {
                state: getState(),
                action: action,
                player: player,
                valid: true,
                reason: null,
                reward: 0,
                opponentReward: 0,
                done: true
            };
        }

        // Cambiar jugador
        state.currentPlayer = opponent;

        return {
            state: getState(),
            action: action,
            player: player,
            valid: true,
            reason: null,
            reward: 0,
            opponentReward: 0,
            done: false
        };
    }

    function getScore() {
        return {
            X: score.X,
            O: score.O
        };
    }

    return {
        reset: reset,
        step: step,
        getState: getState,
        getScore: getScore,
        getActions: getActions
    };
}


// Compatible con Node.js
if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        createGame: createGame
    };
}


// Disponible en el navegador
if (typeof window !== "undefined") {
    window.createGame = createGame;
}