# V8 Part 4: Ball + Physics + Trail + Camera
content = r'''
/* ====== BALL ====== */
let ballM,ballShadow,aimLine,aimDot;
let trailPts=[];
const TRAIL_MAX=80;
let trailLine=null;

function mkBall(){
  const geo=new THREE.SphereGeometry(.021,16,12);
  const mat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.25,metalness:.05});
  ballM=new THREE.Mesh(geo,mat);
  ballM.castShadow=true;
  ballM.scale.set(3,3,3);
  scene.add(ballM);
  // Shadow
  const sg=new THREE.CircleGeometry(.05,12);
  const sm=new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.3,depthWrite:false});
  ballShadow=new THREE.Mesh(sg,sm);
  ballShadow.rotation.x=-Math.PI/2;
  scene.add(ballShadow);
}

function rstBall(pos){
  G.ball.x=pos.x;G.ball.y=.063;G.ball.z=pos.z;
  G.ball.vx=0;G.ball.vy=0;G.ball.vz=0;
  G.ball.flying=false;G.ball.stopped=true;
  updBallM();
}

function updBallM(){
  if(!ballM)return;
  ballM.position.set(G.ball.x,G.ball.y,G.ball.z);
  ballShadow.position.set(G.ball.x,.005,G.ball.z);
  const h=Math.max(0,G.ball.y-.063);
  ballShadow.scale.setScalar(1+h*2);
  ballShadow.material.opacity=.3/(1+h*3);
}

/* ====== AIM LINE ====== */
function mkAimLine(){
  const geo=new THREE.BufferGeometry();
  const pos=new Float32Array(60*3);
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  const mat=new THREE.LineBasicMaterial({color:0xffff44,transparent:true,opacity:.7,linewidth:2});
  aimLine=new THREE.Line(geo,mat);
  scene.add(aimLine);
  // Aim dot
  const dg=new THREE.SphereGeometry(.04,8,6);
  aimDot=new THREE.Mesh(dg,new THREE.MeshBasicMaterial({color:0xffff00,transparent:true,opacity:.6}));
  scene.add(aimDot);
}

function updAimLine(pwr){
  if(!aimLine||!G)return;
  const club=CLUBS[G.clubIdx];
  const maxD=club.dist*(pwr/100);
  const loft=rad(club.loft);
  const dir=G.aimAngle;
  const pts=aimLine.geometry.attributes.position.array;
  const n=20;
  const dx=Math.sin(dir),dz=-Math.cos(dir);
  for(let i=0;i<n;i++){
    const t=i/(n-1);
    const d=maxD*t*.3;
    const h=Math.sin(t*Math.PI)*maxD*Math.sin(loft)*.06;
    pts[i*3]=G.ball.x+dx*d;
    pts[i*3+1]=.063+h;
    pts[i*3+2]=G.ball.z+dz*d;
  }
  for(let i=n;i<60;i++){pts[i*3]=pts[i*3+1]=pts[i*3+2]=0}
  aimLine.geometry.attributes.position.needsUpdate=true;
  // Update aim dot at end
  const endD=maxD*.3;
  aimDot.position.set(G.ball.x+dx*endD,.063,G.ball.z+dz*endD);
  aimDot.visible=true;
}

function hideAim(){
  if(aimLine)aimLine.visible=false;
  if(aimDot)aimDot.visible=false;
}
function showAim(){
  if(aimLine)aimLine.visible=true;
  if(aimDot)aimDot.visible=true;
}

/* ====== BALL TRAIL ====== */
function initTrail(){
  const geo=new THREE.BufferGeometry();
  const pos=new Float32Array(TRAIL_MAX*3);
  geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  geo.setDrawRange(0,0);
  const mat=new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.5,linewidth:1});
  trailLine=new THREE.Line(geo,mat);
  scene.add(trailLine);
}

function updTrail(){
  if(!trailLine||!G.ball.flying)return;
  trailPts.push(G.ball.x,G.ball.y,G.ball.z);
  if(trailPts.length>TRAIL_MAX*3)trailPts.splice(0,3);
  const arr=trailLine.geometry.attributes.position.array;
  for(let i=0;i<trailPts.length;i++)arr[i]=trailPts[i];
  trailLine.geometry.attributes.position.needsUpdate=true;
  trailLine.geometry.setDrawRange(0,trailPts.length/3);
  trailLine.visible=true;
}

function clearTrail(){
  trailPts=[];
  if(trailLine){trailLine.geometry.setDrawRange(0,0);trailLine.visible=false}
}

/* ====== PARTICLES ====== */
let particles=[];
function spawnP(x,y,z,color,count=10){
  for(let i=0;i<count;i++){
    const geo=new THREE.SphereGeometry(.015,4,3);
    const mat=new THREE.MeshBasicMaterial({color,transparent:true,opacity:.8});
    const m=new THREE.Mesh(geo,mat);
    m.position.set(x,y,z);
    const v={x:(Math.random()-.5)*.1,y:.05+Math.random()*.1,z:(Math.random()-.5)*.1};
    scene.add(m);
    particles.push({m,v,life:1});
  }
}

function updP(dt){
  for(let i=particles.length-1;i>=0;i--){
    const p=particles[i];
    p.m.position.x+=p.v.x*dt*3;
    p.m.position.y+=p.v.y*dt*3;
    p.m.position.z+=p.v.z*dt*3;
    p.v.y-=.15*dt;
    p.life-=dt*1.5;
    p.m.material.opacity=p.life;
    if(p.life<=0){scene.remove(p.m);particles.splice(i,1)}
  }
}

/* ====== CAMERA CONTROLLER ====== */
const CAM={
  target:new THREE.Vector3(),
  pos:new THREE.Vector3(),
  mode:'behind',
  shakeTime:0,
  shakeIntensity:0,
  
  behind(ballPos,aimAngle){
    const d=3.5,h=2.2;
    const tx=ballPos.x-Math.sin(aimAngle)*1;
    const tz=ballPos.z+Math.cos(aimAngle)*1;
    this.target.set(tx,.3,tz);
    this.pos.set(
      ballPos.x+Math.sin(aimAngle)*d,
      ballPos.y+h,
      ballPos.z+Math.cos(aimAngle)*d
    );
    this.mode='behind';
  },
  
  swingClose(ballPos,aimAngle){
    // Close-up during swing - slightly to the side
    const d=2.5,h=1.5;
    const sideAngle=aimAngle+Math.PI*.15;
    this.target.set(ballPos.x,.8,ballPos.z);
    this.pos.set(
      ballPos.x+Math.sin(sideAngle)*d,
      ballPos.y+h,
      ballPos.z+Math.cos(sideAngle)*d
    );
    this.mode='swing';
  },
  
  follow(ballPos,vel){
    // Follow ball during flight
    const speed=Math.sqrt(vel.x*vel.x+vel.z*vel.z);
    const d=4+speed*.5;
    const h=2+ballPos.y*.5;
    const behind=speed>.1?Math.atan2(-vel.x,-vel.z):G.aimAngle;
    this.target.lerp(new THREE.Vector3(ballPos.x,ballPos.y*.5,ballPos.z),.08);
    this.pos.lerp(new THREE.Vector3(
      ballPos.x+Math.sin(behind)*d,
      h,
      ballPos.z+Math.cos(behind)*d
    ),.06);
    this.mode='follow';
  },
  
  flyover(t,teePos,holePos){
    const progress=clamp(t,0,1);
    const cx=lerp(teePos.x,holePos.x,progress);
    const cz=lerp(teePos.z,holePos.z,progress);
    const dist=teePos.distanceTo(holePos);
    const h=4+dist*.08;
    const angle=Math.atan2(holePos.x-teePos.x,holePos.z-teePos.z);
    this.pos.set(cx+Math.sin(angle+.3)*6,h,cz+Math.cos(angle+.3)*6);
    this.target.set(cx,0,cz);
    this.mode='flyover';
  },
  
  result(holePos){
    const t=performance.now()*.0003;
    this.pos.set(holePos.x+Math.sin(t)*3,2,holePos.z+Math.cos(t)*3);
    this.target.set(holePos.x,.5,holePos.z);
    this.mode='result';
  },
  
  shake(intensity=.03,duration=.2){
    this.shakeTime=duration;
    this.shakeIntensity=intensity;
  },
  
  update(dt){
    const spd=this.mode==='flyover'?.99:this.mode==='result'?.99:.06;
    camera.position.lerp(this.pos,spd);
    const lt=new THREE.Vector3().copy(this.target);
    // Camera shake
    if(this.shakeTime>0){
      this.shakeTime-=dt;
      const s=this.shakeIntensity*(this.shakeTime/.2);
      lt.x+=Math.sin(performance.now()*.05)*s;
      lt.y+=Math.cos(performance.now()*.07)*s;
    }
    camera.lookAt(lt);
  }
};

/* ====== PHYSICS ====== */
function physTick(dt){
  if(!G.ball.flying)return;
  const substeps=3;
  const sdt=dt/substeps;
  for(let s=0;s<substeps;s++){
    // Gravity
    G.ball.vy-=9.81*sdt;
    // Air resistance
    const drag=.03;
    G.ball.vx*=(1-drag*sdt);
    G.ball.vz*=(1-drag*sdt);
    // Wind
    G.ball.vx+=G.wind.x*sdt*.08;
    G.ball.vz+=G.wind.z*sdt*.08;
    // Move
    G.ball.x+=G.ball.vx*sdt;
    G.ball.y+=G.ball.vy*sdt;
    G.ball.z+=G.ball.vz*sdt;
    // Ground collision
    const gh=gndH(G.ball.x,G.ball.z);
    if(G.ball.y<=gh+.063){
      G.ball.y=gh+.063;
      // Check terrain type
      const onGreen=isGrn(G.ball.x,G.ball.z);
      const inBunker=isBnk(G.ball.x,G.ball.z);
      // Bounce
      if(G.ball.vy<-0.3){
        const bounce=inBunker?.15:onGreen?.3:.45;
        G.ball.vy=-G.ball.vy*bounce;
        G.ball.vx*=.7;G.ball.vz*=.7;
        AUD.play('bounce');
        spawnP(G.ball.x,G.ball.y,G.ball.z,inBunker?0xd4b978:0x44aa44,5);
      }else{
        G.ball.vy=0;
      }
      // Rolling friction
      const friction=onGreen?.985:inBunker?.93:.96;
      G.ball.vx*=friction;
      G.ball.vz*=friction;
      // Green slope toward hole
      if(onGreen){
        const dx=holeP.x-G.ball.x,dz=holeP.z-G.ball.z;
        const dd=Math.sqrt(dx*dx+dz*dz);
        if(dd>0.1&&dd<grnR){
          const slope=.015/(dd+.5);
          G.ball.vx+=dx/dd*slope;
          G.ball.vz+=dz/dd*slope;
        }
      }
      // Speed check
      const spd=Math.sqrt(G.ball.vx*G.ball.vx+G.ball.vy*G.ball.vy+G.ball.vz*G.ball.vz);
      if(spd<.02&&Math.abs(G.ball.vy)<.05){
        G.ball.vx=0;G.ball.vy=0;G.ball.vz=0;
        G.ball.flying=false;G.ball.stopped=true;
      }
    }
    // Water check
    for(const w of waters){
      if(Math.abs(G.ball.x-w.x)<w.w&&Math.abs(G.ball.z-w.z)<w.h&&G.ball.y<.1){
        G.ball.flying=false;G.ball.stopped=true;
        G.ball.inWater=true;
        AUD.play('splash');
        spawnP(G.ball.x,.05,G.ball.z,0x4488cc,15);
        CAM.shake(.04,.3);
        return;
      }
    }
    // OB check
    const obDist=Math.hypot(G.ball.x,G.ball.z+holeP.z*.5);
    if(obDist>obB){
      G.ball.flying=false;G.ball.stopped=true;
      G.ball.isOB=true;
      AUD.play('ob');
      return;
    }
    // Hole-in detection
    const hd=Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z);
    const spd2=Math.sqrt(G.ball.vx*G.ball.vx+G.ball.vz*G.ball.vz);
    if(hd<.12&&G.ball.y<.15&&spd2<2){
      G.ball.x=holeP.x;G.ball.z=holeP.z;G.ball.y=0;
      G.ball.vx=0;G.ball.vy=0;G.ball.vz=0;
      G.ball.flying=false;G.ball.stopped=true;
      G.ball.holed=true;
      AUD.play('hole');
      spawnP(holeP.x,.1,holeP.z,0xffd700,20);
      CAM.shake(.02,.3);
      return;
    }
  }
}

// Helper functions
function isGrn(x,z){return Math.hypot(x-grnC.x,z-grnC.z)<grnR}
function isBnk(x,z){for(const b of bunks)if(Math.hypot(x-b.x,z-b.z)<b.r)return true;return false}
function d2h(x,z){return Math.hypot(x-holeP.x,z-holeP.z)}
function gndH(x,z){return Math.sin(x*.05)*Math.cos(z*.05)*.3+Math.sin(x*.12+z*.08)*.15}

'''

with open('/home/user/webapp/index.html','a',encoding='utf-8') as f:
    f.write(content)
import os
print(f"Part4 done. Total: {os.path.getsize('/home/user/webapp/index.html')} bytes")
