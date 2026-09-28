export const NIVELES = [
  // NIVEL 1: fácil, corto, pocos obstáculos
  {
    nombre: 'Fácil',
    meta: 300,                 // metros
    velocidadInicial: 10,
    velocidadMaxima: 14,
    aceleracion: 0.15,
    separacion: 22,            // cada cuántos metros aparece algo
    probObstaculo: 0.35,
    probMoneda: 0.45,
    probIngrediente: 0.25,
  },
  // NIVEL 2: medio, más obstáculos
  {
    nombre: 'Medio',
    meta: 450,
    velocidadInicial: 12,
    velocidadMaxima: 18,
    aceleracion: 0.25,
    separacion: 16,
    probObstaculo: 0.5,
    probMoneda: 0.4,
    probIngrediente: 0.2,
  },
  // NIVEL 3: medio-difícil, meta más lejos
  {
    nombre: 'Difícil',
    meta: 600,
    velocidadInicial: 14,
    velocidadMaxima: 22,
    aceleracion: 0.35,
    separacion: 12,
    probObstaculo: 0.6,
    probMoneda: 0.35,
    probIngrediente: 0.15,
  },
];