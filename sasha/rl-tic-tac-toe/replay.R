#!/usr/bin/env Rscript
# replay.R — El agente entrenado juega en la página real (sasha/tic-tac-toe/index.html).
# Abre Chrome con chromote, juega la política greedy jugada por jugada y saca una foto.
# Uso: Rscript replay.R

suppressPackageStartupMessages({
  library(chromote)
  library(jsonlite)
})

PAUSE <- 0.7  # segundos entre jugadas, para que se vea en pantalla

script_dir <- dirname(normalizePath(sub("^--file=", "",
  grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])))

# La tabla Q que dejó train.R: una matriz, con los estados en las filas y las
# celdas del tablero en las columnas.
q_table <- readRDS(file.path(script_dir, "data", "model-3x3.rds"))
page_url <- paste0("file://", normalizePath(file.path(script_dir, "..", "tic-tac-toe", "index.html")))

# El mismo estado-texto que usó train.R: el tablero aplanado, fila por fila.
board_key <- function(board) paste(ifelse(board == 0, ".", ifelse(board == 1, "X", "O")), collapse = "")

# La jugada greedy: la de mayor Q entre las legales, o al azar si el estado es nuevo.
greedy_action <- function(q_table, state, actions) {
  if (!(state %in% rownames(q_table))) return(actions[sample.int(length(actions), 1L)])
  actions[which.max(q_table[state, as.character(actions)])]
}

b <- ChromoteSession$new()

# Ejecuta JavaScript en la página y devuelve el resultado ya parseado.
js <- function(code) {
  value <- b$Runtime$evaluate(paste0("JSON.stringify(", code, ")"), returnByValue = TRUE)$result$value
  fromJSON(value)
}

invisible(b$Page$navigate(page_url))
# Esperamos a que ui.js haya publicado window.game.
while (!isTRUE(js("typeof game !== 'undefined'"))) Sys.sleep(0.1)

invisible(js("game.reset({ size: 3, opponent: 'random' })"))
Sys.sleep(PAUSE)

repeat {
  state <- js("game.getState()")
  if (isTRUE(state$done)) break
  actions <- js("game.getActions()")
  action <- greedy_action(q_table, board_key(state$board), actions)
  cat("X juega la celda", action, "\n")
  invisible(js(sprintf("game.step(%d)", action)))
  Sys.sleep(PAUSE)
}

final <- js("game.getState()")
cat("\nTablero final:\n")
print(matrix(ifelse(final$board == 0, ".", ifelse(final$board == 1, "X", "O")),
             nrow = final$size, byrow = TRUE))
cat("Resultado:", if (final$winner == 1) "gana X (el agente)"
                  else if (final$winner == 2) "gana O (el azar)" else "empate", "\n")

shot <- file.path(script_dir, "plots", "replay-3x3.png")
invisible(b$screenshot(filename = shot, selector = "body"))
cat("Captura guardada en", shot, "\n")
invisible(b$close())
