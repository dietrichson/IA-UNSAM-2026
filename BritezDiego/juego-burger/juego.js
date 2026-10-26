// juego.js — Burger Runner 2: escena 3D, niveles, power-ups, menús y pantallas
import * as THREE from 'three';
import { guardado, guardar, SOMBREROS, PERSONAJES, comprar, equipar } from './tienda.js';

const CARRILES = [-2.2, 0, 2.2];
const PALABRA = 'TOMATE';
const NIVELES = [
  { nombre: 'Fácil', vel: 13, seg: 35, sepa: 22 },
  { nombre: 'Medio: TOMATE', vel: 16, seg: 50, sepa: 20 },
  { nombre: 'Difícil: lluvia de dientes', vel: 19, seg: 50, sepa: 18 },
  { nombre: 'Jefe final: F o clic disparan', vel: 12, seg: 9999, sepa: 20 },
];
const $ = id => document.getElementById(id);

// ---------- Sonido (WebAudio, sin archivos) ----------
let audio;
function tono(f, d = .12, tipo = 'sine') {
  try {
    audio = audio || new AudioContext();
    const o = audio.createOscillator(), g = audio.createGain();
    o.type = tipo; o.frequency.value = f;
    g.gain.setValueAtTime(.12, audio.currentTime);
    g.gain.exponentialRampToValueAtTime(.001, audio.currentTime + d);
    o.connect(g).connect(audio.destination); o.start(); o.stop(audio.currentTime + d);
  } catch (e) { /* sin audio */ }
}

// ---------- Escena, luces cálidas y sombras suaves ----------
const render = new THREE.WebGLRenderer({ antialias: true });
render.shadowMap.enabled = true;
render.shadowMap.type = THREE.PCFSoftShadowMap;
$('escena').appendChild(render.domElement);
const escena = new THREE.Scene();
escena.background = new THREE.Color(0x8fd8d8);
escena.fog = new THREE.Fog(0x8fd8d8, 25, 70);
const cam = new THREE.PerspectiveCamera(60, 1, .1, 100);
cam.position.set(0, 4.2, 7); cam.lookAt(0, 1, -6);
const hemi = new THREE.HemisphereLight(0xfff2d6, 0xc79a5b, 1.1); escena.add(hemi);
const sol = new THREE.DirectionalLight(0xffe0a8, 1.6);
sol.position.set(5, 14, -4); sol.target.position.set(0, 0, -10);
sol.castShadow = true; sol.shadow.mapSize.set(1024, 1024); sol.shadow.radius = 4;
Object.assign(sol.shadow.camera, { left: -12, right: 12, top: 20, bottom: -20, far: 50 });
escena.add(sol, sol.target);
function ajustar() {
  render.setPixelRatio(Math.min(devicePixelRatio, 2));
  render.setSize(innerWidth, innerHeight);
  cam.aspect = innerWidth / innerHeight;
  cam.fov = cam.aspect < 1 ? 75 : 60; // más ancho de campo en pantallas verticales
  cam.updateProjectionMatrix();
}
addEventListener('resize', ajustar); ajustar();

// Suelo de arena y rayas de carril que se mueven
const suelo = new THREE.Mesh(new THREE.PlaneGeometry(9, 200), new THREE.MeshStandardMaterial({ color: 0xf0cf8e, roughness: 1 }));
suelo.rotation.x = -Math.PI / 2; suelo.position.z = -70; suelo.receiveShadow = true; escena.add(suelo);
const lado = new THREE.Mesh(new THREE.PlaneGeometry(140, 220), new THREE.MeshStandardMaterial({ color: 0x8d8a86, roughness: 1 }));
lado.rotation.x = -Math.PI / 2; lado.position.set(0, -.03, -70); escena.add(lado); // terreno a los costados
const rayas = [];
for (const x of [-1.1, 1.1]) for (let i = 0; i < 16; i++) {
  const r = new THREE.Mesh(new THREE.BoxGeometry(.12, .02, 1.6), new THREE.MeshStandardMaterial({ color: 0xd9a95a }));
  r.position.set(x * 2, .01, -i * 4); escena.add(r); rayas.push(r);
}

// ---------- Ayudas de geometría (formas redondeadas) ----------
const mat = (c, e = 0) => new THREE.MeshToonMaterial({ color: c, emissive: c, emissiveIntensity: e });
const CONTORNO = new THREE.MeshBasicMaterial({ color: 0x3a2412, side: THREE.BackSide });
// Estilo caricatura: cada malla lleva un contorno oscuro (casco invertido)
const malla = (g, c, e = 0) => { const m = new THREE.Mesh(g, mat(c, e)); m.castShadow = true; const o = new THREE.Mesh(g, CONTORNO); o.scale.setScalar(1.07); m.add(o); return m; };
const esf = (r, c, sx = 1, sy = 1, sz = 1) => { const m = malla(new THREE.SphereGeometry(r, 24, 16), c); m.scale.set(sx, sy, sz); return m; };
const cil = (r, h, c, s = 20) => malla(new THREE.CylinderGeometry(r, r, h, s), c);
const pos = (m, x, y, z) => { m.position.set(x, y, z); return m; };

// Ficha redonda con texto (para letras y bolsas)
function etiqueta(txt, col = '#ffd23f', tam = 1.6) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const x = c.getContext('2d');
  x.lineWidth = 8; x.strokeStyle = '#8a5a00';
  if (col) { x.fillStyle = col; x.beginPath(); x.arc(64, 64, 60, 0, 7); x.fill(); x.stroke(); }
  x.font = `bold ${txt.length > 1 ? 54 : 72}px Fredoka, Arial`; x.textAlign = 'center'; x.textBaseline = 'middle';
  if (!col) { x.lineWidth = 10; x.strokeText(txt, 64, 70); }
  x.fillStyle = col ? '#5b3a00' : '#fff3c4'; x.fillText(txt, 64, 70);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c) }));
  s.scale.set(tam, tam, 1); return s;
}

// Textura de moneda: dorada con carita sonriente
const TEX_MON = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const x = c.getContext('2d'), g = x.createRadialGradient(50, 50, 10, 64, 64, 64);
  g.addColorStop(0, '#fff3a0'); g.addColorStop(1, '#e0a412');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  x.strokeStyle = x.fillStyle = '#a56a00'; x.lineWidth = 8;
  x.beginPath(); x.arc(64, 64, 54, 0, 7); x.stroke();
  x.beginPath(); x.arc(46, 52, 7, 0, 7); x.arc(82, 52, 7, 0, 7); x.fill();
  x.lineWidth = 6; x.beginPath(); x.arc(64, 68, 26, .15 * Math.PI, .85 * Math.PI); x.stroke();
  return new THREE.CanvasTexture(c);
})();

