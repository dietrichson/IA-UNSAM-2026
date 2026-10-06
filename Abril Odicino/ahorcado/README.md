# Ahorcado

## Especificación

El programa es una versión mínima del juego Ahorcado. Al abrir `index.html` con doble clic, la persona usuaria ve una palabra oculta, un teclado de letras, un contador de errores y las letras fallidas. Puede elegir letras con el mouse o con el teclado. Gana cuando descubre todas las letras de la palabra y pierde al llegar a seis errores. La partida también termina en esos dos casos y el botón "Nueva palabra" inicia otra.

El agente debía producir `index.html`, `style.css`, `game.js`, `ui.js`, `game.test.js`, `package.json` y este `README.md`. La lógica debía estar separada de la interfaz: `game.js` no manipula el DOM y `ui.js` se encarga de mostrar el estado y recibir acciones. El programa no debía tener niveles, puntaje alto, sonido, imágenes externas, dependencias, servidor ni instalación. La interfaz debía ser mínima y funcionar al abrir el archivo HTML localmente.

Para verificarlo, los tests debían comprobar que una partida nueva oculta la palabra, que una letra correcta se revela, que una incorrecta suma un error sin duplicarse, que se puede ganar y que se puede perder. Además, `getState()` debía devolver un objeto con el estado visible de la partida para poder inspeccionarla.

## Prompt textual enviado al agente

```text
Construí un juego de Ahorcado mínimo dentro de la carpeta Abril Odicino/ahorcado/.

Debe funcionar por completo al abrir index.html con doble clic, sin servidor, sin instalar nada y sin dependencias externas. Usá HTML, CSS y JavaScript modular. Separá la lógica pura en game.js y la interfaz del navegador en ui.js. La lógica no debe manipular el DOM.

Reglas: el juego usa una palabra elegida de una lista corta. La persona puede elegir letras con botones o teclado. Gana al descubrir todas las letras y pierde al llegar a seis errores. Las letras repetidas no deben sumar errores. Exponé una función getState() que devuelva un objeto con el estado visible de la partida.

La interfaz debe ser mínima y retro. No agregues niveles, puntaje alto, sonido, imágenes externas, explicaciones largas ni funciones que no se pidieron.

Creá index.html, style.css, game.js, ui.js, game.test.js, package.json y README.md. Escribí los comentarios y el README en español. Agregá tests con node --test para una partida nueva, aciertos, errores sin duplicados, victoria y derrota.

Al terminar, corré node --test, verificá que pase todo y mostrá la salida cruda en el README antes de finalizar.
```

## Salida de `node --test`

```text
✔ una partida nueva oculta todas las letras (1.0185ms)
✔ una letra correcta se revela sin sumar errores (1.2023ms)
✔ una letra incorrecta suma un solo error y no se repite (0.2413ms)
✔ la partida termina al encontrar todas las letras (0.2109ms)
✔ la partida termina al llegar al máximo de errores (0.1661ms)
ℹ tests 5
ℹ suites 0
ℹ pass 5
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 106.0935
```

## Verificación manual

Abrí `index.html` con doble clic. Verificá que se pueda seleccionar una letra con el mouse y con el teclado, que las letras usadas queden deshabilitadas, que el contador aumente solo con errores y que "Nueva palabra" reinicie la partida.

Resultado: se probó la partida en el navegador. Las letras se pueden elegir con mouse y teclado, los errores se cuentan correctamente y el botón “Nueva palabra” reinicia el juego. No se observaron fallas.

## Reflexión

La parte más difícil del pedido fue decidir qué dejar afuera. Ahorcado puede crecer con categorías, dibujos complejos, pistas y puntajes, pero esas funciones no mejoraban el objetivo del laboratorio. El pedido funcionó porque dejó claras las reglas, los archivos esperados y la forma de verificarlo. Si tuviera que enviarlo de nuevo, aclararía además que la lista de palabras debe mantenerse pequeña y sin caracteres especiales para que las pruebas sean más directas.
El agente no agregó funciones ajenas al pedido, como niveles, puntajes, sonidos o imágenes externas. Tampoco dejó sin implementar ninguna de las funciones solicitadas: el juego funciona, la lógica está separada de la interfaz y los cinco tests pasan correctamente.
