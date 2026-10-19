'use strict';
/* Canvas renderer, menu, input and presentation layer. */
const canvas=document.getElementById('gameCanvas'),ctx=canvas.getContext('2d');
const W=1180,H=650;
const $=id=>document.getElementById(id);
const menu=$('menu'), levels=$('levels'), overlay=$('overlay'), overlayTitle=$('overlayTitle'), overlayText=$('overlayText'), overlayButtons=$('overlayButtons');
const message=$('message');
let last=performance.now(), menuOpen=true, raf=0;
window.__mbrKeys={};

function sx(x){return x-game.cameraX+W*.28;}
function theme(){return getLevelData().theme;}
function sky(){
  const t=theme();
  const g=ctx.createLinearGradient(0,0,0,H);
  if(t==='green'){g.addColorStop(0,'#6ecbf5');g.addColorStop(1,'#d8f2dc')}
  if(t==='rock'){g.addColorStop(0,'#5da8db');g.addColorStop(1,'#e5c99b')}
  if(t==='snow'){g.addColorStop(0,'#496c9b');g.addColorStop(1,'#e7f3ff')}
  if(t==='canyon'){g.addColorStop(0,'#6d91b7');g.addColorStop(1,'#efad75')}
  if(t==='summit'){g.addColorStop(0,'#172a55');g.addColorStop(1,'#f2b76e')}
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
}
function sun(){ctx.save();let x=940,y=105;ctx.globalAlpha=.22;ctx.fillStyle='#fff7b2';ctx.beginPath();ctx.arc(x,y,70,0,Math.PI*2);ctx.fill();ctx.globalAlpha=.95;ctx.beginPath();ctx.arc(x,y,34,0,Math.PI*2);ctx.fillStyle='#fff4a6';ctx.fill();ctx.restore()}
function clouds(){ctx.save();ctx.globalAlpha=theme()==='summit'?.25:.55;for(let i=0;i<7;i++){let x=((i*250-game.cameraX*.08)%1450)-120,y=70+(i%3)*58;ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(x,y,22,0,Math.PI*2);ctx.arc(x+25,y-10,30,0,Math.PI*2);ctx.arc(x+58,y,24,0,Math.PI*2);ctx.fill()}ctx.restore()}
function mountainLayer(parallax,color,base,height){ctx.save();ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(0,H);for(let x=-80;x<W+120;x+=150){let wx=(x+game.cameraX*parallax);let y=base-height*(.45+.55*Math.abs(Math.sin(wx*.006)));ctx.lineTo(x,y);ctx.lineTo(x+75,y-height*.45)}ctx.lineTo(W,H);ctx.closePath();ctx.fill();ctx.restore()}
function mountains(){
  const t=theme();
  if(t==='green'){mountainLayer(.05,'#6f9c86',420,170);mountainLayer(.11,'#4d806f',445,145);}
  if(t==='rock'){mountainLayer(.05,'#89969d',420,210);mountainLayer(.12,'#65757d',450,180);}
  if(t==='snow'){mountainLayer(.04,'#9eb5c9',420,250);mountainLayer(.11,'#738ba5',445,220);}
  if(t==='canyon'){mountainLayer(.04,'#b26f4f',430,230);mountainLayer(.12,'#8e523f',455,195);}
  if(t==='summit'){mountainLayer(.03,'#304d72',430,290);mountainLayer(.09,'#243b5c',450,245);}
}
function worldBase(){
  ctx.fillStyle=theme()==='snow'?'#edf5fa':theme()==='canyon'?'#9a5d3e':theme()==='rock'?'#76664f':'#6c9a55';ctx.fillRect(0,430,W,220);
}
function ground(){
  ctx.save();ctx.beginPath();ctx.moveTo(0,H);for(let sxp=0;sxp<=W;sxp+=12){let wx=game.cameraX-sxp+W*.28;ctx.lineTo(sxp,getGroundY(wx));}ctx.lineTo(W,H);ctx.closePath();
  let g=ctx.createLinearGradient(0,400,0,H);if(theme()==='snow'){g.addColorStop(0,'#fff');g.addColorStop(1,'#b9c9d3')}else if(theme()==='canyon'){g.addColorStop(0,'#c78250');g.addColorStop(1,'#71442f')}else{g.addColorStop(0,'#78b34f');g.addColorStop(1,'#3f6938')}ctx.fillStyle=g;ctx.fill();
  ctx.beginPath();for(let sxp=0;sxp<=W;sxp+=12){let wx=game.cameraX-sxp+W*.28;let y=getGroundY(wx);if(sxp===0)ctx.moveTo(sxp,y);else ctx.lineTo(sxp,y)}ctx.strokeStyle=theme()==='snow'?'#d9edf6':'#365b31';ctx.lineWidth=5;ctx.stroke();ctx.restore();
}
function drawWater(){
  if(theme()!=='rock'&&theme()!=='canyon')return;ctx.save();ctx.globalAlpha=.65;ctx.fillStyle=theme()==='rock'?'#5ab8d8':'#5c94ad';ctx.fillRect(0,560,W,90);for(let x=0;x<W;x+=80){ctx.strokeStyle='#ffffff55';ctx.beginPath();ctx.moveTo(x,585+Math.sin(x)*3);ctx.quadraticCurveTo(x+20,578,x+40,585);ctx.stroke()}ctx.restore();
}
function drawScenery(){for(const s of game.scenery){const x=sx(s.x);if(x<-100||x>W+100)continue;const y=s.y;ctx.save();ctx.translate(x,y);ctx.scale(s.s,s.s);if(s.type==='tree'){ctx.fillStyle='#68442c';ctx.fillRect(-7,-72,14,72);ctx.fillStyle='#28633a';for(const yy of [-95,-70,-45]){ctx.beginPath();ctx.arc(0,yy,32,0,Math.PI*2);ctx.fill()}}else if(s.type==='pine'){ctx.fillStyle='#244f46';for(let i=0;i<3;i++){ctx.beginPath();ctx.moveTo(0,-110+i*27);ctx.lineTo(-38, -35+i*27);ctx.lineTo(38,-35+i*27);ctx.closePath();ctx.fill()}ctx.fillStyle='#6b4b35';ctx.fillRect(-5,-35,10,35)}else if(s.type==='cactus'){ctx.fillStyle='#3e8750';ctx.fillRect(-8,-80,16,80);ctx.fillRect(-34,-60,26,12);ctx.fillRect(-34,-60,12,30);ctx.fillRect(8,-42,28,12);ctx.fillRect(24,-42,12,25)}else{ctx.fillStyle='#756b63';ctx.beginPath();ctx.moveTo(-35,0);ctx.lineTo(-18,-50);ctx.lineTo(12,-65);ctx.lineTo(38,-15);ctx.lineTo(24,5);ctx.closePath();ctx.fill()}ctx.restore()}}
function drawRamps(){for(const r of game.ramps){const x=sx(r.x),y=r.y;if(x<-120||x>W+120)continue;ctx.save();ctx.fillStyle='#5a3c2b';ctx.beginPath();ctx.moveTo(x-r.w/2,y+5);ctx.lineTo(x+r.w/2,y+5);ctx.lineTo(x+r.w/2,y-r.h);ctx.closePath();ctx.fill();ctx.fillStyle=theme()==='snow'?'#eaf5fb':'#7bb34c';ctx.beginPath();ctx.moveTo(x-r.w/2,y);ctx.lineTo(x+r.w/2,y);ctx.lineTo(x+r.w/2,y-r.h+7);ctx.closePath();ctx.fill();ctx.strokeStyle='#d9eab7';ctx.stroke();ctx.restore()}}
function drawObstacles(){for(const o of game.obstacles){const x=sx(o.x),y=o.y;if(x<-130||x>W+130)continue;ctx.save();ctx.translate(x,y);if(o.type==='rock'){ctx.fillStyle='#5e6667';ctx.beginPath();ctx.moveTo(-28,0);ctx.lineTo(-18,-38);ctx.lineTo(8,-47);ctx.lineTo(30,-20);ctx.lineTo(24,0);ctx.closePath();ctx.fill();ctx.fillStyle='#879091';ctx.beginPath();ctx.moveTo(-18,-38);ctx.lineTo(8,-47);ctx.lineTo(0,-25);ctx.closePath();ctx.fill()}else if(o.type==='barrel'){ctx.fillStyle='#8b552e';ctx.fillRect(-20,-40,40,40);ctx.strokeStyle='#d1a36c';ctx.lineWidth=5;ctx.strokeRect(-20,-40,40,40);ctx.beginPath();ctx.moveTo(-20,-27);ctx.lineTo(20,-27);ctx.moveTo(-20,-8);ctx.lineTo(20,-8);ctx.stroke()}else{ctx.fillStyle='#67462e';ctx.rotate(-.05);ctx.fillRect(-45,-12,90,24);ctx.fillStyle='#a77a4e';ctx.beginPath();ctx.arc(-38,0,13,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(38,0,13,0,Math.PI*2);ctx.fill()}ctx.restore()}}
function drawHazards(){for(const h of game.hazards){const x=sx(h.x);if(x<-150||x>W+150)continue;ctx.save();ctx.fillStyle=h.type==='gap'?'#1d1a1b':'#5b452d';ctx.beginPath();ctx.moveTo(x,getGroundY(h.x));ctx.lineTo(x+h.w,getGroundY(h.x+h.w));ctx.lineTo(x+h.w,H);ctx.lineTo(x,H);ctx.closePath();ctx.fill();if(h.type==='gap'){ctx.strokeStyle='#efc36c';ctx.setLineDash([10,10]);ctx.stroke()}ctx.restore()}}
function drawCheckpoints(){for(const c of game.checkpoints){const x=sx(c.x);if(x<-60||x>W+60)continue;const y=c.y;ctx.save();ctx.strokeStyle=c.passed?'#76f5a3':'#fff';ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y-105);ctx.stroke();ctx.fillStyle=c.passed?'#76f5a3':'#f2c94c';ctx.beginPath();ctx.moveTo(x,y-103);ctx.lineTo(x+52,y-88);ctx.lineTo(x,y-70);ctx.closePath();ctx.fill();ctx.restore()}}
function drawFinish(){const x=sx(getLevelData().length),y=getGroundY(getLevelData().length);ctx.save();ctx.strokeStyle='#fff';ctx.lineWidth=8;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x,y-145);ctx.stroke();for(let i=0;i<5;i++)for(let j=0;j<4;j++){ctx.fillStyle=(i+j)%2?'#fff':'#222';ctx.fillRect(x+i*18,y-145+j*18,18,18)}ctx.restore()}
function drawCoins(){for(const c of game.coins){if(c.collected)continue;const x=sx(c.x);if(x<-30||x>W+30)continue;const sc=.72+.28*Math.abs(Math.sin(c.spin));ctx.save();ctx.translate(x,c.y);ctx.scale(sc,1);ctx.shadowBlur=18;ctx.shadowColor='#ffe27a';ctx.fillStyle='#ffd34d';ctx.beginPath();ctx.arc(0,0,c.r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#fff2a0';ctx.beginPath();ctx.arc(-3,-3,3,0,Math.PI*2);ctx.fill();ctx.restore()}}
function drawParticles(){for(const p of game.particles){const x=sx(p.x);ctx.save();ctx.globalAlpha=Math.max(0,p.life);ctx.fillStyle=p.type==='dust'?'#d9c39a':p.type==='hit'?'#ff765b':'#ffe36d';ctx.beginPath();ctx.arc(x,p.y,p.size,0,Math.PI*2);ctx.fill();ctx.restore()}}
function drawTexts(){for(const f of game.floatingTexts){ctx.save();ctx.globalAlpha=Math.max(0,f.life);ctx.fillStyle='#fff';ctx.font='900 18px Arial';ctx.textAlign='center';ctx.fillText(f.text,sx(f.x),f.y);ctx.restore()}}
function drawBike(){const b=game.bike;if(!b)return;const x=sx(b.x),y=b.y;ctx.save();ctx.translate(x,y);ctx.rotate(b.angle);if(game.invulnerable>0&&Math.floor(game.invulnerable*12)%2===0)ctx.globalAlpha=.45;
  const spin=game.time*(b.vx*.9+3);ctx.lineWidth=4;ctx.strokeStyle='#202832';for(const wx of [-32,32]){ctx.fillStyle='#151b22';ctx.beginPath();ctx.arc(wx,14,20,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#aeb9c4';ctx.lineWidth=2;ctx.stroke();for(let i=0;i<8;i++){ctx.save();ctx.rotate(spin+i*Math.PI/4);ctx.beginPath();ctx.moveTo(wx,14);ctx.lineTo(wx+18,14);ctx.stroke();ctx.restore()}}
  ctx.strokeStyle='#e94f4f';ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(-32,14);ctx.lineTo(-8,-18);ctx.lineTo(32,14);ctx.lineTo(-32,14);ctx.lineTo(8,-18);ctx.lineTo(32,14);ctx.moveTo(-8,-18);ctx.lineTo(8,-18);ctx.stroke();
  ctx.strokeStyle='#222';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(8,-18);ctx.lineTo(17,-31);ctx.lineTo(29,-32);ctx.stroke();ctx.fillStyle='#242d38';ctx.fillRect(1,-29,20,5);ctx.fillStyle='#e7c2a4';ctx.beginPath();ctx.arc(0,-54,10,0,Math.PI*2);ctx.fill();ctx.fillStyle='#f0c84b';ctx.beginPath();ctx.arc(0,-58,11,Math.PI,Math.PI*2);ctx.fill();ctx.strokeStyle='#273241';ctx.lineWidth=6;ctx.beginPath();ctx.moveTo(0,-43);ctx.lineTo(-8,-18);ctx.lineTo(10,-6);ctx.moveTo(-6,-39);ctx.lineTo(15,-30);ctx.lineTo(25,-30);ctx.moveTo(-8,-18);ctx.lineTo(-22,4);ctx.moveTo(10,-7);ctx.lineTo(24,10);ctx.stroke();ctx.restore()}
function updateHud(){const s=getState();$('hLevel').textContent=`${s.level} · ${s.levelName}`;$('hScore').textContent=s.score;$('hCoins').textContent=s.coinsCollected;$('hSpeed').textContent=Math.round(Math.max(0,s.velocityX)*10);$('hLives').textContent=s.lives;$('hProgress').style.width=`${s.progress*100}%`;if(game.messageTimer>0){message.textContent=game.message;message.classList.add('show')}else message.classList.remove('show')}
function draw(){sky();sun();clouds();mountains();worldBase();drawWater();drawScenery();ground();drawHazards();drawRamps();drawCheckpoints();drawFinish();drawCoins();drawObstacles();drawParticles();drawTexts();drawBike();}
function cameraUpdate(){if(!game.bike)return;const target=Math.max(0,game.bike.x-W*.28);game.cameraX+=(target-game.cameraX)*.09;if(game.shake>0){game.cameraX+=(Math.random()-.5)*game.shake*30}}
function showOverlay(title,text,buttons){overlayTitle.textContent=title;overlayText.textContent=text;overlayButtons.innerHTML='';for(const b of buttons){const el=document.createElement('button');el.className='btn '+(b.secondary?'secondary':'');el.textContent=b.label;el.onclick=b.onClick;overlayButtons.appendChild(el)}overlay.classList.add('show')}
function hideOverlay(){overlay.classList.remove('show')}
function openMenu(){menuOpen=true;menu.classList.remove('hidden');hideOverlay();renderLevels()}
function renderLevels(){levels.innerHTML='';for(const d of LEVELS){const b=document.createElement('button');b.className='levelBtn'+(d.id>game.unlockedLevel?' locked':'');b.innerHTML=`${d.id}<br>${d.name}`;if(d.id>game.unlockedLevel)b.disabled=true;else b.onclick=()=>{menuOpen=false;menu.classList.add('hidden');startLevel(d.id)};levels.appendChild(b)}}
$('playBtn').onclick=()=>{menuOpen=false;menu.classList.add('hidden');startLevel(1)};
$('levelsBtn').onclick=()=>{levels.classList.toggle('open');renderLevels()};
window.addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','Space'].includes(e.code))e.preventDefault();window.__mbrKeys[e.code]=true;if(e.code==='KeyP')togglePause();if(e.code==='KeyR'&&game.started&&!game.levelComplete&&!game.won){startLevel(game.level)} });
window.addEventListener('keyup',e=>{window.__mbrKeys[e.code]=false});
function afterState(){
  if(game.levelComplete&&!game.won&&overlay.classList.contains('show')===false){
    showOverlay('NIVEL COMPLETADO',`Nivel ${game.level}: ${getLevelData().name}\nPuntos: ${game.score}\nMonedas: ${game.levelCoins}`,[
      {label:game.level<5?'SIGUIENTE NIVEL':'FINALIZAR',onClick:()=>{hideOverlay();if(game.level<5)startLevel(game.level+1);else{game.won=true;showVictory()}}},
      {label:'MENÚ',secondary:true,onClick:openMenu}
    ]);
  }
  if(game.gameOver&&!overlay.classList.contains('show'))showOverlay('GAME OVER',`Puntuación: ${game.score}\nMonedas: ${game.coinsCollected}\nDistancia: ${Math.round(game.distance)} m`,[{label:'REINTENTAR',onClick:()=>{hideOverlay();startLevel(game.level)}},{label:'MENÚ',secondary:true,onClick:openMenu}]);
  if(game.won&&!overlay.classList.contains('show'))showVictory();
}
function showVictory(){showOverlay('CUMBRE CONQUISTADA',`MOUNTAIN BIKE RUSH\nPuntuación final: ${game.score}\nMejor puntuación: ${game.bestScore}\nMonedas: ${game.coinsCollected}`,[{label:'JUGAR DE NUEVO',onClick:()=>{hideOverlay();game.score=0;startLevel(1)}},{label:'MENÚ',secondary:true,onClick:openMenu}])}
function loop(now){const dt=Math.min(.05,(now-last)/1000);last=now;if(!menuOpen&&!overlay.classList.contains('show')&&!game.paused)updateKeyboard();cameraUpdate();draw();updateHud();if(game.paused&&!menuOpen&&!overlay.classList.contains('show')){showOverlay('PAUSA','El juego está pausado.',[{label:'CONTINUAR',onClick:()=>{game.paused=false;hideOverlay()}},{label:'MENÚ',secondary:true,onClick:openMenu}])}afterState();raf=requestAnimationFrame(loop)}
renderLevels();loop(performance.now());
