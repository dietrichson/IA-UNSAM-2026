# Ta-te-ti con API para aprendizaje por refuerzo

## Descripción

Este proyecto implementa un juego de Ta-te-ti en JavaScript pensado para ser utilizado tanto desde una interfaz web como desde un agente de aprendizaje por refuerzo.

El proyecto utiliza HTML, CSS y JavaScript sin frameworks ni dependencias externas. La lógica principal del juego se encuentra separada de la interfaz para permitir su ejecución y prueba de manera independiente.

El tablero admite tamaños de 3×3, 4×4 y 5×5, con una cantidad configurable de símbolos necesarios para ganar.

## Archivos

* `index.html`: interfaz gráfica del juego.
* `game.js`: motor y lógica pura del juego.
* `ui.js`: integración con el navegador, tablero, controles y visualización.
* `test.js`: pruebas automáticas del motor utilizando el runner incorporado de Node.js.
* `README.md`: documentación del proyecto.

## Arquitectura

La aplicación se divide en dos partes principales:

### Motor del juego

`game.js` contiene la lógica del Ta-te-ti sin depender del DOM.

Esto permite que el motor pueda ser utilizado por un agente de aprendizaje por refuerzo sin necesidad de interactuar con elementos visuales.

El motor permite:

* crear partidas de distintos tamaños;
* determinar las acciones legales;
* ejecutar acciones;
* detectar victorias horizontales, verticales y diagonales;
* detectar empates;
* rechazar acciones inválidas;
* impedir acciones después de finalizar una partida;
* reiniciar el estado;
* consultar el puntaje acumulado.

### Interfaz

`ui.js` se encarga de conectar el motor con el navegador.

La interfaz permite:

* visualizar el tablero;
* seleccionar el tamaño;
* seleccionar la cantidad necesaria para ganar;
* jugar entre dos personas;
* jugar contra un oponente aleatorio;
* reiniciar la partida;
* visualizar el resultado;
* visualizar el puntaje acumulado.

La instancia del juego queda disponible mediante:

```javascript
window.game
```

Esto permite interactuar con la API desde la consola del navegador.

## API para el agente

La API principal está compuesta por cinco operaciones.

### `reset()`

Reinicia el tablero y devuelve el estado inicial de la partida.

```javascript
game.reset()
```

El puntaje acumulado no se reinicia.

### `step(action)`

Ejecuta una acción sobre una casilla.

Las acciones se representan mediante números enteros que corresponden al índice de la casilla.

Por ejemplo, en un tablero 5×5:

```text
0  1  2  3  4
5  6  7  8  9
10 11 12 13 14
15 16 17 18 19
20 21 22 23 24
```

Una llamada como:

```javascript
game.step(0)
```

intenta colocar el símbolo del jugador actual en la primera casilla.

La transición devuelve información sobre la acción, el jugador, su validez, la recompensa y si el episodio terminó.

### `getState()`

Devuelve el estado completo y serializable de la partida.

Incluye:

* `board`
* `size`
* `winLength`
* `currentPlayer`
* `gameOver`
* `winner`
* `result`

Ejemplo:

```javascript
game.getState()
```

### `getActions()`

Devuelve las acciones actualmente legales.

Por ejemplo, al comenzar una partida 5×5:

```javascript
game.getActions()
```

devuelve los índices de las 25 casillas disponibles.

Cuando la partida termina, devuelve:

```javascript
[]
```

### `getScore()`

Devuelve el puntaje acumulado de X y O.

```javascript
game.getScore()
```

El puntaje se mantiene entre partidas mientras la instancia del juego continúe activa.

## Contrato de recompensas

Se definió el contrato de recompensas antes de implementar y probar el motor.

| Situación                     | `reward` del jugador que ejecuta la acción | `opponentReward` | `done`  |
| ----------------------------- | -----------------------------------------: | ---------------: | ------- |
| Movimiento válido no terminal |                                          0 |                0 | `false` |
| Victoria                      |                                         +1 |               -1 | `true`  |
| Empate                        |                                          0 |                0 | `true`  |
| Acción inválida               |                                         -1 |                0 | `false` |
| Acción después del final      |                                         -1 |                0 | `true`  |

Las acciones inválidas pueden producirse, por ejemplo, cuando se intenta utilizar una casilla ocupada, una posición fuera del tablero o un valor que no corresponde a un índice entero válido.

## Pruebas automáticas

Las pruebas se ejecutan mediante el runner incorporado de Node.js:

```bash
node --test test.js
```

La suite contiene 20 pruebas.

Se verificaron:

1. estado inicial;
2. acciones legales iniciales;
3. movimiento válido;
4. acción no entera;
5. acción fuera de rango;
6. casilla ocupada;
7. victoria horizontal;
8. victoria vertical;
9. victoria diagonal descendente;
10. victoria diagonal ascendente;
11. empate;
12. acción después del final;
13. reinicio;
14. puntaje;
15. tablero 4×4;
16. victoria en 4×4;
17. tablero 5×5;
18. victoria en 5×5;
19. `winLength` configurable;
20. transición completa de `step()`.

Resultado obtenido:

```text
tests 20
pass 20
fail 0
cancelled 0
skipped 0
todo 0
```

## Verificación en navegador

La interfaz fue ejecutada en el navegador y se verificó el funcionamiento del juego.

También se utilizó la consola del navegador para comprobar la API mediante:

```javascript
game.getState()
game.getActions()
game.getScore()
game.reset()
game.step(0)
```

Se verificó además el comportamiento de una acción inválida intentando ejecutar nuevamente:

```javascript
game.step(0)
```

sobre una casilla que ya había sido ocupada.

El resultado indicó:

```text
valid: false
reason: "occupied"
```

confirmando que el motor rechaza correctamente la acción.

## Revisión de errores durante el desarrollo

Durante el desarrollo aparecieron algunos errores que fueron utilizados para revisar la separación entre archivos y el funcionamiento del proyecto.

Primero, `test.js` fue creado accidentalmente como un directorio en lugar de un archivo. Esto impedía utilizarlo como archivo de pruebas.

El problema se solucionó eliminando el directorio y creando nuevamente `test.js` como archivo.

También se produjo un error al colocar accidentalmente código de pruebas dentro de `game.js`. Esto provocó errores relacionados con la exportación de `createGame`.

La solución fue separar nuevamente las responsabilidades:

* `game.js`: únicamente lógica del juego.
* `test.js`: únicamente pruebas.
* `ui.js`: únicamente interacción con la interfaz.

Luego de realizar estas correcciones, la suite finalizó con 20 pruebas aprobadas y ninguna fallida.

## Flujo de interacción del agente

El flujo básico pensado para un agente de aprendizaje por refuerzo es:

```text
1. reset()
      ↓
2. getState()
      ↓
3. getActions()
      ↓
4. elegir una acción
      ↓
5. step(action)
      ↓
6. recibir nuevo estado + reward + done
      ↓
7. continuar mientras done = false
```

De esta manera, el agente puede interactuar con el entorno sin depender directamente de la interfaz gráfica.

## Limitaciones

El oponente aleatorio implementado en la interfaz selecciona una acción legal al azar y no constituye un agente de aprendizaje entrenado.

El proyecto proporciona la interfaz y el entorno necesarios para que posteriormente pueda conectarse un agente de aprendizaje por refuerzo.

No se utilizan frameworks ni dependencias externas.