// ---------- Personajes ----------
function crearPersonaje(tipo, somb) {
  const g = new THREE.Group(), c = new THREE.Group(); g.add(c);
  let zc = .7, yc = 1.15;
  if (tipo === 'esponja') {
    const b = malla(new THREE.CapsuleGeometry(.55, .5, 8, 16), 0xf7d64a); b.scale.z = .6; c.add(pos(b, 0, .75, 0));
    c.add(pos(cil(.6, .25, 0x7a4a20), 0, .3, 0), pos(cil(.57, .12, 0xffffff), 0, .48, 0)); // pantalón y camisa
    for (const [px, py] of [[-.3, 1.15], [.32, 1.0], [-.25, .72], [.28, .66], [0, 1.35]]) c.add(pos(esf(.07, 0xd9b52a, 1, 1, .4), px, py, .3)); // poros
    c.add(pos(malla(new THREE.BoxGeometry(.12, .16, .05), 0xffffff), -.07, .62, .36), pos(malla(new THREE.BoxGeometry(.12, .16, .05), 0xffffff), .07, .62, .36)); // dientitos
    zc = .36; yc = .95;
  } else if (tipo === 'alga') {
    c.add(pos(esf(.6, 0x59c25c, 1, 1.2, .9), 0, .75, 0));
    c.add(pos(cil(.03, .5, 0x2f7a33), .15, 1.7, 0), pos(esf(.08, 0xffe14a), .15, 1.98, 0));
    zc = .5; yc = .85;
  } else { // hamburguesa: pan, carne, queso derretido, lechuga, tomate, pan con semillas
    c.add(pos(esf(.75, 0xe8a24a, 1, .42, 1), 0, .32, 0));
    c.add(pos(cil(.74, .2, 0x5b3320, 24), 0, .6, 0));
    const q = malla(new THREE.BoxGeometry(1.5, .05, 1.5), 0xffc82e); q.rotation.y = Math.PI / 4; c.add(pos(q, 0, .74, 0));
    const l = malla(new THREE.TorusGeometry(.66, .1, 8, 24), 0x62b84a); l.rotation.x = Math.PI / 2; c.add(pos(l, 0, .8, 0));
    c.add(pos(cil(.6, .08, 0xe0432f, 24), 0, .88, 0));
    const pan = malla(new THREE.SphereGeometry(.75, 24, 14, 0, Math.PI * 2, 0, Math.PI / 2), 0xeaa64d); pan.scale.y = .85; c.add(pos(pan, 0, .92, 0));
    for (let i = 0; i < 6; i++) { const a = i * 1.1; c.add(pos(esf(.05, 0xfff1c8, 1, .5, 1), Math.cos(a) * .3, 1.5, Math.sin(a) * .3 - .1)); }
  }
  // Ojos y anteojos
  for (const s of [-1, 1]) {
    c.add(pos(esf(.17, 0xffffff), .27 * s, yc, zc), pos(esf(.11, 0x2a1a10), .27 * s, yc, zc + .1), pos(esf(.04, 0xffffff), .27 * s + .04, yc + .05, zc + .2));
    c.add(pos(malla(new THREE.TorusGeometry(.23, .035, 8, 20), 0x222222), .27 * s, yc, zc + .14));
    c.add(pos(esf(.08, 0xff8fa3, 1, .6, .4), .5 * s, yc - .22, zc - .05)); // cachetes
  }
  const puente = pos(cil(.03, .14, 0x222222), 0, yc, zc + .14); puente.rotation.z = Math.PI / 2; c.add(puente);
  const sonrisa = malla(new THREE.TorusGeometry(.17, .03, 6, 12, Math.PI), 0x6b2a1a); sonrisa.rotation.z = Math.PI; c.add(pos(sonrisa, 0, yc - .3, zc + .1));
  // Sombreros
  if (somb === 'gorra') { const h = malla(new THREE.SphereGeometry(.55, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), 0xd93a3a); c.add(pos(h, 0, 1.4, 0), pos(cil(.4, .05, 0xb02a2a), 0, 1.42, .55)); }
  if (somb === 'corona') { c.add(pos(cil(.4, .3, 0xffc400, 8), 0, 1.6, 0)); for (let i = 0; i < 4; i++) c.add(pos(malla(new THREE.ConeGeometry(.1, .25, 8), 0xffc400), Math.cos(i * 1.57) * .35, 1.85, Math.sin(i * 1.57) * .35)); }
  if (somb === 'birrete') { c.add(pos(cil(.35, .25, 0x222a44), 0, 1.6, 0), pos(malla(new THREE.BoxGeometry(1.1, .08, 1.1), 0x222a44), 0, 1.75, 0), pos(esf(.07, 0xffc400), .5, 1.65, .5)); }
  const piernas = [-1, 1].map(s => {
    const p = new THREE.Group();
    p.add(pos(cil(.05, .5, 0xf0c890), 0, -.25, 0), pos(esf(.16, 0x333333, 1, .6, 1.5), 0, -.5, .08));
    p.position.set(.3 * s, .5, 0); g.add(p); return p;
  });
  return { g, c, piernas };
}

