/* Mountain Bike Rush - game logic and RL API
 * Vanilla JS. No DOM/Canvas dependency in the core so it can be tested with Node.
 */
'use strict';

const LEVELS = [
  { id:1, name:'Campo Verde', length:5600, lives:3, difficulty:1, theme:'green', speed:9.5 },
  { id:2, name:'Valle Rocoso', length:7000, lives:3, difficulty:2, theme:'rock', speed:10.0 },
  { id:3, name:'Montaña Nevada', length:8600, lives:3, difficulty:3, theme:'snow', speed:10.5 },
  { id:4, name:'Cañón Extremo', length:10200, lives:2, difficulty:4, theme:'canyon', speed:11.0 },
  { id:5, name:'Cumbre Final', length:12500, lives:2, difficulty:5, theme:'summit', speed:11.5 }
];

const ACTIONS = ['nothing','accelerate','brake','jump'];
const game = {
  version:'ultimate-1.0', started:false, paused:false, level:1, unlockedLevel:1,
  score:0, bestScore:0, coinsCollected:0, distance:0, lives:3,
  gameOver:false, levelComplete:false, won:false, cameraX:0,
  combo:1, comboTimer:0, time:0, shake:0, message:'', messageTimer:0,
  obstacles:[], ramps:[], coins:[], checkpoints:[], scenery:[], hazards:[],
  particles:[], floatingTexts:[], bike:null, checkpointIndex:0, levelScore:0,
  levelCoins:0, totalCheckpoints:0, invulnerable:0, lastAction:'nothing',
  audioEnabled:true, seed:1
};

function clamp(v,a,b){ return Math.max(a,Math.min(b,v)); }
function rand(){ game.seed=(game.seed*1664525+1013904223)>>>0; return game.seed/4294967296; }
function choose(arr){ return arr[Math.floor(rand()*arr.length)]; }
function levelData(){ return LEVELS[game.level-1]; }

function loadProgress(){
  if(typeof localStorage==='undefined') return;
  try{
    const u=Number(localStorage.getItem('mbr_unlocked'));
    const b=Number(localStorage.getItem('mbr_best'));
    if(Number.isFinite(u)) game.unlockedLevel=clamp(u,1,5);
    if(Number.isFinite(b)) game.bestScore=Math.max(0,b);
  }catch(e){}
}
function saveProgress(){
  if(typeof localStorage==='undefined') return;
  try{
    localStorage.setItem('mbr_unlocked',String(game.unlockedLevel));
    localStorage.setItem('mbr_best',String(game.bestScore));
  }catch(e){}
}

function getLevelData(id=game.level){ return LEVELS[id-1] || LEVELS[0]; }

function getGroundY(x){
  const d=levelData();
  let y=430;
  if(d.theme==='green') y=425+22*Math.sin(x/260)+10*Math.sin(x/93);
  if(d.theme==='rock') y=420+30*Math.sin(x/310)+15*Math.sin(x/120)+8*Math.sin(x/47);
  if(d.theme==='snow') y=415+34*Math.sin(x/360)+20*Math.sin(x/145)+10*Math.sin(x/65);
  if(d.theme==='canyon') y=420+42*Math.sin(x/330)+22*Math.sin(x/115)+14*Math.sin(x/54);
  if(d.theme==='summit') y=425+30*Math.sin(x/410)+22*Math.sin(x/155)+14*Math.sin(x/70);
  if(x>d.length-1900){
    const p=(x-(d.length-1900))/1900;
    y-=p*115;
    y+=Math.sin(x/90)*8*(1-p);
  }
  return y;
}
function getSlope(x){ return (getGroundY(x+2)-getGroundY(x-2))/4; }

function makeParticle(x,y,type,count=1){
  for(let i=0;i<count;i++){
    const a=rand()*Math.PI*2, s=type==='dust'?1+rand()*2.5:2+rand()*4;
    game.particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s-(type==='dust'?1:2),life:1,size:2+rand()*4,type});
  }
}
function floatText(text,x,y){ game.floatingTexts.push({text,x,y,life:1,vy:-.7}); }

