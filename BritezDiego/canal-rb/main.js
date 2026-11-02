// main.js — Primicia (Fase 1): menú, personaje, oficina, estrellas, pausa y guardado
'use strict';

const $ = id => document.getElementById(id);
const CLAVE = 'primicia_v1';

// Las tres tareas del día (una estrella cada una)
const PUERTAS = [
  { x: 190, color: 'coral', nombre: 'Redacción', texto: 'Acá vas a armar la nota sobre el accidente en Avenida San Martín y Juan Domingo Perón: título, bajada, cuerpo y cierre, con cuidado en lo que está o no confirmado.' },
  { x: 480, color: 'verde', nombre: 'Producción', texto: 'Acá vas a armar la grilla del programa (clima, deportes, política y espectáculos) y a decidir qué hacer con la noticia de último momento.' },
  { x: 770, color: 'azul', nombre: 'Al Aire', texto: 'Acá vas a presentar el noticiero siguiendo la grilla que armaste, y a leer la noticia de último momento en el orden correcto.' },
];

const V = 230;                                        // velocidad al caminar (px/s)
const LIM = { x0: 40, x1: 920, y0: 262, y1: 520 };    // zona caminable
const MESAS = [[80, 240, 350, 430], [720, 880, 350, 430]]; // escritorios (bloqueados)

let datos = { nombre: '', genero: 'el', hechas: [false, false, false], fin: false };
let estado = 'titulo', P = { x: 480, y: 450, dir: 1 }, destino = null, actual = 0, ult = 0, genSel = 'el', tAviso;
const teclas = new Set();

// ---------- Guardado (localStorage) ----------
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(datos)); } catch (e) { /* sin guardado */ } };
function cargar() {
  try { const d = JSON.parse(localStorage.getItem(CLAVE)); return d && d.nombre ? d : null; } catch (e) { return null; }
}

// ---------- Personaje formal: camisa, saco, corbata y anteojos ----------
function personajeSVG(g) {
  const saco = '#3E4C6B';
  const pelo = g === 'ella'
    ? '<path d="M14 28Q12 5 30 5Q48 5 46 28V46Q43 49 40 42V26Q30 14 20 26V42Q17 49 14 46Z" fill="#5A3A28"/>'
    : '<path d="M17 23Q17 7 30 7Q43 7 43 23Q36 15 17 23Z" fill="#3B2A20"/>';
  return `<svg viewBox="0 0 60 110" width="60" height="110">
    <rect x="19" y="78" width="9" height="26" rx="3" fill="#34405A"/><rect x="32" y="78" width="9" height="26" rx="3" fill="#34405A"/>
    <ellipse cx="23" cy="106" rx="8" ry="4" fill="#26303F"/><ellipse cx="37" cy="106" rx="8" ry="4" fill="#26303F"/>
    <rect x="6" y="42" width="9" height="34" rx="4.5" fill="${saco}"/><rect x="45" y="42" width="9" height="34" rx="4.5" fill="${saco}"/>
    <path d="M13 44Q13 38 22 38H38Q47 38 47 44V82H13Z" fill="${saco}"/>
    <path d="M23 38L30 54L37 38Z" fill="#fff"/><path d="M28 46h4l2.5 20-4.5 4-4.5-4z" fill="#E07A6F"/>
    <circle cx="30" cy="24" r="13" fill="#F2C9A5"/>${pelo}
    <circle cx="24" cy="25" r="4.6" fill="none" stroke="#222" stroke-width="1.6"/><circle cx="36" cy="25" r="4.6" fill="none" stroke="#222" stroke-width="1.6"/>
    <path d="M28.6 25h2.8" stroke="#222" stroke-width="1.6"/><circle cx="24" cy="25" r="1.4" fill="#222"/><circle cx="36" cy="25" r="1.4" fill="#222"/>
    <path d="M25.5 31Q30 35 34.5 31" stroke="#9A5A4A" stroke-width="1.6" fill="none" stroke-linecap="round"/></svg>`;
}

// ---------- Pantallas y ventanas ----------
function ir(id) { document.querySelectorAll('.pantalla').forEach(s => s.classList.toggle('activa', s.id === id)); estado = id; }
const modal = (id, on) => $(id).classList.toggle('activo', on);
function aviso(t) {
  const a = $('aviso'); a.textContent = t; a.classList.add('ver');
  clearTimeout(tAviso); tAviso = setTimeout(() => a.classList.remove('ver'), 2200);
}
function volverMenu() {
  ['pausa', 'final', 'tarea', 'ayuda'].forEach(m => modal(m, false));
  ir('titulo'); $('bReanudar').classList.toggle('oculto', !cargar());
}
function marcar() { document.querySelectorAll('.tarjeta').forEach(t => t.classList.toggle('sel', t.dataset.g === genSel)); }

function entrarOficina() {
  ir('oficina'); P = { x: 480, y: 450, dir: 1 }; destino = null;
  $('yo').innerHTML = `<div class="flip"><div class="bob">${personajeSVG(datos.genero)}</div></div>`;
  $('hNombre').textContent = datos.nombre; pintarPuertas();
}
function pintarPuertas() {
  PUERTAS.forEach((p, i) => {
    const g = $('p' + i);
    g.classList.toggle('bloq', i > 0 && !datos.hechas[i - 1]);
    g.classList.toggle('hecha', datos.hechas[i]);
  });
  document.querySelectorAll('#hEstrellas i').forEach((e, i) => { e.className = datos.hechas[i] ? PUERTAS[i].color : ''; });
}

