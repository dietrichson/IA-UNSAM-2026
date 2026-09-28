export class Audio {
  constructor() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
  }
  beep(freq = 440, dur = 0.1) {
    const o = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    o.frequency.value = freq;
    o.connect(g).connect(this.ctx.destination);
    o.start();
    g.gain.setValueAtTime(0.15, this.ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + dur);
    o.stop(this.ctx.currentTime + dur);
  }
  moneda() { this.beep(880, 0.08); }
  salto()  { this.beep(520, 0.12); }
  choque() { this.beep(120, 0.3); }
}