function generateLevel(){
  const d=levelData();
  game.obstacles=[]; game.ramps=[]; game.coins=[]; game.checkpoints=[]; game.scenery=[]; game.hazards=[];
  game.particles=[]; game.floatingTexts=[]; game.seed=game.level*9371+17;
  const spacing=Math.max(260,520-d.difficulty*38);
  for(let x=420;x<d.length-500;x+=spacing*(.75+rand()*.6)){
    if(rand()<.78){
      const type=choose(['rock','barrel','log']);
      game.obstacles.push({x,y:getGroundY(x),type,w:type==='log'?90:type==='rock'?52:40,h:type==='log'?22:type==='rock'?42:48,hit:false});
    }
    if(rand()<.42) game.ramps.push({x:x+90+rand()*90,y:getGroundY(x+90),w:75+d.difficulty*8,h:42+rand()*14,type:rand()<.45?'big':'small'});
  }
  for(let x=300;x<d.length-400;x+=260+rand()*230){
    const base=getGroundY(x)-70-(rand()*45);
    const count=3+Math.floor(rand()*4);
    for(let i=0;i<count;i++) game.coins.push({x:x+i*38,y:base-Math.sin(i/(count-1||1)*Math.PI)*35,r:10,collected:false,spin:rand()*Math.PI*2});
  }
  const cpCount=4+d.difficulty;
  for(let i=1;i<=cpCount;i++){
    const x=(d.length/(cpCount+1))*i;
    game.checkpoints.push({x,y:getGroundY(x),passed:false});
  }
  game.totalCheckpoints=game.checkpoints.length;
  for(let x=80;x<d.length;x+=130+rand()*210){
    const y=getGroundY(x);
    let type='tree';
    if(d.theme==='snow') type='pine';
    if(d.theme==='canyon') type=rand()<.5?'cactus':'rock';
    if(d.theme==='rock') type=rand()<.65?'tree':'rock';
    if(d.theme==='summit') type=rand()<.6?'pine':'rock';
    game.scenery.push({x,y,type,s:0.7+rand()*0.7,front:rand()<.25});
  }
  if(d.difficulty>=3){
    for(let x=700;x<d.length-700;x+=900+rand()*900) game.hazards.push({x,w:110+rand()*80,type:rand()<.5?'mud':'gap'});
  }
}

function createBike(){
  return {x:180,y:getGroundY(180)-46,w:92,h:50,vx:0,vy:0,angle:0,angularVelocity:0,onGround:true,wasOnGround:true};
}

function startLevel(id=game.level){
  id=clamp(Number(id)||1,1,5);
  if(id>game.unlockedLevel) return false;
  game.level=id; const d=levelData();
  game.started=true; game.paused=false; game.gameOver=false; game.levelComplete=false; game.won=false;
  game.score=game.score||0; game.levelScore=0; game.levelCoins=0; game.distance=0; game.lives=d.lives;
  game.combo=1; game.comboTimer=0; game.cameraX=0; game.time=0; game.checkpointIndex=0; game.invulnerable=0;
  game.message=`${d.name}`; game.messageTimer=2.2; game.bike=createBike();
  generateLevel();
  return true;
}

function resetGame(){
  game.score=0; game.coinsCollected=0; game.distance=0; game.lives=levelData().lives;
  game.gameOver=false; game.levelComplete=false; game.won=false; game.started=false; game.paused=false;
  game.combo=1; game.comboTimer=0; game.cameraX=0; game.message=''; game.messageTimer=0;
  game.bike=null; game.checkpointIndex=0; game.levelScore=0; game.levelCoins=0;
  game.particles=[]; game.floatingTexts=[];
}
function nextLevel(){
  if(game.level<5){ game.unlockedLevel=Math.max(game.unlockedLevel,game.level+1); saveProgress(); return startLevel(game.level+1); }
  game.won=true; game.levelComplete=false; game.started=true; game.bestScore=Math.max(game.bestScore,game.score); saveProgress(); return true;
}

function damageBike(reason='impact'){
  if(game.invulnerable>0 || game.gameOver) return;
  game.lives--; game.invulnerable=1.8; game.shake=.55; game.combo=1; game.comboTimer=0;
  game.score=Math.max(0,game.score-150); floatText(reason==='hazard'?'PELIGRO':'-150',game.bike.x,game.bike.y-55); makeParticle(game.bike.x,game.bike.y,'hit',18);
  game.bike.vx*=.35; game.bike.vy=-6; game.bike.angularVelocity=0.12;
  if(game.lives<=0){ game.gameOver=true; game.message='GAME OVER'; game.messageTimer=99; }
}

