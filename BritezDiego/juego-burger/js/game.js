import * as THREE from 'three';
import { Player } from './player.js';
import { World } from './world.js';
import { NIVELES } from './levels.js';

export class Game {
  constructor(scene, renderer, camera) {
    this.scene = scene;
    this.renderer = renderer;
    this.camera = camera;

    this.nivelActual = 0;
    this.monedas = 0;
    this.distancia = 0;
    this.velocidad = 12; // m/s
    this.activo = true;

    this.player = new Player(scene);
    this.world = new World(scene);

    this.cargarNivel(0);
    this._actualizarHUD();
  }

  cargarNivel(indice) {
    const nivel = NIVELES[indice];
    this.nivelActual = indice;
    this.nivel = nivel;
    this.distancia = 0;
    this.monedas = 0;
    this.velocidad = nivel.velocidadInicial;
    this.player.reset();
    this.world.limpiar();
    this.world.generar(nivel);
    this.activo = true;
  }

  update(dt) {
    if (!this.activo) return;

    this.distancia += this.velocidad * dt;
    this.velocidad = Math.min(
      this.velocidad + this.nivel.aceleracion * dt,
      this.nivel.velocidadMaxima
    );

    this.player.update(dt, this);
    this.world.update(dt, this);

    // Meta
    if (this.distancia >= this.nivel.meta) {
      this.terminarNivel();
      return;
    }

    this._actualizarHUD();
  }

  recogerMoneda() { this.monedas++; }
  recogerIngrediente(tipo) { this.player.agregarIngrediente(tipo); }

  chocar() {
    this.activo = false;
    document.getElementById('gameover').style.display = 'flex';
  }

  terminarNivel() {
    this.activo = false;
    document.getElementById('gameover-texto').textContent =
      `¡Nivel ${this.nivelActual + 1} completado! 🏁`;
    document.getElementById('gameover').style.display = 'flex';
  }

  reintentar() {
    document.getElementById('gameover').style.display = 'none';
    this.cargarNivel(this.nivelActual);
  }

  _actualizarHUD() {
    document.getElementById('nivel').textContent = this.nivelActual + 1;
    document.getElementById('monedas').textContent = this.monedas;
    document.getElementById('distancia').textContent = Math.floor(this.distancia);
    document.getElementById('power').textContent =
      this.player.superSaltoListo ? '¡SALTO!' : '—';
  }
}