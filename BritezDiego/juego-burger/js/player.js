import * as THREE from 'three';

const CARRILES = [-2.5, 0, 2.5];
const VELOCIDAD_CARRIL = 12;
const FUERZA_SALTO = 12;
const GRAVEDAD = -28;

export class Player {
  constructor(scene) {
    this.scene = scene;
    this.grupo = new THREE.Group();
    scene.add(this.grupo);
    this._construir();

    this.carrilActual = 1;
    this.xObjetivo = CARRILES[1];
    this.y = 0.5;
    this.vy = 0;
    this.enSuelo = true;
    this.superSaltoListo = false;
    this.ingredientes = new Set();
  }

  _construir() {
    const panAbajo = new THREE.Mesh(
      new THREE.BoxGeometry(1.4, 0.4, 1.4),
      new THREE.MeshStandardMaterial({ color: 0xd9a44a })
    );
    panAbajo.position.y = -0.4;
    this.grupo.add(panAbajo);

    const carne = new THREE.Mesh(
      new THREE.BoxGeometry(1.3, 0.35, 1.3),
      new THREE.MeshStandardMaterial({ color: 0x6b3a1f })
    );
    carne.position.y = -0.05;
    this.grupo.add(carne);

    const queso = new THREE.Mesh(
      new THREE.BoxGeometry(1.35, 0.1, 1.35),
      new THREE.MeshStandardMaterial({ color: 0xffd34d })
    );
    queso.position.y = 0.2;
    this.grupo.add(queso);

    const panArriba = new THREE.Mesh(
      new THREE.BoxGeometry(1.4, 0.4, 1.4),
      new THREE.MeshStandardMaterial({ color: 0xd9a44a })
    );
    panArriba.position.y = 0.55;
    this.grupo.add(panArriba);

    // Ojitos
    for (const dx of [-0.3, 0.3]) {
      const ojo = new THREE.Mesh(
        new THREE.SphereGeometry(0.08, 8, 8),
        new THREE.MeshStandardMaterial({ color: 0x000000 })
      );
      ojo.position.set(dx, 0.6, 0.71);
      this.grupo.add(ojo);
    }
  }

  reset() {
    this.grupo.position.set(CARRILES[1], 0.5, 0);
    this.carrilActual = 1;
    this.xObjetivo = CARRILES[1];
    this.y = 0.5;
    this.vy = 0;
    this.enSuelo = true;
    this.superSaltoListo = false;
    this.ingredientes.clear();
  }

  moverIzquierda() {
    if (this.carrilActual > 0) {
      this.carrilActual--;
      this.xObjetivo = CARRILES[this.carrilActual];
    }
  }

  moverDerecha() {
    if (this.carrilActual < 2) {
      this.carrilActual++;
      this.xObjetivo = CARRILES[this.carrilActual];
    }
  }

  saltar() {
    if (!this.enSuelo) return;
    this.vy = this.superSaltoListo ? FUERZA_SALTO * 1.6 : FUERZA_SALTO;
    this.enSuelo = false;
    if (this.superSaltoListo) {
      this.superSaltoListo = false;
      this.ingredientes.clear();
    }
  }

  agregarIngrediente(tipo) {
    this.ingredientes.add(tipo);
    if (this.ingredientes.size >= 3) this.superSaltoListo = true;
  }

  update(dt, game) {
    // Movimiento lateral suave
    const x = this.grupo.position.x;
    this.grupo.position.x = x + (this.xObjetivo - x) * Math.min(1, dt * VELOCIDAD_CARRIL);

    // Salto
    this.vy += GRAVEDAD * dt;
    this.y += this.vy * dt;
    if (this.y <= 0.5) {
      this.y = 0.5;
      this.vy = 0;
      this.enSuelo = true;
    }
    this.grupo.position.y = this.y;

    // Rotación "corriendo"
    this.grupo.rotation.z = Math.sin(performance.now() * 0.01) * 0.08;
  }
}