function collectCoins(){
  for(const c of game.coins){
    if(c.collected) continue;
    const dx=c.x-game.bike.x, dy=c.y-game.bike.y;
    if(dx*dx+dy*dy<55*55){
      c.collected=true; game.coinsCollected++; game.levelCoins++;
      game.combo=clamp(game.combo+0.25,1,5); game.comboTimer=2.6;
      const pts=Math.round(100*game.combo); game.score+=pts; game.levelScore+=pts;
      floatText(`+${pts}`,c.x,c.y); makeParticle(c.x,c.y,'spark',12);
    }
  }
}
function checkCheckpoints(){
  for(let i=0;i<game.checkpoints.length;i++){
    const c=game.checkpoints[i];
    if(!c.passed && game.bike.x>=c.x){
      c.passed=true; game.checkpointIndex=i+1; game.score+=250; game.levelScore+=250; game.combo=clamp(game.combo+0.5,1,5); game.comboTimer=3;
      game.message='CHECKPOINT'; game.messageTimer=1.2; floatText('+250 CHECKPOINT',c.x,c.y-70); makeParticle(c.x,c.y-55,'spark',22);
    }
  }
}
function checkObstacles(){
  for(const o of game.obstacles){
    if(o.hit || Math.abs(o.x-game.bike.x)>90) continue;
    const bikeBottom=game.bike.y+game.bike.h*.45;
    const nearY=Math.abs(bikeBottom-(o.y-o.h*.5))<45;
    const nearX=Math.abs(game.bike.x-o.x)<(game.bike.w*.45+o.w*.45);
    if(nearX&&nearY){ o.hit=true; damageBike('impact'); }
  }
}
function checkHazards(){
  for(const h of game.hazards){
    if(game.bike.x>h.x&&game.bike.x<h.x+h.w&&game.bike.y>getGroundY(game.bike.x)-80){ damageBike('hazard'); }
  }
}
function checkFinish(){
  const d=levelData();
  if(game.bike.x>=d.length){
    game.distance=d.length; game.levelComplete=true; game.score+=1000*d.difficulty;
    game.bestScore=Math.max(game.bestScore,game.score); saveProgress();
    game.message=game.level===5?'CUMBRE CONQUISTADA':'NIVEL COMPLETADO'; game.messageTimer=99;
    makeParticle(game.bike.x,getGroundY(game.bike.x)-50,'spark',60);
  }
}

function physics(action){
  const b=game.bike, d=levelData();
  const accel=.22, brake=.38, friction=.988, gravity=.62;
  if(action==='accelerate') b.vx+=accel;
  if(action==='brake') b.vx-=brake;
  if(action==='jump' && b.onGround){ b.vy=-13.6; b.onGround=false; b.angularVelocity=-.08; makeParticle(b.x,b.y+b.h*.35,'dust',12); }
  if(!b.onGround && action==='accelerate') b.angularVelocity-=.006;
  if(!b.onGround && action==='brake') b.angularVelocity+=.006;
  b.vx*=friction; b.vx=clamp(b.vx,-2.2,d.speed);
  if(b.vx<0) b.vx*=.96;
  b.vy+=gravity;
  b.x+=b.vx; b.y+=b.vy;
  const ground=getGroundY(b.x)-b.h*.48;
  b.wasOnGround=b.onGround;
  if(b.y>=ground){
    if(!b.wasOnGround && b.vy>5){ game.score+=Math.round(Math.min(400,b.vy*35)); game.levelScore+=Math.round(Math.min(400,b.vy*35)); makeParticle(b.x,b.y+b.h*.4,'dust',12); game.shake=.15; }
    b.y=ground; b.vy=0; b.onGround=true; b.angle*=.72;
  }else b.onGround=false;
  if(b.onGround){ const slope=getSlope(b.x); b.angle=slope*.75; b.angularVelocity*=.65; }
  else { b.angle+=b.angularVelocity; b.angle=clamp(b.angle,-1.35,1.35); }
  if(b.onGround && b.vx>2 && rand()<.35) makeParticle(b.x-34,b.y+22,'dust',1);
  game.distance=Math.max(game.distance,clamp(b.x-180,0,d.length));
}

