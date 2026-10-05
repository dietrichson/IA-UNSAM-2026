/**
 * juego.js
 * Lógica pura del Memotest (sin manipulación del DOM).
 */

const EMOJIS = ['🐶', '🐱', '🦊', '🐼', '🐸', '🦁', '🐯', '🐨', '🐵', '🦄', '🐷', '🐔', '🐙', '🦋', '🐢', '🦉', '🐝', '🐞'];

const CONFIGURACIONES = {
    facil:   { filas: 2, columnas: 4, pares: 4  },
    medio:   { filas: 4, columnas: 4, pares: 8  },
    dificil: { filas: 4, columnas: 6, pares: 12 },
    experto: { filas: 6, columnas: 6, pares: 18 }
};

/**
 * Mezcla un array usando el algoritmo Fisher-Yates.
 */
function mezclar(array) {
    const copia = [...array];
    for (let i = copia.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copia[i], copia[j]] = [copia[j], copia[i]];
    }
    return copia;
}

/**
 * Genera un mazo de cartas mezclado.
 */
function generarMazo(dificultad) {
    const config = CONFIGURACIONES[dificultad];
    if (!config) throw new Error(`Dificultad inválida: ${dificultad}`);

    const emojisSeleccionados = EMOJIS.slice(0, config.pares);
    const cartas = [];
    emojisSeleccionados.forEach((emoji, index) => {
        cartas.push({ id: index * 2,     parId: index, emoji, volteada: false, encontrada: false });
        cartas.push({ id: index * 2 + 1, parId: index, emoji, volteada: false, encontrada: false });
    });

    return mezclar(cartas);
}

/**
 * Calcula el puntaje en base a movimientos, tiempo y dificultad.
 */
function calcularPuntaje(movimientos, segundos, dificultad) {
    const multiplicador = { facil: 1, medio: 1.5, dificil: 2, experto: 3 }[dificultad] || 1;
    const base = 1000;
    const penalizacionMov = movimientos * 10;
    const penalizacionTiempo = segundos * 2;
    const puntaje = Math.max(0, Math.round((base - penalizacionMov - penalizacionTiempo) * multiplicador));
    return puntaje;
}

/**
 * Formatea segundos a mm:ss
 */
function formatearTiempo(segundos) {
    const m = String(Math.floor(segundos / 60)).padStart(2, '0');
    const s = String(segundos % 60).padStart(2, '0');
    return `${m}:${s}`;
}

// Exportar para uso en navegador y en tests (Node)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EMOJIS,
        CONFIGURACIONES,
        mezclar,
        generarMazo,
        calcularPuntaje,
        formatearTiempo
    };
}