// ---------- Obstáculos: 'alto' no se salta, 'bajo' sí ----------
function diente(k = 1) {
  const g = new THREE.Group();
  g.add(pos(esf(.6, 0xfffaf0, 1, .95, .9), 0, 1.15, 0));
  for (const s of [-1, 1]) {
    g.add(pos(esf(.22, 0xfffaf0, 1, .8, 1), .3 * s, 1.68, 0)); // cúspides
    const r = malla(new THREE.ConeGeometry(.2, .75, 10), 0xf2e4c4); r.rotation.z = Math.PI; g.add(pos(r, .3 * s, .4, 0)); // raíces
    g.add(pos(esf(.12, 0xffffff), .24 * s, 1.3, .5), pos(esf(.06, 0x222222), .24 * s, 1.3, .6));
    const ce = pos(malla(new THREE.BoxGeometry(.28, .06, .05), 0x7a4a20), .24 * s, 1.5, .55); ce.rotation.z = -.4 * s; g.add(ce); // ceño
  }
  const boca = malla(new THREE.TorusGeometry(.2, .035, 6, 12, Math.PI), 0x7a2a1a); boca.rotation.z = Math.PI; g.add(pos(boca, 0, .95, .55));
  g.scale.setScalar(k); return g;
}
const OBST = [
  () => { // tenedor
    const g = new THREE.Group(), m = 0xc9ced6;
    g.add(pos(cil(.12, 1.2, m), 0, .6, 0), pos(malla(new THREE.BoxGeometry(.8, .15, .15), m), 0, 1.25, 0));
    for (let i = -1.5; i <= 1.5; i++) g.add(pos(cil(.045, .9, 0xdfe3ea), i * .22, 1.75, 0));
    return { malla: g, tipo: 'alto', y: 0 };
  },
  () => ({ malla: diente(1), tipo: 'alto', y: 0 }), // muela
  () => { // libros apilados
    const g = new THREE.Group(), cols = [0x3b6ea5, 0xb5443a, 0x3f8f5b], p = () => cols[Math.random() * 3 | 0];
    g.add(pos(malla(new THREE.BoxGeometry(1.8, .36, 1.3), p()), 0, .18, 0), pos(malla(new THREE.BoxGeometry(1.6, .3, 1.2), p()), .05, .51, 0), pos(malla(new THREE.BoxGeometry(1.5, .1, 1.1), 0xfff1d0), 0, .3, .1));
    return { malla: g, tipo: 'bajo', y: 0 };
  },
  () => { // pozo
    const g = new THREE.Group(), r = malla(new THREE.TorusGeometry(.95, .12, 8, 28), 0x8a5a2b); r.rotation.x = Math.PI / 2;
    g.add(pos(cil(.95, .06, 0x2a1810, 28), 0, .03, 0), pos(r, 0, .05, 0));
    return { malla: g, tipo: 'bajo', y: 0 };
  },
  () => { // mano
    const g = new THREE.Group(), piel = 0xf2b98a;
    g.add(pos(esf(.5, piel, 1, .9, .6), 0, .9, 0), pos(cil(.3, .6, 0xffffff), 0, .3, 0));
    for (let i = 0; i < 5; i++) { const d = malla(new THREE.CapsuleGeometry(.09, .55, 4, 8), piel); d.rotation.z = (i - 2) * -.28; g.add(pos(d, (i - 2) * .24, 1.55 - Math.abs(i - 2) * .06, 0)); }
    return { malla: g, tipo: 'alto', y: 0 };
  },
];
function crearMoneda() {
  const g = new THREE.Group(), lado = cil(.45, .1, 0xd9a010); lado.rotation.x = Math.PI / 2; g.add(lado);
  for (const s of [1, -1]) { const cara = new THREE.Mesh(new THREE.CircleGeometry(.4, 24), new THREE.MeshBasicMaterial({ map: TEX_MON })); cara.position.z = .06 * s; cara.rotation.y = s > 0 ? 0 : Math.PI; g.add(cara); }
  return { malla: g, tipo: 'moneda', y: .9, gira: 1 };
}
function crearBolsa() {
  const g = new THREE.Group();
  g.add(pos(esf(.5, 0xd9a03a, .9, 1.15, .8), 0, .55, 0), pos(malla(new THREE.ConeGeometry(.22, .4, 10), 0xb37a22), 0, 1.15, 0), pos(cil(.16, .08, 0xd93a3a), 0, .98, 0), pos(etiqueta('$10', null, 1.1), 0, .55, .45));
  return { malla: g, tipo: 'bolsa', y: 0 };
}
// Ingredientes: frasco de mayonesa amarillo con piquito, tomate con hojitas y feta de queso cuadrada
function crearIng() {
  const n = ['mayonesa', 'tomate', 'queso'][Math.random() * 3 | 0], g = new THREE.Group();
  if (n === 'mayonesa') {
    g.add(pos(cil(.28, .6, 0xffd93b), 0, 0, 0), pos(cil(.29, .25, 0xffffff), 0, -.02, 0), pos(malla(new THREE.ConeGeometry(.16, .3, 12), 0xffd93b), 0, .42, 0), pos(cil(.05, .12, 0xfff7d6), 0, .62, 0));
  } else if (n === 'tomate') {
    g.add(pos(esf(.36, 0xe2503a, 1.1, .9, 1.1), 0, 0, 0), pos(esf(.08, 0xffffff, 1, .5, .5), -.15, .12, .32));
    for (let i = 0; i < 5; i++) { const h = malla(new THREE.ConeGeometry(.07, .22, 6), 0x3f9a3a); h.rotation.z = Math.PI / 2; h.rotation.y = i * 1.26; g.add(pos(h, Math.cos(i * 1.26) * .13, .33, Math.sin(i * 1.26) * .13)); }
  } else {
    const f = malla(new THREE.BoxGeometry(.7, .08, .7), 0xffc933, .15); f.rotation.x = .35; g.add(f);
    for (const [x, z] of [[-.15, .1], [.18, -.12], [.05, .2]]) g.add(pos(cil(.07, .1, 0xe0a112, 10), x, .02, z));
  }
  return { malla: g, tipo: 'ing', ing: n, y: 1.1, gira: 1 };
}
function crearEstrella() { // estrella celeste: sortea un poder
  const s = new THREE.Shape();
  for (let i = 0; i < 10; i++) { const rr = i % 2 ? .22 : .5, a = i * Math.PI / 5 + Math.PI / 2; i ? s.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : s.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); }
  return { malla: malla(new THREE.ExtrudeGeometry(s, { depth: .15, bevelEnabled: false }), 0x5fd0ff, .5), tipo: 'estrella', y: 1.2, gira: 1 };
}
function crearCorazon() {
  const s = new THREE.Shape(); s.moveTo(0, -.4); s.bezierCurveTo(-.7, .1, -.4, .6, 0, .25); s.bezierCurveTo(.4, .6, .7, .1, 0, -.4);
  return { malla: malla(new THREE.ExtrudeGeometry(s, { depth: .2, bevelEnabled: false }), 0xff4d6d, .3), tipo: 'corazon', y: 1.1, gira: 1 };
}
const pistola = () => { // pistola de agua
  const g = new THREE.Group(); g.add(pos(malla(new THREE.BoxGeometry(.18, .25, .5), 0x3aa7ff), 0, 0, 0), pos(cil(.06, .4, 0x2a7fd0), 0, .12, .3));
  g.children[1].rotation.x = Math.PI / 2; g.position.set(.7, 1, .5); return g;
};
function crearDiente() { return { malla: diente(1.5), tipo: 'lluvia', y: 12 }; } // diente gigante que cae

