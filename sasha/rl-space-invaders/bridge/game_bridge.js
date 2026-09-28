/*
 * game_bridge.js — Puente entre Python y el juego.
 *
 * Corre la lógica de sasha/space-invaders/game.js dentro de Node y habla por
 * las tuberías estándar: una línea JSON de entrada, una línea JSON de salida.
 *
 *   entrada:  {"cmd":"reset","seed":1}   o   {"cmd":"step","action":2}
 *   salida:   {"state":{...},"reward":0,"done":false}
 *
 * Es la misma game.js que usa el navegador, así que el agente entrena contra
 * el juego real y no contra una copia.
 */

const readline = require('readline');
const SpaceInvaders = require('../../space-invaders/game.js');

const game = SpaceInvaders.createGame();
const rl = readline.createInterface({ input: process.stdin });

rl.on('line', function (line) {
  const cmd = JSON.parse(line);
  let out;
  if (cmd.cmd === 'reset') {
    // reset() devuelve el estado inicial; no hay recompensa todavía.
    out = { state: game.reset({ seed: cmd.seed }), reward: 0, done: false };
  } else {
    out = game.step(cmd.action);
  }
  process.stdout.write(JSON.stringify(out) + '\n');
});
