#!/usr/bin/env Rscript
# plot.R — Curva de aprendizaje a partir de los CSV que escribió train.R.
# Uso: Rscript plot.R

suppressPackageStartupMessages(library(ggplot2))

THRESHOLD <- 0.90      # win_rate que hay que alcanzar
WINDOW <- 3            # iteraciones de la media móvil
MAX_EPISODES <- 200000 # el tope de partidas que usa train.R

script_dir <- dirname(normalizePath(sub("^--file=", "",
  grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)[1])))

# Media móvil de las últimas `n` observaciones (NA hasta tener n datos).
rolling_mean <- function(x, n) {
  vapply(seq_along(x), function(i) if (i < n) NA_real_ else mean(x[(i - n + 1):i]), numeric(1))
}

files <- sort(Sys.glob(file.path(script_dir, "data", "log-*.csv")))
if (length(files) == 0) stop("No hay CSV en data/. Corré train.R primero.")

logs <- lapply(files, function(f) {
  d <- read.csv(f)
  d$run <- gsub("^log-|\\.csv$", "", basename(f))
  d
})
curves <- do.call(rbind, logs)

# Convergencia: primera iteración con media móvil de 3 de win_rate >= 0.90.
resumen <- do.call(rbind, lapply(logs, function(d) {
  hit <- which(rolling_mean(d$win_rate, WINDOW) >= THRESHOLD)
  ok <- length(hit) > 0
  data.frame(
    run = d$run[1],
    iteraciones = nrow(d),
    partidas = max(d$episodes_cumulative),
    minutos = round(max(d$wall_time_s) / 60, 1),
    estados_Q = max(d$q_table_size),
    win_rate_final = d$win_rate[nrow(d)],
    # El tope que cortó la corrida: si llegó a MAX_EPISODES fue el de partidas.
    tope = if (max(d$episodes_cumulative) >= MAX_EPISODES) "partidas" else "tiempo",
    conv_iteracion = if (ok) d$iteration[hit[1]] else NA_integer_,
    conv_partidas = if (ok) d$episodes_cumulative[hit[1]] else NA_integer_,
    stringsAsFactors = FALSE)
}))

convergidos <- resumen[!is.na(resumen$conv_partidas), ]

p <- ggplot(curves, aes(episodes_cumulative, win_rate, colour = run)) +
  geom_line(linewidth = 0.6) +
  geom_hline(yintercept = THRESHOLD, linetype = "dashed", colour = "grey30") +
  geom_vline(data = convergidos, aes(xintercept = conv_partidas, colour = run),
             linetype = "dashed", show.legend = FALSE) +
  scale_x_log10() +
  scale_y_continuous(limits = c(0, 1)) +
  labs(title = "Ta-te-ti con Q-learning: curva de aprendizaje",
       subtitle = "1.000 partidas de evaluación por iteración, política greedy, contra el oponente aleatorio",
       x = "partidas de entrenamiento acumuladas (escala log)",
       y = "win_rate (evaluación)", colour = "corrida") +
  theme_minimal(base_size = 12)

out <- file.path(script_dir, "plots", "learning-curve.png")
ggsave(out, p, width = 9, height = 5.5, dpi = 150)
cat("Gráfico guardado en", out, "\n\n")

print(resumen, row.names = FALSE)
cat("\nConvergencia = primera iteración con media móvil de", WINDOW,
    "de win_rate >=", THRESHOLD, "\n")
for (i in seq_len(nrow(resumen))) {
  r <- resumen[i, ]
  if (is.na(r$conv_partidas)) {
    cat(sprintf("%-8s no convergió (cortó por tope de %s, %d partidas, %.1f min)\n",
                r$run, r$tope, r$partidas, r$minutos))
  } else {
    cat(sprintf("%-8s convergió en la iteración %d, después de %d partidas\n",
                r$run, r$conv_iteracion, r$conv_partidas))
  }
}