// ---------- Partículas ----------
const parts = [];
function chispas(x, y, z, col = 0xffd23f, n = 24) {
  for (let i = 0; i < n; i++) {
    const m = new THREE.Mesh(new THREE.SphereGeometry(.08, 6, 6), new THREE.MeshBasicMaterial({ color: col }));
    m.position.set(x, y, z); escena.add(m);
    parts.push({ m, v: new THREE.Vector3((Math.random() - .5) * 6, Math.random() * 5, (Math.random() - .5) * 6), t: .8 });
  }
}

// ---------- Decorados por nivel (se mueven con el mundo) ----------
const dec = [], R = (a, b) => a + Math.random() * (b - a);
const AMB = [
  { cielo: 0x9ad8ff, suelo: 0x6d7180, lado: 0x8d8a86 }, // 1 ciudad
  { cielo: 0xffd9a0, suelo: 0xeadfc8, lado: 0xc9a27a }, // 2 cocinas
  { cielo: 0xa8d8a0, suelo: 0xb08d57, lado: 0x6fae5a }, // 3 bosque y bocas
  { cielo: 0x2b0d14, suelo: 0x2a2226, lado: 0x1a1216 }, // 4 apocalipsis
];
function ambiente(n) {
  const a = AMB[n]; escena.background = new THREE.Color(a.cielo); escena.fog.color.set(a.cielo);
  escena.fog.near = n === 3 ? 35 : 25; escena.fog.far = n === 3 ? 100 : 70;
  suelo.material.color.set(a.suelo); lado.material.color.set(a.lado);
  hemi.color.set(n === 3 ? 0xff7a7a : 0xfff2d6); hemi.intensity = n === 3 ? .9 : 1.1; sol.color.set(n === 3 ? 0xff6a50 : 0xffe0a8);
}
function edificio(s, alto, col, lum = 0xfff1a0, w = R(2.5, 4)) {
  const g = new THREE.Group(); g.add(pos(malla(new THREE.BoxGeometry(w, alto, w), col), 0, alto / 2, 0));
  for (let y = 1; y < alto - .5; y += 1.3) for (const z of [-w / 4, w / 4]) if (Math.random() < .7) { // ventanas hacia la calle
    const v = new THREE.Mesh(new THREE.BoxGeometry(.06, .5, .45), new THREE.MeshBasicMaterial({ color: lum })); v.position.set(-s * (w / 2 + .03), y, z); g.add(v);
  }
  return g;
}
function auto(s) {
  const g = new THREE.Group(), c = [0xe2503a, 0x3b6ea5, 0xffc933, 0x3f8f5b][Math.random() * 4 | 0];
  g.add(pos(malla(new THREE.BoxGeometry(1, .5, 2), c), 0, .5, 0), pos(malla(new THREE.BoxGeometry(.9, .4, 1), 0xdff3ff), 0, .95, -.1));
  for (const [x, z] of [[-.5, -.7], [.5, -.7], [-.5, .7], [.5, .7]]) { const w = cil(.28, .2, 0x222222, 12); w.rotation.z = Math.PI / 2; g.add(pos(w, x, .28, z)); }
  g.scale.setScalar(1.3); return g;
}
const farola = () => { const g = new THREE.Group(); g.add(pos(cil(.08, 4, 0x555555), 0, 2, 0), pos(malla(new THREE.SphereGeometry(.3, 12, 8), 0xfff1a0, 1), 0, 4.1, 0)); return g; };
function restaurante(s) {
  const g = edificio(s, R(3, 5), 0xf0d9a8, 0xffe0a0, 3.2);
  g.add(pos(malla(new THREE.BoxGeometry(1.5, .12, 3.2), 0xd93a3a), -s * 2.3, 2.3, 0), pos(malla(new THREE.BoxGeometry(1.5, .13, 1.1), 0xffffff), -s * 2.3, 2.3, 0)); return g;
}
function cocinero() {
  const g = new THREE.Group();
  g.add(pos(cil(.5, 1.3, 0xffffff), 0, .65, 0), pos(esf(.4, 0xf2b98a), 0, 1.6, 0), pos(cil(.35, .5, 0xffffff), 0, 2.2, 0), pos(esf(.4, 0xffffff), 0, 2.5, 0), pos(cil(.5, .12, 0xd93a3a), 0, 1.1, 0));
  for (const x of [-1, 1]) g.add(pos(esf(.06, 0x222222), .15 * x, 1.65, .36));
  g.scale.setScalar(1.6); return g;
}
function olla() {
  const g = new THREE.Group(); g.add(pos(cil(.9, 1, 0x9aa3ad), 0, .5, 0), pos(cil(1, .15, 0x6f7883), 0, 1.05, 0));
  for (let i = 0; i < 3; i++) g.add(pos(esf(.35 + i * .1, 0xffffff), 0, 1.6 + i * .6, 0)); // vapor
  g.scale.setScalar(1.4); return g;
}
function arbol() {
  const g = new THREE.Group(), h = R(1.6, 2.6); g.add(pos(cil(.25, h, 0x7a4a20), 0, h / 2, 0));
  for (let i = 0; i < 3; i++) g.add(pos(malla(new THREE.ConeGeometry(1.5 - i * .3, 1.8, 10), i % 2 ? 0x3f9a3a : 0x2f8a4a), 0, h + i * .9, 0));
  g.scale.setScalar(R(.9, 1.6)); return g;
}
function boca(s) { // boca gigante con dientes y lengua, mirando a la pista
  const g = new THREE.Group(); g.add(pos(esf(1.7, 0x7a1f2b, 1.2, 1, .5), 0, 2, 0), pos(esf(.9, 0xe8788a, 1.4, .4, .5), 0, 1.3, .25));
  for (let i = -3; i <= 3; i++) g.add(pos(esf(.2, 0xffffff, 1, 1.6, 1), i * .42, 3, .45), pos(esf(.2, 0xffffff, 1, 1.6, 1), i * .42, 1.05, .45));
  const l = malla(new THREE.TorusGeometry(1.9, .22, 8, 24), 0xe0607a); l.scale.set(1.2, 1, .5); g.add(pos(l, 0, 2, 0));
  g.rotation.y = -s * Math.PI / 2; g.scale.setScalar(1.3); return g;
}
function ruina(s) { const g = edificio(s, R(5, 14), 0x2f2f3a, 0xff3b3b); g.rotation.z = R(-.12, .12); return g; }
function nube() { const g = new THREE.Group(); for (let i = 0; i < 4; i++) g.add(pos(esf(R(2, 3.5), 0x5a1018, 1.4, .7, 1), i * 2.5 - 4, R(0, 1.5), R(-1, 1))); g.position.y = R(14, 19); return g; }
const DEC = [
  s => { const q = Math.random(); return q < .25 ? auto(s) : q < .45 ? farola() : edificio(s, R(3, 10), [0x8aa4c8, 0xc9a0a0, 0xa8c8a0, 0xd9c58a][Math.random() * 4 | 0]); },
  s => { const q = Math.random(); return q < .3 ? cocinero() : q < .5 ? olla() : restaurante(s); },
  s => s < 0 ? arbol() : boca(s),
  s => Math.random() < .35 ? nube() : ruina(s),
];
function montarDecorado(n) {
  for (let i = 0; i < 10; i++) for (const s of [-1, 1]) { const d = DEC[n](s); d.position.x = s * R(6.5, 11); d.position.z = -i * 13 - R(0, 4); escena.add(d); dec.push(d); }
}

