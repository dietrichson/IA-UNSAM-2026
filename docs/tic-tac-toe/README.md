# Ta-te-ti

Un ta-te-ti (tic-tac-toe) que corre en el navegador, sin instalar nada y sin
conexión a internet. Se juega con el mouse, pero además expone una API interna
pensada para la clase de **aprendizaje por refuerzo**: un agente escrito en la
consola del navegador puede jugar partidas contra el tablero y ver los
resultados en pantalla.

## Cómo abrirlo

Hacé doble clic en `index.html`. Se abre en el navegador y listo. No hace falta
servidor, ni Node, ni instalar paquetes.

## Cómo jugar

- **Tamaño**: 3x3, 4x4 o 5x5. Hay que alinear tantas marcas como el lado del
  tablero (3 en el 3x3, 5 en el 5x5).
- **Oponente**: *Humano* (dos personas se turnan en la misma computadora) o
  *Aleatorio* (la computadora juega con O eligiendo una celda libre al azar).
- **Nueva partida**: reinicia el tablero. Cambiar el tamaño o el oponente
  también empieza una partida nueva.
- X siempre juega primero. El marcador de abajo acumula resultados desde que se
  abrió la página.

## Los archivos

| Archivo | Qué hace |
|---|---|
| `index.html` | La página: tablero, controles y estado. |
| `game.js` | Las reglas del juego. No toca la pantalla. **Este es el archivo para leer.** |
| `ui.js` | Dibuja el tablero, escucha los clics y publica `window.game`. |
| `style.css` | Los estilos. |
| `test.js` | Pruebas de `game.js`. Se corren con `node --test test.js`. |

## La API interna

Abrí la consola del navegador (F12, o Cmd+Opción+J en Mac) y usá el objeto
`game`. Todo lo que hagas por la API se ve en pantalla al instante.

### `game.reset(opciones)`

Empieza una partida nueva y devuelve el estado.

```js
game.reset({ size: 3 });                          // 3x3, oponente aleatorio
game.reset({ size: 5, winLength: 4 });            // 5x5, gana quien alinee 4
game.reset({ size: 3, opponent: 'none' });        // nadie responde: autojuego
```

- `size`: `3`, `4` o `5`. Si no se aclara, mantiene el tamaño actual.
- `winLength`: cuántas marcas seguidas hacen falta para ganar. Por defecto es
  igual a `size`.
- `opponent`: `'human'`, `'random'` o `'none'`. **Por API el valor por defecto es
  `'random'`**, aunque la página arranque en modo *Humano*.
  - `'human'`: nadie responde automáticamente; los turnos alternan entre X y O.
  - `'random'`: después de la jugada de X, O responde solo con una celda al azar.
  - `'none'`: igual que `'human'`, pero pensado para el autojuego desde código.

### `game.step(accion)`

`accion` es el número de celda (de `0` a `size * size - 1`) para el jugador que
tiene el turno. Devuelve:

```js
{ state, reward, done, illegal }
```

- `reward` está **siempre desde el punto de vista de X**: `+1` si gana X, `-1` si
  gana O, `0` en cualquier otro caso (incluido el empate).
- Con `opponent: 'random'`, `step()` pone la marca de X y, si la partida sigue,
  juega enseguida la respuesta de O. Por eso quien llama sólo ve estados donde
  es el turno de X, o partidas terminadas.
- Una jugada inválida (celda ocupada, número fuera de rango, o partida ya
  terminada) devuelve `reward: -1` e `illegal: true`, y **no cambia el tablero**.

### `game.getState()`

Devuelve una copia nueva del estado actual. Es un objeto de JSON puro, así que se
puede guardar o serializar sin problemas.

```js
{
  size: 3,
  winLength: 3,
  board: [0,0,0, 0,0,0, 0,0,0],  // fila por fila; 0 vacía, 1 = X, 2 = O
  player: 1,                     // de quién es el turno (1 o 2)
  winner: 0,                     // 0 nadie todavía, 1 X, 2 O, 3 empate
  done: false,
  winningLine: null              // las celdas de la línea ganadora, si la hay
}
```

El tablero es una lista **plana**. La celda de la fila `f` y la columna `c` está
en la posición `f * size + c`.

### `game.getActions()`

Devuelve la lista de celdas libres. Si la partida terminó, devuelve `[]`.

### `game.getScore()`

Devuelve `{ x, o, draws }`: partidas ganadas por cada uno y empates acumulados
desde que se abrió la página.

### `game.render()`

Vuelve a dibujar el tablero a partir del estado actual. `reset()` y `step()` ya
lo hacen solos; está para cuando lo necesites a mano.

## Ejemplo: un agente que juega al azar

Copiá esto en la consola del navegador y apretá Enter. Juega 100 partidas contra
el oponente aleatorio y muestra el resultado.

```js
function agenteAlAzar(partidas) {
  for (let i = 0; i < partidas; i++) {
    let estado = game.reset({ size: 3, opponent: 'random' });

    while (!estado.done) {
      const acciones = game.getActions();
      const accion = acciones[Math.floor(Math.random() * acciones.length)];
      const paso = game.step(accion);
      estado = paso.state;
    }
  }
  console.log(game.getScore());
}

agenteAlAzar(100);
```

Como X y O eligen al azar, X gana bastante más seguido: la ventaja es jugar
primero. Ese número es la línea de base a superar con un agente que aprenda.

Para ver las partidas una por una en la pantalla, conviene espaciarlas en el
tiempo:

```js
let quedan = 20;
const reloj = setInterval(() => {
  const acciones = game.getActions();
  if (acciones.length === 0) {
    if (--quedan === 0) return clearInterval(reloj);
    return game.reset({ size: 3, opponent: 'random' });
  }
  game.step(acciones[Math.floor(Math.random() * acciones.length)]);
}, 300);
```

## Las pruebas

`game.js` se puede probar fuera del navegador porque no toca la pantalla. Desde
esta carpeta:

```
node --test test.js
```

Cubren las victorias en fila, columna, diagonal y antidiagonal en los tres
tamaños, el `winLength` más chico que el tablero, el empate, las jugadas
inválidas y el oponente aleatorio.
