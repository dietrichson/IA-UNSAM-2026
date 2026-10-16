/**
 * test.js
 * Tests unitarios simples del Memotest.
 * Se pueden correr en el navegador (ver test.html) o con Node.js
 * incluyendo juego.js antes que test.js.
 */

(function () {
    let pasados = 0;
    let fallados = 0;

    function assert(condicion, mensaje) {
        if (condicion) {
            pasados++;
            console.log(`✅ ${mensaje}`);
        } else {
            fallados++;
            console.error(`❌ ${mensaje}`);
        }
    }

    function assertEquals(a, b, mensaje) {
        assert(a === b, `${mensaje} (esperado: ${b}, recibido: ${a})`);
    }

    console.log('🧪 Corriendo tests del Memotest...\n');

    // ===== Test 1: Mezclar mantiene los elementos =====
    const original = [1, 2, 3, 4, 5];
    const mezclado = mezclar(original);
    assertEquals(mezclado.length, original.length, 'mezclar() conserva la longitud');
    assert(mezclado.every(x => original.includes(x)), 'mezclar() conserva todos los elementos');
    assert(original.join(',') === '1,2,3,4,5', 'mezclar() no muta el array original');

    // ===== Test 2: generarMazo por dificultad =====
    const mazoFacil = generarMazo('facil');
    assertEquals(mazoFacil.length, 8, 'Fácil genera 8 cartas (4 pares)');

    const mazoMedio = generarMazo('medio');
    assertEquals(mazoMedio.length, 16, 'Medio genera 16 cartas (8 pares)');

    const mazoDificil = generarMazo('dificil');
    assertEquals(mazoDificil.length, 24, 'Difícil genera 24 cartas (12 pares)');

    const mazoExperto = generarMazo('experto');
    assertEquals(mazoExperto.length, 36, 'Experto genera 36 cartas (18 pares)');

    // ===== Test 3: Cada par tiene 2 cartas =====
    const mazo = generarMazo('medio');
    const conteoPares = {};
    mazo.forEach(c => {
        conteoPares[c.parId] = (conteoPares[c.parId] || 0) + 1;
    });
    const todosParesDobles = Object.values(conteoPares).every(v => v === 2);
    assert(todosParesDobles, 'Cada parId aparece exactamente 2 veces');

    // ===== Test 4: Dificultad inválida lanza error =====
    let errorLanzado = false;
    try {
        generarMazo('imposible');
    } catch (e) {
        errorLanzado = true;
    }
    assert(errorLanzado, 'generarMazo() lanza error con dificultad inválida');

    // ===== Test 5: formatearTiempo =====
    assertEquals(formatearTiempo(0), '00:00', 'formatearTiempo(0) = 00:00');
    assertEquals(formatearTiempo(59), '00:59', 'formatearTiempo(59) = 00:59');
    assertEquals(formatearTiempo(60), '01:00', 'formatearTiempo(60) = 01:00');
    assertEquals(formatearTiempo(125), '02:05', 'formatearTiempo(125) = 02:05');

    // ===== Test 6: calcularPuntaje =====
    const puntajePerfecto = calcularPuntaje(8, 30, 'medio');
    assert(puntajePerfecto > 0, 'calcularPuntaje() devuelve valor positivo');

    const puntajeMalo = calcularPuntaje(500, 600, 'medio');
    assertEquals(puntajeMalo, 0, 'calcularPuntaje() no devuelve negativos');

    const puntajeFacil = calcularPuntaje(10, 60, 'facil');
    const puntajeExperto = calcularPuntaje(10, 60, 'experto');
    assert(puntajeExperto > puntajeFacil, 'Experto da más puntaje que Fácil (mismo rendimiento)');

    // ===== Test 7: Los emojis son únicos en el mazo =====
    const mazoUnico = generarMazo('facil');
    const emojisUnicos = new Set(mazoUnico.map(c => c.emoji));
    assertEquals(emojisUnicos.size, 4, 'Fácil usa 4 emojis únicos');

    // ===== Resultado final =====
    console.log(`\n📊 Resultados: ${pasados} pasados, ${fallados} fallados`);
    if (fallados === 0) {
        console.log('🎉 ¡Todos los tests pasaron!');
    } else {
        console.error('⚠️ Hay tests fallando.');
    }

    // Exponer resultado globalmente
    window.__testResultado = { pasados, fallados };
})();
