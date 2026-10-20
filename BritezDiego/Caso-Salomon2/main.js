// main.js — motor del juego: personajes, animación del programa, preguntas en el juzgado y veredicto
'use strict';

const $ = id => document.getElementById(id);
let rol = 'ella', beat = 0, timer = null, pausado = false, q = 0, puntos = 0, resp = [], posBuena = [], modo = 'facil', hist = [];
const MAX = PREGUNTAS.length * 2;

// ---------- Personaje formal dibujado en SVG ----------
function persona(o) {
  const c = o.pelo || '#3B2A20';
  const pelo = o.g === 'ella'
    ? `<path d="M14 28Q12 5 30 5Q48 5 46 28V46Q43 49 40 42V26Q30 14 20 26V42Q17 49 14 46Z" fill="${c}"/>`
    : `<path d="M17 23Q17 7 30 7Q43 7 43 23Q36 15 17 23Z" fill="${c}"/>`;
  return `<svg viewBox="0 0 60 110" width="60" height="110">
    <rect x="19" y="78" width="9" height="26" rx="3" fill="#34405A"/><rect x="32" y="78" width="9" height="26" rx="3" fill="#34405A"/>
    <ellipse cx="23" cy="106" rx="8" ry="4" fill="#26303F"/><ellipse cx="37" cy="106" rx="8" ry="4" fill="#26303F"/>
    <rect x="6" y="42" width="9" height="34" rx="4.5" fill="${o.saco}"/><rect x="45" y="42" width="9" height="34" rx="4.5" fill="${o.saco}"/>
    <path d="M13 44Q13 38 22 38H38Q47 38 47 44V82H13Z" fill="${o.saco}"/>
    <path d="M23 38L30 54L37 38Z" fill="#fff"/><path d="M28 46h4l2.5 20-4.5 4-4.5-4z" fill="${o.corbata}"/>
    <circle cx="30" cy="24" r="13" fill="#F2C9A5"/>${pelo}
    <circle cx="24.5" cy="25" r="1.6" fill="#222"/><circle cx="35.5" cy="25" r="1.6" fill="#222"/>
    <path class="sonrisa" d="M25.5 31Q30 35 34.5 31" stroke="#9A5A4A" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <path class="triste" d="M25.5 34Q30 30 34.5 34" stroke="#9A5A4A" stroke-width="1.6" fill="none" stroke-linecap="round"/>
    <circle class="lagrima" cx="24" cy="28" r="1.5" fill="#8DB5D6"/></svg>`;
}
const yo = () => ({ g: rol, saco: '#3E4C6B', corbata: '#E07A6F', pelo: rol === 'ella' ? '#5A3A28' : '#3B2A20' });

// ---------- Pantallas ----------
function ir(id) { document.querySelectorAll('.pantalla').forEach(s => s.classList.toggle('activa', s.id === id)); clearTimeout(timer); if (id === 'cine') { escalar(); verBeat(0); } }
function escalar() { $('est').style.setProperty('--s', Math.min(innerWidth / 960, (innerHeight - 190) / 540)); }
addEventListener('resize', escalar);

// ---------- Inicio y fichas ----------
document.querySelectorAll('.chip').forEach(b => b.onclick = () => { // un grupo para el rol y otro para la dificultad
  const k = b.dataset.r ? 'r' : 'm';
  if (k === 'r') rol = b.dataset.r; else modo = b.dataset.m;
  document.querySelectorAll(`.chip[data-${k}]`).forEach(x => x.classList.toggle('sel', x === b));
});
fetch('/api/estado').then(r => r.json()).then(d => { $('estadoIA').textContent = d.ia ? `Jueza con IA conectada (${d.modelo})` : 'Modo sin IA: falta la clave ANTHROPIC_API_KEY; la jueza usa criterios locales.'; })
  .catch(() => { $('estadoIA').textContent = 'Sin servidor de IA: el modo Difícil necesita ejecutar "python3 servidor.py".'; });
$('bEmp').onclick = () => {
  const carta = (o, n, r) => `<div class="carta">${persona(o)}<b>${n}</b><span>${r}</span></div>`;
  $('cartas').innerHTML = carta(yo(), rol === 'ella' ? 'Vos, la abogada' : 'Vos, el abogado', 'Defendés a Beatriz y a sus hijas en el juicio.') +
    PERSONAJES.map(p => carta(p, p.nombre, p.rol)).join('');
  $('otros').textContent = OTROS; ir('fichas');
};
$('bVer').onclick = () => ir('cine');

