# Mountain Bike Rush — Ultimate Edition

Juego arcade de bicicleta de montaña desarrollado en JavaScript vanilla + Canvas 2D para el proyecto IA-UNSAM-2026.

## Características

- 5 niveles con dificultad progresiva.
- Campo, valle rocoso, nieve, cañón y cumbre final.
- Física de aceleración, frenado, gravedad, salto, control aéreo e inclinación.
- Obstáculos: rocas, barriles y troncos.
- Rampas pequeñas y grandes.
- Monedas animadas y sistema de combo.
- Checkpoints.
- Vidas, daño, invulnerabilidad y game over.
- Cámara con seguimiento suave y shake.
- Partículas de polvo, impactos, monedas y eventos.
- Bicicleta y ciclista dibujados íntegramente con Canvas.
- Decoración procedural: árboles, pinos, cactus, rocas, montañas, nubes, agua y banderas.
- Menú y selector de niveles.
- Progresión y mejor puntuación mediante `localStorage`.
- Pausa, reinicio, victoria por nivel y victoria final.
- API interna para agentes de aprendizaje por refuerzo.
- Sin frameworks ni dependencias externas.

## Ejecución

Desde la carpeta que contiene `Juan Marcos Gatti/`:

```bash
python3 -m http.server 8000
```

Abrir:

```text
http://localhost:8000/Juan%20Marcos%20Gatti/bike/
```

También puede abrirse `index.html` directamente, aunque un servidor local es recomendable.

## Controles

| Acción | Tecla |
|---|---|
| Acelerar | W / Flecha arriba |
| Frenar | S / Flecha abajo |
| Saltar | Espacio |
| Pausar | P |
| Reiniciar nivel | R |

## Niveles

1. **Campo Verde** — introducción, colinas y obstáculos básicos.
2. **Valle Rocoso** — terreno irregular, agua y mayor densidad de obstáculos.
3. **Montaña Nevada** — pinos, nieve, velocidad y saltos más exigentes.
4. **Cañón Extremo** — zonas peligrosas, cactus y obstáculos combinados.
5. **Cumbre Final** — recorrido más largo, ascenso final y pantalla de victoria.

## API para RL

El núcleo está separado del renderizado y puede ejecutarse con Node.js.

### Acciones

```js
getAvailableActions()
```

Devuelve:

```js
['nothing', 'accelerate', 'brake', 'jump']
```

### Ejecutar una acción

```js
step('accelerate')
```

Cada llamada representa un único paso lógico del entorno.

### Obtener observación

```js
getState()
```

Devuelve un objeto serializable que contiene nivel, posición, velocidad, ángulo, progreso, puntuación, vidas, monedas, checkpoints, combo y obstáculos/rampas próximos.

Ejemplo:

```js
const state = getState();
console.log(state.progress);
console.log(state.velocityX);
console.log(state.obstacleAhead);
```

### Reiniciar

```js
resetGame()
```

### Iniciar un nivel

```js
startLevel(2)
```

### Datos de nivel

```js
getLevelData(3)
```

## Tests

Ejecutar:

```bash
node test.js
```

Los tests verifican la API, acciones, movimiento, salto, gravedad, progreso, niveles, bloqueo/desbloqueo, reset, serialización y estados principales.

## Arquitectura

- `index.html`: estructura, HUD, menú, overlays y estilos.
- `game.js`: estado, física, generación de niveles, colisiones, progresión y API RL.
- `ui.js`: Canvas, cámara, gráficos, animaciones, HUD, menú, controles y presentación.
- `test.js`: pruebas automáticas con `node:test` y `node:assert`.

La lógica del juego no depende de Canvas, lo que permite ejecutar `game.js` directamente en Node para pruebas y experimentación con agentes.
