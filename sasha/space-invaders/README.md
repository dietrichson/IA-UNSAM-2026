# Space Invaders — grilla discreta con API para aprendizaje por refuerzo

Un Space Invaders mínimo, pensado como material de clase para el Seminario de
Inteligencia Artificial (UNSAM). Sirve para dos cosas:

1. Leer código: son cuatro archivos cortos, sin frameworks ni dependencias.
2. Entrenar un agente: el juego expone una API interna (`window.game`) con la
   forma clásica `reset` / `step` / estado / recompensa, la misma de Gym.

## Cómo abrirlo y jugar

Hacer doble clic en `index.html`. No hace falta instalar nada ni levantar un
servidor: el juego usa `<script>` comunes y funciona abriendo el archivo
directamente desde el disco (`file://`).

- `←` y `→` mueven la nave una celda.
- `espacio` dispara (una bala por vez).
- El botón **Nueva partida** empieza otro episodio.

## Los archivos

| Archivo      | Qué hace |
|--------------|----------|
| `index.html` | La página: el canvas, la línea de estado y el botón. |
| `game.js`    | La lógica del juego. Pura: sin pantalla, sin teclado, sin relojes. **Es el archivo para leer en clase.** |
| `ui.js`      | Dibuja en el canvas, escucha el teclado, corre el bucle en tiempo real y arma `window.game`. |
| `style.css`  | Estética retro: fondo negro, monoespaciada, verde y blanco. |
| `test.js`    | Tests de `game.js`. Se corren con `node --test test.js`. |

## Reglas del juego

El mundo es una grilla de **20 columnas x 15 filas**. Todo ocupa celdas enteras;
el canvas simplemente agranda cada celda a 24 píxeles.

- La **nave** es una celda en la fila 14 (la de abajo) y se mueve una celda por tick.
- Los **aliens** son un bloque de 3 filas x 8 columnas, separados por una celda
  vacía entre columna y columna. El bloque entero se corre una celda al costado
  cada `alienSpeed` ticks (4 por defecto); cuando tocaría el borde, en vez de
  moverse al costado baja una fila y cambia de sentido.
- La **bala** sube una celda por tick. Si llega a la celda de un alien, los dos
  desaparecen. Puntos según la fila del alien: 30 la de arriba, 20 la del medio,
  10 la de abajo.
- Las **bombas**: cada tick, con probabilidad `bombChance` (0.02 por defecto),
  el alien vivo más bajo de una columna elegida al azar tira una bomba, que baja
  una celda por tick. Si una bomba llega a la nave, se pierde una vida.
- Se empieza con **3 vidas**. La partida termina si se quedan en 0, o si algún
  alien llega a la fila de la nave.
- Si se eliminan todos los aliens, la partida termina con `won: true` y un bonus
  de 100 puntos.

Toda la aleatoriedad pasa por un generador con semilla (mulberry32). Con la
misma semilla, la partida se repite exactamente igual.

## La API interna

Está en `window.game`, o simplemente `game` en la consola del navegador.

```js
game.reset(options)   // options: { seed?, alienSpeed?, bombChance? }
                      // arranca un episodio nuevo, pausa el bucle y devuelve el estado
game.step(action)     // avanza exactamente UN tick; devuelve { state, reward, done }
game.getState()       // el estado actual, como copia nueva serializable a JSON
game.getScore()       // el puntaje actual (número)
game.getActions()     // siempre [0, 1, 2, 3]
game.render()         // vuelve a dibujar el canvas con el estado actual
game.play()           // arranca el bucle en tiempo real para jugar con el teclado (~10 ticks/seg)
game.pause()          // frena el bucle (step() sigue funcionando en pausa)
```

Cada `step()` y cada `reset()` redibujan el canvas, así que se puede mirar al
agente jugando.

### Opciones de `reset()`

| Opción       | Por defecto | Qué controla |
|--------------|-------------|--------------|
| `seed`       | `1`         | Semilla del generador aleatorio. Misma semilla = misma partida. |
| `alienSpeed` | `4`         | Cada cuántos ticks se mueve el bloque de aliens. Más chico = más rápido. |
| `bombChance` | `0.02`      | Probabilidad, en cada tick, de que caiga una bomba nueva. |

Ojo: el botón **Nueva partida** usa una semilla al azar (para que la persona no
juegue siempre la misma partida). `game.reset()` sin argumentos usa siempre la
semilla 1, que es lo que conviene para entrenar y comparar.

### Acciones

| Valor | Significado |
|-------|-------------|
| `0`   | no hacer nada |
| `1`   | mover a la izquierda |
| `2`   | mover a la derecha |
| `3`   | disparar (se ignora si ya hay una bala en el aire) |