// ---------- Animación del programa (relato narrado) ----------
// Ilustración animada de los involucrados (inicio y juzgado)
$('foto').innerHTML = PERSONAJES.map((p, i) => `<figure class="${i < 2 ? 'a' : 'b'}">${persona(p)}<figcaption>${p.nombre}</figcaption></figure>`).join('');
$('elenco').innerHTML = PERSONAJES.map(p => persona(p)).join('');

(function montarCine() {
  $('personas').innerHTML = PERSONAJES.map(p => `<div class="per ${p.id}${p.pareja ? ' pareja' : ''}" data-id="${p.id}">${persona(p)}</div>`).join('');
  let m = ''; // mosaico borroso: la imagen de la cámara oculta no se muestra
  for (let i = 0; i < 12; i++) for (let j = 0; j < 4; j++) { const v = 90 + Math.random() * 90 | 0; m += `<rect x="${314 + i * 27.67}" y="${82 + j * 28.5}" width="27.7" height="28.6" fill="rgb(${v},${v},${v + 8})"/>`; }
  $('mosaico').innerHTML = m;
})();

function verBeat(i) {
  beat = Math.max(0, Math.min(BEATS.length - 1, i)); const B = BEATS[beat], c = $('cine');
  $('subt').textContent = B.t;
  c.classList.toggle('ent', beat >= 1); c.classList.toggle('cam', beat >= 2 && beat <= 4); c.classList.toggle('osc', beat === 5);
  $('bantxt').textContent = beat === 4 ? 'REPETICIÓN · 7 OCT' : 'CÁMARA OCULTA';
  document.querySelectorAll('.per').forEach(p => {
    p.classList.toggle('habla', B.habla.includes(p.dataset.id));
    p.classList.toggle('rie', beat === 4 && (p.dataset.id === 'jorge' || p.dataset.id === 'luis'));
    if (p.dataset.id === 'beatriz') p.classList.toggle('llora', beat >= 3);
  });
  $('fecha').textContent = B.fecha; $('fecha').classList.toggle('oculto', !B.fecha);
  $('puntos').innerHTML = BEATS.map((_, k) => `<i class="${k === beat ? 'on' : ''}"></i>`).join('');
  $('bAdel').textContent = beat === BEATS.length - 1 ? '⚖ Al juzgado' : '▶';
  clearTimeout(timer);
  if (!pausado && beat < BEATS.length - 1) timer = setTimeout(() => verBeat(beat + 1), 8000);
}
// Mezcla uniforme (Fisher-Yates)
function mezclar(a) { for (let i = a.length - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; } return a; }
const alJuzgado = () => { clearTimeout(timer); q = 0; puntos = 0; resp = []; hist = []; $('med').style.width = '0'; posBuena = mezclar([0, 1, 2, 0, 1, 2, Math.random() * 3 | 0, Math.random() * 3 | 0]); ir('juzgado'); pregunta(); };
$('bAtras').onclick = () => verBeat(beat - 1);
$('bAdel').onclick = () => beat === BEATS.length - 1 ? alJuzgado() : verBeat(beat + 1);
$('bPausa').onclick = () => { pausado = !pausado; $('bPausa').textContent = pausado ? '▶' : '⏸'; verBeat(beat); };
$('bSalta').onclick = alJuzgado;

// ---------- Juzgado: preguntas y decisiones ----------
function pregunta() {
  const P = PREGUNTAS[q], H = P.quien === 'jueza' ? JUEZA : ABOGADO;
  $('qn').textContent = `Pregunta ${q + 1} de ${PREGUNTAS.length}`;
  $('orador').innerHTML = persona(H) + `<span>${H.nombre}</span>`;
  $('quien').textContent = H.nombre; $('texto').textContent = P.texto; $('fb').classList.add('oculto'); $('bSig').classList.remove('oculto');
  const libre = modo === 'dificil'; // en el modo difícil se escribe el argumento
  $('ops').classList.toggle('oculto', libre); $('libre').classList.toggle('oculto', !libre);
  $('argumento').value = ''; $('bEnviar').disabled = false; $('bEnviar').textContent = 'Presentar argumento';
  // La opción correcta se reparte entre las 3 posiciones; las otras dos van en orden al azar
  const buena = P.ops.find(o => o.p === 2), ops = mezclar(P.ops.filter(o => o !== buena)); ops.splice(posBuena[q], 0, buena);
  $('ops').innerHTML = '';
  ops.forEach(o => {
    const b = document.createElement('button'); b.className = 'op'; b.textContent = o.t;
    b.onclick = () => elegir(o, b, ops); $('ops').appendChild(b);
  });
}
function elegir(o, b) {
  puntos += o.p; resp.push(o.p);
  document.querySelectorAll('.op').forEach(x => x.disabled = true);
  b.classList.add(o.p === 2 ? 'buena' : o.p === 1 ? 'media' : 'mala');
  $('fbt').textContent = (o.p === 2 ? '✔ Muy buena respuesta. ' : o.p === 1 ? '➖ Respuesta parcial. ' : '✖ Respuesta débil. ') + o.e;
  $('med').style.width = (puntos / MAX * 100) + '%';
  $('bSig').textContent = q === PREGUNTAS.length - 1 ? 'Escuchar la sentencia' : 'Siguiente';
  $('fb').classList.remove('oculto');
}
$('bSig').onclick = () => { if (++q < PREGUNTAS.length) pregunta(); else veredicto(); };

