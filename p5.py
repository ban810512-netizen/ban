#!/usr/bin/env python3
"""v9 Part 5: Game State, UI Helpers, Minimap, Scorecard, Game Flow"""
import pathlib
pathlib.Path('/home/user/webapp/index.html').open('a').write(r"""
/* ========== PART 5: GAME STATE + UI + GAME FLOW ========== */

/* --- Game State --- */
const G={
 state:'menu',course:0,hole:0,par:0,stroke:0,maxStrk:8,
 scores:[],totalPar:0,totalStrk:0,wind:{spd:0,dir:0,dx:0,dz:0},
 power:0,accuracy:0,aimYaw:0,aimPitch:0,
 swingPhase:'idle',gaugeVal:0,gaugeDir:1,gaugeSpd:2.8,
 accVal:0,accDir:1,accSpd:3.4,
 flyoverActive:false,flyoverT:0,
 settled:false,putting:false,ballInHole:false,
 camFollow:false,shotReady:false,
 clubIdx:0,spinX:0,spinZ:0,
 teePos:new THREE.Vector3(),pinPos:new THREE.Vector3(),
 holeDist:0,ballStartPos:new THREE.Vector3(),
 savedScores:null,roundActive:false
};

/* --- UI Element References --- */
const $=id=>document.getElementById(id);
const UI={
 hud:$('hud'),mini:$('minimap'),swing:$('swingPanel'),
 flyover:$('flyoverOvl'),scorecard:$('scorecard'),
 result:$('resultScr'),menu:$('menuScr'),
 courseSelect:$('courseSelect'),records:$('recordsScr'),
 settings:$('settingsScr'),loading:$('loadingScr'),
 bigMsg:$('bigMsg'),
 hCourse:$('hCourse'),hHole:$('hHole'),hPar:$('hPar'),
 hStroke:$('hStroke'),hDist:$('hDist'),hClub:$('hClub'),
 hWind:$('hWind'),hWindDir:$('hWindDir'),
 pwrBar:$('pwrBar'),pwrFill:$('pwrFill'),accBar:$('accBar'),accFill:$('accFill'),
 flyHole:$('flyHole'),flyPar:$('flyPar'),flyDist:$('flyDist'),
 scoreBody:$('scoreBody'),scoreTtl:$('scoreTtl'),
 resCourse:$('resCourse'),resTotal:$('resTotal'),resToPar:$('resToPar'),resBody:$('resBody'),
 csList:$('csList'),recBody:$('recBody'),
 sfxRange:$('sfxRange'),bgmRange:$('bgmRange'),vibChk:$('vibChk'),
 canvas:document.querySelector('canvas')
};

/* --- Show/Hide Screens --- */
function showScr(name){
 ['hud','mini','swing','flyover','scorecard','result','menu','courseSelect','records','settings','loading'].forEach(k=>{
  if(UI[k])UI[k].style.display='none';
 });
 if(name==='game'){
  UI.hud.style.display='flex';UI.mini.style.display='block';
 } else if(name==='swing'){
  UI.hud.style.display='flex';UI.mini.style.display='block';UI.swing.style.display='flex';
 } else if(name==='flyover'){
  UI.hud.style.display='flex';UI.flyover.style.display='flex';
 } else if(name==='scorecard'){
  UI.scorecard.style.display='flex';
 } else if(name==='result'){
  UI.result.style.display='flex';
 } else if(name==='menu'){
  UI.menu.style.display='flex';
 } else if(name==='courseSelect'){
  UI.courseSelect.style.display='flex';
 } else if(name==='records'){
  UI.records.style.display='flex';
 } else if(name==='settings'){
  UI.settings.style.display='flex';
 } else if(name==='loading'){
  UI.loading.style.display='flex';
 }
}

/* --- HUD Update --- */
function updHUD(){
 const c=COURSES[G.course];
 const h=c.holes[G.hole];
 UI.hCourse.textContent=c.name;
 UI.hHole.textContent=`${G.hole+1}홀`;
 UI.hPar.textContent=`PAR ${h.par}`;
 UI.hStroke.textContent=`${G.stroke}타`;
 const d=G.putting?ball.position.distanceTo(G.pinPos):ball.position.distanceTo(G.pinPos);
 UI.hDist.textContent=`${d.toFixed(1)}m`;
 UI.hClub.textContent=CLUBS[G.clubIdx].name;
 UI.hWind.textContent=`${G.wind.spd.toFixed(1)}m/s`;
 const wd=Math.round(G.wind.dir*180/Math.PI);
 UI.hWindDir.style.transform=`rotate(${wd}deg)`;
}

/* --- Big Message --- */
function showBig(txt,dur=1800){
 UI.bigMsg.textContent=txt;UI.bigMsg.style.display='block';
 UI.bigMsg.style.opacity='1';
 setTimeout(()=>{UI.bigMsg.style.opacity='0';setTimeout(()=>{UI.bigMsg.style.display='none'},400)},dur);
}

/* --- Swing Panel --- */
function showSwing(show){
 UI.swing.style.display=show?'flex':'none';
 if(show){
  UI.pwrFill.style.height='0%';UI.accFill.style.height='0%';
  UI.accBar.style.display='none';
  G.swingPhase='power';G.gaugeVal=0;G.gaugeDir=1;
 }
}

/* --- Flyover Overlay --- */
function showFly(h){
 UI.flyHole.textContent=`${G.hole+1}홀`;
 UI.flyPar.textContent=`PAR ${h.par}`;
 UI.flyDist.textContent=`${h.dist}m`;
 UI.flyover.style.display='flex';
}

/* --- Minimap Drawing --- */
function drawMinimap(){
 const cv=UI.mini;if(!cv)return;
 const ctx=cv.getContext('2d');
 const W=cv.width,H=cv.height;
 ctx.clearRect(0,0,W,H);
 /* background */
 ctx.fillStyle='rgba(0,60,0,0.85)';
 ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='rgba(255,255,255,0.3)';ctx.lineWidth=1;ctx.strokeRect(0,0,W,H);
 /* scale: map 140m course to minimap */
 const sc=W/160;
 const ox=W/2,oz=H*0.85;
 function tx(x){return ox+x*sc}
 function tz(z){return oz+z*sc}
 /* fairway area */
 if(curHoleData){
  const hp=curHoleData;
  ctx.fillStyle='rgba(100,200,80,0.4)';
  ctx.beginPath();
  ctx.ellipse(tx((hp.tee[0]+hp.pin[0])/2),tz((hp.tee[2]+hp.pin[2])/2),
   Math.abs(hp.pin[2]-hp.tee[2])*sc/2+10,15,
   Math.atan2(hp.pin[0]-hp.tee[0],hp.pin[2]-hp.tee[2]),0,Math.PI*2);
  ctx.fill();
  /* green */
  ctx.fillStyle='rgba(0,180,60,0.7)';
  ctx.beginPath();ctx.arc(tx(hp.pin[0]),tz(hp.pin[2]),8,0,Math.PI*2);ctx.fill();
  /* pin flag */
  ctx.fillStyle='#ff3333';
  ctx.beginPath();ctx.arc(tx(hp.pin[0]),tz(hp.pin[2]),3,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#fff';ctx.font='bold 8px sans-serif';ctx.textAlign='center';
  ctx.fillText('🏁',tx(hp.pin[0]),tz(hp.pin[2])-5);
  /* tee */
  ctx.fillStyle='#ffcc00';
  ctx.beginPath();ctx.arc(tx(hp.tee[0]),tz(hp.tee[2]),3,0,Math.PI*2);ctx.fill();
 }
 /* water hazards */
 if(waterMeshes){
  waterMeshes.forEach(w=>{
   ctx.fillStyle='rgba(30,100,200,0.5)';
   ctx.beginPath();ctx.arc(tx(w.position.x),tz(w.position.z),5,0,Math.PI*2);ctx.fill();
  });
 }
 /* ball */
 if(ball){
  ctx.fillStyle='#ffffff';ctx.strokeStyle='#000';ctx.lineWidth=1;
  ctx.beginPath();ctx.arc(tx(ball.position.x),tz(ball.position.z),4,0,Math.PI*2);ctx.fill();ctx.stroke();
 }
 /* wind arrow */
 if(G.wind.spd>0){
  ctx.save();ctx.translate(W-20,20);ctx.rotate(G.wind.dir);
  ctx.strokeStyle='#ff6';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(0,-10);ctx.lineTo(0,10);ctx.moveTo(-4,-5);ctx.lineTo(0,-10);ctx.lineTo(4,-5);ctx.stroke();
  ctx.restore();
  ctx.fillStyle='#ff6';ctx.font='9px sans-serif';ctx.textAlign='center';
  ctx.fillText(`${G.wind.spd.toFixed(1)}`,W-20,38);
 }
}

/* water mesh refs for minimap */
let waterMeshes=[];

/* --- Scorecard Builder --- */
function mkScore(){
 const c=COURSES[G.course];
 let html='<tr><th>홀</th>';
 for(let i=0;i<9;i++)html+=`<th>${i+1}</th>`;
 html+='<th>합계</th></tr><tr><td>PAR</td>';
 let tp=0;
 for(let i=0;i<9;i++){tp+=c.holes[i].par;html+=`<td>${c.holes[i].par}</td>`}
 html+=`<td>${tp}</td></tr><tr><td>스코어</td>`;
 let ts=0;
 for(let i=0;i<9;i++){
  const s=G.scores[i];
  if(s!==undefined){ts+=s;
   const diff=s-c.holes[i].par;
   const cls=diff<=-2?'eagle':diff===-1?'birdie':diff===0?'par':diff===1?'bogey':'dbogey';
   html+=`<td class="${cls}">${s}</td>`;
  }else html+='<td>-</td>';
 }
 html+=`<td>${ts||'-'}</td></tr>`;
 UI.scoreBody.innerHTML=html;
 UI.scoreTtl.textContent=ts?`${ts}타 (${ts-tp>=0?'+':''}${ts-tp})`:'';
}

/* --- Set Wind --- */
function setWind(){
 G.wind.spd=Math.random()*4+0.5;
 G.wind.dir=Math.random()*Math.PI*2;
 G.wind.dx=Math.sin(G.wind.dir)*G.wind.spd*0.15;
 G.wind.dz=Math.cos(G.wind.dir)*G.wind.spd*0.15;
}

/* --- Current hole helpers --- */
let curHoleData=null;

/* --- Start Round --- */
function startRound(ci){
 G.course=ci;G.hole=0;G.scores=[];G.totalPar=0;G.totalStrk=0;G.roundActive=true;
 showScr('loading');
 setTimeout(()=>{startHole()},600);
}

/* --- Start Hole --- */
function startHole(){
 const c=COURSES[G.course];const h=c.holes[G.hole];
 G.par=h.par;G.stroke=0;G.settled=false;G.ballInHole=false;G.camFollow=false;G.shotReady=false;
 G.putting=false;G.clubIdx=0;G.spinX=0;G.spinZ=0;
 curHoleData=h;
 setWind();
 /* rebuild course */
 buildCourse(G.course,G.hole);
 /* collect water meshes for minimap */
 waterMeshes=[];
 scene.traverse(o=>{if(o.userData&&o.userData.isWater)waterMeshes.push(o)});
 /* position ball at tee */
 G.teePos.set(h.tee[0],gndH(h.tee[0],h.tee[2])+0.22,h.tee[2]);
 G.pinPos.set(h.pin[0],gndH(h.pin[0],h.pin[2]),h.pin[2]);
 G.holeDist=G.teePos.distanceTo(G.pinPos);
 ball.position.copy(G.teePos);
 ballVel.set(0,0,0);ballSpin.set(0,0,0);
 ball.visible=true;
 if(trail)trail.visible=false;
 trailPts=[];
 G.ballStartPos.copy(G.teePos);
 /* position golfer at tee */
 positionGolfer();
 /* auto select club */
 autoClub();
 /* aim toward pin */
 G.aimYaw=Math.atan2(G.pinPos.x-G.teePos.x,G.pinPos.z-G.teePos.z);
 G.aimPitch=0;
 updAimLine();
 /* flyover */
 G.flyoverActive=true;G.flyoverT=0;
 showScr('flyover');showFly(h);
 CAM.mode='flyover';CAM.flyT=0;
 updHUD();
 drawMinimap();
}

/* --- Position Golfer --- */
function positionGolfer(){
 if(!golfer)return;
 golfer.visible=true;
 const bp=ball.position;
 golfer.position.set(bp.x,gndH(bp.x,bp.z),bp.z);
 golfer.rotation.set(0,G.aimYaw,0);
 P.idle(golfer);
}

/* --- Auto Club Selection --- */
function autoClub(){
 const d=ball.position.distanceTo(G.pinPos);
 if(d<8){G.clubIdx=3;G.putting=true}
 else if(d<30)G.clubIdx=2;
 else if(d<60)G.clubIdx=1;
 else G.clubIdx=0;
 G.putting=G.clubIdx===3;
}

/* --- Aim Line --- */
let aimLine=null,aimDots=[];
function updAimLine(){
 if(!aimLine){
  const geo=new THREE.BufferGeometry();
  const pts=[];for(let i=0;i<30;i++)pts.push(0,0,0);
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));
  aimLine=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xffff44,transparent:true,opacity:0.7}));
  aimLine.frustumCulled=false;scene.add(aimLine);
 }
 const pos=aimLine.geometry.attributes.position;
 const bx=ball.position.x,by=ball.position.y,bz=ball.position.z;
 const dx=Math.sin(G.aimYaw)*Math.cos(G.aimPitch);
 const dy=Math.sin(G.aimPitch);
 const dz=Math.cos(G.aimYaw)*Math.cos(G.aimPitch);
 for(let i=0;i<30;i++){
  const t=i*0.5;
  pos.setXYZ(i,bx+dx*t,by+dy*t*0.3+0.1,bz+dz*t);
 }
 pos.needsUpdate=true;
 aimLine.visible=G.state==='aim';
}

/* --- End Flyover --- */
function endFly(){
 G.flyoverActive=false;
 UI.flyover.style.display='none';
 G.state='aim';G.shotReady=true;
 showScr('game');
 CAM.mode='behind';
 CAM.update(0,ball.position,G.aimYaw);
 positionGolfer();
 P.addr(golfer);
 updAimLine();
 updHUD();
 showBig(`${G.hole+1}홀 PAR ${G.par}`,1500);
}

/* --- Do Swing (launch ball) --- */
function doSwing(power,accuracy){
 G.state='swing';G.settled=false;G.ballInHole=false;G.camFollow=true;
 G.stroke++;
 const club=CLUBS[G.clubIdx];
 /* accuracy offset: 0=perfect center, ±deviation */
 const accOff=(accuracy-50)/50*0.15;
 const yaw=G.aimYaw+accOff;
 /* launch params */
 const spd=club.power*power/100;
 const loft=club.loft*Math.PI/180;
 const vx=Math.sin(yaw)*Math.cos(loft)*spd;
 const vy=Math.sin(loft)*spd;
 const vz=Math.cos(yaw)*Math.cos(loft)*spd;
 ballVel.set(vx,vy,vz);
 /* spin */
 ballSpin.set(G.spinX*0.02,0,G.spinZ*0.02);
 G.ballStartPos.copy(ball.position);
 if(trail)trail.visible=true;
 trailPts=[];
 /* hide aim line */
 if(aimLine)aimLine.visible=false;
 /* swing animation */
 const isPutt=G.putting;
 SA.start(power,isPutt,()=>{
  /* ball launched on impact frame handled by velocity already set */
 });
 CAM.mode='swingClose';
 CAM.shakeT=0.3;
 updHUD();
}

/* --- On Ball Stop --- */
function onStop(){
 G.settled=true;G.camFollow=false;
 /* check hole in */
 const dp=ball.position.distanceTo(G.pinPos);
 if(G.ballInHole||dp<0.7){
  G.ballInHole=true;
  ball.visible=false;
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
  showBig(msg,2500);
  AUD.play('hole');
  if(golfer){P.celebrate(golfer)}
  G.scores[G.hole]=G.stroke;
  setTimeout(()=>showScorecard(),3000);
  return;
 }
 /* max strokes */
 if(G.stroke>=G.maxStrk){
  showBig('최대타수 도달',1500);
  G.scores[G.hole]=G.maxStrk;
  setTimeout(()=>showScorecard(),2000);
  return;
 }
 /* continue */
 autoClub();
 G.aimYaw=Math.atan2(G.pinPos.x-ball.position.x,G.pinPos.z-ball.position.z);
 positionGolfer();
 P.addr(golfer);
 G.state='aim';G.shotReady=true;
 CAM.mode='behind';
 updAimLine();
 updHUD();
 drawMinimap();
}

/* --- Show Scorecard --- */
function showScorecard(){
 mkScore();
 showScr('scorecard');
 G.state='scorecard';
}

/* --- Next Hole --- */
function nextHole(){
 if(G.hole<8){
  G.hole++;
  showScr('loading');
  setTimeout(()=>startHole(),500);
 } else {
  showResult();
 }
}

/* --- Show Result --- */
function showResult(){
 G.roundActive=false;
 const c=COURSES[G.course];
 let tp=0,ts=0;
 for(let i=0;i<9;i++){tp+=c.holes[i].par;ts+=G.scores[i]||0}
 G.totalPar=tp;G.totalStrk=ts;
 UI.resCourse.textContent=c.name;
 UI.resTotal.textContent=`${ts}타`;
 const diff=ts-tp;
 UI.resToPar.textContent=diff===0?'이븐파':diff>0?`+${diff}`:`${diff}`;
 UI.resToPar.style.color=diff<0?'#4f4':diff===0?'#fff':'#f66';
 /* per-hole results */
 let html='';
 for(let i=0;i<9;i++){
  const s=G.scores[i]||0;const p=c.holes[i].par;const d=s-p;
  const cls=d<=-2?'eagle':d===-1?'birdie':d===0?'par':d===1?'bogey':'dbogey';
  html+=`<div class="resHole"><span>${i+1}홀</span><span>PAR${p}</span><span class="${cls}">${s}(${d>=0?'+':''}${d})</span></div>`;
 }
 UI.resBody.innerHTML=html;
 /* save record */
 saveRecord(G.course,ts,tp);
 showScr('result');
 G.state='result';
}

/* --- Save / Load Records --- */
function saveRecord(ci,total,par){
 let data=STO.load()||{};
 if(!data.records)data.records={};
 const key='c'+ci;
 if(!data.records[key]||total<data.records[key].best){
  data.records[key]={best:total,par:par,date:new Date().toLocaleDateString('ko-KR')};
 }
 data.lastCourse=ci;
 STO.save(data);
}

function loadRecords(){
 const data=STO.load()||{};
 if(!data.records)return;
 let html='';
 COURSES.forEach((c,i)=>{
  const r=data.records['c'+i];
  html+=`<div class="recRow"><span>${c.name}</span>`;
  if(r)html+=`<span>${r.best}타(${r.best-r.par>=0?'+':''}${r.best-r.par})</span><span>${r.date}</span>`;
  else html+=`<span>-</span><span>-</span>`;
  html+=`</div>`;
 });
 UI.recBody.innerHTML=html;
}

/* --- Vibration helper --- */
function vib(ms){
 try{if(navigator.vibrate&&UI.vibChk&&UI.vibChk.checked)navigator.vibrate(ms)}catch(e){}
}

""")
print("Part 5 written OK")