### El estado

```js
{
  width: 20, height: 15, tick: 0,
  player: { x: 10 },
  aliens: [ { x, y, row, alive }, ... ],
  bullet: null | { x, y },
  bombs: [ { x, y }, ... ],
  score: 0, lives: 3, done: false, won: false,
  grid: [ [ ... ], ... ]
}
```

Campo por campo:

| Campo    | Significado |
|----------|-------------|
| `width`  | Columnas de la grilla. Siempre 20. |
| `height` | Filas de la grilla. Siempre 15. |
| `tick`   | Cuántos ticks pasaron desde el `reset()`. Empieza en 0. |
| `player.x` | Columna de la nave, de 0 a 19. La fila es siempre 14. |
| `aliens` | Los 24 aliens, vivos y muertos, siempre en el mismo orden. `x` e `y` son la celda; `row` es 0, 1 o 2 (de arriba hacia abajo) y define el puntaje; `alive` dice si sigue en juego. |
| `bullet` | `null` si no hay bala en el aire, o `{ x, y }` con su celda. |
| `bombs`  | Lista de bombas en el aire, cada una con su celda `{ x, y }`. Puede estar vacía. |
| `score`  | Puntaje acumulado del episodio, con el bonus de victoria incluido. |
| `lives`  | Vidas que quedan: 3, 2, 1 o 0. |
| `done`   | `true` cuando el episodio terminó, por victoria o por derrota. |
| `won`    | `true` solo si terminó por haber eliminado a todos los aliens. |
| `grid`   | Matriz de 15 filas x 20 columnas con enteros chicos (ver abajo). |

`grid` se calcula de nuevo cada vez que se lee el estado, a partir de los otros
campos. Es la observación compacta: se le puede pasar a un modelo sin tener que
recorrer listas. Se lee como `grid[fila][columna]`, es decir `grid[y][x]`.

| Valor | Celda |
|-------|-------|
| `0`   | vacía |
| `1`   | alien vivo |
| `2`   | nave |
| `3`   | bala de la nave |
| `4`   | bomba |

Si dos cosas caen en la misma celda, el que manda es el número más alto (se
pintan en orden: aliens, nave, bala, bombas).

### Las recompensas

`step()` devuelve en `reward` la suma de lo que pasó en ese tick:

| Situación | Recompensa |
|-----------|-----------|
| No pasó nada | `0` |
| La bala eliminó un alien de la fila de abajo | `+10` |
| ... de la fila del medio | `+20` |
| ... de la fila de arriba | `+30` |
| Se eliminaron todos los aliens (bonus de victoria) | `+100` |
| Una bomba le pegó a la nave (una vida menos) | `-50` |
| Se perdió la partida: se acabaron las vidas, o un alien llegó abajo | `-100` |

Las recompensas se suman entre sí. Perder la última vida da `-50 - 100 = -150`.
Eliminar al último alien de la fila de abajo da `+10 + 100 = +110`.

Llamar a `step()` cuando `done` ya es `true` devuelve el estado sin cambios y
recompensa `0`.

## Un agente al azar, para copiar y pegar en la consola

Abrir la consola del navegador (F12, pestaña *Console*) y pegar esto:

```js
game.reset({ seed: 42 });

let recompensaTotal = 0;
const bucle = setInterval(() => {
  const acciones = game.getActions();
  const accion = acciones[Math.floor(Math.random() * acciones.length)];
  const { state, reward, done } = game.step(accion);
  recompensaTotal += reward;
  if (done) {
    clearInterval(bucle);
    console.log('Fin del episodio en el tick', state.tick);
    console.log('Puntos:', state.score, '| Recompensa total:', recompensaTotal);
    console.log('¿Ganó?', state.won);
  }
}, 100);
```

El `setInterval` es solo para poder mirarlo. Para correr muchos episodios rápido
conviene un bucle sin pausas:

```js
function episodioAlAzar(semilla) {
  let s = game.reset({ seed: semilla });
  let total = 0;
  while (!s.done && s.tick < 2000) {
    const r = game.step(Math.floor(Math.random() * 4));
    total += r.reward;
    s = r.state;
  }
  return { puntos: s.score, recompensa: total, ganó: s.won, ticks: s.tick };
}

// 20 episodios con semillas distintas
for (let i = 0; i < 20; i++) console.log(i, episodioAlAzar(i));
```

Para volver a jugar con el teclado después de todo esto: `game.play()`.

## Los tests

```
node --test test.js
```

Usan `node:test` y `node:assert`, que vienen con Node: no hay que instalar nada.
Prueban `game.js` directamente, sin navegador.
