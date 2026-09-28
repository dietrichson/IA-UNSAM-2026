import * as THREE from 'three';
import { Game } from './game.js';
import { Input } from './input.js';

const canvas = document.createElement('canvas');
document.body.appendChild(canvas);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x87ceeb);
scene.fog = new THREE.Fog(0x87ceeb, 40, 120);

const camera = new THREE.PerspectiveCamera(
  60, window.innerWidth / window.innerHeight, 0.1, 300
);
camera.position.set(0, 6, 10);
camera.lookAt(0, 0, 0);

const luces = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
scene.add(luces);
const sol = new THREE.DirectionalLight(0xffffff, 1.0);
sol.position.set(5, 20, 10);
scene.add(sol);

const game = new Game(scene, renderer, camera);
const input = new Input(game);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

let ultimoTiempo = performance.now();
function bucle(ahora) {
  const dt = Math.min((ahora - ultimoTiempo) / 1000, 0.1);
  ultimoTiempo = ahora;
  game.update(dt);
  renderer.render(scene, camera);
  requestAnimationFrame(bucle);
}
requestAnimationFrame(bucle);