// ---------- Tareas ----------
function abrirTarea(i) {
  actual = i; destino = null; P.y = 330; teclas.clear();
  $('tTitulo').textContent = PUERTAS[i].nombre; $('tTitulo').className = PUERTAS[i].color;
  $('tTexto').textContent = PUERTAS[i].texto; modal('tarea', true);
}
function revisarPuertas() {
  if (P.y > 292) return;
  PUERTAS.forEach((p, i) => {
    if (Math.abs(P.x - p.x) > 48) return;
    if (i > 0 && !datos.hechas[i - 1]) { aviso('Primero completá ' + PUERTAS[i - 1].nombre); P.y = 320; destino = null; return; }
    abrirTarea(i);
  });
}

// ---------- Movimiento ----------
const libre = (x, y) => x >= LIM.x0 && x <= LIM.x1 && y >= LIM.y0 && y <= LIM.y1 &&
  !MESAS.some(m => x > m[0] && x < m[1] && y > m[2] && y < m[3]);

function bucle(t) {
  requestAnimationFrame(bucle);
  const dt = Math.min((t - ult) / 1000, .05); ult = t;
  if (estado !== 'oficina' || document.querySelector('.modal.activo')) return;
  let dx = (teclas.has('d') || teclas.has('arrowright') ? 1 : 0) - (teclas.has('a') || teclas.has('arrowleft') ? 1 : 0);
  let dy = (teclas.has('s') || teclas.has('arrowdown') ? 1 : 0) - (teclas.has('w') || teclas.has('arrowup') ? 1 : 0);
  if (dx || dy) destino = null;
  else if (destino) {
    const ex = destino.x - P.x, ey = destino.y - P.y, d = Math.hypot(ex, ey);
    if (d < 6) destino = null; else { dx = ex / d; dy = ey / d; }
  }
  let movio = false;
  if (dx || dy) {
    const n = Math.hypot(dx, dy), ax = dx / n * V * dt, ay = dy / n * V * dt;
    if (libre(P.x + ax, P.y)) { P.x += ax; movio = movio || ax !== 0; }
    if (libre(P.x, P.y + ay)) { P.y += ay; movio = movio || ay !== 0; }
    if (dx) P.dir = dx > 0 ? 1 : -1;
    if (!movio) destino = null; // chocó con algo
    revisarPuertas();
  }
  const yo = $('yo');
  yo.classList.toggle('camina', movio);
  yo.style.left = P.x - 30 + 'px'; yo.style.top = P.y - 108 + 'px';
  if (yo.firstChild) yo.firstChild.style.transform = `scaleX(${P.dir})`;
}

function escalar() { $('escenario').style.setProperty('--s', Math.min(innerWidth / 960, innerHeight / 540)); }

function alternarPausa() {
  if ($('ayuda').classList.contains('activo')) return modal('ayuda', false);
  if ($('pausa').classList.contains('activo')) return modal('pausa', false);
  if (estado === 'oficina' && !document.querySelector('.modal.activo')) modal('pausa', true);
}

// ---------- Eventos ----------
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') { if (e.key === 'Enter') $('bEmpezar').click(); return; }
  const k = e.key.toLowerCase();
  if (k === 'escape' || k === 'p') { alternarPausa(); return; }
  if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(k)) e.preventDefault();
  teclas.add(k);
});
addEventListener('keyup', e => teclas.delete(e.key.toLowerCase()));
addEventListener('blur', () => teclas.clear());
addEventListener('resize', escalar);

// Tocar o hacer clic para caminar hacia ese punto
$('escenario').addEventListener('pointerdown', e => {
  if (estado !== 'oficina' || document.querySelector('.modal.activo')) return;
  const r = $('escenario').getBoundingClientRect(), s = r.width / 960;
  destino = { x: Math.min(LIM.x1, Math.max(LIM.x0, (e.clientX - r.left) / s)), y: Math.min(LIM.y1, Math.max(LIM.y0, (e.clientY - r.top) / s)) };
});

document.querySelectorAll('.tarjeta').forEach(t => {
  t.querySelector('.dibujo').innerHTML = personajeSVG(t.dataset.g);
  t.onclick = () => { genSel = t.dataset.g; marcar(); };
});

$('bIniciar').onclick = () => {
  if (cargar() && !confirm('Ya tenés un avance guardado. ¿Querés empezar de nuevo?')) return;
  ir('personaje'); marcar(); $('nombre').focus();
};
$('bReanudar').onclick = () => { datos = cargar(); entrarOficina(); };
$('bEmpezar').onclick = () => {
  datos = { nombre: $('nombre').value.trim() || 'Periodista', genero: genSel, hechas: [false, false, false], fin: false };
  guardar(); entrarOficina();
};
$('bAyuda').onclick = $('bAyuda2').onclick = () => modal('ayuda', true);
$('bCerrarAyuda').onclick = () => modal('ayuda', false);
$('bPausa').onclick = alternarPausa;
$('bReanudar2').onclick = () => modal('pausa', false);
$('bSalir').onclick = volverMenu;
$('bVolver').onclick = () => modal('tarea', false);
$('bSeguir').onclick = () => modal('final', false);
$('bMenu').onclick = volverMenu;
$('bCompletar').onclick = () => { // modo prueba: en las próximas fases se completa jugando
  datos.hechas[actual] = true; modal('tarea', false); pintarPuertas();
  if (datos.hechas.every(Boolean)) {
    datos.fin = true;
    $('fMensaje').textContent = `¡Excelente trabajo, ${datos.nombre}! Cerraste tu primer día completo en Canal RB: la redacción, la producción y el aire salieron redondos. Mañana te esperan nuevas tareas. ¡Descansá, que te lo ganaste!`;
    modal('final', true);
  }
  guardar();
};

escalar(); volverMenu(); requestAnimationFrame(bucle);
