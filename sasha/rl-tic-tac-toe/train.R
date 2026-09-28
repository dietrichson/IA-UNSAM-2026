#!/usr/bin/env Rscript
# train.R — Q-learning para el ta-te-ti de sasha/tic-tac-toe/, en R.
# El juego corre en JavaScript (game.js) dentro de V8; R sólo decide las jugadas.
# Uso: Rscript train.R <size> [winLength]

suppressPackageStartupMessages({
  library(V8)
  library(ReinforcementLearning)
  library(hash)  # viene con ReinforcementLearning: así guarda la tabla Q
})

# --- Configuración -----------------------------------------------------------

args <- commandArgs(trailingOnly = TRUE)
SIZE <- if (length(args) >= 1) as.integer(args[1]) else 3L
WIN_LENGTH <- if (length(args) >= 2) as.integer(args[2]) else SIZE
TAG <- if (WIN_LENGTH == SIZE) paste0(SIZE, "x", SIZE) else paste0(SIZE, "x", SIZE, "-w", WIN_LENGTH)

K <- if (SIZE == 3L) 500L else 2000L   # partidas de entrenamiento por iteración
EVAL_GAMES <- 1000L                    # partidas de evaluación (greedy, sin aprender)
MAX_EPISODES <- 200000L                # tope de partidas de entrenamiento
MAX_SECONDS <- 45 * 60                 # tope de tiempo de pared
MAX_ITER <- MAX_EPISODES %/% K         # iteraciones si sólo mandara el tope de partidas
CONTROL <- list(alpha = 0.2, gamma = 0.9, epsilon = 0.1)  # epsilon lo maneja este script

# epsilon baja en línea recta de 1,0 a 0,1 a lo largo de las MAX_ITER iteraciones.
epsilon_at <- function(iteration) max(0.1, 1 - 0.9 * (iteration - 1) / (MAX_ITER - 1))

set.seed(42L)  # el azar de R; el de JavaScript (Math.random) no se puede fijar

script_dir <- dirname(normalizePath(sub("^--file=", "",
  grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])))

# --- El juego, del lado de JavaScript ----------------------------------------

ct <- v8()
ct$source(file.path(script_dir, "..", "tic-tac-toe", "game.js"))

