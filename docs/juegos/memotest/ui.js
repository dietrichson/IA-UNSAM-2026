/**
 * ui.js
 * Maneja el DOM, eventos e interacción con el usuario.
 */

(function () {
    // ===== Estado del juego =====
    const estado = {
        dificultad: 'medio',
        cartas: [],
        primeraCarta: null,
        segundaCarta: null,
        bloqueado: false,
        movimientos: 0,
        paresEncontrados: 0,
        totalPares: 0,
        segundos: 0,
        temporizador: null,
        juegoIniciado: false
    };

    // ===== Referencias DOM =====
    const tableroEl = document.getElementById('tablero');
    const movimientosEl = document.getElementById('movimientos');
    const paresEl = document.getElementById('pares');
    const tiempoEl = document.getElementById('tiempo');
    const puntajeEl = document.getElementById('puntaje');
    const selectDificultad = document.getElementById('select-dificultad');
    const btnReiniciar = document.getElementById('btn-reiniciar');
    const modal = document.getElementById('modal-ganaste');
    const modalMovimientos = document.getElementById('modal-movimientos');
    const modalTiempo = document.getElementById('modal-tiempo');
    const modalPuntaje = document.getElementById('modal-puntaje');
    const btnJugarDeNuevo = document.getElementById('btn-jugar-de-nuevo');

    // ===== Inicialización =====
    function iniciarJuego() {
        const config = CONFIGURACIONES[estado.dificultad];
        estado.cartas = generarMazo(estado.dificultad);
        estado.primeraCarta = null;
        estado.segundaCarta = null;
        estado.bloqueado = false;
        estado.movimientos = 0;
        estado.paresEncontrados = 0;
        estado.totalPares = config.pares;
        estado.segundos = 0;
        estado.juegoIniciado = false;

        detenerTemporizador();
        actualizarEstadisticas();
        modal.classList.add('oculto');
        renderizarTablero();
    }

    function renderizarTablero() {
        const config = CONFIGURACIONES[estado.dificultad];
        tableroEl.innerHTML = '';
        tableroEl.style.gridTemplateColumns = `repeat(${config.columnas}, 1fr)`;

        estado.cartas.forEach((carta) => {
            const cartaEl = document.createElement('div');
            cartaEl.className = 'carta';
            cartaEl.dataset.id = carta.id;
            cartaEl.innerHTML = `
                <div class="carta-cara carta-frente"></div>
                <div class="carta-cara carta-dorso">${carta.emoji}</div>
            `;
            cartaEl.addEventListener('click', () => manejarClickCarta(carta.id));
            tableroEl.appendChild(cartaEl);
        });
    }

    // ===== Manejo de clics =====
    function manejarClickCarta(id) {
        if (estado.bloqueado) return;

        const carta = estado.cartas.find(c => c.id === id);
        if (!carta || carta.volteada || carta.encontrada) return;

        // Iniciar temporizador en el primer clic
        if (!estado.juegoIniciado) {
            estado.juegoIniciado = true;
            iniciarTemporizador();
        }

        voltearCarta(carta);

        if (!estado.primeraCarta) {
            estado.primeraCarta = carta;
        } else {
            estado.segundaCarta = carta;
            estado.movimientos++;
            actualizarEstadisticas();
            verificarPar();
        }
    }

    function voltearCarta(carta) {
        carta.volteada = true;
        const cartaEl = document.querySelector(`.carta[data-id="${carta.id}"]`);
        cartaEl.classList.add('volteada');
    }

    function verificarPar() {
        const { primeraCarta, segundaCarta } = estado;

        if (primeraCarta.parId === segundaCarta.parId) {
            // Par encontrado
            primeraCarta.encontrada = true;
            segundaCarta.encontrada = true;
            marcarComoEncontradas(primeraCarta, segundaCarta);

            estado.paresEncontrados++;
            estado.primeraCarta = null;
            estado.segundaCarta = null;
            actualizarEstadisticas();

            if (estado.paresEncontrados === estado.totalPares) {
                finalizarJuego();
            }
        } else {
            // No coinciden
            estado.bloqueado = true;
            setTimeout(() => {
                desvoltearCarta(primeraCarta);
                desvoltearCarta(segundaCarta);
                estado.primeraCarta = null;
                estado.segundaCarta = null;
                estado.bloqueado = false;
            }, 900);
        }
    }

    function marcarComoEncontradas(c1, c2) {
        [c1, c2].forEach(carta => {
            const cartaEl = document.querySelector(`.carta[data-id="${carta.id}"]`);
            cartaEl.classList.add('encontrada');
        });
    }

    function desvoltearCarta(carta) {
        carta.volteada = false;
        const cartaEl = document.querySelector(`.carta[data-id="${carta.id}"]`);
        cartaEl.classList.remove('volteada');
    }

    // ===== Temporizador =====
    function iniciarTemporizador() {
        detenerTemporizador();
        estado.temporizador = setInterval(() => {
            estado.segundos++;
            tiempoEl.textContent = formatearTiempo(estado.segundos);
            actualizarPuntajeEnVivo();
        }, 1000);
    }

    function detenerTemporizador() {
        if (estado.temporizador) {
            clearInterval(estado.temporizador);
            estado.temporizador = null;
        }
    }

    // ===== Estadísticas =====
    function actualizarEstadisticas() {
        movimientosEl.textContent = estado.movimientos;
        paresEl.textContent = `${estado.paresEncontrados} / ${estado.totalPares}`;
        tiempoEl.textContent = formatearTiempo(estado.segundos);
        actualizarPuntajeEnVivo();
    }

    function actualizarPuntajeEnVivo() {
        const puntos = calcularPuntaje(estado.movimientos, estado.segundos, estado.dificultad);
        puntajeEl.textContent = puntos;
    }

    // ===== Fin del juego =====
    function finalizarJuego() {
        detenerTemporizador();
        const puntajeFinal = calcularPuntaje(estado.movimientos, estado.segundos, estado.dificultad);

        modalMovimientos.textContent = estado.movimientos;
        modalTiempo.textContent = formatearTiempo(estado.segundos);
        modalPuntaje.textContent = puntajeFinal;

        setTimeout(() => {
            modal.classList.remove('oculto');
        }, 500);
    }

    // ===== Event listeners =====
    btnReiniciar.addEventListener('click', () => {
        estado.dificultad = selectDificultad.value;
        iniciarJuego();
    });

    selectDificultad.addEventListener('change', () => {
        estado.dificultad = selectDificultad.value;
        iniciarJuego();
    });

    btnJugarDeNuevo.addEventListener('click', () => {
        iniciarJuego();
    });

    // ===== Arrancar =====
    iniciarJuego();
})();
