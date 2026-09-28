/**
 * ui.js — Interfaz del Breakout.
 *
 * Se encarga de todo lo que depende del navegador:
 *  - dibujar el juego en el <canvas>,
 *  - dibujar los corazones de vidas,
 *  - leer teclado, mouse y touch,
 *  - mostrar el cartel de fin de partida,
 *  - ejecutar el bucle de animación que hace avanzar a `game.js`.
 *
 * Las reglas del juego NO viven aquí: este archivo solo consulta y
 * modifica el estado a través de la API de `Breakout.Juego`.
 */
(function () {
  'use strict';

  const { Juego, CONFIG } = window.Breakout;

  // ---------------------------------------------------------------------
  // Elementos del DOM
  // ---------------------------------------------------------------------

  const lienzo = document.getElementById('lienzo');
  const ctx = lienzo.getContext('2d');
  const contenedorVidas = document.getElementById('vidas');
  const cartel = document.getElementById('cartel');
  const cartelTitulo = document.getElementById('cartel-titulo');
  const cartelBoton = document.getElementById('cartel-boton');

  // El tamaño interno del lienzo sale de la configuración del juego.
  lienzo.width = CONFIG.ancho;
  lienzo.height = CONFIG.alto;

  // ---------------------------------------------------------------------
  // Estilo visual
  // ---------------------------------------------------------------------

  const COLOR_FONDO = '#15122a';
  const COLOR_MARFIL = '#f1ebdc';
  const COLOR_TEXTO_SUAVE = '#a9a3bd';
  const HUECO_LADRILLO = 1; // separación visual entre ladrillos, en píxeles

  /** Corazón pixelado de 7 x 6 (1 = píxel relleno). */
  const MATRIZ_CORAZON = [
    '0110110',
    '1111111',
    '1111111',
    '0111110',
    '0011100',
    '0001000',
  ];

  /** Construye el SVG de un corazón a partir de la matriz de píxeles. */
  function crearCorazon() {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('viewBox', '0 0 7 6');
    svg.setAttribute('class', 'corazon');
    svg.setAttribute('aria-hidden', 'true');

    MATRIZ_CORAZON.forEach((fila, y) => {
      fila.split('').forEach((celda, x) => {
        if (celda !== '1') return;
        const rect = document.createElementNS(ns, 'rect');
        rect.setAttribute('x', String(x));
        rect.setAttribute('y', String(y));
        rect.setAttribute('width', '1');
        rect.setAttribute('height', '1');
        svg.appendChild(rect);
      });
    });
    return svg;
  }

  // ---------------------------------------------------------------------
  // Estado de la interfaz
  // ---------------------------------------------------------------------

  const juego = new Juego();
  const teclas = { izquierda: false, derecha: false };
  let vidasMostradas = null; // para redibujar los corazones solo cuando cambian

  // ---------------------------------------------------------------------
  // Dibujo
  // ---------------------------------------------------------------------

  /** Un corazón por cada vida restante. */
  function dibujarVidas() {
    if (vidasMostradas === juego.vidas) return;
    vidasMostradas = juego.vidas;

    contenedorVidas.replaceChildren();
    for (let i = 0; i < juego.vidas; i++) {
      contenedorVidas.appendChild(crearCorazon());
    }
    contenedorVidas.setAttribute('aria-label', `Vidas restantes: ${juego.vidas}`);
  }

  /** Dibuja ladrillos, paleta, pelota y la indicación de lanzamiento. */
  function dibujarJuego() {
    ctx.fillStyle = COLOR_FONDO;
    ctx.fillRect(0, 0, CONFIG.ancho, CONFIG.alto);

    // Ladrillos activos, cada uno con el color de su fila.
    for (const l of juego.ladrillos.values()) {
      ctx.fillStyle = l.color;
      ctx.fillRect(
        l.x + HUECO_LADRILLO,
        l.y + HUECO_LADRILLO,
        l.ancho - 2 * HUECO_LADRILLO,
        l.alto - 2 * HUECO_LADRILLO
      );
    }

    // Paleta.
    const pal = juego.paleta;
    ctx.fillStyle = COLOR_MARFIL;
    ctx.fillRect(pal.x, pal.y, pal.ancho, pal.alto);

    // Pelota (cuadrada, acorde a la estética retro).
    const p = juego.pelota;
    ctx.fillRect(p.x - p.radio, p.y - p.radio, p.radio * 2, p.radio * 2);

    // Indicación mientras la pelota espera sobre la paleta.
    if (juego.estado === 'esperando') {
      ctx.fillStyle = COLOR_TEXTO_SUAVE;
      ctx.font = '16px "Courier New", Courier, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('Espacio o clic para lanzar', CONFIG.ancho / 2, 340);
    }
  }

  // ---------------------------------------------------------------------
  // Cartel de fin de partida
  // ---------------------------------------------------------------------

  function mostrarCartel() {
    cartel.dataset.resultado = juego.estado; // 'derrota' o 'victoria'
    cartelTitulo.textContent = juego.mensaje;
    cartelBoton.textContent = juego.textoBoton;
    cartel.hidden = false;
    cartelBoton.focus();
  }

  function ocultarCartel() {
    cartel.hidden = true;
    delete cartel.dataset.resultado;
  }

  // "Quiero revancha" / "Voy por más": nueva partida de inmediato.
  cartelBoton.addEventListener('click', () => {
    juego.reiniciar();
    teclas.izquierda = false;
    teclas.derecha = false;
    ocultarCartel();
  });

  // ---------------------------------------------------------------------
  // Entradas: teclado
  // ---------------------------------------------------------------------

  window.addEventListener('keydown', (evento) => {
    if (!cartel.hidden) return; // con el cartel abierto, manda el botón

    switch (evento.key) {
      case 'ArrowLeft':
      case 'a':
      case 'A':
        teclas.izquierda = true;
        evento.preventDefault();
        break;
      case 'ArrowRight':
      case 'd':
      case 'D':
        teclas.derecha = true;
        evento.preventDefault();
        break;
      case ' ':
      case 'ArrowUp':
        juego.lanzar();
        evento.preventDefault();
        break;
      default:
        break;
    }
  });

  window.addEventListener('keyup', (evento) => {
    switch (evento.key) {
      case 'ArrowLeft':
      case 'a':
      case 'A':
        teclas.izquierda = false;
        break;
      case 'ArrowRight':
      case 'd':
      case 'D':
        teclas.derecha = false;
        break;
      default:
        break;
    }
  });

  // Si la ventana pierde el foco, se sueltan las teclas para que la paleta no quede "pegada".
  window.addEventListener('blur', () => {
    teclas.izquierda = false;
    teclas.derecha = false;
  });

  // ---------------------------------------------------------------------
  // Entradas: mouse y touch (eventos de puntero)
  // ---------------------------------------------------------------------

  /** Convierte una coordenada X de pantalla a coordenada lógica del campo. */
  function xEnCampo(clientX) {
    const rect = lienzo.getBoundingClientRect();
    return ((clientX - rect.left) * CONFIG.ancho) / rect.width;
  }

  window.addEventListener('pointermove', (evento) => {
    juego.colocarPaleta(xEnCampo(evento.clientX));
  });

  lienzo.addEventListener('pointerdown', (evento) => {
    juego.colocarPaleta(xEnCampo(evento.clientX));
    juego.lanzar();
  });

  // ---------------------------------------------------------------------
  // Bucle principal
  // ---------------------------------------------------------------------

  let instanteAnterior = null;

  function cuadro(instante) {
    if (instanteAnterior === null) instanteAnterior = instante;
    // Se limita dt para que una pestaña en segundo plano no produzca saltos enormes.
    const dt = Math.min((instante - instanteAnterior) / 1000, 0.05);
    instanteAnterior = instante;

    const direccion = (teclas.derecha ? 1 : 0) - (teclas.izquierda ? 1 : 0);
    juego.moverPaleta(direccion, dt);
    juego.actualizar(dt);

    // Sincronización: vidas y cartel reflejan siempre el estado del juego.
    dibujarVidas();
    if (juego.finalizado && cartel.hidden) mostrarCartel();
    dibujarJuego();

    window.requestAnimationFrame(cuadro);
  }

  window.requestAnimationFrame(cuadro);
})();