// ---------- Estado de la partida ----------
let E = { estado: 'menu' };
let jug = null, jefe = null;

function limpiar() {
  (E.cosas || []).forEach(c => escena.remove(c.malla));
  parts.splice(0).forEach(p => escena.remove(p.m));
  dec.splice(0).forEach(d => escena.remove(d));
  [...(E.balas || []), ...(E.rayos || [])].forEach(o => o.ms.forEach(x => escena.remove(x)));
  if (jefe) { escena.remove(jefe.g); jefe = null; }
  if (jug) escena.remove(jug.g);
  E.cosas = []; jug = null;
}
function nuevaPartida() { limpiar(); E = { estado: 'jugando', vidas: 3, puntos: 0 }; empezarNivel(0); }
function empezarNivel(n) {
  limpiar();
  Object.assign(E, { nivel: n, t: 0, acum: 0, proxL: 3, gig: 0, balas: [], rayos: [], cd: 0, shake: 0, flashT: 2, flashDur: 0, cor: 0, carril: 1, x: 0, y: 0, vy: 0, monedas: 0, cnt: { mayonesa: 0, tomate: 0, queso: 0 }, ingTot: 0, esq: 0, letras: '', pot: 0, potTipo: '', inv: 0, cosas: [], estado: 'jugando' });
  if (!E.pj) E.pj = guardado.personaje;
  jug = crearPersonaje(E.pj, guardado.sombrero); escena.add(jug.g);
  ambiente(n); montarDecorado(n); $('jefe').classList.toggle('oculto', n !== 3);
  if (n === 3) { // jefe final: el villano contrario al personaje elegido
    E.jefeTipo = E.pj === 'alga' ? 'esponja' : 'alga'; E.jefeMax = E.jefeVida = 40; E.segunda = false;
    jefe = crearPersonaje(E.jefeTipo, 'ninguno'); jefe.g.scale.setScalar(6); jefe.g.position.set(0, 0, -46); escena.add(jefe.g);
    jug.g.add(pistola());
  }
  $('pantalla').classList.add('oculto'); $('hud').classList.remove('oculto');
  mensaje(`Nivel ${n + 1}: ${NIVELES[n].nombre}`);
}
function poner(o, carril, z) { o.malla.position.set(CARRILES[carril], o.y, z); o.carril = carril; escena.add(o.malla); E.cosas.push(o); }
function mensaje(t) { const m = $('mensaje'); m.textContent = t; m.classList.remove('mostrar'); void m.offsetWidth; m.classList.add('mostrar'); }

// Genera una fila de obstáculos con premios en el carril libre
function generar() {
  const l = [0, 1, 2].sort(() => Math.random() - .5), n = Math.random() < .4 ? 2 : 1;
  l.slice(0, n).forEach((c, i) => poner(E.nivel === 2 && i === 0 ? crearDiente() : OBST[Math.random() * 5 | 0](), c, -50));
  const libres = l.slice(n), p = Math.random();
  if (Math.random() < .07) poner(crearEstrella(), libres[libres.length - 1], -58); // estrella bonus
  if (p < .12) poner(crearBolsa(), libres[0], -50);
  else if (p < .3) poner(crearIng(), libres[0], -50);
  else if (p < .55) libres.forEach(c => poner(crearMoneda(), c, -50)); // monedas de a 2
  else for (let i = 0; i < 3; i++) poner(crearMoneda(), libres[0], -50 - i * 2.5);
}
// Nivel 2: tres letras, una por carril; sólo una es la correcta
function generarLetras() {
  const sig = PALABRA[E.letras.length]; if (!sig) return;
  const otras = [...'ABCDEFGHILMNPRSU'].filter(x => x !== sig).sort(() => Math.random() - .5), ok = Math.random() * 3 | 0, gr = {};
  for (let c = 0; c < 3; c++) { const letra = c === ok ? sig : otras.pop(); poner({ malla: etiqueta(letra, '#ffd23f', 1.8), tipo: 'letra', letra, y: 1.3, grupo: gr }, c, -45); }
}
function saltar() { if (E.y <= .01) { E.vy = 12; tono(520, .15); } }

function activarGigante() { // 1 de cada ingrediente: gigante, inmune y recoge los 3 carriles
  E.gig = 5; mensaje('¡Modo gigante!'); chispas(E.x, 1, 0, 0xffffff, 40); tono(300, .5, 'sawtooth');
  const f = $('efecto'); f.classList.remove('flash'); void f.offsetWidth; f.classList.add('flash');
}
function sorteo() { // estrella celeste: ruleta de poderes
  const L = [['vuelo', '🕊️ Vuelo'], ['vel', '⚡ Velocidad'], ['doble', '✨ Monedas x2'], ['gigante', '🍔 Gigante']], el = $('sorteo');
  E.estado = 'sorteo'; el.classList.remove('oculto'); let i = 0;
  const iv = setInterval(() => { el.textContent = L[i++ % 4][1]; tono(500 + i * 40, .05); }, 90);
  setTimeout(() => {
    clearInterval(iv); const g = L[Math.random() * 4 | 0]; el.textContent = g[1]; tono(880, .3, 'triangle');
    setTimeout(() => { el.classList.add('oculto'); if (E.estado === 'sorteo') { E.estado = 'jugando'; g[0] === 'gigante' ? activarGigante() : activarPoder(g[0]); } }, 800);
  }, 1300);
}
function disparar() { // pistola de agua (nivel 4)
  if (E.nivel !== 3 || E.estado !== 'jugando' || E.cd > 0) return;
  E.cd = .3; const m = new THREE.Mesh(new THREE.SphereGeometry(.18, 10, 8), new THREE.MeshBasicMaterial({ color: 0x6fd3ff }));
  m.position.set(E.x, 1.2, -.5); escena.add(m); E.balas.push({ ms: [m] }); tono(1100, .06, 'triangle');
}
function segundoPersonaje() { // con todos los personajes comprados: segunda oportunidad con 2 vidas
  E.segunda = true; E.vidas = 2; E.inv = 2;
  const nuevo = PERSONAJES.find(p => p.id !== E.pj && p.id !== E.jefeTipo);
  escena.remove(jug.g); E.pj = nuevo.id; jug = crearPersonaje(E.pj, guardado.sombrero); escena.add(jug.g); jug.g.add(pistola());
  mensaje(`¡Entra ${nuevo.nombre}! 2 vidas`);
}
function activarPoder(tipo) {
  E.potTipo = tipo; E.pot = 4;
  mensaje({ vel: '¡Superrapidez!', vuelo: '¡A volar!', doble: '¡Monedas x2!' }[tipo]);
  chispas(E.x, 1, 0, 0xffffff, 40); tono(880, .4, 'triangle');
  const f = $('efecto'); f.classList.remove('flash'); void f.offsetWidth; f.classList.add('flash');
}
function golpe() {
  if (E.inv > 0) return;
  E.vidas--; E.inv = 1.6; tono(120, .3, 'sawtooth'); chispas(E.x, 1, 0, 0xe2503a, 16);
  if (E.vidas <= 0) { if (E.nivel === 3 && !E.segunda && PERSONAJES.every(p => guardado.comprados.includes(p.id))) segundoPersonaje(); else finJuego(false); }
}

