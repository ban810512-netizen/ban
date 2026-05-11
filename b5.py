#!/usr/bin/env python3
"""v9 Part 5: Game State, UI, Minimap, Scorecard, Game Flow"""
f = open('/home/user/webapp/index.html', 'a')
f.write(r'''
/* ===== GAME STATE ===== */
const G={
state:'menu',ci:0,hi:0,par:0,stroke:0,maxStk:8,
scores:[],wind:{spd:0,dir:0,x:0,z:0},
aim:0,power:0,accuracy:50,
swPhase:'idle',gaugeVal:0,gaugeDir:1,
accVal:50,accDir:1,
flyT:0,flyActive:false,
ball:{x:0,y:.063,z:0,vx:0,vy:0,vz:0,flying:false,stopped:true,holed:false,inWater:false,isOB:false},
ci_:0,putting:false,settled:false,roundActive:false
};

/* ===== UI HELPERS ===== */
const $=id=>document.getElementById(id);
const SCREENS=['hud','clubBtn','minimap','swingPanel','flyover','scoreScr','resultScr','menuScr','courseScr','recordScr','settingScr','loading'];
function hideAll(){SCREENS.forEach(id=>{const el=$(id);if(el)el.style.display='none'})}

function showScr(name){
hideAll();
if(name==='menu'){$('menuScr').style.display='flex'}
else if(name==='game'){$('hud').style.display='block';$('clubBtn').style.display='block';$('minimap').style.display='block'}
else if(name==='swing'){$('hud').style.display='block';$('minimap').style.display='block';$('swingPanel').style.display='block'}
else if(name==='flyover'){$('hud').style.display='block';$('flyover').style.display='block'}
else if(name==='score'){$('scoreScr').style.display='flex'}
else if(name==='result'){$('resultScr').style.display='flex'}
else if(name==='course'){$('courseScr').style.display='block'}
else if(name==='records'){$('recordScr').style.display='block'}
else if(name==='settings'){$('settingScr').style.display='block'}
else if(name==='loading'){$('loading').style.display='flex'}
}

function updHUD(){
const c=COURSES[G.ci],h=c.par[G.hi];
$('hCrs').textContent=c.name;
$('hHole').textContent=`${G.hi+1}홀`;
$('hPar').textContent=`PAR ${h}`;
$('hStk').textContent=`${G.stroke}타`;
const d=holeP?Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z):0;
$('hDst').textContent=`${d.toFixed(1)}m`;
$('hWnd').innerHTML=`${G.wind.spd.toFixed(1)}<span id="hWndArr" style="display:inline-block;font-size:10px;transform:rotate(${Math.round(G.wind.dir*180/Math.PI)}deg)">↑</span>`;
$('clubBtn').textContent=CLUBS[G.ci_].name;
}

function showBig(txt,dur=1800){
const el=$('bigMsg');el.textContent=txt;el.style.display='block';el.style.opacity='1';
el.style.animation='none';el.offsetHeight;el.style.animation='';
setTimeout(()=>{el.style.opacity='0';setTimeout(()=>el.style.display='none',400)},dur);
}

function showSwing(show){
$('swingPanel').style.display=show?'block':'none';
if(show){$('pwrFill').style.width='0%';$('accFill').style.width='0%';$('accWrap').style.display='none';
G.swPhase='power';G.gaugeVal=0;G.gaugeDir=1;$('swVal').textContent='0%'}}

/* ===== MINIMAP ===== */
function drawMinimap(){
const cv=$('mmCvs');if(!cv)return;const ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
ctx.clearRect(0,0,W,H);
ctx.fillStyle='rgba(0,60,0,0.85)';ctx.fillRect(0,0,W,H);
ctx.strokeStyle='rgba(255,255,255,0.3)';ctx.lineWidth=1;ctx.strokeRect(0,0,W,H);
const sc=W/160,ox=W/2,oz=H*.85;
const tx=x=>ox+x*sc,tz=z=>oz+z*sc;
// Fairway
if(teeP&&holeP){
ctx.fillStyle='rgba(100,200,80,0.4)';ctx.beginPath();
ctx.ellipse(tx((teeP.x+holeP.x)/2),tz((teeP.z+holeP.z)/2),
Math.abs(holeP.z-teeP.z)*sc/2+10,15,
Math.atan2(holeP.x-teeP.x,holeP.z-teeP.z),0,Math.PI*2);ctx.fill();
// Green
ctx.fillStyle='rgba(0,180,60,0.7)';ctx.beginPath();ctx.arc(tx(holeP.x),tz(holeP.z),8,0,Math.PI*2);ctx.fill();
// Pin
ctx.fillStyle='#ff3333';ctx.beginPath();ctx.arc(tx(holeP.x),tz(holeP.z),3,0,Math.PI*2);ctx.fill();
// Tee
ctx.fillStyle='#ffcc00';ctx.beginPath();ctx.arc(tx(teeP.x),tz(teeP.z),3,0,Math.PI*2);ctx.fill()}
// Water
waters.forEach(w=>{ctx.fillStyle='rgba(30,100,200,0.5)';ctx.beginPath();ctx.arc(tx(w.x),tz(w.z),5,0,Math.PI*2);ctx.fill()});
// Ball
ctx.fillStyle='#ffffff';ctx.strokeStyle='#000';ctx.lineWidth=1;
ctx.beginPath();ctx.arc(tx(G.ball.x),tz(G.ball.z),4,0,Math.PI*2);ctx.fill();ctx.stroke();
// Wind arrow
if(G.wind.spd>0){ctx.save();ctx.translate(W-20,20);ctx.rotate(G.wind.dir);
ctx.strokeStyle='#ff6';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,-10);ctx.lineTo(0,10);ctx.moveTo(-4,-5);ctx.lineTo(0,-10);ctx.lineTo(4,-5);ctx.stroke();ctx.restore();
ctx.fillStyle='#ff6';ctx.font='9px sans-serif';ctx.textAlign='center';ctx.fillText(`${G.wind.spd.toFixed(1)}`,W-20,38)}}

/* ===== SCORECARD ===== */
function mkScore(){
const c=COURSES[G.ci];
let html='<tr><th>홀</th>';for(let i=0;i<9;i++)html+=`<th>${i+1}</th>`;html+='<th>합</th></tr>';
html+='<tr><td>PAR</td>';let tp=0;for(let i=0;i<9;i++){tp+=c.par[i];html+=`<td>${c.par[i]}</td>`}html+=`<td>${tp}</td></tr>`;
html+='<tr><td>타수</td>';let ts=0;
for(let i=0;i<9;i++){const s=G.scores[i];
if(s!==undefined){ts+=s;const d=s-c.par[i];const cls=d<=-2?'eagle':d===-1?'birdie':d===0?'par':d===1?'bogey':'dbogey';
html+=`<td class="${cls}">${s}</td>`}else html+='<td>-</td>'}
html+=`<td>${ts||'-'}</td></tr>`;
$('scTbl').innerHTML=html;
$('scTot').textContent=ts?`${ts}타 (${ts-tp>=0?'+':''}${ts-tp})`:'';
$('scTitle').textContent=c.name;$('scSub').textContent=`${G.hi+1}홀 완료`}

/* ===== WIND ===== */
function setWind(){
const c=COURSES[G.ci];
G.wind.spd=Math.random()*(c.wind||3)+.5;
G.wind.dir=Math.random()*Math.PI*2;
G.wind.x=Math.sin(G.wind.dir)*G.wind.spd*.15;
G.wind.z=Math.cos(G.wind.dir)*G.wind.spd*.15}

/* ===== AUTO CLUB ===== */
function autoClub(){
const d=holeP?Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z):50;
if(d<8){G.ci_=3;G.putting=true}
else if(d<25){G.ci_=2;G.putting=false}
else if(d<50){G.ci_=1;G.putting=false}
else{G.ci_=0;G.putting=false}}

/* ===== POSITION GOLFER ===== */
function posGolfer(){
if(!golfer)return;golfer.visible=true;
golfer.position.set(G.ball.x,gndH(G.ball.x,G.ball.z),G.ball.z);
golfer.rotation.set(0,G.aim,0);
P.addr(golfer)}

/* ===== START ROUND ===== */
function startRound(ci){
G.ci=ci;G.hi=0;G.scores=[];G.roundActive=true;
showScr('loading');$('ldFill').style.width='0%';
setTimeout(()=>{$('ldFill').style.width='50%'},100);
setTimeout(()=>{$('ldFill').style.width='100%';startHole()},500)}

/* ===== START HOLE ===== */
function startHole(){
const c=COURSES[G.ci];
G.par=c.par[G.hi];G.stroke=0;G.settled=false;G.putting=false;G.ci_=0;
G.ball.holed=false;G.ball.inWater=false;G.ball.isOB=false;G.ball.flying=false;G.ball.stopped=true;
setWind();buildCourse(G.ci,G.hi);
// Reset ball to tee
G.ball.x=teeP.x;G.ball.y=gndH(teeP.x,teeP.z)+.063;G.ball.z=teeP.z;
G.ball.vx=G.ball.vy=G.ball.vz=0;
updBM();if(ballM)ballM.visible=true;
autoClub();
// Aim toward hole
G.aim=Math.atan2(holeP.x-teeP.x,-(holeP.z-teeP.z));
clearTrail();
// Flyover
G.flyActive=true;G.flyT=0;
showScr('flyover');
$('flyH').textContent=`${G.hi+1}홀`;
$('flyPar').textContent=G.par;
$('flyDist').textContent=c.dist[G.hi];
updHUD();drawMinimap();
AUD.init();AUD.resume()}

/* ===== END FLYOVER ===== */
window.endFly=function(){
G.flyActive=false;G.state='aim';
showScr('game');
posGolfer();
updAim(70);showAimL();
CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim);CAM.mode='behind';
updHUD();drawMinimap();
showBig(`${G.hi+1}홀 PAR ${G.par}`,1500)};

/* ===== DO SWING ===== */
function doSwing(power,accuracy){
G.state='swing';G.settled=false;G.stroke++;
const club=CLUBS[G.ci_];
const accOff=(accuracy-50)/50*.12;
const dir=G.aim+accOff;
const spd=club.power*(power/100);
const loft=rad(club.loft);
G.ball.vx=Math.sin(dir)*Math.cos(loft)*spd;
G.ball.vy=Math.sin(loft)*spd;
G.ball.vz=-Math.cos(dir)*Math.cos(loft)*spd;
G.ball.flying=true;G.ball.stopped=false;G.ball.holed=false;G.ball.inWater=false;G.ball.isOB=false;
hideAim();clearTrail();
if(!G.putting)AUD.play('hit');else AUD.play('putt');
SA.start(power,G.putting,null);
CAM.swingClose({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim);CAM.mode='swing';
CAM.shake(.03,.25);
updHUD()}

/* ===== ON BALL STOP ===== */
function onBallStop(){
if(G.settled)return;G.settled=true;
updBM();
// Holed
if(G.ball.holed){
if(ballM)ballM.visible=false;
const diff=G.stroke-G.par;
let msg='';
if(G.stroke===1)msg='🎉 홀인원!!!';
else if(diff<=-3)msg='🦅 알바트로스!';
else if(diff===-2)msg='🦅 이글!';
else if(diff===-1)msg='🐦 버디!';
else if(diff===0)msg='👍 파!';
else if(diff===1)msg='보기';
else if(diff===2)msg='더블보기';
else msg='트리플보기+';
showBig(msg,2500);if(golfer)P.celebrate(golfer);
G.scores[G.hi]=G.stroke;
setTimeout(()=>showScorecard(),3000);return}
// Water penalty
if(G.ball.inWater){showBig('💦 워터 해저드! +1벌타',1800);G.stroke++;
G.ball.x=teeP.x;G.ball.y=gndH(teeP.x,teeP.z)+.063;G.ball.z=teeP.z;
G.ball.vx=G.ball.vy=G.ball.vz=0;G.ball.flying=false;G.ball.stopped=true;updBM()}
// OB penalty
if(G.ball.isOB){showBig('⚠️ OB! +1벌타',1800);G.stroke++;
G.ball.x=teeP.x;G.ball.y=gndH(teeP.x,teeP.z)+.063;G.ball.z=teeP.z;
G.ball.vx=G.ball.vy=G.ball.vz=0;G.ball.flying=false;G.ball.stopped=true;updBM()}
// Max strokes
if(G.stroke>=G.maxStk){showBig('최대타수 도달',1500);G.scores[G.hi]=G.maxStk;
setTimeout(()=>showScorecard(),2000);return}
// Continue
setTimeout(()=>{
autoClub();
G.aim=Math.atan2(holeP.x-G.ball.x,-(holeP.z-G.ball.z));
posGolfer();updAim(70);showAimL();
G.state='aim';
CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aim);CAM.mode='behind';
showScr('game');updHUD();drawMinimap()},800)}

/* ===== SCORECARD ===== */
function showScorecard(){mkScore();showScr('score');G.state='score'}

/* ===== NEXT HOLE ===== */
window.nextHole=function(){
if(G.hi<8){G.hi++;showScr('loading');$('ldFill').style.width='0%';
setTimeout(()=>{$('ldFill').style.width='100%';startHole()},400)}
else showResult()};

/* ===== RESULT ===== */
function showResult(){
G.roundActive=false;const c=COURSES[G.ci];
let tp=0,ts=0;for(let i=0;i<9;i++){tp+=c.par[i];ts+=G.scores[i]||0}
$('rsTitle').textContent=c.name+' 라운드 결과';
$('rsSub').textContent=`${ts}타`;
const diff=ts-tp;
$('rsTot').textContent=diff===0?'이븐파':diff>0?`+${diff}`:`${diff}`;
$('rsTot').style.color=diff<0?'#4f4':diff===0?'#fff':'#f66';
let html='';for(let i=0;i<9;i++){const s=G.scores[i]||0,p=c.par[i],d=s-p;
const cls=d<=-2?'eagle':d===-1?'birdie':d===0?'par':d===1?'bogey':'dbogey';
html+=`<div class="resHole"><span>${i+1}홀</span><span>PAR${p}</span><span class="${cls}">${s}(${d>=0?'+':''}${d})</span></div>`}
$('rsBody').innerHTML=html;
// Save best
const data=STO.d;const key='c'+G.ci;
if(!data.best[key]||ts<data.best[key]){data.best[key]=ts;STO.save()}
showScr('result');G.state='result'}
''')
f.close()
print(f"Part 5 done: {__import__('os').path.getsize('/home/user/webapp/index.html')} bytes")
