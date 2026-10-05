/**
 * game.js — Reglas del juego y lógica de dominio del Breakout.
 *
 * Este archivo NO conoce el renderizado: no usa `document`, `window` ni
 * ningún elemento de Canvas. Por eso puede cargarse tanto en el navegador
 * (con una etiqueta <script> tradicional) como en Node.js (con `require`)
 * para ejecutar las pruebas unitarias.
 *
 * Sistema de coordenadas: origen en la esquina superior izquierda del
 * campo de juego, eje X hacia la derecha y eje Y hacia abajo. Las unidades
 * son "píxeles lógicos"; la interfaz decide cómo escalarlos.
 */
(function (raiz, fabrica) {
  'use strict';

  const api = fabrica();

  if (typeof module === 'object' && module.exports) {
    // Entorno Node.js (pruebas): se exporta como módulo CommonJS.
    module.exports = api;
  } else {
    // Entorno navegador: se expone un único objeto global `Breakout`.
    raiz.Breakout = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // ---------------------------------------------------------------------
  // Configuración
  // ---------------------------------------------------------------------

  /** Parámetros geométricos y de juego. Todos en píxeles lógicos. */
  const CONFIG = Object.freeze({
    ancho: 650, // 13 columnas x 50 px = 650 px, sin huecos laterales
    alto: 520,
    columnas: 13,
    filas: 6,
    ladrilloAncho: 50,
    ladrilloAlto: 20,
    ladrilloDesdeArriba: 70, // margen libre sobre la primera fila
    vidasIniciales: 3,
    paleta: Object.freeze({
      ancho: 96,
      alto: 12,
      y: 490, // posición vertical fija: la paleta jamás se mueve en Y
      velocidad: 520, // píxeles por segundo (control por teclado)
    }),
    pelota: Object.freeze({
      radio: 6, // media arista del cuadrado que representa a la pelota
      velocidad: 380, // píxeles por segundo, constante durante toda la partida
    }),
  });

  /** Colores de cada fila, de arriba hacia abajo (bandera LGBT). */
  const COLORES_FILAS = Object.freeze([
    '#e63946', // fila 1: rojo
    '#f77f00', // fila 2: naranja
    '#fcd34d', // fila 3: amarillo
    '#2a9d5c', // fila 4: verde
    '#3a86ff', // fila 5: azul
    '#8e44ad', // fila 6: violeta
  ]);

  /** Estados posibles de la partida. */
  const ESTADOS = Object.freeze({
    ESPERANDO: 'esperando', // la pelota descansa sobre la paleta
    JUGANDO: 'jugando', // la pelota está en movimiento
    DERROTA: 'derrota', // se acabaron las vidas
    VICTORIA: 'victoria', // se destruyeron todos los ladrillos
  });

  /** Textos exactos de los carteles de fin de partida. */
  const MENSAJES = Object.freeze({
    derrota: 'Perdiste :(',
    victoria: 'Ganaste :)',
  });

  /** Textos exactos de los botones de los carteles. */
  const BOTONES = Object.freeze({
    derrota: 'Quiero revancha',
    victoria: 'Voy por más',
  });

  /** Ángulo máximo de salida de la pelota al rebotar en el borde de la paleta. */
  const ANGULO_MAXIMO = Math.PI / 3; // 60 grados respecto de la vertical

  /** Inclinación mínima de salida desde la paleta, para evitar rebotes verticales eternos. */
  const ANGULO_MINIMO = 0.12; // radianes (aprox. 7 grados)

  /** Distancia máxima que avanza la pelota por sub-paso (evita atravesar objetos). */
  const PASO_MAXIMO = 3;

  // ---------------------------------------------------------------------
  // Utilidades
  // ---------------------------------------------------------------------

  /** Limita `valor` al rango [minimo, maximo]. */
  function limitar(valor, minimo, maximo) {
    return Math.min(Math.max(valor, minimo), maximo);
  }

  /**
   * Crea el mapa de ladrillos activos. La clave es un identificador numérico
   * (fila * columnas + columna) y el valor describe al ladrillo.
   * Destruir un ladrillo equivale a eliminarlo del mapa.
   */
  function crearLadrillos() {
    const ladrillos = new Map();
    for (let fila = 0; fila < CONFIG.filas; fila++) {
      for (let columna = 0; columna < CONFIG.columnas; columna++) {
        const id = fila * CONFIG.columnas + columna;
        ladrillos.set(id, {
          id,
          fila,
          columna,
          x: columna * CONFIG.ladrilloAncho,
          y: CONFIG.ladrilloDesdeArriba + fila * CONFIG.ladrilloAlto,
          ancho: CONFIG.ladrilloAncho,
          alto: CONFIG.ladrilloAlto,
          color: COLORES_FILAS[fila],
        });
      }
    }
    return ladrillos;
  }

  // ---------------------------------------------------------------------
  // Clase principal
  // ---------------------------------------------------------------------

  class Juego {
    /**
     * @param {Object} [opciones]
     * @param {Function} [opciones.aleatorio] Función que devuelve un número en
     *   [0, 1). Por defecto `Math.random`; se puede inyectar para tests.
     */
    constructor(opciones = {}) {
      this.aleatorio = opciones.aleatorio || Math.random;
      this.reiniciar();
    }

    // -- Ciclo de vida ----------------------------------------------------

    /**
     * Deja la partida como nueva: 3 vidas, 78 ladrillos, paleta centrada,
     * pelota sobre la paleta y sin carteles de victoria/derrota.
     */
    reiniciar() {
      this.vidas = CONFIG.vidasIniciales;
      this.ladrillos = crearLadrillos();
      this.paleta = {
        x: (CONFIG.ancho - CONFIG.paleta.ancho) / 2,
        y: CONFIG.paleta.y,
        ancho: CONFIG.paleta.ancho,
        alto: CONFIG.paleta.alto,
      };
      this.pelota = { x: 0, y: 0, vx: 0, vy: 0, radio: CONFIG.pelota.radio };
      this.estado = ESTADOS.ESPERANDO;
      this._pegarPelotaALaPaleta();
    }

    // -- Consultas --------------------------------------------------------

    /** Verdadero cuando la partida terminó (derrota o victoria). */
    get finalizado() {
      return this.estado === ESTADOS.DERROTA || this.estado === ESTADOS.VICTORIA;
    }

    /** Texto del cartel de fin de partida, o `null` si la partida sigue. */
    get mensaje() {
      if (this.estado === ESTADOS.DERROTA) return MENSAJES.derrota;
      if (this.estado === ESTADOS.VICTORIA) return MENSAJES.victoria;
      return null;
    }

    /** Texto del botón del cartel de fin de partida, o `null` si la partida sigue. */
    get textoBoton() {
      if (this.estado === ESTADOS.DERROTA) return BOTONES.derrota;
      if (this.estado === ESTADOS.VICTORIA) return BOTONES.victoria;
      return null;
    }

    // -- Acciones del jugador ---------------------------------------------

    /** Lanza la pelota desde la paleta con un ángulo levemente aleatorio. */
    lanzar() {
      if (this.estado !== ESTADOS.ESPERANDO) return;
      // Ángulo entre 0,15 y 0,50 rad, hacia izquierda o derecha, para que la
      // pelota nunca suba exactamente en vertical.
      const signo = this.aleatorio() < 0.5 ? -1 : 1;
      const angulo = signo * (0.15 + this.aleatorio() * 0.35);
      this.pelota.vx = CONFIG.pelota.velocidad * Math.sin(angulo);
      this.pelota.vy = -CONFIG.pelota.velocidad * Math.cos(angulo);
      this.estado = ESTADOS.JUGANDO;
    }

    /**
     * Coloca el centro de la paleta en `centroX` (control con mouse o touch).
     * Solo cambia la coordenada X: la paleta nunca se mueve verticalmente.
     */
    colocarPaleta(centroX) {
      if (this.finalizado) return;
      const x = centroX - this.paleta.ancho / 2;
      this.paleta.x = limitar(x, 0, CONFIG.ancho - this.paleta.ancho);
      this._pegarPelotaALaPaleta();
    }

    /**
     * Mueve la paleta en horizontal (control por teclado).
     * @param {number} direccion -1 (izquierda), 0 (quieta) o 1 (derecha).
     * @param {number} dt Tiempo transcurrido, en segundos.
     */
    moverPaleta(direccion, dt) {
      if (this.finalizado || direccion === 0) return;
      const desplazamiento = Math.sign(direccion) * CONFIG.paleta.velocidad * dt;
      this.colocarPaleta(this.paleta.x + this.paleta.ancho / 2 + desplazamiento);
    }

    // -- Reglas -----------------------------------------------------------

    /**
     * Destruye un ladrillo (lo elimina del mapa de ladrillos activos).
     * Si era el último, la partida pasa al estado de victoria.
     * @param {number} id Identificador del ladrillo.
     * @returns {boolean} `true` si el ladrillo existía y fue destruido.
     */
    destruirLadrillo(id) {
      if (!this.ladrillos.delete(id)) return false;
      if (this.ladrillos.size === 0) {
        this.estado = ESTADOS.VICTORIA;
      }
      return true;
    }

    /**
     * Resta una vida. Con 0 vidas la partida termina en derrota; si no, la
     * pelota vuelve a la paleta a la espera de un nuevo lanzamiento.
     */
    perderVida() {
      if (this.finalizado) return;
      this.vidas -= 1;
      if (this.vidas <= 0) {
        this.vidas = 0;
        this.estado = ESTADOS.DERROTA;
        this.pelota.vx = 0;
        this.pelota.vy = 0;
      } else {
        this.estado = ESTADOS.ESPERANDO;
        this._pegarPelotaALaPaleta();
      }
    }

    /**
     * Avanza la simulación `dt` segundos. Solo tiene efecto mientras la
     * pelota está en movimiento. El avance se divide en sub-pasos cortos
     * para que la pelota no atraviese ladrillos ni la paleta.
     */
    actualizar(dt) {
      if (this.estado !== ESTADOS.JUGANDO || !(dt > 0)) return;

      const distancia = CONFIG.pelota.velocidad * dt;
      const pasos = Math.max(1, Math.ceil(distancia / PASO_MAXIMO));
      const subDt = dt / pasos;

      for (let i = 0; i < pasos && this.estado === ESTADOS.JUGANDO; i++) {
        this._avanzar(subDt);
      }
    }

    // -- Internos ---------------------------------------------------------

    /** Apoya la pelota, centrada, sobre la paleta (solo si está esperando). */
    _pegarPelotaALaPaleta() {
      if (this.estado !== ESTADOS.ESPERANDO) return;
      this.pelota.x = this.paleta.x + this.paleta.ancho / 2;
      this.pelota.y = this.paleta.y - this.pelota.radio;
      this.pelota.vx = 0;
      this.pelota.vy = 0;
    }

    /** Un sub-paso de simulación: movimiento y todas las colisiones. */
    _avanzar(dt) {
      const p = this.pelota;
      p.x += p.vx * dt;
      p.y += p.vy * dt;

      this._rebotarEnParedes();

      // Límite inferior del marco: se pierde una vida.
      if (p.y + p.radio >= CONFIG.alto) {
        this.perderVida();
        return;
      }

      this._rebotarEnPaleta();
      this._rebotarEnLadrillos();
    }

    /** Paredes izquierda, derecha y superior. */
    _rebotarEnParedes() {
      const p = this.pelota;
      if (p.x - p.radio < 0) {
        p.x = p.radio;
        p.vx = Math.abs(p.vx);
      } else if (p.x + p.radio > CONFIG.ancho) {
        p.x = CONFIG.ancho - p.radio;
        p.vx = -Math.abs(p.vx);
      }
      if (p.y - p.radio < 0) {
        p.y = p.radio;
        p.vy = Math.abs(p.vy);
      }
    }

    /**
     * Rebote en la paleta. El ángulo de salida depende del punto de impacto:
     * en el centro sale casi vertical y en los bordes sale más inclinada.
     */
    _rebotarEnPaleta() {
      const p = this.pelota;
      const pal = this.paleta;

      if (p.vy <= 0) return; // solo rebota cuando la pelota va hacia abajo
      if (p.y > pal.y + pal.alto / 2) return; // ya pasó: golpe lateral, no rebota

      const toca =
        p.y + p.radio >= pal.y &&
        p.x + p.radio > pal.x &&
        p.x - p.radio < pal.x + pal.ancho;
      if (!toca) return;

      const centro = pal.x + pal.ancho / 2;
      const relativo = limitar((p.x - centro) / (pal.ancho / 2 + p.radio), -1, 1);
      let angulo = relativo * ANGULO_MAXIMO;

      // Si el impacto fue casi exactamente en el centro, se fuerza una leve
      // inclinación (hacia el lado del impacto, o al azar si fue justo al medio).
      if (Math.abs(angulo) < ANGULO_MINIMO) {
        const signo = angulo !== 0 ? Math.sign(angulo) : this.aleatorio() < 0.5 ? -1 : 1;
        angulo = signo * ANGULO_MINIMO;
      }

      p.vx = CONFIG.pelota.velocidad * Math.sin(angulo);
      p.vy = -CONFIG.pelota.velocidad * Math.cos(angulo);
      p.y = pal.y - p.radio;
    }

    /**
     * Rebote y destrucción de ladrillos. Se procesa como máximo un ladrillo
     * por sub-paso. El eje del rebote es el de menor penetración.
     */
    _rebotarEnLadrillos() {
      const p = this.pelota;

      for (const ladrillo of this.ladrillos.values()) {
        const penetracionX = Math.min(
          p.x + p.radio - ladrillo.x,
          ladrillo.x + ladrillo.ancho - (p.x - p.radio)
        );
        const penetracionY = Math.min(
          p.y + p.radio - ladrillo.y,
          ladrillo.y + ladrillo.alto - (p.y - p.radio)
        );

        // Sin solapamiento en alguno de los ejes: no hay choque.
        if (penetracionX <= 0 || penetracionY <= 0) continue;

        if (penetracionX < penetracionY) {
          // Choque lateral: se invierte el movimiento horizontal.
          const desdeIzquierda = p.x < ladrillo.x + ladrillo.ancho / 2;
          p.vx = desdeIzquierda ? -Math.abs(p.vx) : Math.abs(p.vx);
          p.x += desdeIzquierda ? -penetracionX : penetracionX;
        } else {
          // Choque superior o inferior: se invierte el movimiento vertical.
          const desdeArriba = p.y < ladrillo.y + ladrillo.alto / 2;
          p.vy = desdeArriba ? -Math.abs(p.vy) : Math.abs(p.vy);
          p.y += desdeArriba ? -penetracionY : penetracionY;
        }

        this.destruirLadrillo(ladrillo.id);
        return;
      }
    }
  }

  return {
    Juego,
    CONFIG,
    COLORES_FILAS,
    ESTADOS,
    MENSAJES,
    BOTONES,
  };
});