function actualizar(dt) {
  const N = NIVELES[E.nivel], vuela = E.pot > 0 && E.potTipo === 'vuelo';
  const v = N.vel * (E.pot > 0 && E.potTipo === 'vel' ? 1.7 : 1);
  E.t += dt; E.acum += v * dt; E.inv = Math.max(0, E.inv - dt); E.pot = Math.max(0, E.pot - dt); E.gig = Math.max(0, E.gig - dt);
  rayas.forEach(r => { r.position.z += v * dt; if (r.position.z > 8) r.position.z -= 64; });
  dec.forEach(d => { d.position.z += v * dt; if (d.position.z > 12) d.position.z -= 130; });
  if (E.acum >= N.sepa) { E.acum = 0; if (E.nivel === 3) { const c = Math.random() * 3 | 0; for (let i = 0; i < 3; i++) poner(crearMoneda(), c, -50 - i * 2.5); } else generar(); }
  // Jugador
  E.x += (CARRILES[E.carril] - E.x) * Math.min(1, 12 * dt);
  if (vuela) { E.y += (2.6 - E.y) * Math.min(1, 6 * dt); E.vy = 0; }
  else { E.vy -= 32 * dt; E.y = Math.max(0, E.y + E.vy * dt); if (E.y === 0) E.vy = 0; }
  jug.g.position.set(E.x, E.y, 0); jug.g.scale.setScalar(jug.g.scale.x + ((E.gig > 0 ? 2 : 1) - jug.g.scale.x) * .2);
  jug.g.visible = E.inv <= 0 || Math.floor(E.inv * 10) % 2 === 0;
  jug.piernas.forEach((p, i) => p.rotation.x = E.y > .05 ? .5 : Math.sin(E.t * 14 + i * Math.PI) * .8);
  jug.c.position.y = E.y > .05 ? 0 : Math.abs(Math.sin(E.t * 14)) * .1;
  cam.position.x += (E.x * .4 - cam.position.x) * .1;
  if (E.nivel === 3) { // ---- jefe final ----
    E.cd -= dt; E.shake = Math.max(0, E.shake - dt); E.golpeJefe = Math.max(0, (E.golpeJefe || 0) - dt);
    jefe.g.position.y = Math.abs(Math.sin(E.t * 2)) * .4; jefe.g.rotation.y = Math.sin(E.t) * .15; jefe.g.scale.setScalar(6 + E.golpeJefe * 3);
    jefe.piernas.forEach((p, i) => p.rotation.x = Math.sin(E.t * 6 + i * Math.PI) * .5);
    if ((E.flashT -= dt) <= 0) { E.flashT = R(2, 5); E.flashDur = .15; E.shake = .4; tono(90, .3, 'sawtooth'); } // rayos rojos de fondo
    escena.background.set(E.flashDur > 0 ? 0x8a1c26 : AMB[3].cielo); E.flashDur -= dt;
    cam.position.y = 4.2 + (E.shake > 0 ? (Math.random() - .5) * .35 : 0);
    if ((E.rayoT = (E.rayoT ?? 3) - dt) <= 0) { // el jefe avisa y lanza rayos en 1 o 2 carriles
      E.rayoT = R(3, 4.5); const ls = [0, 1, 2].sort(() => Math.random() - .5).slice(0, Math.random() < .35 ? 2 : 1);
      ls.forEach(l => { const a = new THREE.Mesh(new THREE.BoxGeometry(1.8, .05, 12), new THREE.MeshBasicMaterial({ color: 0xff2a2a, transparent: true, opacity: .5 })); a.position.set(CARRILES[l], .05, -3); escena.add(a); E.rayos.push({ lane: l, t: 1.1, ms: [a] }); });
      tono(200, .3, 'square');
    }
    for (const q of E.rayos) {
      q.t -= dt;
      if (!q.gol && q.t <= 0) {
        q.gol = 1; q.ms[0].visible = false; const b = new THREE.Mesh(new THREE.CylinderGeometry(.3, .5, 22, 8), new THREE.MeshBasicMaterial({ color: 0xff5a5a }));
        b.position.set(CARRILES[q.lane], 11, -1); escena.add(b); q.ms.push(b); E.shake = .5; tono(80, .35, 'sawtooth');
        if (Math.abs(CARRILES[q.lane] - E.x) < 1.2) golpe();
      }
      if (q.t < -.35) { q.ms.forEach(m => escena.remove(m)); q.fin = 1; }
    }
    E.rayos = E.rayos.filter(q => !q.fin);
    if (E.cor < 3 && E.jefeVida / E.jefeMax <= [.75, .5, .25][E.cor]) { E.cor++; poner(crearCorazon(), Math.random() * 3 | 0, -40); } // 3 corazones en todo el nivel
    for (const b of E.balas) {
      b.ms[0].position.z -= 34 * dt;
      if (b.ms[0].position.z < -40) {
        b.fin = 1; escena.remove(b.ms[0]); E.jefeVida--; E.golpeJefe = .15; chispas(0, 4, -40, 0x6fd3ff, 6);
        if (E.jefeVida <= 0 && E.estado === 'jugando') { finNivel(); break; }
      }
    }
    E.balas = E.balas.filter(b => !b.fin);
    $('jefeBarra').style.width = Math.max(0, 100 * E.jefeVida / E.jefeMax) + '%';
  }
  // Objetos del mundo
  for (const c of E.cosas) {
    const m = c.malla; m.position.z += v * dt; const z = m.position.z;
    if (c.gira) m.rotation.y += dt * 3;
    if (c.tipo === 'lluvia') m.position.y = Math.max(0, -z * .5 - 1);
    if (c.hecho) continue;
    const carril = Math.abs(m.position.x - E.x) < 1.1;
    if (Math.abs(z) < .9 && (carril || E.gig > 0 && ['moneda', 'bolsa', 'ing', 'corazon', 'estrella'].includes(c.tipo))) {
      if (c.tipo === 'moneda') { c.hecho = 1; E.monedas += E.pot > 0 && E.potTipo === 'doble' ? 2 : 1; tono(1200, .08); chispas(m.position.x, 1, 0, 0xffd23f, 6); }
      else if (c.tipo === 'bolsa') { c.hecho = 1; E.monedas += 10 * (E.pot > 0 && E.potTipo === 'doble' ? 2 : 1); tono(700, .25, 'triangle'); chispas(m.position.x, 1, 0, 0xffd23f, 20); }
      else if (c.tipo === 'estrella') { c.hecho = 1; m.visible = false; sorteo(); }
      else if (c.tipo === 'corazon') { c.hecho = 1; E.vidas = Math.min(5, E.vidas + 1); tono(760, .3, 'triangle'); chispas(m.position.x, 1, 0, 0xff6b81, 16); }
      else if (c.tipo === 'ing') {
        c.hecho = 1; E.cnt[c.ing]++; E.ingTot++; tono(900, .15);
        const P = { mayonesa: 'vuelo', tomate: 'vel', queso: 'doble' }, k = Object.keys(E.cnt);
        if (E.cnt[c.ing] >= 3) { E.cnt[c.ing] = 0; activarPoder(P[c.ing]); } // 3 iguales: poder del ingrediente
        else if (k.every(x => E.cnt[x] >= 1)) { k.forEach(x => E.cnt[x]--); activarGigante(); } // uno de cada
        else mensaje(`+ ${c.ing}`);
      } else if (c.tipo === 'letra') {
        c.hecho = 1;
        E.cosas.filter(o => o.grupo === c.grupo).forEach(o => { o.hecho = 1; o.malla.visible = false; });
        if (c.letra === PALABRA[E.letras.length]) { E.letras += c.letra; tono(1000, .2, 'triangle'); chispas(m.position.x, 1.3, 0); }
        else tono(200, .2, 'square');
      } else if (!vuela && !(E.gig > 0) && !(c.tipo === 'bajo' && E.y > .9)) { c.hecho = 1; golpe(); }
    }
    if (z > 2 && !c.hecho && ['alto', 'bajo', 'lluvia'].includes(c.tipo)) { // esquivado
      c.hecho = 1; E.esq++;
      if (E.nivel === 1 && E.esq >= E.proxL && !E.cosas.some(o => o.tipo === 'letra' && !o.hecho)) { generarLetras(); E.proxL = E.esq + 3; }
    }
  }
  E.cosas = E.cosas.filter(c => { if (c.malla.position.z > 6) { escena.remove(c.malla); return false; } return true; });
  if (E.estado === 'jugando' && E.t >= N.seg) finNivel();
  actualizarHud();
}
function actualizarHud() {
  $('hVidas').textContent = '❤️'.repeat(Math.max(0, E.vidas));
  $('hNivel').textContent = `Nivel ${E.nivel + 1}`;
  $('hMon').textContent = `🪙 ${E.monedas}`;
  $('hPts').textContent = `⭐ ${E.puntos}`;
  $('hTiempo').textContent = E.nivel === 3 ? `⏱ ${Math.floor(E.t)}` : `⏱ ${Math.max(0, Math.ceil(NIVELES[E.nivel].seg - E.t))}`;
  $('hPot').textContent = E.gig > 0 ? `🍔 ${E.gig.toFixed(1)}` : E.nivel === 3 ? '💦 F o clic' : E.pot > 0 ? `${{ vel: '⚡', vuelo: '🕊️', doble: '✨x2' }[E.potTipo]} ${E.pot.toFixed(1)}` : `🫙${E.cnt.mayonesa} 🍅${E.cnt.tomate} 🧀${E.cnt.queso}`;
  $('palabra').innerHTML = E.nivel === 1 ? [...PALABRA].map((l, i) => `<span class="${i < E.letras.length ? 'ok' : ''}">${l}</span>`).join('') : '';
}

