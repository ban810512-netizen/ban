# V8 Part 5: Game Logic + UI + Minimap + Scorecard
content = r'''
/* ====== GAME STATE ====== */
const G={
  state:'menu', // menu,course,flyover,aim,swing,flying,stopped,score,result,settings,records
  courseIdx:0,holeIdx:0,
  strokes:0,scores:[],totalScore:0,
  clubIdx:0,
  aimAngle:0,
  swingPhase:'idle', // idle,power,accuracy
  power:0,accuracy:50,
  powerDir:1,accDir:1,
  ball:{x:0,y:.063,z:0,vx:0,vy:0,vz:0,flying:false,stopped:true,holed:false,inWater:false,isOB:false},
  wind:{x:0,z:0,speed:0,angle:0},
  flyT:0,
  isPractice:false,
  prevBallPos:null,
};

/* ====== UI HELPERS ====== */
const $=id=>document.getElementById(id);

function showScr(id){
  for(const s of['menuScr','courseScr','recordScr','settingScr','scoreScr','resultScr','flyover'])
    $(s).style.display='none';
  if(id)$(id).style.display='flex';
}

function showHUD(v){
  $('hud').style.display=v?'':'none';
  $('clubBtn').style.display=v?'':'none';
  $('minimap').style.display=v?'':'none';
}

function updHUD(){
  const c=COURSES[G.courseIdx];
  $('hHole').querySelector('.hv').textContent=G.holeIdx+1;
  $('hPar').querySelector('.hv').textContent=c.par[G.holeIdx];
  $('hCrs').querySelector('.hv').textContent=c.name;
  $('hStk').querySelector('.hv').textContent=G.strokes;
  const dist=d2h(G.ball.x,G.ball.z);
  $('hDst').querySelector('.hv').textContent=dist<1?(dist*100).toFixed(0)+'cm':dist.toFixed(1)+'m';
  $('hWnd').querySelector('.hv').textContent=G.wind.speed.toFixed(1)+'m/s';
  $('clubBtn').textContent=CLUBS[G.clubIdx].icon+' '+CLUBS[G.clubIdx].name;
}

function showBig(main,sub,dur=2000){
  const el=$('bigMsg');
  el.querySelector('.bm').textContent=main;
  el.querySelector('.bs').textContent=sub||'';
  el.style.display='block';
  el.querySelector('.bm').style.animation='none';
  void el.querySelector('.bm').offsetWidth;
  el.querySelector('.bm').style.animation='popIn .4s cubic-bezier(.17,.67,.35,1.2)';
  setTimeout(()=>el.style.display='none',dur);
}

function showSwing(v){
  $('swingPanel').style.display=v?'':'none';
  if(v){
    $('pwrFill').style.width='0%';
    $('pwrMark').style.display='none';
    $('accWrap').style.display='none';
    $('accNdl').style.display='none';
    $('swBtn').textContent='스윙';
    $('swingLabel').textContent='POWER';
    $('swingVal').textContent='0%';
    G.swingPhase='idle';G.power=0;G.accuracy=50;G.powerDir=1;G.accDir=1;
  }
}

function showFly(ci,hi){
  const c=COURSES[ci];
  $('flyH').textContent='Hole '+(hi+1);
  $('flyD').innerHTML='<span>Par <em>'+c.par[hi]+'</em></span><span>거리 <em>'+c.dist[hi]+'m</em></span><span>바람 <em>'+G.wind.speed.toFixed(1)+'m/s</em></span>';
  $('flyover').style.display='block';
}

/* ====== MINIMAP ====== */
function drawMinimap(){
  const cvs=$('mmCvs');
  if(!cvs)return;
  const ctx=cvs.getContext('2d');
  const W=160,H=160;
  ctx.clearRect(0,0,W,H);
  // Background
  ctx.fillStyle='rgba(0,40,0,.85)';
  ctx.fillRect(0,0,W,H);
  // Calculate bounds
  const dist=COURSES[G.courseIdx].dist[G.holeIdx];
  const scale=W/(dist*.5);
  const ox=W/2,oz=H-20;
  const toX=x=>ox+x*scale;
  const toZ=z=>oz+z*scale;
  // Fairway
  ctx.strokeStyle='rgba(60,160,60,.6)';ctx.lineWidth=8*scale;
  ctx.beginPath();
  for(let i=0;i<fwPath.length;i++){
    const mx=toX(fwPath[i].x),mz=toZ(fwPath[i].z);
    if(i===0)ctx.moveTo(mx,mz);else ctx.lineTo(mx,mz);
  }
  ctx.stroke();
  // Green
  ctx.fillStyle='rgba(60,200,60,.5)';
  ctx.beginPath();ctx.arc(toX(grnC.x),toZ(grnC.z),grnR*scale,0,Math.PI*2);ctx.fill();
  // Bunkers
  ctx.fillStyle='rgba(210,180,100,.5)';
  for(const b of bunks){ctx.beginPath();ctx.arc(toX(b.x),toZ(b.z),b.r*scale,0,Math.PI*2);ctx.fill()}
  // Water
  ctx.fillStyle='rgba(30,100,180,.5)';
  for(const w of waters){ctx.fillRect(toX(w.x-w.w),toZ(w.z-w.h),w.w*2*scale,w.h*2*scale)}
  // Hole
  ctx.fillStyle='#ff0';
  ctx.beginPath();ctx.arc(toX(holeP.x),toZ(holeP.z),3,0,Math.PI*2);ctx.fill();
  // Ball
  ctx.fillStyle='#fff';
  ctx.beginPath();ctx.arc(toX(G.ball.x),toZ(G.ball.z),4,0,Math.PI*2);ctx.fill();
  // Aim direction
  if(G.state==='aim'){
    ctx.strokeStyle='rgba(255,255,0,.6)';ctx.lineWidth=1;
    ctx.beginPath();
    ctx.moveTo(toX(G.ball.x),toZ(G.ball.z));
    const ad=CLUBS[G.clubIdx].dist*.3;
    ctx.lineTo(toX(G.ball.x+Math.sin(G.aimAngle)*ad),toZ(G.ball.z-Math.cos(G.aimAngle)*ad));
    ctx.stroke();
  }
}

/* ====== SCORECARD ====== */
function mkScore(elId,scores,ci){
  const c=COURSES[ci];
  const el=$(elId);
  let html='<tr><th>홀</th>';
  for(let i=0;i<9;i++)html+='<th>'+(i+1)+'</th>';
  html+='<th>합계</th></tr><tr><td class="par">파</td>';
  let pSum=0;
  for(let i=0;i<9;i++){html+='<td class="par">'+c.par[i]+'</td>';pSum+=c.par[i]}
  html+='<td class="par">'+pSum+'</td></tr><tr><td>스코어</td>';
  let sSum=0;
  for(let i=0;i<9;i++){
    if(i<scores.length){
      const s=scores[i],diff=s-c.par[i];
      let cls='';
      if(diff<=-2)cls='eagle';else if(diff===-1)cls='birdie';
      else if(diff===1)cls='bogey';else if(diff>=2)cls='dbogey';
      html+='<td class="'+cls+'">'+s+'</td>';
      sSum+=s;
    }else{
      html+='<td>-</td>';
    }
  }
  html+='<td><b>'+(sSum||'-')+'</b></td></tr>';
  el.innerHTML=html;
  return sSum;
}

function scoreName(strokes,par){
  const diff=strokes-par;
  const key=(diff>0?'+':'')+diff;
  return SNAMES[key]||(diff>3?'+'+ diff:'');
}

/* ====== GAME FLOW ====== */
function setWind(ci){
  const c=COURSES[ci];
  const base=c.wind;
  G.wind.speed=base*.5+Math.random()*base;
  G.wind.angle=Math.random()*Math.PI*2;
  G.wind.x=Math.cos(G.wind.angle)*G.wind.speed;
  G.wind.z=Math.sin(G.wind.angle)*G.wind.speed;
}

function startRound(ci,practice){
  G.courseIdx=ci;G.holeIdx=0;
  G.scores=[];G.totalScore=0;
  G.isPractice=practice;
  showScr(null);
  startHole();
}

function startHole(){
  const ci=G.courseIdx,hi=G.holeIdx;
  G.strokes=0;G.clubIdx=0;
  G.swingPhase='idle';
  setWind(ci);
  buildCourse(ci,hi);
  // Place golfer
  if(golfer){scene.remove(golfer)}
  golfer=createGolfer();
  scene.add(golfer);
  // Position golfer at tee
  positionGolfer(teeP,G.aimAngle);
  POSE.idle(golfer);
  rstBall(teeP);
  clearTrail();
  showHUD(true);
  updHUD();
  G.aimAngle=Math.atan2(holeP.x-teeP.x,-(holeP.z-teeP.z));
  // Start flyover
  G.state='flyover';G.flyT=0;
  showFly(ci,hi);
  showSwing(false);
  hideAim();
}

function positionGolfer(pos,aimAngle){
  if(!golfer)return;
  golfer.position.set(pos.x,0,pos.z);
  golfer.rotation.y=aimAngle;
}

function endFly(){
  G.state='aim';
  $('flyover').style.display='none';
  showAim();
  showSwing(true);
  $('aimGuide').style.display='';
  const isPutt=isGrn(G.ball.x,G.ball.z);
  if(isPutt){
    G.clubIdx=3;
    $('puttInfo').style.display='';
    $('puttInfo').textContent='퍼팅 '+d2h(G.ball.x,G.ball.z).toFixed(1)+'m';
    POSE.putt_address(golfer);
  }else{
    POSE.address(golfer);
  }
  positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
  CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aimAngle);
  updAimLine(50);
  updHUD();
  drawMinimap();
}

function doSwing(power,accuracy){
  G.strokes++;
  const club=CLUBS[G.clubIdx];
  const isPutt=G.clubIdx===3;
  hideAim();
  showSwing(false);
  $('aimGuide').style.display='none';
  $('puttInfo').style.display='none';
  // Calculate accuracy offset
  const accOff=(accuracy-50)/50; // -1 to 1
  const angleOff=accOff*rad(8);
  const dir=G.aimAngle+angleOff;
  const pwr=power/100;
  const dist=club.dist*pwr;
  const loft=rad(club.loft);
  const speed=dist*.35;
  // Store previous position for penalty
  G.prevBallPos={x:G.ball.x,z:G.ball.z};
  // Camera close-up for swing
  CAM.swingClose({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aimAngle);
  // Start swing animation, ball fires on impact callback
  SWING_ANIM.start(power,isPutt,()=>{
    // Ball velocity
    G.ball.vx=Math.sin(dir)*speed;
    G.ball.vz=-Math.cos(dir)*speed;
    G.ball.vy=isPutt?.01:Math.sin(loft)*speed*.7;
    G.ball.flying=true;
    G.ball.stopped=false;
    G.ball.holed=false;
    G.ball.inWater=false;
    G.ball.isOB=false;
    G.state='flying';
    clearTrail();
    AUD.play(isPutt?'putt':'hit');
    CAM.shake(isPutt?.01:.03,.2);
  });
  G.state='swing';
  updHUD();
}

function onStop(){
  clearTrail();
  if(G.ball.holed){
    // Holed!
    const c=COURSES[G.courseIdx];
    const par=c.par[G.holeIdx];
    const diff=G.strokes-par;
    const name=scoreName(G.strokes,par);
    G.scores.push(G.strokes);
    if(G.strokes===1){
      showBig('홀인원!!! 🏆','믿을 수 없는 샷!',3000);
      AUD.play('applause');
    }else if(diff<=-2){
      showBig(name+'! 🦅','놀라운 플레이!',2500);
      AUD.play('applause');
    }else if(diff===-1){
      showBig(name+'! 🐦','좋은 샷!',2000);
    }else if(diff===0){
      showBig(name,'안정적인 플레이',1500);
    }else{
      showBig(name,'다음 홀 화이팅!',1500);
    }
    // Show golfer celebration
    if(golfer&&diff<0){
      // Arms up celebration
      const u=golfer.userData;
      u.lArm.rotation.set(-1.2,0,.3);
      u.rArm.rotation.set(-1.2,0,-.3);
      u.lForearm.rotation.set(0,0,0);
      u.rForearm.rotation.set(0,0,0);
    }
    setTimeout(()=>{
      G.state='score';
      showScorecard();
    },diff<0?2500:1500);
  }else if(G.ball.inWater){
    showBig('워터 해저드 💧','1벌타 추가',2000);
    G.strokes++;
    setTimeout(()=>{
      rstBall(G.prevBallPos?{x:G.prevBallPos.x,z:G.prevBallPos.z}:teeP);
      positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
      enterAim();
    },2000);
  }else if(G.ball.isOB){
    showBig('OB ⚠️','1벌타 추가',2000);
    G.strokes++;
    setTimeout(()=>{
      rstBall(G.prevBallPos?{x:G.prevBallPos.x,z:G.prevBallPos.z}:teeP);
      positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
      enterAim();
    },2000);
  }else{
    // Ball stopped normally
    positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
    setTimeout(()=>enterAim(),500);
  }
}

function enterAim(){
  G.state='aim';
  const isPutt=isGrn(G.ball.x,G.ball.z);
  if(isPutt){
    G.clubIdx=3;
    $('puttInfo').style.display='';
    $('puttInfo').textContent='퍼팅 '+d2h(G.ball.x,G.ball.z).toFixed(1)+'m';
    POSE.putt_address(golfer);
  }else{
    // Auto-select club based on distance
    const dist=d2h(G.ball.x,G.ball.z);
    if(dist>50)G.clubIdx=0;
    else if(dist>30)G.clubIdx=1;
    else if(dist>10)G.clubIdx=2;
    else G.clubIdx=3;
    POSE.address(golfer);
  }
  G.aimAngle=Math.atan2(holeP.x-G.ball.x,-(holeP.z-G.ball.z));
  positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
  showAim();
  showSwing(true);
  $('aimGuide').style.display='';
  CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aimAngle);
  updAimLine(50);
  updHUD();
  drawMinimap();
}

function showScorecard(){
  const ci=G.courseIdx;
  const c=COURSES[ci];
  $('scNm').textContent=c.name+' - '+c.city;
  $('scSub').textContent='Hole '+(G.holeIdx+1)+' 완료';
  mkScore('scTbl',G.scores,ci);
  let sum=0;for(const s of G.scores)sum+=s;
  let parSum=0;for(let i=0;i<G.scores.length;i++)parSum+=c.par[i];
  const diff=sum-parSum;
  $('scTot').textContent='합계: '+sum+' ('+(diff>0?'+':'')+diff+')';
  if(G.holeIdx<8){
    $('scNxt').textContent='다음 홀 ▶';
  }else{
    $('scNxt').textContent='결과 보기';
  }
  showScr('scoreScr');
  $('scoreScr').style.display='block';
}

function nextHole(){
  showScr(null);
  if(G.holeIdx<8){
    G.holeIdx++;
    startHole();
  }else{
    showResult();
  }
}

function showResult(){
  const ci=G.courseIdx;
  const c=COURSES[ci];
  $('rsNm').textContent=c.name+' - '+c.city;
  $('rsSub').textContent='라운드 완료!';
  mkScore('rsTbl',G.scores,ci);
  let sum=0;for(const s of G.scores)sum+=s;
  let parSum=0;for(let i=0;i<9;i++)parSum+=c.par[i];
  const diff=sum-parSum;
  $('rsTot').textContent='최종: '+sum+' ('+(diff>0?'+':'')+diff+')';
  // Rank
  let rank='B',cls='b';
  if(diff<=-5){rank='S';cls='s'}
  else if(diff<=-2){rank='A';cls='a'}
  $('rsRnk').innerHTML='<span class="rnk '+cls+'">랭크 '+rank+'</span>';
  // Save record
  if(!G.isPractice){
    STO.d.records.unshift({course:c.name,score:sum,diff,date:new Date().toLocaleDateString('ko'),par:parSum});
    if(STO.d.records.length>50)STO.d.records.pop();
    if(!STO.d.best[ci]||sum<STO.d.best[ci])STO.d.best[ci]=sum;
    STO.save();
  }
  showScr('resultScr');
  $('resultScr').style.display='block';
  G.state='result';
  CAM.result(holeP);
}

'''

with open('/home/user/webapp/index.html','a',encoding='utf-8') as f:
    f.write(content)
import os
print(f"Part5 done. Total: {os.path.getsize('/home/user/webapp/index.html')} bytes")
