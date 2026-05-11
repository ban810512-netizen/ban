c = r'''
function mkTree(type,x,z,sc=1){const g=new THREE.Group(),s=(.7+Math.random()*.6)*sc;
if(type==='palm'){const pts=[];for(let i=0;i<=10;i++){const t=i/10;pts.push(new THREE.Vector3(Math.sin(t*1.5)*.3*s,t*3*s,Math.cos(t*.5)*.1*s))}
const curve=new THREE.CatmullRomCurve3(pts);const trunk=new THREE.Mesh(new THREE.TubeGeometry(curve,12,.06*s,6,false),M.bark);trunk.castShadow=true;g.add(trunk);
for(let i=0;i<7;i++){const a=i/7*Math.PI*2,len=1.2*s+Math.random()*.5*s,sh=new THREE.Shape();sh.moveTo(0,0);sh.quadraticCurveTo(len*.3,.15*s,len,-.1*s);sh.quadraticCurveTo(len*.3,-.05*s,0,0);
const fr=new THREE.Mesh(new THREE.ShapeGeometry(sh),new THREE.MeshStandardMaterial({color:0x228833,roughness:.7,side:THREE.DoubleSide}));fr.position.copy(pts[10]);fr.rotation.set(-.3+Math.random()*.3,a,Math.random()*.2-.1);fr.castShadow=true;g.add(fr)}}
else if(type==='pine'){const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.04*s,.06*s,2*s,6),M.bark);trunk.position.y=s;trunk.castShadow=true;g.add(trunk);
for(let i=0;i<4;i++){const y=.8*s+i*.5*s,r=(.7-i*.12)*s,h=.6*s;const cone=new THREE.Mesh(new THREE.ConeGeometry(r,h,8),new THREE.MeshStandardMaterial({color:new THREE.Color().setHSL(.28+Math.random()*.05,.6,.25+i*.05),roughness:.78}));cone.position.y=y+h/2;cone.castShadow=true;g.add(cone)}}
else{const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.04*s,.07*s,1.5*s,6),M.bark);trunk.position.y=.75*s;trunk.castShadow=true;g.add(trunk);
const cc=[0x2d8a2d,0x3a9a3a,0x228822,0x44aa44];for(let i=0;i<5;i++){const r=(.4+Math.random()*.3)*s;const sp=new THREE.Mesh(new THREE.SphereGeometry(r,8,6),new THREE.MeshStandardMaterial({color:cc[i%4],roughness:.72}));sp.position.set((Math.random()-.5)*.3*s,1.5*s+Math.random()*.5*s,(Math.random()-.5)*.3*s);sp.castShadow=true;g.add(sp)}}
g.position.set(x,0,z);return g}
function mkMountains(){const g=new THREE.Group();
for(let layer=0;layer<3;layer++){const dist=70+layer*35,color=[0x3a6a3a,0x4a7a4a,0x6a9a6a][layer],peaks=10+layer*4;
const verts=[],idx=[];for(let i=0;i<=peaks;i++){const a=(i/peaks)*Math.PI*2,r=dist+Math.random()*12,x=Math.cos(a)*r,z=Math.sin(a)*r,h=(10+Math.random()*18)*(1-layer*.25);
verts.push(x,0,z,x,h,z);if(i<peaks){const b=i*2;idx.push(b,b+1,b+2,b+1,b+3,b+2)}}
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geo.setIndex(idx);geo.computeVertexNormals();
g.add(Object.assign(new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness:.82,flatShading:true})),{receiveShadow:true}))}return g}
function buildCourse(ci,hi){if(grp)scene.remove(grp);grp=new THREE.Group();bunks=[];waters=[];fwPath=[];
const c=COURSES[ci],seed=ci*100+hi,rng=mulberry32(seed),dist=c.dist[hi];
teeP=new THREE.Vector3(0,0,0);const ang=rng()*Math.PI*.4-.2;holeP=new THREE.Vector3(Math.sin(ang)*dist*.3,0,-dist*.3);
const gndGeo=new THREE.PlaneGeometry(140,140,80,80),pa=gndGeo.attributes.position.array;
for(let i=0;i<pa.length;i+=3){const gx=pa[i],gy=pa[i+1];pa[i+2]=Math.sin(gx*.04)*Math.cos(gy*.04)*.4+Math.sin(gx*.1+gy*.07)*.2+Math.cos(gx*.06-gy*.09)*.15}
gndGeo.computeVertexNormals();const gnd=new THREE.Mesh(gndGeo,M.grass);gnd.rotation.x=-Math.PI/2;gnd.receiveShadow=true;grp.add(gnd);
const midX=(teeP.x+holeP.x)/2+(rng()-.5)*dist*.15;
for(let i=0;i<=20;i++){const t=i/20,x=teeP.x*(1-t)*(1-t)+2*midX*t*(1-t)+holeP.x*t*t,z=teeP.z*(1-t)+holeP.z*t;fwPath.push(new THREE.Vector3(x,.01,z))}
const fwW=2.8+dist*.015;
for(let i=0;i<fwPath.length-1;i++){const p1=fwPath[i],p2=fwPath[i+1],dx=p2.x-p1.x,dz=p2.z-p1.z,len=Math.sqrt(dx*dx+dz*dz);
const fw=new THREE.Mesh(new THREE.PlaneGeometry(fwW,len),M.fairway);fw.rotation.x=-Math.PI/2;fw.rotation.z=-Math.atan2(dz,dx)+Math.PI/2;
fw.position.set((p1.x+p2.x)/2,.015,(p1.z+p2.z)/2);fw.receiveShadow=true;grp.add(fw);
for(const side of[-1,1]){const rw=new THREE.Mesh(new THREE.PlaneGeometry(fwW*.7,len),M.rough);const nx=-dz/len*side,nz=dx/len*side;
rw.rotation.x=-Math.PI/2;rw.rotation.z=-Math.atan2(dz,dx)+Math.PI/2;rw.position.set((p1.x+p2.x)/2+nx*(fwW*.5+fwW*.35),.012,(p1.z+p2.z)/2+nz*(fwW*.5+fwW*.35));rw.receiveShadow=true;grp.add(rw)}}
const tb=new THREE.Mesh(new THREE.PlaneGeometry(2.2,2.8),M.tee);tb.rotation.x=-Math.PI/2;tb.position.set(teeP.x,.02,teeP.z);tb.receiveShadow=true;grp.add(tb);
for(const sx of[-.6,.6]){const mk=new THREE.Mesh(new THREE.SphereGeometry(.055,8,6),M.white);mk.position.set(teeP.x+sx,.055,teeP.z+.8);mk.castShadow=true;grp.add(mk)}
grnR=2.8+dist*.012;grnC=holeP.clone();
const gm=new THREE.Mesh(new THREE.CircleGeometry(grnR,32),M.green);gm.rotation.x=-Math.PI/2;gm.position.set(grnC.x,.025,grnC.z);gm.receiveShadow=true;grp.add(gm);
const fr=new THREE.Mesh(new THREE.RingGeometry(grnR,grnR+.6,32),M.fairway);fr.rotation.x=-Math.PI/2;fr.position.set(grnC.x,.018,grnC.z);fr.receiveShadow=true;grp.add(fr);
grp.add(new THREE.Mesh(new THREE.CylinderGeometry(.054,.054,.05,16),new THREE.MeshStandardMaterial({color:0x111111})));grp.children[grp.children.length-1].position.set(holeP.x,0,holeP.z);
const pl=new THREE.Mesh(new THREE.CylinderGeometry(.007,.007,1.2,6),M.pole);pl.position.set(holeP.x,.6,holeP.z);pl.castShadow=true;grp.add(pl);
const fs=new THREE.Shape();fs.moveTo(0,0);fs.lineTo(.28,-.07);fs.lineTo(0,-.14);
flagM=new THREE.Mesh(new THREE.ShapeGeometry(fs),M.red);flagM.position.set(holeP.x+.007,1.18,holeP.z);flagM.castShadow=true;grp.add(flagM);
if(rng()>.25){const nb=1+Math.floor(rng()*2);for(let i=0;i<nb;i++){const bt=.5+rng()*.35,bp=new THREE.Vector3();bp.lerpVectors(teeP,holeP,bt);
const bpx=bp.x+(rng()-.5)*fwW*1.5,bpz=bp.z+(rng()-.5)*2,br=.8+rng()*.9;
const bm=new THREE.Mesh(new THREE.CircleGeometry(br,16),M.sand);bm.rotation.x=-Math.PI/2;bm.position.set(bpx,.022,bpz);bm.receiveShadow=true;grp.add(bm);
const lip=new THREE.Mesh(new THREE.TorusGeometry(br,.055,6,24),new THREE.MeshStandardMaterial({color:0xc4a44a,roughness:.78}));lip.rotation.x=-Math.PI/2;lip.position.set(bpx,.05,bpz);lip.castShadow=true;grp.add(lip);
bunks.push({x:bpx,z:bpz,r:br})}}
if(c.water.includes(hi+1)){const wt=.3+rng()*.35,wp=new THREE.Vector3();wp.lerpVectors(teeP,holeP,wt);
const woff=(rng()>.5?1:-1)*(fwW*.8+rng()*2),wx=wp.x+woff,wz=wp.z+(rng()-.5)*3,ww=3.5+rng()*3.5,wh=2.5+rng()*2;
const wm=new THREE.Mesh(new THREE.PlaneGeometry(ww,wh),M.water);wm.rotation.x=-Math.PI/2;wm.position.set(wx,.008,wz);wm.receiveShadow=true;grp.add(wm);
waters.push({x:wx,z:wz,w:ww/2,h:wh/2,mesh:wm});
for(let i=0;i<8;i++){const ra=rng()*Math.PI*2,rd=Math.max(ww,wh)/2+.2+rng()*.5;
const rk=new THREE.Mesh(new THREE.DodecahedronGeometry(.12+rng()*.22,0),M.rock);rk.position.set(wx+Math.cos(ra)*rd,.08,wz+Math.sin(ra)*rd);rk.rotation.set(rng(),rng(),rng());rk.castShadow=true;grp.add(rk)}}
const nTrees=12+Math.floor(rng()*12);for(let i=0;i<nTrees;i++){const ta=rng()*Math.PI*2,td=5+rng()*45;
const tx=Math.cos(ta)*td,tz=-dist*.15+Math.sin(ta)*td;let onFw=false;for(const fp of fwPath)if(Math.hypot(tx-fp.x,tz-fp.z)<fwW*1.3){onFw=true;break}
if(onFw)continue;const tt=c.trees==='mixed'?['deciduous','pine','palm'][Math.floor(rng()*3)]:c.trees;grp.add(mkTree(tt,tx,tz,.8+rng()*.5))}
const nFl=6+Math.floor(rng()*10);const fMats=[M.fl1,M.fl2,M.fl3];
for(let i=0;i<nFl;i++){const fa=rng()*Math.PI*2,fd=4+rng()*22,fx=Math.cos(fa)*fd,fz=-dist*.15+Math.sin(fa)*fd;
const fl=new THREE.Mesh(new THREE.SphereGeometry(.06+rng()*.05,6,4),fMats[Math.floor(rng()*3)]);fl.position.set(fx,.07+rng()*.04,fz);fl.castShadow=true;grp.add(fl);
grp.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.006,.006,.08,4),new THREE.MeshStandardMaterial({color:0x228822})),{position:new THREE.Vector3(fx,.035,fz)}))}
const cp=new THREE.Mesh(new THREE.PlaneGeometry(.65,dist*.38),M.dirt);cp.rotation.x=-Math.PI/2;cp.position.set(teeP.x+fwW+1.8,.013,(teeP.z+holeP.z)/2);cp.receiveShadow=true;grp.add(cp);
obB=16+dist*.13;for(let a=0;a<Math.PI*2;a+=Math.PI/6){const ox=Math.cos(a)*obB,oz=-dist*.15+Math.sin(a)*obB;grp.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.018,.018,.38,4),M.ob),{position:new THREE.Vector3(ox,.19,oz)}))}
grp.add(mkMountains());scene.add(grp)}
let ballM,ballShadow,aimLine,aimDot,trailPts=[],trailLine=null,particles=[];
function mkBall(){ballM=new THREE.Mesh(new THREE.SphereGeometry(.021,16,12),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.22,metalness:.05}));ballM.castShadow=true;ballM.scale.set(3,3,3);scene.add(ballM);
ballShadow=new THREE.Mesh(new THREE.CircleGeometry(.05,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.28,depthWrite:false}));ballShadow.rotation.x=-Math.PI/2;scene.add(ballShadow)}
function rstBall(p){G.ball.x=p.x;G.ball.y=.063;G.ball.z=p.z;G.ball.vx=0;G.ball.vy=0;G.ball.vz=0;G.ball.flying=false;G.ball.stopped=true;updBM()}
function updBM(){if(!ballM)return;ballM.position.set(G.ball.x,G.ball.y,G.ball.z);ballShadow.position.set(G.ball.x,.004,G.ball.z);const h=Math.max(0,G.ball.y-.063);ballShadow.scale.setScalar(1+h*2);ballShadow.material.opacity=.28/(1+h*3)}
function mkAim(){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(60*3),3));
aimLine=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xffff44,transparent:true,opacity:.65}));scene.add(aimLine);
aimDot=new THREE.Mesh(new THREE.SphereGeometry(.035,8,6),new THREE.MeshBasicMaterial({color:0xffff00,transparent:true,opacity:.55}));scene.add(aimDot)}
function updAim(pwr){if(!aimLine||!G)return;const club=CLUBS[G.ci],maxD=club.dist*(pwr/100),loft=rad(club.loft),dir=G.aim;
const pts=aimLine.geometry.attributes.position.array,n=20,dx=Math.sin(dir),dz=-Math.cos(dir);
for(let i=0;i<n;i++){const t=i/(n-1),d=maxD*t*.3,h=Math.sin(t*Math.PI)*maxD*Math.sin(loft)*.06;pts[i*3]=G.ball.x+dx*d;pts[i*3+1]=.063+h;pts[i*3+2]=G.ball.z+dz*d}
for(let i=n;i<60;i++)pts[i*3]=pts[i*3+1]=pts[i*3+2]=0;aimLine.geometry.attributes.position.needsUpdate=true;
aimDot.position.set(G.ball.x+dx*maxD*.3,.063,G.ball.z+dz*maxD*.3);aimDot.visible=true}
function hideAim(){if(aimLine)aimLine.visible=false;if(aimDot)aimDot.visible=false}
function showAimL(){if(aimLine)aimLine.visible=true;if(aimDot)aimDot.visible=true}
function initTrail(){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(80*3),3));geo.setDrawRange(0,0);
trailLine=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.45}));scene.add(trailLine)}
function updTrail(){if(!trailLine||!G.ball.flying)return;trailPts.push(G.ball.x,G.ball.y,G.ball.z);if(trailPts.length>240)trailPts.splice(0,3);
const a=trailLine.geometry.attributes.position.array;for(let i=0;i<trailPts.length;i++)a[i]=trailPts[i];trailLine.geometry.attributes.position.needsUpdate=true;trailLine.geometry.setDrawRange(0,trailPts.length/3);trailLine.visible=true}
function clearTrail(){trailPts=[];if(trailLine){trailLine.geometry.setDrawRange(0,0);trailLine.visible=false}}
function spawnP(x,y,z,color,cnt=10){for(let i=0;i<cnt;i++){const m=new THREE.Mesh(new THREE.SphereGeometry(.012,4,3),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.75}));m.position.set(x,y,z);scene.add(m);particles.push({m,v:{x:(Math.random()-.5)*.1,y:.04+Math.random()*.1,z:(Math.random()-.5)*.1},life:1})}}
function updPart(dt){for(let i=particles.length-1;i>=0;i--){const p=particles[i];p.m.position.x+=p.v.x*dt*3;p.m.position.y+=p.v.y*dt*3;p.m.position.z+=p.v.z*dt*3;p.v.y-=.15*dt;p.life-=dt*1.5;p.m.material.opacity=p.life;if(p.life<=0){scene.remove(p.m);particles.splice(i,1)}}}
const CAM={tgt:new THREE.Vector3(),pos:new THREE.Vector3(),mode:'behind',skT:0,skI:0,
behind(bp,a){const d=3.5,h=2.2;this.tgt.set(bp.x-Math.sin(a)*1,.3,bp.z+Math.cos(a)*1);this.pos.set(bp.x+Math.sin(a)*d,bp.y+h,bp.z+Math.cos(a)*d);this.mode='behind'},
swing(bp,a){const sa=a+Math.PI*.15;this.tgt.set(bp.x,.8,bp.z);this.pos.set(bp.x+Math.sin(sa)*2.5,bp.y+1.5,bp.z+Math.cos(sa)*2.5);this.mode='swing'},
follow(bp,v){const spd=Math.sqrt(v.x*v.x+v.z*v.z),d=4+spd*.5,h=2+bp.y*.5,ba=spd>.1?Math.atan2(-v.x,-v.z):G.aim;
this.tgt.lerp(new THREE.Vector3(bp.x,bp.y*.5,bp.z),.08);this.pos.lerp(new THREE.Vector3(bp.x+Math.sin(ba)*d,h,bp.z+Math.cos(ba)*d),.06);this.mode='follow'},
flyover(t,tp,hp){const p=clamp(t,0,1),cx=lerp(tp.x,hp.x,p),cz=lerp(tp.z,hp.z,p),dist=tp.distanceTo(hp),h=4+dist*.08,a=Math.atan2(hp.x-tp.x,hp.z-tp.z);
this.pos.set(cx+Math.sin(a+.3)*6,h,cz+Math.cos(a+.3)*6);this.tgt.set(cx,0,cz);this.mode='flyover'},
result(hp){const t=performance.now()*.0003;this.pos.set(hp.x+Math.sin(t)*3,2,hp.z+Math.cos(t)*3);this.tgt.set(hp.x,.5,hp.z);this.mode='result'},
shake(i=.03,d=.2){this.skT=d;this.skI=i},
update(dt){const s=this.mode==='flyover'||this.mode==='result'?.99:.06;camera.position.lerp(this.pos,s);
const lt=this.tgt.clone();if(this.skT>0){this.skT-=dt;const s=this.skI*(this.skT/.2);lt.x+=Math.sin(performance.now()*.05)*s;lt.y+=Math.cos(performance.now()*.07)*s}camera.lookAt(lt)}};
function isGrn(x,z){return Math.hypot(x-grnC.x,z-grnC.z)<grnR}
function isBnk(x,z){for(const b of bunks)if(Math.hypot(x-b.x,z-b.z)<b.r)return true;return false}
function d2h(x,z){return Math.hypot(x-holeP.x,z-holeP.z)}
function gndH(x,z){return Math.sin(x*.04)*Math.cos(z*.04)*.4+Math.sin(x*.1+z*.07)*.2+Math.cos(x*.06-z*.09)*.15}
function physTick(dt){if(!G.ball.flying)return;const sub=3,sd=dt/sub;
for(let s=0;s<sub;s++){G.ball.vy-=9.81*sd;G.ball.vx*=(1-.03*sd);G.ball.vz*=(1-.03*sd);
G.ball.vx+=G.wind.x*sd*.08;G.ball.vz+=G.wind.z*sd*.08;
G.ball.x+=G.ball.vx*sd;G.ball.y+=G.ball.vy*sd;G.ball.z+=G.ball.vz*sd;
const gh=gndH(G.ball.x,G.ball.z);if(G.ball.y<=gh+.063){G.ball.y=gh+.063;
const og=isGrn(G.ball.x,G.ball.z),ib=isBnk(G.ball.x,G.ball.z);
if(G.ball.vy<-.3){G.ball.vy*=-(ib?.15:og?.3:.45);G.ball.vx*=.7;G.ball.vz*=.7;AUD.play('bounce');spawnP(G.ball.x,G.ball.y,G.ball.z,ib?0xd4b978:0x44aa44,5)}else G.ball.vy=0;
const fr=og?.985:ib?.93:.96;G.ball.vx*=fr;G.ball.vz*=fr;
if(og){const dx=holeP.x-G.ball.x,dz=holeP.z-G.ball.z,dd=Math.sqrt(dx*dx+dz*dz);if(dd>.1&&dd<grnR){const sl=.015/(dd+.5);G.ball.vx+=dx/dd*sl;G.ball.vz+=dz/dd*sl}}
const spd=Math.sqrt(G.ball.vx**2+G.ball.vy**2+G.ball.vz**2);if(spd<.02&&Math.abs(G.ball.vy)<.05){G.ball.vx=G.ball.vy=G.ball.vz=0;G.ball.flying=false;G.ball.stopped=true}}
for(const w of waters){if(Math.abs(G.ball.x-w.x)<w.w&&Math.abs(G.ball.z-w.z)<w.h&&G.ball.y<.1){G.ball.flying=false;G.ball.stopped=true;G.ball.inWater=true;AUD.play('splash');spawnP(G.ball.x,.05,G.ball.z,0x4488cc,15);CAM.shake(.04,.3);return}}
if(Math.hypot(G.ball.x,G.ball.z+holeP.z*.5)>obB){G.ball.flying=false;G.ball.stopped=true;G.ball.isOB=true;AUD.play('ob');return}
const hd=Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z),sp2=Math.sqrt(G.ball.vx**2+G.ball.vz**2);
if(hd<.12&&G.ball.y<.15&&sp2<2){G.ball.x=holeP.x;G.ball.z=holeP.z;G.ball.y=0;G.ball.vx=G.ball.vy=G.ball.vz=0;G.ball.flying=false;G.ball.stopped=true;G.ball.holed=true;AUD.play('hole');spawnP(holeP.x,.1,holeP.z,0xffd700,20);CAM.shake(.02,.3);return}}}
'''
with open('/home/user/webapp/index.html','a') as f: f.write(c)
import os; print(f"P4: {os.path.getsize('/home/user/webapp/index.html')}b")