// ---------- Pantallas y menús ----------
// Vista previa de la tienda: un segundo renderizador pequeño que hace girar al personaje
const rv = new THREE.WebGLRenderer({ antialias: true, alpha: true }); rv.setSize(200, 200);
const ev = new THREE.Scene(), cv = new THREE.PerspectiveCamera(40, 1, .1, 50);
cv.position.set(0, 1.6, 6); cv.lookAt(0, .9, 0); ev.add(new THREE.HemisphereLight(0xfff2d6, 0xc79a5b, 2.2));
let pv = { p: 'burger', s: 'ninguno' }, mv = null, enTienda = false;
const mostrar = h => { enTienda = false; const p = $('pantalla'); p.innerHTML = `<div class="panel">${h}</div>`; p.classList.remove('oculto'); };
const tabla = () => `<ol class="rank">${guardado.ranking.map(r => `<li>${r.n} <b>${r.p}</b></li>`).join('') || '<li>Todavía no hay puntajes</li>'}</ol>`;

function pantallaInicio() {
  limpiar(); ambiente(0); E = { estado: 'menu' }; $('hud').classList.add('oculto');
  mostrar(`<div class="anim"><span class="cang">🏠</span><span class="vill">👽</span><span class="hamb">🍔</span><span class="mon m1">🪙</span><span class="mon m2">🪙</span></div>
    <h1>Burger Runner</h1><p class="sub">Escapá del Doctor Alga desde La Cangrejería Crujiente</p>
    <p class="mon-tot">🪙 ${guardado.monedas} monedas</p>
    <button data-acc="jugar">Jugar</button><button class="sec" data-acc="tienda">Tienda</button>
    <h3>Mejores puntajes</h3>${tabla()}
    <p class="ayuda">← → cambian de carril · Espacio salta · P pausa (en el celular: deslizá)</p>`);
}
function pantallaTienda(msg = '') {
  const fila = (it, t) => {
    const tengo = guardado.comprados.includes(it.id), eq = (t === 'p' ? guardado.personaje : guardado.sombrero) === it.id;
    const b = eq ? '<b class="eq">Equipado</b>' : tengo ? `<button class="chico" data-acc="equipar" data-t="${t}" data-id="${it.id}">Equipar</button>` : `<button class="chico precio" data-acc="comprar" data-t="${t}" data-id="${it.id}">🪙 ${it.precio}</button>`;
    return `<div class="item"><span>${it.nombre}</span><span><button class="chico sec" data-acc="ver" data-t="${t}" data-id="${it.id}">Ver</button> ${b}</span></div>`;
  };
  mostrar(`<h2>Tienda</h2><div id="vista"></div><p class="mon-tot">🪙 ${guardado.monedas} monedas</p><p class="aviso">${msg}</p>
    <h3>Personajes</h3>${PERSONAJES.map(i => fila(i, 'p')).join('')}
    <h3>Sombreros</h3>${SOMBREROS.map(i => fila(i, 's')).join('')}
    <button data-acc="inicio">Volver</button>`);
  $('vista').appendChild(rv.domElement); enTienda = true;
  if (mv) ev.remove(mv.g);
  mv = crearPersonaje(pv.p, pv.s); ev.add(mv.g);
}
function finNivel() {
  E.estado = 'fin';
  const sinPalabra = E.nivel === 1 && E.letras !== PALABRA;
  const pn = sinPalabra ? 0 : E.monedas * 10 + E.esq * 5 + E.ingTot * 50 + (E.nivel === 1 ? 300 : 0) + (E.nivel === 3 ? 500 : 0);
  E.puntos += pn; guardado.monedas += E.monedas;
  let extra = '';
  if (E.nivel > 0 && pn > 500) { E.vidas = Math.min(5, E.vidas + 1); extra = '<p class="aviso">¡+1 vida por superar 500 puntos!</p>'; }
  if (sinPalabra) extra += '<p class="aviso">No completaste TOMATE: este nivel no suma puntos.</p>';
  guardar(); tono(660, .4, 'triangle');
  mostrar(`<h2>Nivel ${E.nivel + 1} completo</h2>
    <p>⏱ Tiempo: ${Math.round(E.t)} s</p><p>🪙 Monedas: ${E.monedas}</p><p>🥫 Ingredientes: ${E.ingTot}</p>
    <p>⭐ Puntos del nivel: ${pn}</p><p>Total: <b>${E.puntos}</b></p>${extra}
    <button data-acc="${E.nivel === 3 ? 'terminar' : 'siguiente'}">${E.nivel === 3 ? 'Ver resultado' : 'Siguiente nivel'}</button>`);
}
function finJuego(gano) {
  E.estado = 'fin'; guardado.monedas += E.monedas; guardar();
  mostrar(`<h2>${gano ? '¡Completaste el juego!' : 'Fin del juego'}</h2><p>Puntaje final: <b>${E.puntos}</b></p>
    <input id="nombre" maxlength="12" placeholder="Tu nombre" autocomplete="off">
    <button data-acc="nombre">Guardar en el ranking</button><button class="sec" data-acc="reiniciar">Reiniciar</button>`);
}
function alternarPausa() {
  if (E.estado === 'jugando') { E.estado = 'pausa'; mostrar('<h2>Pausa</h2><button data-acc="reanudar">Reanudar</button><button class="sec" data-acc="reiniciar">Volver a empezar</button><button class="sec" data-acc="inicio">Volver al inicio</button>'); }
  else if (E.estado === 'pausa') ACC.reanudar();
}
const ACC = {
  jugar: nuevaPartida, reiniciar: nuevaPartida, inicio: pantallaInicio, tienda: () => { pv = { p: guardado.personaje, s: guardado.sombrero }; pantallaTienda(); },
  ver: d => { pv[d.t] = d.id; pantallaTienda(); },
  siguiente: () => empezarNivel(E.nivel + 1), terminar: () => finJuego(true),
  reanudar: () => { E.estado = 'jugando'; $('pantalla').classList.add('oculto'); },
  comprar: d => pantallaTienda(comprar(d.id) ? '¡Comprado!' : 'No alcanzan las monedas'),
  equipar: d => { equipar(d.t, d.id); pantallaTienda(); },
  nombre: () => {
    guardado.ranking.push({ n: ($('nombre').value.trim() || 'Anónimo').slice(0, 12), p: E.puntos });
    guardado.ranking.sort((a, b) => b.p - a.p); guardado.ranking = guardado.ranking.slice(0, 5); guardar(); pantallaInicio();
  },
};
$('pantalla').addEventListener('click', e => { const b = e.target.closest('[data-acc]'); if (b) ACC[b.dataset.acc](b.dataset); });