# `env` es el entorno de RL: las mismas reglas del navegador, sin pantalla.
# Un estado es el tablero aplanado como texto ("...X.O..."), fila por fila.
ct$eval('
var env = {
  state: null,
  key: function (s) {
    return s.board.map(function (c) { return c === 0 ? "." : (c === 1 ? "X" : "O"); }).join("");
  },
  reset: function (size, winLength) {
    env.state = TicTacToe.createState({ size: size, winLength: winLength });
    return { state: env.key(env.state), actions: TicTacToe.legalMoves(env.state) };
  },
  // Juega la celda `action` con X y, si la partida sigue, O responde al azar.
  step: function (action) {
    TicTacToe.applyMove(env.state, action);
    if (!env.state.done) TicTacToe.applyMove(env.state, TicTacToe.randomMove(env.state));
    return { state: env.key(env.state), reward: TicTacToe.reward(env.state),
             done: env.state.done, actions: TicTacToe.legalMoves(env.state) };
  }
};
')

# --- La política -------------------------------------------------------------

# Q(estado, ·) para las jugadas legales, o NULL si el estado nunca se vio.
# El paquete guarda Q en un hash anidado: estado -> acción -> valor.
q_row <- function(model, state, actions) {
  if (is.null(model) || !has.key(state, model$Q_hash)) return(NULL)
  row <- model$Q_hash[[state]]
  vapply(as.character(actions), function(a) if (has.key(a, row)) row[[a]] else 0, numeric(1))
}

# epsilon-greedy: al azar con probabilidad epsilon, y también si el estado es nuevo.
choose_action <- function(model, state, actions, epsilon) {
  q <- if (runif(1) < epsilon) NULL else q_row(model, state, actions)
  if (is.null(q)) actions[sample.int(length(actions), 1L)] else actions[which.max(q)]
}

# --- Partidas y tuplas -------------------------------------------------------

# Una partida completa. Devuelve las tuplas (State, Action, Reward, NextState).
play_game <- function(model, epsilon) {
  obs <- ct$call("env.reset", SIZE, WIN_LENGTH)
  states <- character(0); acts <- character(0); rews <- numeric(0); nexts <- character(0)
  repeat {
    state <- obs$state
    action <- choose_action(model, state, obs$actions, epsilon)
    obs <- ct$call("env.step", action)
    states <- c(states, state); acts <- c(acts, as.character(action))
    rews <- c(rews, obs$reward); nexts <- c(nexts, obs$state)
    if (obs$done) break
  }
  list(state = states, action = acts, reward = rews, next_state = nexts)
}

# Un lote de partidas, ya en el formato que pide ReinforcementLearning().
collect <- function(model, epsilon, n_games) {
  games <- lapply(seq_len(n_games), function(i) play_game(model, epsilon))
  data.frame(State = unlist(lapply(games, `[[`, "state")),
             Action = unlist(lapply(games, `[[`, "action")),
             Reward = unlist(lapply(games, `[[`, "reward")),
             NextState = unlist(lapply(games, `[[`, "next_state")),
             stringsAsFactors = FALSE)
}

# Partidas de prueba con la política greedy (epsilon = 0): acá no se aprende.
# Devuelve la recompensa final de cada partida: +1 gana X, -1 gana O, 0 empate.
evaluate <- function(model, n_games) {
  vapply(seq_len(n_games), function(i) {
    rewards <- play_game(model, 0)$reward
    rewards[length(rewards)]
  }, numeric(1))
}

# --- El registro -------------------------------------------------------------

log_path <- file.path(script_dir, "data", paste0("log-", TAG, ".csv"))
cat("iteration,episodes_cumulative,epsilon,wins,draws,losses,win_rate,mean_reward,q_table_size,wall_time_s\n",
    file = log_path)

# --- El loop -----------------------------------------------------------------

cat(sprintf("Entrenando %s | K=%d partidas/iteración | topes: %d partidas o %d min\n",
            TAG, K, MAX_EPISODES, MAX_SECONDS %/% 60))

model <- NULL
episodes <- 0L
iteration <- 0L
started <- Sys.time()
last_iter_s <- 0
cap <- "ninguno"

repeat {
  elapsed <- as.numeric(difftime(Sys.time(), started, units = "secs"))
  if (episodes >= MAX_EPISODES) { cap <- "partidas"; break }
  # Si la iteración que viene no entra en el presupuesto de tiempo, cortamos acá.
  if (elapsed + last_iter_s > MAX_SECONDS) { cap <- "tiempo"; break }

  iteration <- iteration + 1L
  iter_start <- Sys.time()
  epsilon <- epsilon_at(iteration)

  t0 <- Sys.time()
  experience <- collect(model, epsilon, K)
  t_play <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

  t0 <- Sys.time()
  model <- ReinforcementLearning(experience, s = "State", a = "Action", r = "Reward",
                                 s_new = "NextState", model = model, control = CONTROL,
                                 verbose = FALSE)
  t_fit <- as.numeric(difftime(Sys.time(), t0, units = "secs"))

  rewards <- evaluate(model, EVAL_GAMES)

  episodes <- episodes + K
  last_iter_s <- as.numeric(difftime(Sys.time(), iter_start, units = "secs"))
  total_s <- as.numeric(difftime(Sys.time(), started, units = "secs"))
  win_rate <- mean(rewards == 1)

  cat(sprintf("%d,%d,%.4f,%d,%d,%d,%.4f,%.4f,%d,%.2f\n",
              iteration, episodes, epsilon, sum(rewards == 1), sum(rewards == 0),
              sum(rewards == -1), win_rate, mean(rewards), nrow(model$Q), total_s),
      file = log_path, append = TRUE)

  cat(sprintf("iter %3d | eps %.2f | win_rate %.3f | |Q| %6d | %5.1fs (juego %.1f, fit %.1f) | %.0f partidas/s | %.0f filas/s\n",
              iteration, epsilon, win_rate, nrow(model$Q), last_iter_s, t_play, t_fit,
              K / t_play, nrow(experience) / t_fit))
}

# Guardamos la tabla Q (matriz estado x acción), que es lo que hace falta para
# jugar. El objeto entero del paquete pesa gigabytes: guarda Q además como un
# hash de hashes y serializar medio millón de entornos de R tarda media hora.
saveRDS(model$Q, file.path(script_dir, "data", paste0("model-", TAG, ".rds")))
cat(sprintf("Fin: %d iteraciones, %d partidas, %.1f min, tope alcanzado: %s\n",
            iteration, episodes, as.numeric(difftime(Sys.time(), started, units = "mins")), cap))
