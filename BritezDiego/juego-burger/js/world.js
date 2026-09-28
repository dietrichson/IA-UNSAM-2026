import * as THREE from 'three';

const CARRILES = [-2.5, 0, 2.5];

export class World {
  constructor(scene) {
    this.scene = scene;
    this.objetos = [];   // obstáculos
    this.monedas = [];   // monedas
    this.ingredientes = [];
    this.zSpawn = -120;
    this.piso = this._crearPiso();
    scene.add(this.piso);
  }

  _crearPiso() {
    const geo = new THREE.PlaneGeometry(20, 400);
    const mat = new THREE.MeshStandardMaterial({ color: 0x3a7d44 });
    const piso = new THREE.Mesh(geo, mat);
    piso.rotation.x = -Math.PI / 2;
    piso.position.z = -180;
    return piso;
  }

  generar(nivel) {
    for (let z = -20; z > -nivel.meta; z -= nivel.separacion) {
      const carril = CARRILES[Math.floor(Math.random() * 3)];
      if (Math.random() < nivel.probObstaculo) {
        this._spawnObstaculo(carril, z);
      } else if (Math.random() < nivel.probMoneda) {
        this._spawnMoneda(carril, z);
      }
      if (Math.random() < nivel.probIngrediente) {
        const carrilIng = CARRILES[Math.floor(Math.random() * 3)];
        this._spawnIngrediente(carrilIng, z - 5);
      }
    }
  }

  _spawnObstaculo(x, z) {
    const alto = Math.random() < 0.5;
    const geo = new THREE.BoxGeometry(1.2, alto ? 0.8 : 2, 1.2);
    const mat = new THREE.MeshStandardMaterial({ color: 0xc0392b });
    const obs = new THREE.Mesh(geo, mat);
    obs.position.set(x, alto ? 0.9 : 1.5, z);
    obs.userData.tipo = 'obstaculo';
    obs.userData.alto = !alto;
    this.scene.add(obs);
    this.objetos.push(obs);
  }

  _spawnMoneda(x, z) {
    const geo = new THREE.TorusGeometry(0.35, 0.12, 8, 16);
    const mat = new THREE.MeshStandardMaterial({ color: 0xffcc00, metalness: 0.7 });
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, 1.2, z);
    m.rotation.x = Math.PI / 2;
    m.userData.tipo = 'moneda';
    this.scene.add(m);
    this.monedas.push(m);
  }

  _spawnIngrediente(x, z) {
    const colores = { mayonesa: 0xffffff, tomate: 0xff4444, queso: 0xffd34d };
    const tipos = ['mayonesa', 'tomate', 'queso'];
    const tipo = tipos[Math.floor(Math.random() * 3)];
    const geo = new THREE.SphereGeometry(0.4, 12, 12);
    const mat = new THREE.MeshStandardMaterial({ color: colores[tipo] });
    const ing = new THREE.Mesh(geo, mat);
    ing.position.set(x, 1.2, z);
    ing.userData.tipo = 'ingrediente';
    ing.userData.sabor = tipo;
    this.scene.add(ing);
    this.ingredientes.push(ing);
  }

  update(dt, game) {
    const avance = game.velocidad * dt;
    const mover = (arr) => {
      for (let i = arr.length - 1; i >= 0; i--) {
        arr[i].position.z += avance;
        if (arr[i].position.z > 15) {
          this.scene.remove(arr[i]);
          arr.splice(i, 1);
        }
      }
    };
    mover(this.objetos);
    mover(this.monedas);
    mover(this.ingredientes);

    // Colisiones
    const pp = game.player.grupo.position;
    const py = game.player.y;

    for (let i = this.objetos.length - 1; i >= 0; i--) {
      const o = this.objetos[i];
      if (this._colision(pp, py, o)) {
        // Si es alto y está saltando, lo pasa
        if (o.userData.alto && py > 1.5) continue;
        game.chocar();
        return;
      }
    }

    for (let i = this.monedas.length - 1; i >= 0; i--) {
      const m = this.monedas[i];
      if (this._colision(pp, py, m, 1.0)) {
        this.scene.remove(m);
        this.monedas.splice(i, 1);
        game.recogerMoneda();
      }
    }

    for (let i = this.ingredientes.length - 1; i >= 0; i--) {
      const ing = this.ingredientes[i];
      if (this._colision(pp, py, ing, 1.0)) {
        game.recogerIngrediente(ing.userData.sabor);
        this.scene.remove(ing);
        this.ingredientes.splice(i, 1);
      }
    }
  }

  _colision(pos, y, obj, radio = 0.9) {
    const dx = Math.abs(pos.x - obj.position.x);
    const dz = Math.abs(pos.z - obj.position.z);
    const dy = Math.abs(y - obj.position.y);
    return dx < radio && dz < radio && dy < 1.2;
  }

  limpiar() {
    for (const arr of [this.objetos, this.monedas, this.ingredientes]) {
      for (const o of arr) this.scene.remove(o);
      arr.length = 0;
    }
  }
}