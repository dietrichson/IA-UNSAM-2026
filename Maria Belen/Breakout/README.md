# Breakout retro

Videojuego web 2D tipo Breakout, con estética retro y minimalista. Está hecho con HTML, CSS y JavaScript puro: no necesita instalar nada, ni servidor, ni dependencias.

## Cómo jugar

1. Abrí `index.html` con doble clic. Funciona directamente desde el protocolo `file://`.
2. Mové la paleta y lanzá la pelota.
3. Destruí los 78 ladrillos sin quedarte sin vidas.

### Controles

| Acción            | Cómo                                              |
| ----------------- | ------------------------------------------------- |
| Mover la paleta   | Mouse, flechas izquierda/derecha, o teclas `A`/`D` |
| Lanzar la pelota  | Barra espaciadora, flecha arriba o clic/toque      |

La paleta solo se mueve en **horizontal**. En pantallas táctiles alcanza con arrastrar el dedo sobre el juego.

## Reglas

- **Área de juego:** un marco visible limita la pantalla. La pelota rebota en las paredes izquierda, derecha y superior.
- **Ladrillos:** 78 ladrillos en 13 columnas por 6 filas. Cada choque destruye el ladrillo impactado. Los colores por fila, de arriba hacia abajo, son: rojo, naranja, amarillo, verde, azul y violeta.
- **Vidas:** se empieza con 3, mostradas como corazones en la parte superior. Se pierde una vida cada vez que la pelota toca el límite inferior del marco. Después de perder una vida, la pelota vuelve a la paleta y hay que lanzarla de nuevo.
- **Derrota:** al llegar a 0 vidas aparece el cartel `Perdiste :(` con el botón `Quiero revancha`, que reinicia el juego de inmediato con 3 vidas y 78 ladrillos nuevos.
- **Victoria:** al destruir los 78 ladrillos aparece el cartel `Ganaste :)` con el botón `Voy por más`, que inicia una nueva partida.
- **Sin extras:** no hay sonido, ni música, ni niveles, ni dificultad creciente. La velocidad de la pelota es siempre la misma.

## Estructura del proyecto

```
index.html   Estructura de la aplicación
style.css    Estilos y estética retro
game.js      Reglas del juego y lógica de dominio (sin dependencias del navegador)
ui.js        Renderizado en Canvas, entradas del usuario y sincronización con game.js
test.js      Pruebas unitarias para Node.js
README.md    Esta documentación
```

## Arquitectura

El proyecto separa a propósito las reglas del juego de su presentación.

### `game.js`: lógica de dominio

Contiene la clase `Juego`, que guarda todo el estado (vidas, ladrillos, paleta, pelota y estado de la partida) y aplica las reglas: movimiento, rebotes, destrucción de ladrillos, pérdida de vidas, victoria, derrota y reinicio.

- **No usa** `document`, `window` ni `HTMLCanvasElement`, por lo que se puede ejecutar y probar en Node.js.
- Se carga con una etiqueta `<script>` común. En el navegador expone un único objeto global, `Breakout`. En Node.js se exporta con `module.exports`.
- Los ladrillos activos viven en un `Map`: destruir un ladrillo es eliminarlo del mapa, y el juego se gana cuando el mapa queda vacío.
- Los estados posibles son `esperando`, `jugando`, `derrota` y `victoria`.
- La simulación avanza en sub-pasos cortos para que la pelota nunca atraviese un ladrillo ni la paleta, aunque el cuadro de animación sea largo.
- Los textos de los carteles y botones (`Perdiste :(`, `Quiero revancha`, `Ganaste :)`, `Voy por más`) están definidos aquí, no en la interfaz.

API principal de `Juego`:

| Miembro                     | Descripción                                                        |
| --------------------------- | ------------------------------------------------------------------ |
| `vidas`                     | Vidas restantes                                                    |
| `ladrillos`                 | `Map` de ladrillos activos                                         |
| `estado`                    | `esperando`, `jugando`, `derrota` o `victoria`                     |
| `finalizado`                | `true` si la partida terminó                                       |
| `mensaje` / `textoBoton`    | Textos del cartel de fin de partida (`null` si la partida sigue)   |
| `lanzar()`                  | Lanza la pelota desde la paleta                                    |
| `colocarPaleta(centroX)`    | Centra la paleta en una posición X (limitada al marco)             |
| `moverPaleta(direccion, dt)`| Mueve la paleta en horizontal a velocidad fija                     |
| `actualizar(dt)`            | Avanza la simulación `dt` segundos                                 |
| `destruirLadrillo(id)`      | Elimina un ladrillo y detecta la victoria                          |
| `perderVida()`              | Resta una vida y detecta la derrota                                |
| `reiniciar()`               | Vuelve a 3 vidas, 78 ladrillos y limpia los carteles               |

### `ui.js`: interfaz

