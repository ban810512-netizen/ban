# V8 Part 6: Input + Menu + Main Loop + Init + Close
content = r'''
/* ====== INPUT HANDLING ====== */
function initInput(){
  let dragStart=null,dragging=false;
  const canvas=renderer.domElement;
  
  canvas.addEventListener('pointerdown',e=>{
    AUD.init();AUD.resume();
    dragStart={x:e.clientX,y:e.clientY};
    dragging=false;
  });
  
  canvas.addEventListener('pointermove',e=>{
    if(!dragStart)return;
    const dx=e.clientX-dragStart.x;
    const dy=e.clientY-dragStart.y;
    if(Math.abs(dx)>5||Math.abs(dy)>5)dragging=true;
    if(dragging&&G.state==='aim'){
      G.aimAngle-=dx*.003;
      dragStart={x:e.clientX,y:e.clientY};
      positionGolfer({x:G.ball.x,z:G.ball.z},G.aimAngle);
      const isPutt=G.clubIdx===3;
      if(isPutt)POSE.putt_address(golfer);else POSE.address(golfer);
      updAimLine(50);
      CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aimAngle);
      drawMinimap();
    }
  });
  
  canvas.addEventListener('pointerup',()=>{dragStart=null;dragging=false});
  canvas.addEventListener('pointercancel',()=>{dragStart=null;dragging=false});
  
  // Swing button
  $('swBtn').addEventListener('click',()=>{
    if(G.state!=='aim')return;
    AUD.init();AUD.resume();
    if(G.swingPhase==='idle'){
      G.swingPhase='power';
      G.power=0;G.powerDir=1;
      $('swBtn').textContent='파워 결정!';
      $('swingLabel').textContent='POWER';
    }else if(G.swingPhase==='power'){
      G.swingPhase='accuracy';
      $('pwrMark').style.display='block';
      $('pwrMark').style.left=G.power+'%';
      $('accWrap').style.display='block';
      $('accNdl').style.display='block';
      G.accuracy=0;G.accDir=1;
      // Set accuracy zone based on power
      const zw=30-G.power*.15; // higher power = smaller zone
      const center=50;
      $('accZone').style.left=(center-zw/2)+'%';
      $('accZone').style.width=zw+'%';
      $('accPerf').style.left=center+'%';
      $('swBtn').textContent='정확도 결정!';
      $('swingLabel').textContent='ACCURACY';
    }else if(G.swingPhase==='accuracy'){
      G.swingPhase='idle';
      doSwing(G.power,G.accuracy);
    }
  });
  
  // Club button
  $('clubBtn').addEventListener('click',()=>{
    if(G.state!=='aim')return;
    G.clubIdx=(G.clubIdx+1)%CLUBS.length;
    const isPutt=G.clubIdx===3;
    if(isPutt){
      POSE.putt_address(golfer);
    }else{
      POSE.address(golfer);
    }
    updAimLine(50);
    updHUD();
    drawMinimap();
  });
  
  // Flyover skip
  $('flySk').addEventListener('click',()=>{
    if(G.state==='flyover')endFly();
  });
  
  // Score next
  $('scNxt').addEventListener('click',()=>nextHole());
  
  // Result menu
  $('rsMenu').addEventListener('click',()=>{
    showScr('menuScr');showHUD(false);
    G.state='menu';
    // Show menu background
    buildCourse(0,0);
    CAM.flyover(.5,new THREE.Vector3(0,0,0),new THREE.Vector3(0,0,-20));
  });
  
  // Menu buttons
  $('btnPlay').addEventListener('click',()=>{
    AUD.init();
    showCourseList(false);
  });
  $('btnPrac').addEventListener('click',()=>{
    AUD.init();
    showCourseList(true);
  });
  $('btnRec').addEventListener('click',()=>{
    showRecords();
  });
  $('btnSet').addEventListener('click',()=>{
    showSettings();
  });
  
  // Course back
  $('cBack').addEventListener('click',()=>{showScr('menuScr');G.state='menu'});
  $('rBack').addEventListener('click',()=>{showScr('menuScr');G.state='menu'});
  $('sBack').addEventListener('click',()=>{showScr('menuScr');G.state='menu'});
  
  // Settings save
  $('sSave').addEventListener('click',()=>{
    STO.d.name=$('sNm').value||'플레이어';
    STO.d.vol=parseInt($('sVol').value);
    STO.save();
    AUD.setVol(STO.d.vol/100);
    $('mPlayer').textContent=STO.d.name;
    showScr('menuScr');G.state='menu';
  });
  
  // Vibration toggle
  $('sVib').addEventListener('click',()=>{
    STO.d.vib=!STO.d.vib;
    $('sVib').classList.toggle('on',STO.d.vib);
    STO.save();
  });
}

/* ====== MENU FUNCTIONS ====== */
let pendingPractice=false;

function showCourseList(practice){
  pendingPractice=practice;
  const list=$('cList');
  list.innerHTML='';
  const icons=['🌳','🌊','🍂','☀️','🏖️','🏛️','⛰️','🗻','🌴','🏘️'];
  const colors=['#2d8a2d','#2980b9','#c0392b','#f39c12','#1abc9c','#8e44ad','#27ae60','#34495e','#e67e22','#16a085'];
  COURSES.forEach((c,i)=>{
    const item=document.createElement('div');
    item.className='cItem';
    const best=STO.d.best[i];
    let parSum=0;for(const p of c.par)parSum+=p;
    item.innerHTML=`
      <div class="cIcon" style="background:${colors[i]}">${icons[i]}</div>
      <div class="cInfo">
        <div class="cNm">${c.name}</div>
        <div class="cCity">${c.city} · Par ${parSum} · 바람 ${c.wind}단계</div>
        ${best?`<div class="cBest">베스트: ${best} (${best-parSum>0?'+':''}${best-parSum})</div>`:''}
      </div>
    `;
    item.addEventListener('click',()=>{
      showScr(null);
      startRound(i,pendingPractice);
    });
    list.appendChild(item);
  });
  showScr('courseScr');
  $('courseScr').style.display='block';
}

function showRecords(){
  const list=$('rList');
  list.innerHTML='';
  if(STO.d.records.length===0){
    list.innerHTML='<div style="padding:40px;text-align:center;color:rgba(255,255,255,.5)">아직 기록이 없습니다</div>';
  }else{
    STO.d.records.forEach(r=>{
      const item=document.createElement('div');
      item.className='rItem';
      item.innerHTML=`
        <div class="rNm">${r.course}</div>
        <div class="rDt">${r.date}</div>
        <div class="rSc">${r.score} (${r.diff>0?'+':''}${r.diff})</div>
      `;
      list.appendChild(item);
    });
  }
  showScr('recordScr');
  $('recordScr').style.display='block';
}

function showSettings(){
  $('sNm').value=STO.d.name;
  $('sVol').value=STO.d.vol;
  $('sVib').classList.toggle('on',STO.d.vib);
  showScr('settingScr');
  $('settingScr').style.display='block';
}

/* ====== MAIN GAME LOOP ====== */
let lastTime=0;

function loop(time){
  requestAnimationFrame(loop);
  const dt=Math.min((time-lastTime)/1000,.05);
  lastTime=time;
  
  // State machine
  switch(G.state){
    case'menu':{
      // Slow rotate camera around menu scene
      const t=time*.0002;
      camera.position.set(Math.sin(t)*15,6,Math.cos(t)*15);
      camera.lookAt(0,0,-8);
      break;
    }
    case'flyover':{
      G.flyT+=dt*.3;
      CAM.flyover(G.flyT,teeP,holeP);
      CAM.update(dt);
      if(G.flyT>=1.2)endFly();
      break;
    }
    case'aim':{
      CAM.behind({x:G.ball.x,y:G.ball.y,z:G.ball.z},G.aimAngle);
      CAM.update(dt);
      // Power/accuracy gauge animation
      if(G.swingPhase==='power'){
        G.power+=G.powerDir*dt*80;
        if(G.power>=100){G.power=100;G.powerDir=-1}
        if(G.power<=0){G.power=0;G.powerDir=1}
        $('pwrFill').style.width=G.power+'%';
        $('swingVal').textContent=Math.round(G.power)+'%';
        updAimLine(G.power);
      }
      if(G.swingPhase==='accuracy'){
        G.accuracy+=G.accDir*dt*120;
        if(G.accuracy>=100){G.accuracy=100;G.accDir=-1}
        if(G.accuracy<=0){G.accuracy=0;G.accDir=1}
        $('accNdl').style.left=G.accuracy+'%';
        $('swingVal').textContent=Math.abs(Math.round(G.accuracy-50))<5?'PERFECT!':Math.round(G.accuracy)+'%';
      }
      break;
    }
    case'swing':{
      SWING_ANIM.update(dt);
      CAM.update(dt);
      break;
    }
    case'flying':{
      physTick(dt);
      updBallM();
      updTrail();
      updP(dt);
      CAM.follow({x:G.ball.x,y:G.ball.y,z:G.ball.z},{x:G.ball.vx,z:G.ball.vz});
      CAM.update(dt);
      updHUD();
      // Hide golfer during long flights
      if(golfer){
        const dFromBall=Math.hypot(G.ball.x-golfer.position.x,G.ball.z-golfer.position.z);
        golfer.visible=dFromBall<15;
      }
      if(G.ball.stopped){
        G.state='stopped';
        setTimeout(()=>onStop(),300);
      }
      break;
    }
    case'stopped':{
      CAM.update(dt);
      updP(dt);
      break;
    }
    case'result':{
      CAM.result(holeP);
      CAM.update(dt);
      break;
    }
  }
  
  // Animate water
  for(const w of waters){
    if(w.mesh&&w.mesh.material.map){
      w.mesh.material.map.offset.x=Math.sin(time*.0003)*.05;
      w.mesh.material.map.offset.y=Math.cos(time*.0004)*.05;
    }
  }
  
  // Animate flag
  if(flagM){
    flagM.rotation.y=Math.sin(time*.003)*.15;
    flagM.position.x=holeP.x+.008+Math.sin(time*.004)*.01;
  }
  
  // Golfer idle breathing when in aim
  if(golfer&&G.state==='aim'&&G.swingPhase==='idle'){
    const breath=Math.sin(time*.002)*.005;
    golfer.userData.torso.position.y=.85+breath;
  }
  
  renderer.render(scene,camera);
}

/* ====== INITIALIZATION ====== */
async function init(){
  // Loading progress
  const ldFill=$('ldFill');
  ldFill.style.width='10%';
  
  STO.load();
  
  ldFill.style.width='20%';
  await new Promise(r=>setTimeout(r,50));
  
  initScene();
  ldFill.style.width='40%';
  await new Promise(r=>setTimeout(r,50));
  
  initMaterials();
  ldFill.style.width='60%';
  await new Promise(r=>setTimeout(r,50));
  
  mkBall();
  mkAimLine();
  initTrail();
  hideAim();
  
  ldFill.style.width='80%';
  await new Promise(r=>setTimeout(r,50));
  
  // Build a background course for menu
  buildCourse(0,0);
  golfer=createGolfer();
  scene.add(golfer);
  golfer.position.set(0,0,0);
  POSE.idle(golfer);
  
  ldFill.style.width='100%';
  
  initInput();
  
  // Setup menu
  $('mPlayer').textContent=STO.d.name;
  showScr('menuScr');
  showHUD(false);
  G.state='menu';
  
  // Hide loading
  setTimeout(()=>{
    $('loading').style.display='none';
  },500);
  
  // Start loop
  requestAnimationFrame(loop);
  
  // Register SW
  if('serviceWorker' in navigator){
    navigator.serviceWorker.register('./sw.js').catch(()=>{});
  }
}

init();

</script>
</body>
</html>
'''

with open('/home/user/webapp/index.html','a',encoding='utf-8') as f:
    f.write(content)
import os
print(f"Part6 done. Total: {os.path.getsize('/home/user/webapp/index.html')} bytes")
