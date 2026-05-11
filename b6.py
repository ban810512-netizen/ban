#!/usr/bin/env python3
"""v9 Part 6: Input, Menu, Game Loop, Init, Closing HTML"""
f = open('/home/user/webapp/index.html', 'a')
f.write(r'''
/* ===== GAUGE TICK ===== */
function tickGauge(dt){
if(G.swPhase==='power'){
G.gaugeVal+=G.gaugeDir*2.8*dt*100;
if(G.gaugeVal>=100){G.gaugeVal=100;G.gaugeDir=-1}
if(G.gaugeVal<=0){G.gaugeVal=0;G.gaugeDir=1}
$('pwrFill').style.width=G.gaugeVal+'%';
$('swVal').textContent=Math.round(G.gaugeVal)+'%'}
else if(G.swPhase==='accuracy'){
G.accVal+=G.accDir*3.4*dt*100;
if(G.accVal>=100){G.accVal=100;G.accDir=-1}
if(G.accVal<=0){G.accVal=0;G.accDir=1}
$('accFill').style.width=G.accVal+'%'}}

/* ===== SWING TAP ===== */
window.onSwTap=function(e){
if(e)e.preventDefault();
if(G.swPhase==='power'){
G.power=G.gaugeVal;G.swPhase='accuracy';
$('accWrap').style.display='block';G.accVal=50;G.accDir=1;
$('swVal').textContent='정확도';AUD.play('click')}
else if(G.swPhase==='accuracy'){
G.accuracy=G.accVal;G.swPhase='idle';
showSwing(false);showScr('game');
doSwing(G.power,G.accuracy);AUD.play('click')}};

/* ===== TOUCH / MOUSE INPUT ===== */
let dragStart=null,dragging=false,lastTouch=null;
function getXY(e){if(e.touches&&e.touches.length>0)return{x:e.touches[0].clientX,y:e.touches[0].clientY};return{x:e.clientX,y:e.clientY}}

function onPtrDown(e){
AUD.init();AUD.resume();
const p=getXY(e);dragStart={x:p.x,y:p.y};dragging=false;lastTouch=p}

function onPtrMove(e){
if(!dragStart)return;const p=getXY(e);
if(Math.abs(p.x-dragStart.x)+Math.abs(p.y-dragStart.y)>5)dragging=true;
if(dragging&&G.state==='aim'){
const sens=0.004;
G.aim-=(p.x-lastTouch.x)*sens;
updAim(70);
if(golfer)golfer.rotation.y=G.aim;
CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim);CAM.update(0)}
lastTouch=p}

function onPtrUp(e){
if(!dragging){
if(G.state==='aim'){
showSwing(true);showScr('swing');
if(G.putting)P.paddr(golfer);else P.addr(golfer)}
else if(G.flyActive){endFly()}}
dragStart=null;dragging=false}

/* Keyboard */
function onKey(e){
if(e.code==='Space'||e.code==='Enter'){
if(G.state==='aim'){showSwing(true);showScr('swing')}
else if(G.swPhase==='power'||G.swPhase==='accuracy'){onSwTap()}
else if(G.flyActive){endFly()}
else if(G.state==='score'){nextHole()}}
if(G.state==='aim'){
if(e.code==='ArrowLeft'){G.aim+=.03;updAim(70);if(golfer)golfer.rotation.y=G.aim;CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim)}
if(e.code==='ArrowRight'){G.aim-=.03;updAim(70);if(golfer)golfer.rotation.y=G.aim;CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim)}}}

function bindInput(){
const cv=renderer.domElement;
cv.addEventListener('mousedown',onPtrDown);cv.addEventListener('mousemove',onPtrMove);cv.addEventListener('mouseup',onPtrUp);
cv.addEventListener('touchstart',onPtrDown,{passive:true});cv.addEventListener('touchmove',onPtrMove,{passive:true});cv.addEventListener('touchend',onPtrUp);
document.addEventListener('keydown',onKey)}

/* ===== CLUB CYCLE ===== */
$('clubBtn').onclick=function(){
G.ci_=(G.ci_+1)%4;G.putting=G.ci_===3;
updHUD();AUD.play('click')};

/* ===== MENU FUNCTIONS ===== */
window.showMenu=function(){G.state='menu';showScr('menu')};
window.openCourseSelect=function(){
let html='';COURSES.forEach((c,i)=>{
const tp=c.par.reduce((a,v)=>a+v,0);
const best=STO.d.best&&STO.d.best['c'+i]?` 🏆 ${STO.d.best['c'+i]}타`:'';
html+=`<div class="ci" onclick="startRound(${i})"><div style="width:40px;height:40px;border-radius:8px;background:linear-gradient(135deg,#2a8a2a,#4aba4a);display:flex;align-items:center;justify-content:center;font-size:18px;margin-right:12px">⛳</div><div><div class="cn">${c.name}</div><div class="cc">${c.city} · 9홀 · PAR ${tp}${best}</div></div></div>`});
$('cList').innerHTML=html;showScr('course');G.state='course'};
window.openRecords=function(){
let html='';COURSES.forEach((c,i)=>{
const tp=c.par.reduce((a,v)=>a+v,0);
const best=STO.d.best&&STO.d.best['c'+i];
html+=`<div style="padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05)"><div style="display:flex;justify-content:space-between"><span style="color:#fff;font-weight:700">${c.name}</span><span style="color:${best?'#ffd700':'rgba(255,255,255,.3)'}">${best?best+'타':'-'}</span></div><div style="font-size:10px;color:rgba(255,255,255,.4)">${c.city} · PAR ${tp}${best?` (${best-tp>=0?'+':''}${best-tp})`:''}</div></div>`});
$('rList').innerHTML=html;showScr('records');G.state='records'};
window.openSettings=function(){showScr('settings');G.state='settings'};
window.startRound=startRound;

/* ===== MAIN GAME LOOP ===== */
const clock=new THREE.Clock();
let lastMiniT=0;

function gameLoop(){
requestAnimationFrame(gameLoop);
const dt=Math.min(clock.getDelta(),.05);
const elapsed=clock.getElapsedTime();

// Gauge
if(G.swPhase==='power'||G.swPhase==='accuracy')tickGauge(dt);

// Swing animation
SA.update(dt);

// Flyover
if(G.flyActive){
G.flyT+=dt*.35;
if(G.flyT>=1)endFly();
else{const t=G.flyT;CAM.flyover(t,teeP,holeP);CAM.update(dt)}}

// Physics
if(G.state==='swing'&&G.ball.flying){
physTick(dt);updBM();updTrail();
CAM.follow({x:G.ball.x,y:G.ball.y,z:G.ball.z},{x:G.ball.vx,z:G.ball.vz});CAM.update(dt);
if(G.ball.stopped&&!G.settled){setTimeout(()=>onBallStop(),400)}}

// Camera in aim
if(G.state==='aim'){CAM.update(dt)}

// Result cam orbit
if(G.state==='result'&&holeP){CAM.result(holeP);CAM.update(dt)}

// Particles
updP(dt);

// Water animation
waters.forEach(w=>{if(w.mesh)w.mesh.position.y=w.mesh.userData.baseY+Math.sin(elapsed*1.5+w.x*.1)*.05});

// Flag wave
if(flagM)flagM.rotation.y=Math.sin(elapsed*3)*.3;

// Golfer idle breathing
if(golfer&&golfer.visible&&G.state==='aim'&&!SA.active){
const b=Math.sin(elapsed*2)*.008;
golfer.userData.torso.position.y=golfer.userData.torsoBaseY+b}

// Minimap
if(elapsed-lastMiniT>.3&&(G.state==='aim'||G.state==='swing')){drawMinimap();lastMiniT=elapsed}

renderer.render(scene,camera)}

/* ===== INITIALIZATION ===== */
function init(){
initScene();initMaterials();
createGolfer();mkBall();mkAim();initTrail();
bindInput();
showScr('menu');G.state='menu';
$('loading').style.display='none';
gameLoop();
console.log('Park Golf Pro v9 initialized')}

/* ===== SERVICE WORKER ===== */
if('serviceWorker' in navigator){
navigator.serviceWorker.register('sw.js').catch(e=>console.warn('SW:',e))}

/* ===== START ===== */
window.addEventListener('DOMContentLoaded',()=>setTimeout(init,100));

</script>
</body>
</html>
''')
f.close()
print(f"Part 6 done: {__import__('os').path.getsize('/home/user/webapp/index.html')} bytes")
