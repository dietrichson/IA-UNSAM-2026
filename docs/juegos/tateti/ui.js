let game;

let sizeSelect;
let winLengthSelect;
let opponentSelect;
let boardElement;
let statusElement;
let resultElement;
let scoreElement;
let resetButton;

let randomTimer = null;


function startGame() {
    const size = Number(sizeSelect.value);
    let winLength = Number(winLengthSelect.value);

    if (winLength > size) {
        winLength = size;
        winLengthSelect.value = String(size);
    }

    game = createGame({
        size: size,
        winLength: winLength
    });

    window.game = game;

    render();
}


function render() {
    const state = game.getState();

    renderBoard(state);
    renderStatus(state);
    renderResult(state);
    renderScore();
}


function renderBoard(state) {
    boardElement.innerHTML = "";

    boardElement.style.gridTemplateColumns =
        `repeat(${state.size}, 1fr)`;

    for (let i = 0; i < state.board.length; i++) {

        const cell = document.createElement("button");

        cell.className = "cell";

        cell.textContent = state.board[i] || "";

        cell.dataset.action = i;

        cell.addEventListener("click", function () {
            playHumanMove(i);
        });

        if (
            state.board[i] !== null ||
            state.gameOver ||
            (
                opponentSelect.value === "random" &&
                state.currentPlayer === "O"
            )
        ) {
            cell.disabled = true;
        }

        boardElement.appendChild(cell);
    }
}


function playHumanMove(action) {

    const state = game.getState();

    if (state.gameOver) {
        return;
    }

    if (
        opponentSelect.value === "random" &&
        state.currentPlayer === "O"
    ) {
        return;
    }

    const result = game.step(action);

    if (!result.valid) {
        render();
        return;
    }

    render();

    if (
        opponentSelect.value === "random" &&
        !game.getState().gameOver &&
        game.getState().currentPlayer === "O"
    ) {
        playRandomMove();
    }
}


function playRandomMove() {

    if (randomTimer !== null) {
        clearTimeout(randomTimer);
    }

    randomTimer = setTimeout(function () {

        randomTimer = null;

        const state = game.getState();

        if (state.gameOver) {
            return;
        }

        if (state.currentPlayer !== "O") {
            return;
        }

        const actions = game.getActions();

        if (actions.length === 0) {
            return;
        }

        const randomIndex =
            Math.floor(Math.random() * actions.length);

        const action = actions[randomIndex];

        game.step(action);

        render();

    }, 300);
}


function renderStatus(state) {

    if (state.gameOver) {

        if (state.result === "win") {
            statusElement.textContent =
                `Ganó ${state.winner}`;
        } else {
            statusElement.textContent =
                "Empate";
        }

        return;
    }

    statusElement.textContent =
        `Turno de ${state.currentPlayer}`;
}


function renderResult(state) {

    if (!state.gameOver) {
        resultElement.textContent = "";
        return;
    }

    if (state.result === "win") {
        resultElement.textContent =
            `Resultado: victoria de ${state.winner}`;
    } else {
        resultElement.textContent =
            "Resultado: empate";
    }
}


function renderScore() {

    const score = game.getScore();

    scoreElement.textContent =
        `Puntaje acumulado — X: ${score.X} | O: ${score.O}`;
}


function resetGame() {

    if (randomTimer !== null) {
        clearTimeout(randomTimer);
        randomTimer = null;
    }

    game.reset();

    render();
}


function updateWinLengthOptions() {

    const size = Number(sizeSelect.value);

    for (const option of winLengthSelect.options) {

        const value = Number(option.value);

        option.disabled = value > size;
    }

    if (Number(winLengthSelect.value) > size) {
        winLengthSelect.value = String(size);
    }
}


function initializeUI() {

    sizeSelect =
        document.getElementById("size");

    winLengthSelect =
        document.getElementById("winLength");

    opponentSelect =
        document.getElementById("opponent");

    boardElement =
        document.getElementById("board");

    statusElement =
        document.getElementById("status");

    resultElement =
        document.getElementById("result");

    scoreElement =
        document.getElementById("score");

    resetButton =
        document.getElementById("reset");


    sizeSelect.addEventListener("change", function () {
        updateWinLengthOptions();
        startGame();
    });


    winLengthSelect.addEventListener("change", function () {
        startGame();
    });


    opponentSelect.addEventListener("change", function () {
        startGame();
    });


    resetButton.addEventListener("click", function () {
        resetGame();
    });


    updateWinLengthOptions();

    startGame();
}


document.addEventListener("DOMContentLoaded", initializeUI)