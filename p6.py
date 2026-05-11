#!/usr/bin/env python3
"""v9 Part 6: Input Handling, Menu, Main Loop, Init, Closing HTML"""
import pathlib
pathlib.Path('/home/user/webapp/index.html').open('a').write(r"""
/* ========== PART 6: INPUT + MENU + LOOP + INIT ========== */

/* --- Gauge Tick (power & accuracy bars) --- */
function tickGauge(dt){
 if(G.swingPhase==='power'){
  G.gaugeVal+=G.gaugeDir*G.gaugeSpd*dt*100;
  if(G.gaugeVal>=100){G.gaugeVal=100;G.gaugeDir=-1}
  if(G.gaugeVal<=0){G.gaugeVal=0;G.gaugeDir=1}
  UI.pwrFill.style.height=G.gaugeVal+'%';
 } else if(G.swingPhase==='accuracy'){
  G.accVal+=G.accDir*G.accSpd*dt*100;
  if(G.accVal>=100){G.accVal=100;G.accDir=-1}
  if(G.accVal<=0){G.accVal=0;G.accDir=1}
  UI.accFill.style.height=G.accVal+'%';
 }
}

/* --- Swing Tap Handler --- */
function onSwingTap(){
 if(G.swingPhase==='power'){
  G.power=G.gaugeVal;
  G.swingPhase='accuracy';
  UI.accBar.style.display='block';
  G.accVal=50;G.accDir=1;
  AUD.play('click');
 } else if(G.swingPhase==='accuracy'){
  G.accuracy=G.accVal;
  G.swingPhase='idle';
  showSwing(false);
  doSwing(G.power,G.accuracy);
  AUD.play('click');
 }
}

/* --- Touch / Mouse Input --- */
let dragStart=null,dragging=false,lastTouch=null;

function getXY(e){
 if(e.touches&&e.touches.length>0)return{x:e.touches[0].clientX,y:e.touches[0].clientY};
 return{x:e.clientX,y:e.clientY};
}

function onPointerDown(e){
 const p=getXY(e);
 dragStart={x:p.x,y:p.y};dragging=false;lastTouch=p;
}

function onPointerMove(e){
 if(!dragStart)return;
 const p=getXY(e);
 const dx=p.x-dragStart.x,dy=p.y-dragStart.y;
 if(Math.abs(dx)+Math.abs(dy)>5)dragging=true;
 if(dragging&&G.state==='aim'){
  const sens=0.004;
  G.aimYaw-=(p.x-lastTouch.x)*sens;
  G.aimPitch=Math.max(-0.15,Math.min(0.3,G.aimPitch+(p.y-lastTouch.y)*sens*0.5));
  updAimLine();
  if(golfer)golfer.rotation.y=G.aimYaw;
  CAM.update(0,ball.position,G.aimYaw);
 }
 lastTouch=p;
}

function onPointerUp(e){
 if(!dragging){
  /* tap */
  if(G.state==='aim'&&G.shotReady){
   G.shotReady=false;
   showSwing(true);
   showScr('swing');
   P.addr(golfer);
  } else if(G.swingPhase==='power'||G.swingPhase==='accuracy'){
   onSwingTap();
  } else if(G.flyoverActive){
   endFly();
  } else if(G.state==='scorecard'){
   nextHole();
  }
 }
 dragStart=null;dragging=false;
}

/* keyboard support */
function onKeyDown(e){
 if(e.code==='Space'||e.code==='Enter'){
  if(G.state==='aim'&&G.shotReady){
   G.shotReady=false;showSwing(true);showScr('swing');P.addr(golfer);
  } else if(G.swingPhase==='power'||G.swingPhase==='accuracy'){
   onSwingTap();
  } else if(G.flyoverActive){endFly()}
  else if(G.state==='scorecard'){nextHole()}
 }
 if(G.state==='aim'){
  if(e.code==='ArrowLeft')G.aimYaw+=0.03;
  if(e.code==='ArrowRight')G.aimYaw-=0.03;
  if(e.code==='ArrowUp')G.clubIdx=Math.max(0,G.clubIdx-1);
  if(e.code==='ArrowDown')G.clubIdx=Math.min(3,G.clubIdx+1);
  G.putting=G.clubIdx===3;
  updAimLine();updHUD();
  if(golfer)golfer.rotation.y=G.aimYaw;
 }
}

/* bind events */
function bindInput(){
 const c=renderer.domElement;
 c.addEventListener('mousedown',onPointerDown);
 c.addEventListener('mousemove',onPointerMove);
 c.addEventListener('mouseup',onPointerUp);
 c.addEventListener('touchstart',onPointerDown,{passive:true});
 c.addEventListener('touchmove',onPointerMove,{passive:true});
 c.addEventListener('touchend',onPointerUp);
 document.addEventListener('keydown',onKeyDown);
}

/* --- Club Cycle Button --- */
function cycleClub(){
 G.clubIdx=(G.clubIdx+1)%4;
 G.putting=G.clubIdx===3;
 updHUD();AUD.play('click');
}

/* --- Menu Functions --- */
function showMenu(){
 G.state='menu';showScr('menu');
}

function openCourseSelect(){
 let html='';
 COURSES.forEach((c,i)=>{
  html+=`<div class="csItem" onclick="startRound(${i})"><span class="csName">${c.name}</span><span class="csInfo">9홀 · PAR ${c.holes.reduce((a,h)=>a+h.par,0)}</span></div>`;
 });
 UI.csList.innerHTML=html;
 showScr('courseSelect');G.state='courseSelect';
}

function openRecords(){
 loadRecords();showScr('records');G.state='records';
}

function openSettings(){
 showScr('settings');G.state='settings';
}

function backToMenu(){
 showMenu();
}

function resumeGame(){
 if(G.roundActive){
  G.state='aim';G.shotReady=true;showScr('game');
  CAM.mode='behind';updHUD();drawMinimap();
 }
}

/* --- Resize Handler --- */
function onResize(){
 const w=window.innerWidth,h=window.innerHeight;
 camera.aspect=w/h;camera.updateProjectionMatrix();
 renderer.setSize(w,h);
}

/* --- Main Game Loop --- */
const clock=new THREE.Clock();
let lastMiniT=0;

function gameLoop(){
 requestAnimationFrame(gameLoop);
 const dt=Math.min(clock.getDelta(),0.05);
 const elapsed=clock.getElapsedTime();

 /* gauge animation */
 if(G.swingPhase==='power'||G.swingPhase==='accuracy')tickGauge(dt);

 /* swing animation */
 SA.update(dt);

 /* flyover camera */
 if(G.flyoverActive){
  G.flyoverT+=dt*0.35;
  if(G.flyoverT>=1){endFly()}
  else{
   const t=G.flyoverT;
   const tp=G.teePos,pp=G.pinPos;
   const mx=(tp.x+pp.x)/2,mz=(tp.z+pp.z)/2;
   const dist=tp.distanceTo(pp);
   const cx=mx+Math.sin(t*Math.PI)*dist*0.4;
   const cy=15+dist*0.15+Math.sin(t*Math.PI)*8;
   const cz=mz+Math.cos(t*Math.PI)*dist*0.4;
   camera.position.set(cx,cy,cz);
   const lookT=t<0.5?t*2:1;
   const lx=tp.x+(pp.x-tp.x)*lookT;
   const lz=tp.z+(pp.z-tp.z)*lookT;
   camera.lookAt(lx,gndH(lx,lz)+1,lz);
  }
 }

 /* ball physics */
 if(G.state==='swing'&&!G.settled){
  const stopped=physTick(dt);
  /* trail update */
  if(ball.visible){
   trailPts.push(ball.position.clone());
   if(trailPts.length>90)trailPts.shift();
   updTrail();
  }
  if(stopped){
   setTimeout(()=>onStop(),500);
  }
  /* camera follow */
  if(G.camFollow){
   CAM.update(dt,ball.position,G.aimYaw);
  }
 }

 /* camera update in aim mode */
 if(G.state==='aim'){
  CAM.update(dt,ball.position,G.aimYaw);
 }

 /* animate water */
 scene.traverse(o=>{
  if(o.userData&&o.userData.isWater&&o.material){
   o.position.y=o.userData.baseY+Math.sin(elapsed*1.5+o.position.x*0.1)*0.05;
  }
 });

 /* animate flag */
 scene.traverse(o=>{
  if(o.userData&&o.userData.isFlag&&o.material){
   o.rotation.y=Math.sin(elapsed*3)*0.3;
  }
 });

 /* golfer breathing idle */
 if(golfer&&golfer.visible&&G.state==='aim'&&!SA.active){
  const b=Math.sin(elapsed*2)*0.01;
  golfer.userData.torso.position.y=golfer.userData.torsoBaseY+(b);
 }

 /* minimap refresh every 0.3s */
 if(elapsed-lastMiniT>0.3&&(G.state==='aim'||G.state==='swing')){
  drawMinimap();lastMiniT=elapsed;
 }

 renderer.render(scene,camera);
}

/* --- Initialization --- */
function init(){
 /* init Three.js scene */
 initScene();
 initMaterials();

 /* create golfer */
 createGolfer();

 /* create ball */
 const bg=new THREE.SphereGeometry(0.22,16,16);
 const bm=new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.3,metalness:0.05});
 ball=new THREE.Mesh(bg,bm);ball.castShadow=true;ball.visible=false;scene.add(ball);

 /* trail */
 const tg=new THREE.BufferGeometry();
 const tp=new Float32Array(90*3);
 tg.setAttribute('position',new THREE.BufferAttribute(tp,3));
 trail=new THREE.Line(tg,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:0.4}));
 trail.frustumCulled=false;trail.visible=false;scene.add(trail);

 /* bind input */
 bindInput();
 window.addEventListener('resize',onResize);
 onResize();

 /* connect menu buttons */
 const btnStart=$('btnStart');if(btnStart)btnStart.onclick=openCourseSelect;
 const btnRecords=$('btnRecords');if(btnRecords)btnRecords.onclick=openRecords;
 const btnSettings=$('btnSettings');if(btnSettings)btnSettings.onclick=openSettings;
 const btnResume=$('btnResume');if(btnResume)btnResume.onclick=resumeGame;
 const btnBack=$('btnBack');if(btnBack)btnBack.onclick=backToMenu;
 const btnBackR=$('btnBackR');if(btnBackR)btnBackR.onclick=backToMenu;
 const btnBackS=$('btnBackS');if(btnBackS)btnBackS.onclick=backToMenu;
 const btnClub=$('btnClub');if(btnClub)btnClub.onclick=cycleClub;
 const btnMenu=$('btnMenu');if(btnMenu)btnMenu.onclick=showMenu;
 const btnScNext=$('btnScNext');if(btnScNext)btnScNext.onclick=nextHole;
 const btnResMenu=$('btnResMenu');if(btnResMenu)btnResMenu.onclick=showMenu;
 const btnResReplay=$('btnResReplay');if(btnResReplay)btnResReplay.onclick=()=>startRound(G.course);

 /* settings */
 if(UI.sfxRange)UI.sfxRange.oninput=e=>{/* sfx vol */};
 if(UI.bgmRange)UI.bgmRange.oninput=e=>{/* bgm vol */};

 /* show menu */
 showScr('menu');
 G.state='menu';

 /* hide loading */
 UI.loading.style.display='none';

 /* start loop */
 gameLoop();
 console.log('Park Golf Pro v9 initialized');
}

/* --- Register Service Worker --- */
if('serviceWorker' in navigator){
 navigator.serviceWorker.register('sw.js').catch(e=>console.warn('SW reg fail:',e));
}

/* --- Start --- */
window.addEventListener('DOMContentLoaded',()=>{
 setTimeout(init,100);
});

</script>
</body>
</html>
""")
print("Part 6 written OK - file complete!")