Dibuja el juego en el `<canvas>`, muestra un corazón por cada vida, lee teclado, mouse y toque, y muestra el cartel de fin de partida. Ejecuta el bucle de animación (`requestAnimationFrame`) que llama a `actualizar` en cada cuadro. No contiene reglas de juego.

## Pruebas automatizadas

Las pruebas usan el test runner nativo de Node.js (`node:test` y `node:assert`), sin instalar nada. Hace falta Node.js 18 o superior.

```bash
node --test test.js
```

Cubren:

1. **Estado inicial:** 3 vidas, 78 ladrillos activos y partida no finalizada.
2. **Pérdida de vidas y derrota:** la pelota que toca el fondo resta una vida, y al llegar a 0 el estado pasa a derrota (`Perdiste :(`).
3. **Destrucción de ladrillos:** la colisión con un ladrillo lo elimina del mapa de ladrillos activos.
4. **Condición de victoria:** al eliminar el ladrillo número 78 el estado pasa a victoria (`Ganaste :)`).
5. **Reinicio:** `reiniciar()` restablece 3 vidas y 78 ladrillos, y limpia los carteles de victoria y derrota.

## Decisiones de diseño

- **Pelota cuadrada:** encaja con la estética retro y simplifica las colisiones, que se calculan entre rectángulos.
- **Ángulo de rebote en la paleta:** depende del punto de impacto. En el centro la pelota sale casi vertical, y en los bordes sale más inclinada (hasta 60 grados).
- **Lanzamiento con ángulo aleatorio:** la pelota nunca sale en vertical exacta, para evitar rebotes repetitivos. El generador de azar se puede inyectar (`new Juego({ aleatorio })`), lo que hace las pruebas deterministas.
- **Sin dependencias ni fuentes externas:** todo funciona sin conexión a internet.

# Brief
Crea un videojuego tipo Breakout usando vibecoding. El gameplay consiste en controlar una paleta horizontal para rebotar una pelota y destruir los ladrillos que se encuentran en la parte superior de la pantalla. Los ladrillos son 78 y están distribuidos en 13 filas de 6 ladrillos cada una. La pelota rebota en las paredes (un marco rectilíneo que limita el área de juego), en la paleta y en los ladrillos. Cada vez que la pelota golpea un ladrillo, este desaparece. El jugador ve en pantalla el marco rectilíneo que limita el área de juego, los ladrillos, la paleta y la pelota pero solo puede mover la paleta y este movimiento solo puede en sentido horizontal, NUNCA vertical. El jugador gana cuando logra eliminar todos los ladrillos. El jugador posee tres vidas en cada partida. El jugador pierde una vida cada vez que la pelota toca el límite inferior de la pantalla. Cuando se agotan las tres vidas, el jugador pierde el juego y la partida termina. Cuando el jugador pierda debe aparecer un cartel que diga “Perdiste :(“ y un botón debajo del cartel que diga “Quiero revancha”. Cuando el jugador aprieta el botón “Quiero revancha”, se inicia una nueva partida. Cuando el jugador gana, la partida termina. Cuando el jugador gane debe aparecer un cartel que diga “Ganaste :)“ y un botón debajo del cartel que diga “Voy por más”. Cuando el jugador aprieta el botón “Voy por más”, se inicia una nueva partida. El videojuego NO debe tener sonido, NO debe tener niveles y se debe indicar la cantidad de vidas que tiene el jugador en la parte superior de la pantalla a través de corazones (cada corazón representa una vida). La estetica debe ser retro, con graficos minimalistas y los ladrillos deben tener los colores de la bandera LGTB (en orden horizontal de arriba hacia abajo, las hileras deben ser de color rojo, naranja, amarillo, verde, azul y violeta respectivamente). El juego debe correr de forma íntegra en el navegador, abriendo un index.html con doble click. NO usar módulos ES (type="module"): Todo el código JavaScript en index.html debe cargarse mediante etiquetas <script> tradicionales para permitir la ejecución directa haciendo doble clic sobre el archivo mediante el protocolo file://.  El agente debe generar un videojuego con un código chico y modular: la lógica separada de la interfaz, los  archivos que debe generar son:
1. `index.html` - estructura principal de la aplicación
2. ‘game.js’ - las reglas del juego.
3. style.css - los estilos
4. ui.js: Control de rendering en HTML/Canvas, manejo de inputs del usuario y sincronización con la lógica de game.js.
5. `test.js`    — tests of `game.js` runnable with `node --test test.js`
6. `README.md` en español
## NO se deben generar archivos por fuera de los mencionados. Antes de terminar, run node --test, corregi todos los errores y verifica que pasa todos los test. Verifica que TODOS los archivos mencionados arriba están presentes. El correcto funcionamiento se valida verificando que la aplicación abra sin errores en cualquier navegador web actual de manera offline. Además, la lógica central de juego (game.js) debe contar con una suite de pruebas automatizadas ejecutable mediante el comando node --test test.js (o dentro de un archivo de pruebas equivalente para Node.js). Los tests deben comprobar al 100%:
1. El estado inicial (3 vidas, 78 ladrillos restantes).
2. La resta de vidas al caer la pelota al fondo y el cambio al estado de derrota al llegar a 0 vidas.
3. La eliminación de un ladrillo tras una colisión.
4. La detección de la condición de victoria al eliminar todos los ladrillos.
5. El correcto reinicio del estado al solicitar una nueva partida.