// ---------- Modo difícil: la jueza (IA) evalúa el argumento escrito ----------
async function api(ruta, cuerpo) {
  const r = await fetch(ruta, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(cuerpo) });
  const d = await r.json(); if (!r.ok || d.error) throw new Error(d.error || r.status); return d;
}
const citas = f => f && f.length ? `  Fuentes: ${f.join(', ')}.` : '';
$('bEnviar').onclick = async () => {
  const txt = $('argumento').value.trim();
  if (txt.length < 20) { $('argumento').placeholder = 'Escriba al menos una o dos oraciones con su argumento.'; return; }
  $('bEnviar').disabled = true; $('bEnviar').textContent = 'La jueza está deliberando…';
  try {
    const r = await api('/api/evaluar', { n: q, respuesta: txt, historial: hist });
    puntos += r.puntos; resp.push(r.puntos);
    hist.push({ tema: PREGUNTAS[q].tema, respuesta: txt, puntos: r.puntos, comentario: r.comentario });
    $('libre').classList.add('oculto');
    $('fbt').textContent = r.comentario + citas(r.fuentes) + (r.modo === 'local' ? ' (Modo sin IA)' : '');
    $('med').style.width = (puntos / MAX * 100) + '%';
    $('bSig').textContent = q === PREGUNTAS.length - 1 ? 'Escuchar la sentencia' : 'Siguiente';
  } catch (e) {
    $('bEnviar').disabled = false; $('bEnviar').textContent = 'Presentar argumento';
    $('fbt').textContent = 'No pude conectar con la jueza. Ejecute "python3 servidor.py" en la carpeta del juego y recargue la página.'; $('bSig').classList.add('oculto');
  }
  $('fb').classList.remove('oculto');
};

// ---------- Veredicto ----------
async function veredicto() {
  const n = [2, 1, 0].map(v => resp.filter(x => x === v).length), pct = Math.round(puntos / MAX * 100);
  ir('final');
  let V = VEREDICTOS.find(v => puntos >= v.min), cons = '';
  if (modo === 'dificil') { // la jueza dicta sentencia considerando todo el desarrollo
    $('vTit').className = ''; $('vTit').textContent = 'La jueza está deliberando…'; $('vTxt').textContent = ''; $('vCons').textContent = '';
    try {
      const s = await api('/api/sentencia', { historial: hist });
      V = { t: s.titulo, c: { favorable: 'verde', parcial: 'azul', rechazada: 'coral' }[s.resultado] || 'azul', x: s.texto };
      cons = (s.consejo ? 'Consejo de la jueza: ' + s.consejo : '') + citas(s.fuentes);
    } catch (e) { cons = 'No pude conectar con la jueza; se muestra la sentencia calculada por puntaje.'; }
  }
  $('vTit').textContent = V.t; $('vTit').className = V.c; $('vTxt').textContent = V.x; $('vCons').textContent = cons;
  $('vPts').textContent = `Solidez del caso: ${pct} % · ${n[0]} respuestas muy buenas, ${n[1]} parciales y ${n[2]} débiles (de ${PREGUNTAS.length} preguntas)`;
  $('vLista').innerHTML = PREGUNTAS.map((p, i) => `<li>${resp[i] === 2 ? '✔' : resp[i] === 1 ? '➖' : '✖'} ${p.tema}</li>`).join('');
}
$('bReal').onclick = () => { $('linea').innerHTML = REALIDAD.map(r => `<li><b>${r[0]}:</b> ${r[1]}</li>`).join(''); $('real').classList.add('activo'); };
$('bCerrar').onclick = () => $('real').classList.remove('activo');
$('bOtra').onclick = () => ir('titulo');
