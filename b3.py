#!/usr/bin/env python3
"""v9 Part 3: Scene, Materials, Golfer, Poses, Swing Animation"""
f = open('/home/user/webapp/index.html', 'a')
f.write(r'''
/* ===== SCENE SETUP ===== */
let scene,camera,renderer,sunLight;
let grp,grnC,grnR,teeP,holeP,flagM,bunks=[],waters=[],obB,fwPath=[];
let M={},golfer=null;

function initScene(){
scene=new THREE.Scene();
camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.1,600);
renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
renderer.outputColorSpace=THREE.SRGBColorSpace;
document.getElementById('GC').prepend(renderer.domElement);
sunLight=new THREE.DirectionalLight(0xfff8e8,3);
sunLight.position.set(40,60,25);sunLight.castShadow=true;
sunLight.shadow.mapSize.set(2048,2048);
const sc=sunLight.shadow.camera;sc.left=-70;sc.right=70;sc.top=70;sc.bottom=-70;sc.near=1;sc.far=180;
sunLight.shadow.bias=-.0008;sunLight.shadow.normalBias=.02;
scene.add(sunLight);
scene.add(new THREE.AmbientLight(0x5588aa,.55));
scene.add(new THREE.HemisphereLight(0x88ccff,0x445522,.45));
scene.background=TEX.sky();scene.environment=scene.background;
scene.fog=new THREE.FogExp2(0xa8d4f0,.003);
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)})}

function initMaterials(){
M={
grass:new THREE.MeshStandardMaterial({map:TEX.grass(),roughness:.82}),
fairway:new THREE.MeshStandardMaterial({map:TEX.fairway(),roughness:.65}),
green:new THREE.MeshStandardMaterial({map:TEX.green(),roughness:.45}),
sand:new THREE.MeshStandardMaterial({map:TEX.sand(),roughness:.92}),
water:new THREE.MeshStandardMaterial({map:TEX.water(),roughness:.08,metalness:.35,transparent:true,opacity:.82}),
dirt:new THREE.MeshStandardMaterial({map:TEX.dirt(),roughness:.88}),
bark:new THREE.MeshStandardMaterial({map:TEX.bark(),roughness:.88}),
rough:new THREE.MeshStandardMaterial({map:TEX.rough(),roughness:.88}),
white:new THREE.MeshStandardMaterial({color:0xfafafa,roughness:.25,metalness:.08}),
red:new THREE.MeshStandardMaterial({color:0xcc2222,roughness:.45}),
pole:new THREE.MeshStandardMaterial({color:0xe8e8e8,roughness:.25,metalness:.5}),
tee:new THREE.MeshStandardMaterial({color:0x3da83d,roughness:.55}),
ob:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.5}),
rock:new THREE.MeshStandardMaterial({color:0x7a7a7a,roughness:.82,metalness:.06}),
skin:new THREE.MeshStandardMaterial({color:0xf0be98,roughness:.65}),
shirt:new THREE.MeshStandardMaterial({color:0x1a55aa,roughness:.55}),
pants:new THREE.MeshStandardMaterial({color:0x2a3545,roughness:.65}),
shoes:new THREE.MeshStandardMaterial({color:0x1a1a1a,roughness:.45,metalness:.1}),
hat:new THREE.MeshStandardMaterial({color:0xf0f0f0,roughness:.45}),
glove:new THREE.MeshStandardMaterial({color:0xe8e8e8,roughness:.45}),
clubM:new THREE.MeshStandardMaterial({color:0xb0b0b0,roughness:.15,metalness:.85}),
grip:new THREE.MeshStandardMaterial({color:0x2a2a2a,roughness:.8}),
hair:new THREE.MeshStandardMaterial({color:0x2a1a0a,roughness:.75}),
fl1:new THREE.MeshStandardMaterial({color:0xff6688,roughness:.6}),
fl2:new THREE.MeshStandardMaterial({color:0xffaa33,roughness:.6}),
fl3:new THREE.MeshStandardMaterial({color:0xaa44ff,roughness:.6})
}}

/* ===== 3D GOLFER ===== */
function createGolfer(){
const g=new THREE.Group();
const torso=new THREE.Group();torso.name='torso';
torso.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.13,.11,.38,8),M.shirt),{castShadow:true}));
// Collar
const collar=new THREE.Mesh(new THREE.TorusGeometry(.115,.012,6,12),M.shirt);
collar.position.y=.18;collar.rotation.x=Math.PI/2;torso.add(collar);
torso.position.y=.82;g.add(torso);
// Hips + Belt
const hips=new THREE.Group();hips.name='hips';
hips.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.11,.12,.12,8),M.pants),{castShadow:true}));
hips.position.y=.6;g.add(hips);
const belt=new THREE.Mesh(new THREE.TorusGeometry(.113,.01,6,16),M.shoes);
belt.rotation.x=Math.PI/2;belt.position.y=.66;g.add(belt);
// Head + Face
const head=new THREE.Group();head.name='head';
head.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(.088,12,10),M.skin),{castShadow:true}));
for(const sx of[-.028,.028]){
const eye=new THREE.Mesh(new THREE.SphereGeometry(.01,6,4),new THREE.MeshBasicMaterial({color:0x222222}));
eye.position.set(sx,.008,.078);head.add(eye)}
// Hair + Cap
head.add(new THREE.Mesh(new THREE.SphereGeometry(.09,12,8,0,Math.PI*2,0,Math.PI*.5),M.hair));
const cap=new THREE.Mesh(new THREE.CylinderGeometry(.095,.095,.03,12),M.hat);cap.position.y=.06;cap.castShadow=true;head.add(cap);
const visor=new THREE.Mesh(new THREE.BoxGeometry(.08,.008,.06),M.hat);visor.position.set(0,.05,.08);head.add(visor);
head.position.y=.32;torso.add(head);
// Arms
function mkArm(name,side){
const arm=new THREE.Group();arm.name=name;
arm.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.032,.028,.2,6),M.shirt),{position:new THREE.Vector3(0,-.1,0),castShadow:true}));
const fore=new THREE.Group();fore.name=name.replace('Arm','Fore');
fore.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.028,.022,.18,6),M.skin),{position:new THREE.Vector3(0,-.09,0),castShadow:true}));
fore.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(.023,6,5),side<0?M.glove:M.skin),{position:new THREE.Vector3(0,-.18,0)}));
fore.position.y=-.2;arm.add(fore);
arm.position.set(side*.16,.04,0);torso.add(arm);return{arm,fore}}
const la=mkArm('lArm',1),ra=mkArm('rArm',-1);
// Legs
function mkLeg(name,side){
const leg=new THREE.Group();leg.name=name;
leg.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.048,.038,.26,6),M.pants),{position:new THREE.Vector3(0,-.13,0),castShadow:true}));
const shin=new THREE.Group();shin.name=name.replace('Leg','Shin');
shin.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.038,.032,.26,6),M.pants),{position:new THREE.Vector3(0,-.13,0),castShadow:true}));
shin.add(Object.assign(new THREE.Mesh(new THREE.BoxGeometry(.048,.028,.09),M.shoes),{position:new THREE.Vector3(0,-.27,.018),castShadow:true}));
shin.position.y=-.26;leg.add(shin);
leg.position.set(side*.065,0,0);hips.add(leg);return{leg,shin}}
const ll=mkLeg('lLeg',1),rl=mkLeg('rLeg',-1);
// Golf Club
const club=new THREE.Group();club.name='club';
const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.005,.005,.65,6),M.clubM);shaft.position.y=-.325;club.add(shaft);
club.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.008,.007,.13,6),M.grip),{position:new THREE.Vector3(0,0,0)}));
const ch=new THREE.Mesh(new THREE.BoxGeometry(.055,.018,.035),M.clubM);ch.position.y=-.65;ch.castShadow=true;club.add(ch);
club.position.set(0,-.18,0);la.fore.add(club);
// Shadow disc
const shd=new THREE.Mesh(new THREE.CircleGeometry(.2,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.22,depthWrite:false}));
shd.rotation.x=-Math.PI/2;shd.position.y=.003;g.add(shd);
g.userData={torso,hips,head,lArm:la.arm,lFore:la.fore,rArm:ra.arm,rFore:ra.fore,lLeg:ll.leg,lShin:ll.shin,rLeg:rl.leg,rShin:rl.shin,club,torsoBaseY:torso.position.y};
g.scale.set(1.8,1.8,1.8);
golfer=g;scene.add(g);golfer.visible=false;
return g}

/* ===== POSE SYSTEM ===== */
const P={
idle(g){const u=g.userData;u.torso.rotation.set(0,0,0);u.hips.rotation.set(0,0,0);u.head.rotation.set(0,0,0);
u.lArm.rotation.set(.08,0,0);u.lFore.rotation.set(0,0,0);u.rArm.rotation.set(.08,0,0);u.rFore.rotation.set(0,0,0);
u.lLeg.rotation.set(0,0,0);u.lShin.rotation.set(0,0,0);u.rLeg.rotation.set(0,0,0);u.rShin.rotation.set(0,0,0)},
addr(g){const u=g.userData;u.torso.rotation.set(.22,0,0);u.hips.rotation.set(.06,0,0);u.head.rotation.set(.05,0,0);
u.lArm.rotation.set(.65,0,.14);u.lFore.rotation.set(.22,0,0);u.rArm.rotation.set(.65,0,-.14);u.rFore.rotation.set(.22,0,0);
u.lLeg.rotation.set(-.04,0,-.03);u.lShin.rotation.set(.07,0,0);u.rLeg.rotation.set(-.04,0,.03);u.rShin.rotation.set(.07,0,0)},
back(g,t){const u=g.userData,T=clamp(t,0,1),e=T<.5?2*T*T:1-Math.pow(-2*T+2,2)/2;
u.torso.rotation.set(.18-e*.12,e*.65,e*.06);u.hips.rotation.set(.06,e*.18,0);u.head.rotation.set(.05,-e*.22,0);
u.lArm.rotation.set(.55-e*.9,e*.35,.14+e*.22);u.lFore.rotation.set(.22+e*1.3,0,0);
u.rArm.rotation.set(.55+e*.35,-e*.45,-.14-e*.32);u.rFore.rotation.set(.22+e*.85,0,0);
u.lLeg.rotation.set(-.04+e*.06,0,-.03);u.lShin.rotation.set(.07,0,0);
u.rLeg.rotation.set(-.04-e*.09,0,.03);u.rShin.rotation.set(.07+e*.12,0,0)},
down(g,t){const u=g.userData,T=clamp(t,0,1),e=T*T*T;
u.torso.rotation.set(lerp(.06,.32,e),lerp(.65,-.35,e),lerp(.06,0,e));
u.hips.rotation.set(.06,lerp(.18,-.22,e),0);u.head.rotation.set(.05,lerp(-.22,.12,e),0);
u.lArm.rotation.set(lerp(-.35,1.05,e),lerp(.35,-.12,e),lerp(.36,.04,e));u.lFore.rotation.set(lerp(1.52,.2,e),0,0);
u.rArm.rotation.set(lerp(.9,.18,e),lerp(-.45,.22,e),lerp(-.46,.06,e));u.rFore.rotation.set(lerp(1.07,.18,e),0,0);
u.lLeg.rotation.set(lerp(.02,-.09,e),0,-.03);u.rLeg.rotation.set(lerp(-.13,.02,e),0,.03);u.rShin.rotation.set(lerp(.19,.07,e),0,0)},
impact(g){const u=g.userData;u.torso.rotation.set(.32,-.35,0);u.hips.rotation.set(.06,-.22,0);u.head.rotation.set(0,.12,0);
u.lArm.rotation.set(1.05,-.12,.04);u.lFore.rotation.set(.2,0,0);u.rArm.rotation.set(.18,.22,.06);u.rFore.rotation.set(.18,0,0);
u.lLeg.rotation.set(-.09,0,-.03);u.rLeg.rotation.set(.02,0,.03);u.rShin.rotation.set(.07,0,0)},
follow(g,t){const u=g.userData,T=clamp(t,0,1),e=1-Math.pow(1-T,3);
u.torso.rotation.set(lerp(.32,.22,e),lerp(-.35,-.9,e),-e*.06);u.hips.rotation.set(.04,lerp(-.22,-.55,e),0);
u.head.rotation.set(-e*.12,lerp(.12,.47,e),0);
u.lArm.rotation.set(lerp(1.05,-.55,e),lerp(-.12,-.35,e),lerp(.04,-.18,e));u.lFore.rotation.set(lerp(.2,.72,e),0,0);
u.rArm.rotation.set(lerp(.18,-.65,e),lerp(.22,.65,e),lerp(.06,.35,e));u.rFore.rotation.set(lerp(.18,.85,e),0,0);
u.lLeg.rotation.set(lerp(-.09,-.02,e),0,-.03);u.rLeg.rotation.set(lerp(.02,-.18,e),0,.03);u.rShin.rotation.set(lerp(.07,.29,e),0,0)},
paddr(g){const u=g.userData;u.torso.rotation.set(.26,0,0);u.hips.rotation.set(.08,0,0);u.head.rotation.set(.1,0,0);
u.lArm.rotation.set(.52,0,.07);u.lFore.rotation.set(.14,0,0);u.rArm.rotation.set(.52,0,-.07);u.rFore.rotation.set(.14,0,0);
u.lLeg.rotation.set(-.03,0,-.04);u.rLeg.rotation.set(-.03,0,.04);u.lShin.rotation.set(.04,0,0);u.rShin.rotation.set(.04,0,0)},
pstroke(g,t){const u=g.userData;u.torso.rotation.set(.26,0,0);
u.lArm.rotation.set(.52+t*.22,0,.07);u.lFore.rotation.set(.14-t*.1,0,0);
u.rArm.rotation.set(.52+t*.22,0,-.07);u.rFore.rotation.set(.14-t*.1,0,0)},
celebrate(g){const u=g.userData;u.torso.rotation.set(-.08,0,0);u.hips.rotation.set(0,0,0);u.head.rotation.set(-.15,0,0);
u.lArm.rotation.set(-1.3,0,.35);u.lFore.rotation.set(0,0,0);u.rArm.rotation.set(-1.3,0,-.35);u.rFore.rotation.set(0,0,0);
u.lLeg.rotation.set(0,0,-.02);u.rLeg.rotation.set(0,0,.02);u.lShin.rotation.set(0,0,0);u.rShin.rotation.set(0,0,0)}
};

/* ===== SWING ANIMATION ===== */
const SA={active:false,phase:'idle',time:0,power:0,isPutt:false,cb:null,
dur:{back:.55,down:.15,hit:.04,follow:.75},
start(pwr,putt,cb){this.active=true;this.phase=putt?'pb':'back';this.time=0;this.power=pwr;this.isPutt=putt;this.cb=cb;if(!putt)AUD.play('swing')},
update(dt){if(!this.active||!golfer)return;this.time+=dt;this.isPutt?this._putt():this._full()},
_full(){const d=this.dur;
if(this.phase==='back'){const t=this.time/d.back;P.back(golfer,t);if(t>=1){this.phase='down';this.time=0}}
else if(this.phase==='down'){const t=this.time/d.down;P.down(golfer,t);if(t>=1){this.phase='hit';this.time=0;if(this.cb){this.cb();this.cb=null}vib(30)}}
else if(this.phase==='hit'){const t=this.time/d.hit;P.impact(golfer);if(t>=1){this.phase='follow';this.time=0}}
else if(this.phase==='follow'){const t=this.time/d.follow;P.follow(golfer,t);if(t>=1){this.active=false;this.phase='idle'}}},
_putt(){const T=this.time/.55;
if(T<.38)P.pstroke(golfer,-(T/.38));
else if(T<.58){P.pstroke(golfer,-1+(T-.38)/.2*2);if(T>=.48&&this.cb){this.cb();this.cb=null;vib(15)}}
else if(T<1)P.pstroke(golfer,1-(T-.58)/.42);
else{this.active=false;this.phase='idle';P.paddr(golfer)}},
reset(){this.active=false;this.phase='idle';this.time=0}};
''')
f.close()
print(f"Part 3 done: {__import__('os').path.getsize('/home/user/webapp/index.html')} bytes")
