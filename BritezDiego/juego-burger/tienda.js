// tienda.js — catálogo de la tienda y guardado persistente (localStorage)
export const CLAVE = 'burgerRunner_v2';

export const SOMBREROS = [
  { id: 'ninguno', nombre: 'Sin sombrero', precio: 0 },
  { id: 'gorra', nombre: 'Gorra roja', precio: 50 },
  { id: 'birrete', nombre: 'Birrete', precio: 80 },
  { id: 'corona', nombre: 'Corona', precio: 120 },
];

export const PERSONAJES = [
  { id: 'burger', nombre: 'Hamburguesa con anteojos', precio: 0 },
  { id: 'esponja', nombre: 'Señor Esponjoso', precio: 240 },
  { id: 'alga', nombre: 'Doctor Alga', precio: 790 },
];

const porDefecto = () => ({ monedas: 0, comprados: ['ninguno', 'burger'], sombrero: 'ninguno', personaje: 'burger', ranking: [] });

function cargar() {
  try { return Object.assign(porDefecto(), JSON.parse(localStorage.getItem(CLAVE) || '{}')); }
  catch (e) { return porDefecto(); }
}

export const guardado = cargar();

export function guardar() {
  try { localStorage.setItem(CLAVE, JSON.stringify(guardado)); } catch (e) { /* modo privado: se ignora */ }
}

// Compra un artículo si alcanzan las monedas. Devuelve true si se pudo.
export function comprar(id) {
  const it = [...SOMBREROS, ...PERSONAJES].find(x => x.id === id);
  if (!it || guardado.comprados.includes(id) || guardado.monedas < it.precio) return false;
  guardado.monedas -= it.precio;
  guardado.comprados.push(id);
  guardar();
  return true;
}

// tipo: 'p' = personaje, 's' = sombrero
export function equipar(tipo, id) {
  if (!guardado.comprados.includes(id)) return;
  if (tipo === 'p') guardado.personaje = id; else guardado.sombrero = id;
  guardar();
}