# PROMPT PARA EL AGENTE DE CÓDIGO (VIBECODING)
Actúa como un desarrollador de software experto. Tu tarea es construir un videojuego web 2D tipo Breakout con estética retro y minimalista, siguiendo estrictamente la arquitectura, reglas y restricciones especificadas a continuación.
---
## 1. Archivos Requeridos
Debes generar ÚNICAMENTE los siguientes 6 archivos en la raíz del proyecto. NO crees ningún otro archivo ni carpeta adicional:
1. `index.html`: Estructura principal de la aplicación.
2. `style.css`: Estilos de la aplicación y la estética retro.
3. `game.js`: Reglas del juego y lógica de dominio pura (independiente del renderizado).
4. `ui.js`: Control de rendering (Canvas/HTML), manejo de eventos/inputs y sincronización con `game.js`.
5. `test.js`: Suite de pruebas unitarias ejecutables en Node.js mediante el test runner nativo (`node --test test.js`).
6. `README.md`: Documentación completa del proyecto explicada en español.

---

## 2. Especificación Técnica y Gameplay

### Reglas del Juego y Mecánicas
* **Área de juego:** Definida por un marco rectilíneo visible que limita los bordes de la pantalla.
* **Ladrillos:** Exactamente 78 ladrillos dispuestos en 13 columnas por 6 filas.
  * Cada choque con la pelota destruye el ladrillo impactado (desaparece).
  * Colores por fila (de arriba hacia abajo, siguiendo la bandera LGBT):
    * Fila 1 (superior): Rojo
    * Fila 2: Naranja
    * Fila 3: Amarillo
    * Fila 4: Verde
    * Fila 5: Azul
    * Fila 6 (inferior): Violeta
* **Paleta:** Ubicada en la zona inferior. El jugador solo puede moverla en sentido **horizontal** (nunca vertical ni diagonal).
* **Pelota:** Rebota en las paredes del marco (superior, izquierda y derecha), en la paleta y en los ladrillos.
* **Sistema de Vidas:**
  * El jugador inicia con **3 vidas**.
  * Se representa gráficamente en la parte superior de la pantalla mediante **corazones** (un corazón por vida).
  * Se pierde 1 vida cada vez que la pelota toca el límite inferior del marco.
* **Condición de Derrota:**
  * Al llegar a 0 vidas, la partida termina.
  * Debe desplegarse un cartel/modal que diga exactamente: `Perdiste :(`
  * Debajo del cartel debe incluirse un botón con el texto exacto: `Quiero revancha`
  * Al presionar `Quiero revancha`, el juego se reinicia de inmediato con 3 vidas y 78 ladrillos nuevos.
* **Condición de Victoria:**
  * Al destruir los 78 ladrillos, la partida termina.
  * Debe desplegarse un cartel/modal que diga exactamente: `Ganaste :)`
  * Debajo del cartel debe incluirse un botón con el texto exacto: `Voy por más`
  * Al presionar `Voy por más`, se inicia una nueva partida.

### Restricciones Estrictas (LO QUE NO DEBES HACER)
* **NO usar efectos de sonido ni música de fondo.**
* **NO incluir múltiples niveles ni incremento de dificultad.**
* **NO usar módulos ES (`type="module"`)**: El juego debe poder abrirse directamente en el navegador con un doble clic sobre `index.html` utilizando el protocolo `file://`. Carga los scripts con etiquetas `<script>` tradicionales (ej. `<script src="game.js"></script>`).
* **NO mezclar la lógica de juego con el renderizado**: `game.js` debe ser 100% agnóstico a la interfaz para poder ser testeado en Node.js sin navegador (sin depender de `document`, `window` ni `HTMLCanvasElement`).

---

## 3. Idioma y Estilo de Código
* **Comentarios y Documentación:** Todos los comentarios dentro del código fuente y el archivo `README.md` deben redactarse íntegramente en **español**.
* **Diseño:** Estética retro, gráficos minimalistas y paleta de colores limpia.

---

## 4. Requisitos de Pruebas Automatizadas (`test.js`)

El archivo `test.js` debe probar la lógica contenida en `game.js` utilizando la librería nativa de tests de Node.js (`node:test` y `node:assert`). Debe cubrir al 100% los siguientes puntos:

1. **Estado inicial:** Verifica que la partida arranque con 3 vidas, los 78 ladrillos activos y estado no finalizado.
2. **Pérdida de vidas y derrota:** Verifica que la pelota al tocar el fondo reste 1 vida y que, al llegar a 0 vidas, el juego cambie al estado de derrota (`Perdiste :(`).
3. **Destrucción de ladrillos:** Verifica que la colisión con un ladrillo lo elimine del mapa de ladrillos activos.
4. **Condición de victoria:** Verifica que al eliminar el ladrillo número 78 el juego cambie al estado de victoria (`Ganaste :)`).
5. **Reinicio del juego:** Verifica que llamar a la función de reinicio vuelva a establecer las 3 vidas, los 78 ladrillos y limpie las pantallas de victoria/derrota.

---

## 5. Instrucciones de Ejecución y Cláusula de Cierre

Antes de dar por finalizado el trabajo, debes seguir obligatoriamente los siguientes pasos:

1. Escribe todo el código de los 6 archivos solicitados (`index.html`, `style.css`, `game.js`, `ui.js`, `test.js`, `README.md`).
2. Ejecuta en la terminal el comando:
   ```bash
   node --test test.js
# Salida del test
▶ Estado inicial
  ✔ arranca con 3 vidas (4.541547ms)
  ✔ arranca con los 78 ladrillos activos (13 columnas x 6 filas) (0.398752ms)
  ✔ asigna a cada fila su color: rojo, naranja, amarillo, verde, azul y violeta (0.267105ms)
  ✔ arranca sin haber finalizado y sin mensaje de fin de partida (0.307311ms)
✔ Estado inicial (8.311441ms)
▶ Pérdida de vidas y derrota
  ✔ resta una vida cuando la pelota toca el límite inferior (0.79006ms)
  ✔ al llegar a 0 vidas el juego pasa al estado de derrota (Perdiste :() (0.352115ms)
  ✔ con la partida terminada la pelota ya no se mueve ni se restan más vidas (0.319163ms)
✔ Pérdida de vidas y derrota (1.857854ms)
▶ Destrucción de ladrillos
  ✔ la colisión con un ladrillo lo elimina del mapa de ladrillos activos (0.772049ms)
  ✔ la pelota rebota (invierte su sentido vertical) al chocar con un ladrillo (0.335278ms)
  ✔ cada choque destruye únicamente el ladrillo impactado (0.473239ms)
✔ Destrucción de ladrillos (4.132731ms)
▶ Condición de victoria
  ✔ al eliminar el ladrillo número 78 el juego pasa al estado de victoria (Ganaste :)) (1.527722ms)
  ✔ destruir un ladrillo que ya no existe no cambia nada (0.257217ms)
✔ Condición de victoria (1.941856ms)
▶ Reinicio del juego
  ✔ después de una derrota restablece 3 vidas, 78 ladrillos y limpia el cartel (0.393807ms)
  ✔ después de una victoria restablece 3 vidas, 78 ladrillos y limpia el cartel (0.380537ms)
  ✔ tras reiniciar se puede volver a jugar con normalidad (0.225237ms)
✔ Reinicio del juego (1.424695ms)
ℹ tests 15
ℹ suites 5
ℹ pass 15
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 278.17875

# Notas sobre el proceso
El agente hizo exactamente lo que le pedí, no generó archivos extras ni le faltó crear otros. En lo que respecta a la estética del juego, Claude tomó decisiones respecto a los colores, ya que solo explicite en el prompt el de los ladrillos, y la tipografía basándose en la premisa general de juego retro con estilo minimalista. A diferencia del juego que Thiago creó en clase, no tuve problemas con las decisiones tomadas por el agente y considero que el programa tiene un aspecto agradable. Respecto al gameplay, el videojuego corre correctamente. Se puede perder, ganar e iniciar una nueva partida. También está el feature de las tres vidas, que se van descontando cada vez que la pelota toca la parte inferior de la pantalla. A su vez, el juego pasó los tests realizados a través de la terminal. Lo que me generó más dificultades al momento de escribir el brief fue explicitar las reglas y el funcionamiento del juego ya que había varios aspectos, como por ejemplo el rectángulo que marca los límites del espacio en el que se mueven los elementos o que la paleta solo se mueva de forma horizontal, que yo daba por naturales y sabidos. También me costó identificar qué archivos tenía que solicitarle al agente y diferenciar cuál era la función de cada uno. Por último, si tuviera que realizar el ejercicio de nuevo, le agregaría al prompt una variable para regular la dificultad (fácil, intermedia y difícil) en función de qué tan rápido se mueve la pelota al rebotar. Esto se debe a que, al probar el juego tal y como fue obtenido en esta corrida, me resultó bastante fácil. 

