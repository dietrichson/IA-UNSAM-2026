/**
 * test.js — Pruebas unitarias de la lógica de game.js.
 *
 * Se ejecutan con el test runner nativo de Node.js:
 *
 *   node --test test.js
 */
'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert');

const { Juego, CONFIG, COLORES_FILAS, ESTADOS, MENSAJES, BOTONES } = require('./game.js');

// -----------------------------------------------------------------------
// Ayudantes
// -----------------------------------------------------------------------

/** Crea un juego con azar determinista (siempre lanza hacia la derecha). */
function crearJuego() {
  return new Juego({ aleatorio: () => 0.9 });
}

/** Deja la pelota en movimiento, apenas por encima del límite inferior del marco. */
function ponerPelotaCercaDelFondo(juego) {
  juego.lanzar();
  juego.pelota.x = 20; // lejos de la paleta, que está centrada
  juego.pelota.y = CONFIG.alto - CONFIG.pelota.radio - 1;
  juego.pelota.vx = 0;
  juego.pelota.vy = CONFIG.pelota.velocidad;
}

/**
 * Deja la pelota en movimiento apenas debajo de un ladrillo, subiendo hacia él,
 * de modo que el próximo paso de simulación choque con ese ladrillo.
 */
function apuntarAlLadrillo(juego, ladrillo) {
  juego.lanzar();
  juego.pelota.x = ladrillo.x + ladrillo.ancho / 2;
  juego.pelota.y = ladrillo.y + ladrillo.alto + juego.pelota.radio - 1;
  juego.pelota.vx = 0;
  juego.pelota.vy = -CONFIG.pelota.velocidad;
}

// -----------------------------------------------------------------------
// 1. Estado inicial
// -----------------------------------------------------------------------

describe('Estado inicial', () => {
  it('arranca con 3 vidas', () => {
    const juego = crearJuego();
    assert.strictEqual(juego.vidas, 3);
  });

  it('arranca con los 78 ladrillos activos (13 columnas x 6 filas)', () => {
    const juego = crearJuego();
    assert.strictEqual(CONFIG.columnas, 13);
    assert.strictEqual(CONFIG.filas, 6);
    assert.strictEqual(juego.ladrillos.size, 78);

    const columnasPorFila = new Map();
    for (const ladrillo of juego.ladrillos.values()) {
      columnasPorFila.set(ladrillo.fila, (columnasPorFila.get(ladrillo.fila) || 0) + 1);
    }
    assert.strictEqual(columnasPorFila.size, 6);
    for (const cantidad of columnasPorFila.values()) {
      assert.strictEqual(cantidad, 13);
    }
  });

  it('asigna a cada fila su color: rojo, naranja, amarillo, verde, azul y violeta', () => {
    const juego = crearJuego();
    assert.strictEqual(COLORES_FILAS.length, 6);
    for (const ladrillo of juego.ladrillos.values()) {
      assert.strictEqual(ladrillo.color, COLORES_FILAS[ladrillo.fila]);
    }
  });

  it('arranca sin haber finalizado y sin mensaje de fin de partida', () => {
    const juego = crearJuego();
    assert.strictEqual(juego.finalizado, false);
    assert.strictEqual(juego.mensaje, null);
    assert.strictEqual(juego.textoBoton, null);
    assert.notStrictEqual(juego.estado, ESTADOS.DERROTA);
    assert.notStrictEqual(juego.estado, ESTADOS.VICTORIA);
  });
});

// -----------------------------------------------------------------------
// 2. Pérdida de vidas y derrota
// -----------------------------------------------------------------------

describe('Pérdida de vidas y derrota', () => {
  it('resta una vida cuando la pelota toca el límite inferior', () => {
    const juego = crearJuego();
    ponerPelotaCercaDelFondo(juego);

    juego.actualizar(0.05);

    assert.strictEqual(juego.vidas, 2);
    assert.strictEqual(juego.finalizado, false);
    // La pelota vuelve a la paleta, esperando un nuevo lanzamiento.
    assert.strictEqual(juego.estado, ESTADOS.ESPERANDO);
  });

  it('al llegar a 0 vidas el juego pasa al estado de derrota (Perdiste :()', () => {
    const juego = crearJuego();

    for (let vidasEsperadas = 2; vidasEsperadas >= 0; vidasEsperadas--) {
      ponerPelotaCercaDelFondo(juego);
      juego.actualizar(0.05);
      assert.strictEqual(juego.vidas, vidasEsperadas);
    }

    assert.strictEqual(juego.estado, ESTADOS.DERROTA);
    assert.strictEqual(juego.finalizado, true);
    assert.strictEqual(juego.mensaje, 'Perdiste :(');
    assert.strictEqual(juego.mensaje, MENSAJES.derrota);
    assert.strictEqual(juego.textoBoton, 'Quiero revancha');
    assert.strictEqual(juego.textoBoton, BOTONES.derrota);
  });

  it('con la partida terminada la pelota ya no se mueve ni se restan más vidas', () => {
    const juego = crearJuego();
    for (let i = 0; i < 3; i++) {
      ponerPelotaCercaDelFondo(juego);
      juego.actualizar(0.05);
    }
    const { x, y } = juego.pelota;

    juego.actualizar(1);
    juego.perderVida();

    assert.strictEqual(juego.vidas, 0);
    assert.strictEqual(juego.pelota.x, x);
    assert.strictEqual(juego.pelota.y, y);
  });
});