// ---------- Entrada: teclado y deslizamiento táctil ----------
const mover = d => { if (E.estado === 'jugando') E.carril = Math.min(2, Math.max(0, E.carril + d)); };
addEventListener('keydown', e => {
  const k = e.key.toLowerCase();
  if (k === 'p' || k === 'escape') { if (E.estado === 'jugando' || E.estado === 'pausa') alternarPausa(); return; }
  if (E.estado !== 'jugando') return;
  if (k === 'arrowleft' || k === 'a') mover(-1);
  else if (k === 'arrowright' || k === 'd') mover(1);
  else if (k === 'f' || k === 'enter') disparar();
  else if (k === ' ' || k === 'arrowup' || k === 'w') { e.preventDefault(); saltar(); }
});
$('escena').addEventListener('click', disparar);
let t0;
addEventListener('touchstart', e => t0 = e.touches[0]);
addEventListener('touchend', e => {
  if (!t0 || E.estado !== 'jugando') return;
  const dx = e.changedTouches[0].clientX - t0.clientX, dy = e.changedTouches[0].clientY - t0.clientY;
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 30) mover(Math.sign(dx)); else if (dy < -30) saltar();
});

// ---------- Bucle principal ----------
const reloj = new THREE.Clock();
function bucle() {
  requestAnimationFrame(bucle);
  const dt = Math.min(reloj.getDelta(), .05);
  if (E.estado === 'jugando') actualizar(dt);
  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i]; p.m.position.addScaledVector(p.v, dt); p.v.y -= 9 * dt;
    if ((p.t -= dt) <= 0) { escena.remove(p.m); parts.splice(i, 1); }
  }
  if (enTienda && mv) { mv.g.rotation.y += dt * 1.2; rv.render(ev, cv); }
  render.render(escena, cam);
}
export function iniciar() { pantallaInicio(); bucle(); }