function updateEffects(dt){
  game.time+=dt; if(game.invulnerable>0) game.invulnerable-=dt;
  if(game.comboTimer>0) game.comboTimer-=dt; else game.combo=1;
  if(game.messageTimer>0) game.messageTimer-=dt;
  game.shake=Math.max(0,game.shake-dt*1.7);
  for(const c of game.coins) if(!c.collected) c.spin+=dt*5;
  for(const p of game.particles){p.x+=p.vx;p.y+=p.vy;p.vy+=.08;p.life-=dt*1.5;p.size*=.995;}
  game.particles=game.particles.filter(p=>p.life>0);
  for(const f of game.floatingTexts){f.y+=f.vy;f.life-=dt*.8;}
  game.floatingTexts=game.floatingTexts.filter(f=>f.life>0);
}

function step(action='nothing'){
  if(!ACTIONS.includes(action)) action='nothing';
  game.lastAction=action;
  if(!game.started || game.paused || game.gameOver || game.levelComplete || game.won) return getState();
  physics(action); collectCoins(); checkCheckpoints(); checkObstacles(); checkHazards(); checkFinish(); updateEffects(1/60);
  return getState();
}
function getAvailableActions(){ return ACTIONS.slice(); }
function getState(){
  const d=levelData(), b=game.bike||{x:0,y:0,vx:0,vy:0,angle:0,onGround:false};
  const obstacleAhead=game.obstacles.filter(o=>!o.hit&&o.x>=b.x).sort((a,c)=>a.x-c.x)[0];
  const rampAhead=game.ramps.filter(r=>r.x>=b.x).sort((a,c)=>a.x-c.x)[0];
  return {
    version:game.version, started:game.started, paused:game.paused, level:game.level, levelName:d.name,
    theme:d.theme,x:Number(b.x.toFixed(3)),y:Number(b.y.toFixed(3)),velocityX:Number(b.vx.toFixed(3)),velocityY:Number(b.vy.toFixed(3)),
    angle:Number(b.angle.toFixed(3)),groundY:Number(getGroundY(b.x).toFixed(3)),onGround:!!b.onGround,
    distance:Number(game.distance.toFixed(2)),levelLength:d.length,progress:Number(clamp(b.x/d.length,0,1).toFixed(4)),
    score:game.score,bestScore:game.bestScore,lives:game.lives,coinsCollected:game.coinsCollected,
    remainingCoins:game.coins.filter(c=>!c.collected).length,checkpointsPassed:game.checkpointIndex,totalCheckpoints:game.totalCheckpoints,
    combo:Number(game.combo.toFixed(2)),comboTimer:Number(Math.max(0,game.comboTimer).toFixed(2)),gameOver:game.gameOver,
    levelComplete:game.levelComplete,won:game.won,unlockedLevel:game.unlockedLevel,lastAction:game.lastAction,
    obstacleAhead:obstacleAhead?{x:Number(obstacleAhead.x.toFixed(2)),distance:Number((obstacleAhead.x-b.x).toFixed(2)),type:obstacleAhead.type}:null,
    rampAhead:rampAhead?{x:Number(rampAhead.x.toFixed(2)),distance:Number((rampAhead.x-b.x).toFixed(2)),width:rampAhead.w,type:rampAhead.type}:null
  };
}

function togglePause(){ if(game.started&&!game.gameOver&&!game.levelComplete&&!game.won) game.paused=!game.paused; }
function updateKeyboard(){
  if(typeof window==='undefined') return;
  const k=window.__mbrKeys||{};
  let action='nothing';
  if(k.Space) action='jump'; else if(k.ArrowUp||k.KeyW) action='accelerate'; else if(k.ArrowDown||k.KeyS) action='brake';
  step(action);
}

loadProgress();

if(typeof window!=='undefined'){
  window.MBR={game,LEVELS,ACTIONS,startLevel,resetGame,nextLevel,step,getState,getAvailableActions,getLevelData,togglePause,updateKeyboard};
  window.game=game;
}
if(typeof module!=='undefined') module.exports={game,LEVELS,ACTIONS,startLevel,resetGame,nextLevel,step,getState,getAvailableActions,getLevelData,togglePause,updateKeyboard};