// -----------------------------------------------------------------------
// 3. Destrucción de ladrillos
// -----------------------------------------------------------------------

describe('Destrucción de ladrillos', () => {
  it('la colisión con un ladrillo lo elimina del mapa de ladrillos activos', () => {
    const juego = crearJuego();
    const objetivo = juego.ladrillos.get(71); // fila inferior de ladrillos, columna central (sin ladrillos debajo)
    assert.ok(objetivo, 'el ladrillo objetivo debería existir');

    apuntarAlLadrillo(juego, objetivo);
    juego.actualizar(0.001);

    assert.strictEqual(juego.ladrillos.has(objetivo.id), false);
    assert.strictEqual(juego.ladrillos.size, 77);
  });

  it('la pelota rebota (invierte su sentido vertical) al chocar con un ladrillo', () => {
    const juego = crearJuego();
    const objetivo = juego.ladrillos.get(65);

    apuntarAlLadrillo(juego, objetivo);
    juego.actualizar(0.001);

    assert.ok(juego.pelota.vy > 0, 'la pelota debería empezar a bajar');
  });

  it('cada choque destruye únicamente el ladrillo impactado', () => {
    const juego = crearJuego();
    const objetivo = juego.ladrillos.get(68);

    apuntarAlLadrillo(juego, objetivo);
    juego.actualizar(0.001);

    for (const id of juego.ladrillos.keys()) {
      assert.notStrictEqual(id, objetivo.id);
    }
    assert.strictEqual(juego.ladrillos.size, 77);
  });
});

// -----------------------------------------------------------------------
// 4. Condición de victoria
// -----------------------------------------------------------------------

describe('Condición de victoria', () => {
  it('al eliminar el ladrillo número 78 el juego pasa al estado de victoria (Ganaste :))', () => {
    const juego = crearJuego();
    const ids = [...juego.ladrillos.keys()];
    assert.strictEqual(ids.length, 78);

    // Los primeros 77 no alcanzan para ganar.
    for (const id of ids.slice(0, 77)) {
      juego.destruirLadrillo(id);
      assert.strictEqual(juego.finalizado, false);
    }
    assert.strictEqual(juego.ladrillos.size, 1);

    // El ladrillo 78 se destruye por una colisión real de la pelota.
    const ultimo = juego.ladrillos.get(ids[77]);
    apuntarAlLadrillo(juego, ultimo);
    juego.actualizar(0.001);

    assert.strictEqual(juego.ladrillos.size, 0);
    assert.strictEqual(juego.estado, ESTADOS.VICTORIA);
    assert.strictEqual(juego.finalizado, true);
    assert.strictEqual(juego.mensaje, 'Ganaste :)');
    assert.strictEqual(juego.mensaje, MENSAJES.victoria);
    assert.strictEqual(juego.textoBoton, 'Voy por más');
    assert.strictEqual(juego.textoBoton, BOTONES.victoria);
  });

  it('destruir un ladrillo que ya no existe no cambia nada', () => {
    const juego = crearJuego();
    assert.strictEqual(juego.destruirLadrillo(0), true);
    assert.strictEqual(juego.destruirLadrillo(0), false);
    assert.strictEqual(juego.ladrillos.size, 77);
  });
});

// -----------------------------------------------------------------------
// 5. Reinicio del juego
// -----------------------------------------------------------------------

describe('Reinicio del juego', () => {
  it('después de una derrota restablece 3 vidas, 78 ladrillos y limpia el cartel', () => {
    const juego = crearJuego();
    juego.destruirLadrillo(0);
    juego.destruirLadrillo(1);
    for (let i = 0; i < 3; i++) {
      ponerPelotaCercaDelFondo(juego);
      juego.actualizar(0.05);
    }
    assert.strictEqual(juego.mensaje, 'Perdiste :(');

    juego.reiniciar();

    assert.strictEqual(juego.vidas, 3);
    assert.strictEqual(juego.ladrillos.size, 78);
    assert.strictEqual(juego.finalizado, false);
    assert.strictEqual(juego.mensaje, null);
    assert.strictEqual(juego.textoBoton, null);
    assert.strictEqual(juego.estado, ESTADOS.ESPERANDO);
  });

  it('después de una victoria restablece 3 vidas, 78 ladrillos y limpia el cartel', () => {
    const juego = crearJuego();
    for (const id of [...juego.ladrillos.keys()]) {
      juego.destruirLadrillo(id);
    }
    assert.strictEqual(juego.mensaje, 'Ganaste :)');

    juego.reiniciar();

    assert.strictEqual(juego.vidas, 3);
    assert.strictEqual(juego.ladrillos.size, 78);
    assert.strictEqual(juego.finalizado, false);
    assert.strictEqual(juego.mensaje, null);
    assert.strictEqual(juego.textoBoton, null);
  });

  it('tras reiniciar se puede volver a jugar con normalidad', () => {
    const juego = crearJuego();
    for (let i = 0; i < 3; i++) {
      ponerPelotaCercaDelFondo(juego);
      juego.actualizar(0.05);
    }
    juego.reiniciar();

    ponerPelotaCercaDelFondo(juego);
    juego.actualizar(0.05);

    assert.strictEqual(juego.vidas, 2);
    assert.strictEqual(juego.finalizado, false);
  });
});
