c = r'''
let scene,camera,renderer,clock,grp,grnC,grnR,teeP,holeP,flagM,bunks=[],waters=[],obB,fwPath=[],M={},golfer=null,sunLight;
function initScene(){
scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(50,innerWidth/innerHeight,.1,500);
renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
renderer.outputColorSpace=THREE.SRGBColorSpace;
document.getElementById('GC').prepend(renderer.domElement);clock=new THREE.Clock();
sunLight=new THREE.DirectionalLight(0xfff8e8,2.8);sunLight.position.set(30,50,20);sunLight.castShadow=true;
sunLight.shadow.mapSize.set(2048,2048);const sc=sunLight.shadow.camera;sc.left=-60;sc.right=60;sc.top=60;sc.bottom=-60;sc.near=1;sc.far=150;
sunLight.shadow.bias=-.0008;sunLight.shadow.normalBias=.02;scene.add(sunLight);
scene.add(new THREE.AmbientLight(0x5599bb,.55));scene.add(new THREE.HemisphereLight(0x88bbff,0x445522,.45));
scene.background=TEX.sky();scene.environment=scene.background;scene.fog=new THREE.FogExp2(0xa8d4f0,.003);
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)})}
function initMaterials(){
const wrap=t=>{t.wrapS=t.wrapT=THREE.RepeatWrapping;return t};
const gt=wrap(TEX.grass());gt.repeat.set(15,15);const ft=wrap(TEX.fairway());ft.repeat.set(2,10);
const gnt=wrap(TEX.green());const st=wrap(TEX.sand());st.repeat.set(2,2);
const wt=wrap(TEX.water());wt.repeat.set(3,3);const dt=wrap(TEX.dirt());dt.repeat.set(4,4);
const bt=wrap(TEX.bark());const rt=wrap(TEX.rough());rt.repeat.set(8,8);
M={grass:new THREE.MeshStandardMaterial({map:gt,roughness:.82}),fairway:new THREE.MeshStandardMaterial({map:ft,roughness:.65}),
green:new THREE.MeshStandardMaterial({map:gnt,roughness:.45}),sand:new THREE.MeshStandardMaterial({map:st,roughness:.92}),
water:new THREE.MeshStandardMaterial({map:wt,roughness:.08,metalness:.35,transparent:true,opacity:.82}),
dirt:new THREE.MeshStandardMaterial({map:dt,roughness:.88}),bark:new THREE.MeshStandardMaterial({map:bt,roughness:.88}),
rough:new THREE.MeshStandardMaterial({map:rt,roughness:.88}),
white:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.25,metalness:.08}),
red:new THREE.MeshStandardMaterial({color:0xcc2222,roughness:.45}),
pole:new THREE.MeshStandardMaterial({color:0xeeeeee,roughness:.25,metalness:.5}),
tee:new THREE.MeshStandardMaterial({color:0x44aa44,roughness:.55}),
ob:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.45}),
rock:new THREE.MeshStandardMaterial({color:0x888888,roughness:.82,metalness:.05}),
skin:new THREE.MeshStandardMaterial({color:0xf0bb90,roughness:.65}),
shirt:new THREE.MeshStandardMaterial({color:0x2060bb,roughness:.55}),
pants:new THREE.MeshStandardMaterial({color:0x334455,roughness:.65}),
shoes:new THREE.MeshStandardMaterial({color:0x1a1a1a,roughness:.45,metalness:.1}),
hat:new THREE.MeshStandardMaterial({color:0xf8f8f8,roughness:.45}),
glove:new THREE.MeshStandardMaterial({color:0xeeeeee,roughness:.45}),
clubM:new THREE.MeshStandardMaterial({color:0xaaaaaa,roughness:.15,metalness:.85}),
grip:new THREE.MeshStandardMaterial({color:0x222222,roughness:.82}),
hair:new THREE.MeshStandardMaterial({color:0x2a1a0a,roughness:.78}),
fl1:new THREE.MeshStandardMaterial({color:0xff6688,roughness:.55}),
fl2:new THREE.MeshStandardMaterial({color:0xffaa33,roughness:.55}),
fl3:new THREE.MeshStandardMaterial({color:0xaa44ff,roughness:.55})}}
function createGolfer(){
const g=new THREE.Group();
const torso=new THREE.Group();torso.name='torso';
torso.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.13,.11,.38,8),M.shirt),{castShadow:true}));
torso.position.y=.82;g.add(torso);
const hips=new THREE.Group();hips.name='hips';
hips.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.11,.12,.11,8),M.pants),{castShadow:true}));
hips.position.y=.6;g.add(hips);
const head=new THREE.Group();head.name='head';
head.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(.085,12,10),M.skin),{castShadow:true}));
head.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(.088,12,10,0,Math.PI*2,0,Math.PI*.5),M.hair),{position:{x:0,y:.01,z:0}}));
const cap=new THREE.Mesh(new THREE.CylinderGeometry(.095,.095,.028,12),M.hat);cap.position.y=.058;cap.castShadow=true;head.add(cap);
const visor=new THREE.Mesh(new THREE.BoxGeometry(.075,.008,.055),M.hat);visor.position.set(0,.048,.075);head.add(visor);
head.position.y=.3;torso.add(head);
function mkArm(name,side){
const arm=new THREE.Group();arm.name=name;
arm.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.032,.028,.2,6),M.shirt),{position:{x:0,y:-.1,z:0},castShadow:true}));
const fore=new THREE.Group();fore.name=name+'Fore';
fore.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.028,.022,.18,6),M.skin),{position:{x:0,y:-.09,z:0},castShadow:true}));
fore.add(Object.assign(new THREE.Mesh(new THREE.SphereGeometry(.023,6,6),side<0?M.glove:M.skin),{position:{x:0,y:-.18,z:0}}));
fore.position.y=-.2;arm.add(fore);
arm.position.set(side*.16,.04,0);torso.add(arm);return{arm,fore}}
const la=mkArm('lArm',1),ra=mkArm('rArm',-1);
function mkLeg(name,side){
const leg=new THREE.Group();leg.name=name;
leg.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.048,.038,.26,6),M.pants),{position:{x:0,y:-.13,z:0},castShadow:true}));
const shin=new THREE.Group();shin.name=name+'Shin';
shin.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.038,.032,.26,6),M.pants),{position:{x:0,y:-.13,z:0},castShadow:true}));
shin.add(Object.assign(new THREE.Mesh(new THREE.BoxGeometry(.048,.028,.09),M.shoes),{position:{x:0,y:-.27,z:.018},castShadow:true}));
shin.position.y=-.26;leg.add(shin);
leg.position.set(side*.065,0,0);hips.add(leg);return{leg,shin}}
const ll=mkLeg('lLeg',1),rl=mkLeg('rLeg',-1);
const club=new THREE.Group();club.name='club';
club.add(new THREE.Mesh(new THREE.CylinderGeometry(.005,.005,.65,6),M.clubM));
club.children[0].position.y=-.325;
club.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.008,.007,.13,6),M.grip),{position:{x:0,y:0,z:0}}));
const ch=new THREE.Mesh(new THREE.BoxGeometry(.055,.018,.035),M.clubM);ch.position.y=-.65;ch.castShadow=true;club.add(ch);
club.position.set(0,-.18,0);la.fore.add(club);
const sh=new THREE.Mesh(new THREE.CircleGeometry(.18,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.22,depthWrite:false}));
sh.rotation.x=-Math.PI/2;sh.position.y=.003;g.add(sh);
g.userData={torso,hips,head,lArm:la.arm,lFore:la.fore,rArm:ra.arm,rFore:ra.fore,lLeg:ll.leg,lShin:ll.shin,rLeg:rl.leg,rShin:rl.shin,club};
g.scale.set(1.8,1.8,1.8);return g}
const P={
idle(g){const u=g.userData;u.torso.rotation.set(0,0,0);u.hips.rotation.set(0,0,0);
u.lArm.rotation.set(.08,0,0);u.lFore.rotation.set(0,0,0);u.rArm.rotation.set(.08,0,0);u.rFore.rotation.set(0,0,0);
u.lLeg.rotation.set(0,0,0);u.lShin.rotation.set(0,0,0);u.rLeg.rotation.set(0,0,0);u.rShin.rotation.set(0,0,0);u.head.rotation.set(0,0,0)},
addr(g){const u=g.userData;u.torso.rotation.set(.22,0,0);u.hips.rotation.set(.06,0,0);
u.lArm.rotation.set(.65,0,.14);u.lFore.rotation.set(.22,0,0);u.rArm.rotation.set(.65,0,-.14);u.rFore.rotation.set(.22,0,0);
u.lLeg.rotation.set(-.04,0,-.03);u.lShin.rotation.set(.07,0,0);u.rLeg.rotation.set(-.04,0,.03);u.rShin.rotation.set(.07,0,0);u.head.rotation.set(.05,0,0)},
back(g,t){const u=g.userData,T=clamp(t,0,1),e=T<.5?2*T*T:1-Math.pow(-2*T+2,2)/2;
u.torso.rotation.set(.18-e*.12,e*.65,e*.06);u.hips.rotation.set(.06,e*.18,0);
u.lArm.rotation.set(.55-e*.9,e*.35,.14+e*.22);u.lFore.rotation.set(.22+e*1.3,0,0);
u.rArm.rotation.set(.55+e*.35,-e*.45,-.14-e*.32);u.rFore.rotation.set(.22+e*.85,0,0);
u.lLeg.rotation.set(-.04+e*.06,0,-.03);u.lShin.rotation.set(.07,0,0);
u.rLeg.rotation.set(-.04-e*.09,0,.03);u.rShin.rotation.set(.07+e*.12,0,0);u.head.rotation.set(.05,-e*.22,0)},
down(g,t){const u=g.userData,T=clamp(t,0,1),e=1-Math.pow(1-T,3),b=1-e;
u.torso.rotation.set(.18-.12*b+e*.18,.65*b-e*.35,.06*b);u.hips.rotation.set(.06,.18*b-e*.22,0);
u.lArm.rotation.set(.55-.9*b+e*.55,.35*b-e*.12,.14+.22*b-e*.12);u.lFore.rotation.set(.22+1.3*b-e*1.1,0,0);
u.rArm.rotation.set(.55+.35*b-e*.55,-.45*b+e*.22,-.14-.32*b+e*.22);u.rFore.rotation.set(.22+.85*b-e*.65,0,0);
u.lLeg.rotation.set(-.04+.06*b-e*.04,0,-.03);u.rLeg.rotation.set(-.04-.09*b+e*.06,0,.03);u.head.rotation.set(.05,-.22*b+e*.12,0)},
impact(g){const u=g.userData;u.torso.rotation.set(.32,-.35,0);u.hips.rotation.set(.06,-.22,0);
u.lArm.rotation.set(1.05,-.12,.04);u.lFore.rotation.set(.2,0,0);u.rArm.rotation.set(.18,.22,.06);u.rFore.rotation.set(.18,0,0);
u.lLeg.rotation.set(-.09,0,-.03);u.rLeg.rotation.set(.02,0,.03);u.head.rotation.set(0,.12,0)},
follow(g,t){const u=g.userData,T=clamp(t,0,1),e=T<.5?2*T*T:1-Math.pow(-2*T+2,2)/2;
u.torso.rotation.set(.12+e*.12,-.35-e*.55,-e*.06);u.hips.rotation.set(.02,-.22-e*.32,0);
u.lArm.rotation.set(1.05-e*1.6,-.12-e*.32,.04-e*.22);u.lFore.rotation.set(.2+e*.55,0,0);
u.rArm.rotation.set(.18-e*.85,.22+e*.45,.06+e*.32);u.rFore.rotation.set(.18+e*.65,0,0);
u.lLeg.rotation.set(-.09+e*.12,0,-.03+e*.03);u.rLeg.rotation.set(.02-e*.16,0,.03);u.rShin.rotation.set(.07+e*.22,0,0);
u.head.rotation.set(-e*.12,.12+e*.35,0)},
paddr(g){const u=g.userData;u.torso.rotation.set(.26,0,0);u.hips.rotation.set(.08,0,0);
u.lArm.rotation.set(.52,0,.07);u.lFore.rotation.set(.14,0,0);u.rArm.rotation.set(.52,0,-.07);u.rFore.rotation.set(.14,0,0);
u.lLeg.rotation.set(-.03,0,-.04);u.rLeg.rotation.set(-.03,0,.04);u.head.rotation.set(.1,0,0)},
pstroke(g,t){const u=g.userData;u.torso.rotation.set(.26,0,0);
u.lArm.rotation.set(.52+t*.22,0,.07);u.lFore.rotation.set(.14-t*.1,0,0);
u.rArm.rotation.set(.52+t*.22,0,-.07);u.rFore.rotation.set(.14-t*.1,0,0)}
};
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
'''
with open('/home/user/webapp/index.html','a') as f: f.write(c)
import os; print(f"P3: {os.path.getsize('/home/user/webapp/index.html')}b")
