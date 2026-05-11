import re

with open('/home/user/webapp/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ============================================================
# FIX 1: SWING GAUGE — Slow down significantly, add visual polish
# ============================================================

# 1a. Swing panel CSS improvements — better gauge bars, accuracy label, sweet spot marker
src = src.replace(
    '#pwrFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#2ecc40,#f1c40f 50%,#e74c3c 85%);transition:none}',
    '#pwrFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#2ecc40 0%,#2ecc40 40%,#f1c40f 60%,#e74c3c 85%,#c0392b 100%);transition:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.25)}'
)

src = src.replace(
    '#accFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#e74c3c,#2ecc40 45%,#2ecc40 55%,#e74c3c);transition:none}',
    '#accFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#e74c3c 0%,#f39c12 20%,#2ecc40 42%,#27ae60 50%,#2ecc40 58%,#f39c12 80%,#e74c3c 100%);transition:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.25)}'
)

# 1b. Add sweet spot indicator CSS and accuracy label
src = src.replace(
    '.barWrap{position:relative;height:22px;border-radius:11px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.12);margin-bottom:8px}',
    '.barWrap{position:relative;height:26px;border-radius:13px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.15);margin-bottom:10px}\n.barWrap .sweet{position:absolute;top:0;left:42%;width:16%;height:100%;border-left:2px solid rgba(255,255,255,.5);border-right:2px solid rgba(255,255,255,.5);background:rgba(46,204,113,.12);z-index:1;pointer-events:none}\n.gaugeLabel{display:flex;justify-content:space-between;margin-bottom:4px;font-size:10px;font-weight:700}\n.gaugeLabel .gl{color:rgba(255,255,255,.5)}\n.gaugeLabel .gv{color:#ffd700;font-size:13px;font-weight:800}'
)

# 1c. Replace the swing panel HTML with better labels and sweet spot
src = src.replace(
    '''<div id="swingPanel"><div id="swingInner">
<div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:rgba(255,255,255,.5);font-size:10px;font-weight:700">파워</span><span id="swVal" style="color:#ffd700;font-size:13px;font-weight:800">0%</span></div>
<div class="barWrap" id="pwrWrap"><div id="pwrFill"></div></div>
<div class="barWrap" id="accWrap"><div id="accFill"></div></div>
<button id="swBtn" ontouchstart="onSwTap(event)" onclick="onSwTap(event)">스윙!</button>
</div></div>''',
    '''<div id="swingPanel"><div id="swingInner">
<div class="gaugeLabel"><span class="gl">⚡ 파워</span><span class="gv" id="swVal">0%</span></div>
<div class="barWrap" id="pwrWrap"><div id="pwrFill"></div></div>
<div class="gaugeLabel" id="accLabel" style="display:none"><span class="gl">🎯 정확도</span><span class="gv" id="accValTxt">조준중...</span></div>
<div class="barWrap" id="accWrap"><div class="sweet"></div><div id="accFill"></div></div>
<button id="swBtn" ontouchstart="onSwTap(event)" onclick="onSwTap(event)">스윙!</button>
</div></div>'''
)

# 1d. Fix tickGauge — reduce speeds from 2.8/3.4 to 1.0/1.4
src = src.replace(
    '''/* ===== GAUGE TICK ===== */
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
$('accFill').style.width=G.accVal+'%'}}''',
    '''/* ===== GAUGE TICK ===== */
function tickGauge(dt){
if(G.swPhase==='power'){
G.gaugeVal+=G.gaugeDir*1.0*dt*100;
if(G.gaugeVal>=100){G.gaugeVal=100;G.gaugeDir=-1}
if(G.gaugeVal<=0){G.gaugeVal=0;G.gaugeDir=1}
$('pwrFill').style.width=G.gaugeVal+'%';
$('swVal').textContent=Math.round(G.gaugeVal)+'%';
updAim(G.gaugeVal)}
else if(G.swPhase==='accuracy'){
G.accVal+=G.accDir*1.4*dt*100;
if(G.accVal>=100){G.accVal=100;G.accDir=-1}
if(G.accVal<=0){G.accVal=0;G.accDir=1}
$('accFill').style.width=G.accVal+'%';
const d=Math.abs(G.accVal-50);
$('accValTxt').textContent=d<8?'Perfect!':d<18?'Good':'조준중...'}}'''
)

# 1e. Fix showSwing to also show accuracy label
src = src.replace(
    "function showSwing(show){\n$('swingPanel').style.display=show?'block':'none';\nif(show){$('pwrFill').style.width='0%';$('accFill').style.width='0%';$('accWrap').style.display='none';\nG.swPhase='power';G.gaugeVal=0;G.gaugeDir=1;$('swVal').textContent='0%'}}",
    "function showSwing(show){\n$('swingPanel').style.display=show?'block':'none';\nif(show){$('pwrFill').style.width='0%';$('accFill').style.width='0%';$('accWrap').style.display='none';$('accLabel').style.display='none';\nG.swPhase='power';G.gaugeVal=0;G.gaugeDir=1;$('swVal').textContent='0%'}}"
)

# 1f. Fix onSwTap to show accuracy label
src = src.replace(
    "if(G.swPhase==='power'){\nG.power=G.gaugeVal;G.swPhase='accuracy';\n$('accWrap').style.display='block';G.accVal=50;G.accDir=1;\n$('swVal').textContent='정확도';AUD.play('click')}",
    "if(G.swPhase==='power'){\nG.power=G.gaugeVal;G.swPhase='accuracy';\n$('accWrap').style.display='block';$('accLabel').style.display='flex';G.accVal=50;G.accDir=1;\n$('swVal').textContent=Math.round(G.power)+'%';AUD.play('click');vib(15)}"
)

# 1g. Update swing button text
src = src.replace(
    '''<button id="swBtn" ontouchstart="onSwTap(event)" onclick="onSwTap(event)">스윙!</button>''',
    '''<button id="swBtn" ontouchstart="onSwTap(event)" onclick="onSwTap(event)">탭하여 스윙!</button>'''
)

# ============================================================
# FIX 2: ENHANCED SKY & BACKGROUNDS — More realistic
# ============================================================

# 2a. Replace sky texture with much more realistic version
old_sky = '''sky(){const c=document.createElement('canvas');c.width=4096;c.height=2048;const x=c.getContext('2d');
const g=x.createLinearGradient(0,0,0,2048);
g.addColorStop(0,'#050d1a');g.addColorStop(.08,'#0a1a3a');g.addColorStop(.2,'#1a3a6a');g.addColorStop(.35,'#3a7abe');g.addColorStop(.48,'#6aabe8');
g.addColorStop(.58,'#8ec8f0');g.addColorStop(.68,'#b8ddf5');g.addColorStop(.76,'#e0eef8');g.addColorStop(.82,'#f0e8d0');
g.addColorStop(.88,'#d0b888');g.addColorStop(.93,'#88a868');g.addColorStop(1,'#4a7838');
x.fillStyle=g;x.fillRect(0,0,4096,2048);
for(let i=0;i<60;i++){const cx=Math.random()*4096,cy=350+Math.random()*500,cw=120+Math.random()*350,ch=20+Math.random()*50;
for(let j=0;j<12;j++){const ox=cx+(Math.random()-.5)*cw,oy=cy+(Math.random()-.5)*ch,r=20+Math.random()*55;
const rg=x.createRadialGradient(ox,oy,0,ox,oy,r);rg.addColorStop(0,'rgba(255,255,255,.2)');rg.addColorStop(.4,'rgba(255,255,255,.1)');rg.addColorStop(1,'rgba(255,255,255,0)');
x.fillStyle=rg;x.fillRect(ox-r,oy-r,r*2,r*2)}}
const sg=x.createRadialGradient(2800,850,0,2800,850,350);sg.addColorStop(0,'rgba(255,245,220,.25)');sg.addColorStop(.3,'rgba(255,230,180,.12)');sg.addColorStop(1,'rgba(255,200,100,0)');
x.fillStyle=sg;x.fillRect(2300,500,1000,700);
const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;return t}'''

new_sky = '''sky(){const c=document.createElement('canvas');c.width=4096;c.height=2048;const x=c.getContext('2d');
// Photorealistic sky gradient
const g=x.createLinearGradient(0,0,0,2048);
g.addColorStop(0,'#0a1628');g.addColorStop(.05,'#0f2040');g.addColorStop(.12,'#1a3868');
g.addColorStop(.22,'#2a5fa0');g.addColorStop(.32,'#4088cc');g.addColorStop(.42,'#62ade4');
g.addColorStop(.50,'#82c4f0');g.addColorStop(.56,'#9ed4f6');g.addColorStop(.62,'#b5e0f8');
g.addColorStop(.68,'#cceafc');g.addColorStop(.73,'#dff0fa');g.addColorStop(.77,'#f0f5f8');
g.addColorStop(.80,'#fff8ee');g.addColorStop(.83,'#ffe8c8');g.addColorStop(.86,'#f0d4a0');
g.addColorStop(.89,'#c8b888');g.addColorStop(.92,'#8aaa6a');g.addColorStop(.95,'#5a8a4a');
g.addColorStop(1,'#3a6a30');
x.fillStyle=g;x.fillRect(0,0,4096,2048);
// Atmospheric haze near horizon
const hz=x.createLinearGradient(0,1300,0,1700);
hz.addColorStop(0,'rgba(200,220,240,0)');hz.addColorStop(.5,'rgba(220,235,250,.18)');hz.addColorStop(1,'rgba(240,245,255,.08)');
x.fillStyle=hz;x.fillRect(0,1300,4096,400);
// Volumetric cumulus clouds - big realistic shapes
for(let i=0;i<45;i++){const cx=Math.random()*4096,cy=280+Math.random()*580;
const cw=180+Math.random()*500,ch=35+Math.random()*80;
// Cloud base shadow
for(let j=0;j<18;j++){const ox=cx+(Math.random()-.5)*cw,oy=cy+(Math.random()-.5)*ch+ch*.2;
const r=25+Math.random()*45;
const rg=x.createRadialGradient(ox,oy,0,ox,oy,r);
rg.addColorStop(0,'rgba(140,150,170,.06)');rg.addColorStop(1,'rgba(140,150,170,0)');
x.fillStyle=rg;x.fillRect(ox-r,oy-r,r*2,r*2)}
// Cloud bright tops
for(let j=0;j<25;j++){const ox=cx+(Math.random()-.5)*cw*.9,oy=cy+(Math.random()-.5)*ch*.7-ch*.15;
const r=20+Math.random()*65;
const rg=x.createRadialGradient(ox,oy-r*.1,r*.15,ox,oy,r);
rg.addColorStop(0,'rgba(255,255,255,.28)');rg.addColorStop(.3,'rgba(255,255,255,.18)');
rg.addColorStop(.6,'rgba(245,248,255,.08)');rg.addColorStop(1,'rgba(245,248,255,0)');
x.fillStyle=rg;x.fillRect(ox-r,oy-r,r*2,r*2)}}
// Wispy cirrus clouds high up
for(let i=0;i<30;i++){const cx=Math.random()*4096,cy=120+Math.random()*250;
x.save();x.translate(cx,cy);x.rotate((Math.random()-.5)*.3);
x.globalAlpha=.04+Math.random()*.06;
x.fillStyle='#fff';x.beginPath();
const w=80+Math.random()*200,h=2+Math.random()*5;
x.ellipse(0,0,w,h,0,0,Math.PI*2);x.fill();x.restore();x.globalAlpha=1}
// Sun glow - warm & realistic
const sunX=2900,sunY=780;
const s1=x.createRadialGradient(sunX,sunY,0,sunX,sunY,80);
s1.addColorStop(0,'rgba(255,255,240,.45)');s1.addColorStop(.3,'rgba(255,250,220,.25)');
s1.addColorStop(.7,'rgba(255,240,200,.08)');s1.addColorStop(1,'rgba(255,230,180,0)');
x.fillStyle=s1;x.fillRect(sunX-100,sunY-100,200,200);
// Wide sun halo
const s2=x.createRadialGradient(sunX,sunY,0,sunX,sunY,450);
s2.addColorStop(0,'rgba(255,248,230,.2)');s2.addColorStop(.2,'rgba(255,240,210,.1)');
s2.addColorStop(.5,'rgba(255,225,180,.04)');s2.addColorStop(1,'rgba(255,200,150,0)');
x.fillStyle=s2;x.fillRect(sunX-500,sunY-500,1000,1000);
// God rays from sun
for(let i=0;i<12;i++){const a=-Math.PI*.3+Math.random()*Math.PI*.6;
const len=300+Math.random()*400;
x.save();x.translate(sunX,sunY);x.rotate(a);
const rg=x.createLinearGradient(0,0,0,len);
rg.addColorStop(0,'rgba(255,245,220,.06)');rg.addColorStop(.5,'rgba(255,240,200,.02)');
rg.addColorStop(1,'rgba(255,235,190,0)');
x.fillStyle=rg;x.fillRect(-8,0,16,len);x.restore()}
const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;return t}'''

src = src.replace(old_sky, new_sky)

# 2b. Enhance scene setup — better lighting, fog color, add secondary lights
old_scene_setup = '''sunLight=new THREE.DirectionalLight(0xfff8e8,3);
sunLight.position.set(40,60,25);sunLight.castShadow=true;
sunLight.shadow.mapSize.set(2048,2048);
const sc=sunLight.shadow.camera;sc.left=-70;sc.right=70;sc.top=70;sc.bottom=-70;sc.near=1;sc.far=180;
sunLight.shadow.bias=-.0008;sunLight.shadow.normalBias=.02;
scene.add(sunLight);
scene.add(new THREE.AmbientLight(0x5588aa,.55));
scene.add(new THREE.HemisphereLight(0x88ccff,0x445522,.45));
scene.background=TEX.sky();scene.environment=scene.background;
scene.fog=new THREE.FogExp2(0xa8d4f0,.003)'''

new_scene_setup = '''sunLight=new THREE.DirectionalLight(0xfff5e0,3.2);
sunLight.position.set(45,65,30);sunLight.castShadow=true;
sunLight.shadow.mapSize.set(2048,2048);
const sc=sunLight.shadow.camera;sc.left=-70;sc.right=70;sc.top=70;sc.bottom=-70;sc.near=1;sc.far=180;
sunLight.shadow.bias=-.0008;sunLight.shadow.normalBias=.02;
scene.add(sunLight);
// Warm fill light from opposite side
const fillLight=new THREE.DirectionalLight(0xffeedd,.6);fillLight.position.set(-30,20,-15);scene.add(fillLight);
// Rim/back light for depth
const rimLight=new THREE.DirectionalLight(0xaaccff,.4);rimLight.position.set(-10,40,-40);scene.add(rimLight);
scene.add(new THREE.AmbientLight(0x6699bb,.5));
scene.add(new THREE.HemisphereLight(0x99ccff,0x556633,.55));
scene.background=TEX.sky();scene.environment=scene.background;
scene.fog=new THREE.FogExp2(0xc0ddf0,.0022)'''

src = src.replace(old_scene_setup, new_scene_setup)

# 2c. Enhance grass texture — more blade detail, richer colors
old_grass = '''grass(w=1024,h=1024){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
for(let y=0;y<h;y+=2){const b=.22+Math.sin(y*.01)*.03;
x.fillStyle=`hsl(${110+Math.random()*15},${55+Math.random()*15}%,${(b+Math.random()*.04)*100}%)`;x.fillRect(0,y,w,2)}
for(let i=0;i<12000;i++){const bx=Math.random()*w,by=Math.random()*h,bl=4+Math.random()*12;
x.strokeStyle=`hsla(${100+Math.random()*30},${40+Math.random()*30}%,${18+Math.random()*22}%,${.3+Math.random()*.4})`;
x.lineWidth=.4+Math.random()*.8;x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo(bx+(Math.random()-.5)*3,by-bl*.5,bx+(Math.random()-.5)*2,by-bl);x.stroke()}
for(let i=0;i<25;i++){const px=Math.random()*w,py=Math.random()*h,pr=20+Math.random()*50;
const rg=x.createRadialGradient(px,py,0,px,py,pr);rg.addColorStop(0,`rgba(${80+Math.random()*40},${140+Math.random()*60},${40+Math.random()*30},${.06+Math.random()*.06})`);
rg.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=rg;x.fillRect(px-pr,py-pr,pr*2,pr*2)}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(15,15);t.anisotropy=4;return t}'''

new_grass = '''grass(w=1024,h=1024){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
// Rich base with subtle color variation
for(let y=0;y<h;y+=1){const b=.20+Math.sin(y*.008)*.04+Math.sin(y*.025)*.02;
x.fillStyle=`hsl(${108+Math.sin(y*.01)*8},${52+Math.sin(y*.015)*10}%,${(b+Math.random()*.03)*100}%)`;x.fillRect(0,y,w,1)}
// Subtle light/dark patches (dappled sunlight)
for(let i=0;i<40;i++){const px=Math.random()*w,py=Math.random()*h,pr=30+Math.random()*80;
const bright=Math.random()>.5;
const rg=x.createRadialGradient(px,py,0,px,py,pr);
rg.addColorStop(0,bright?`rgba(120,200,80,.08)`:`rgba(30,80,20,.06)`);
rg.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=rg;x.fillRect(px-pr,py-pr,pr*2,pr*2)}
// Dense grass blades with variety
for(let i=0;i<18000;i++){const bx=Math.random()*w,by=Math.random()*h,bl=3+Math.random()*14;
const hue=95+Math.random()*35,sat=35+Math.random()*35,lit=16+Math.random()*24;
x.strokeStyle=`hsla(${hue},${sat}%,${lit}%,${.25+Math.random()*.4})`;
x.lineWidth=.3+Math.random()*.9;x.beginPath();x.moveTo(bx,by);
const bend=(Math.random()-.5)*4;x.quadraticCurveTo(bx+bend,by-bl*.5,bx+bend*.7,by-bl);x.stroke()}
// Tiny flowers/clover scattered
for(let i=0;i<200;i++){const fx=Math.random()*w,fy=Math.random()*h;
x.fillStyle=Math.random()>.7?`rgba(255,255,200,.12)`:`rgba(180,220,160,.08)`;
x.beginPath();x.arc(fx,fy,.5+Math.random()*1,0,Math.PI*2);x.fill()}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(14,14);t.anisotropy=4;return t}'''

src = src.replace(old_grass, new_grass)

# 2d. Enhance mountains with snow caps and better colors
old_mountains = '''function mkMountains(){const g=new THREE.Group();
for(let layer=0;layer<3;layer++){const dist=70+layer*35,color=[0x3a6a3a,0x4a7a4a,0x6a9a6a][layer],peaks=10+layer*4;
const verts=[],idx=[];for(let i=0;i<=peaks;i++){const a=(i/peaks)*Math.PI*2,r=dist+Math.random()*12,x=Math.cos(a)*r,z=Math.sin(a)*r,h=(10+Math.random()*18)*(1-layer*.25);
verts.push(x,0,z,x,h,z);if(i<peaks){const b=i*2;idx.push(b,b+1,b+2,b+1,b+3,b+2)}}
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));geo.setIndex(idx);geo.computeVertexNormals();
const m=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color,roughness:.82,flatShading:true}));m.receiveShadow=true;g.add(m)}return g}'''

new_mountains = '''function mkMountains(){const g=new THREE.Group();
const layerColors=[[0x2a5a2a,0x4a8a4a],[0x3a6a3a,0x5a9a5a],[0x5a8a5a,0x7aaa7a]];
for(let layer=0;layer<3;layer++){const dist=75+layer*38,peaks=12+layer*5;
const verts=[],idx=[],colors=[];
for(let i=0;i<=peaks;i++){const a=(i/peaks)*Math.PI*2,r=dist+Math.random()*15;
const x=Math.cos(a)*r,z=Math.sin(a)*r,h=(12+Math.random()*22)*(1-layer*.22);
verts.push(x,0,z,x,h,z);
// Base color
const bc=new THREE.Color(layerColors[layer][0]);colors.push(bc.r,bc.g,bc.b);
// Peak color - snow caps on tallest peaks
const peak=h>18?new THREE.Color(0xe8e8f0):h>14?new THREE.Color(0x8aaa7a):new THREE.Color(layerColors[layer][1]);
colors.push(peak.r,peak.g,peak.b);
if(i<peaks){const b=i*2;idx.push(b,b+1,b+2,b+1,b+3,b+2)}}
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
geo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
geo.setIndex(idx);geo.computeVertexNormals();
const m=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({vertexColors:true,roughness:.78,flatShading:true}));m.receiveShadow=true;g.add(m)}
// Distant haze layer
const hazeGeo=new THREE.RingGeometry(110,180,32);
const hazeMat=new THREE.MeshBasicMaterial({color:0xc0ddf0,transparent:true,opacity:.15,side:THREE.DoubleSide,depthWrite:false});
const haze=new THREE.Mesh(hazeGeo,hazeMat);haze.rotation.x=-Math.PI/2;haze.position.y=2;g.add(haze);
return g}'''

src = src.replace(old_mountains, new_mountains)

# 2e. Update tone mapping exposure for richer look
src = src.replace("renderer.toneMappingExposure=1.3;", "renderer.toneMappingExposure=1.25;")

# ============================================================
# FIX 3: IMPROVED GOLFER CHARACTER — More organic, less robotic
# ============================================================

# 3a. Better skin material (warmer, subsurface-like)
src = src.replace(
    "skin:new THREE.MeshStandardMaterial({color:0xf0be98,roughness:.65}),",
    "skin:new THREE.MeshStandardMaterial({color:0xf2c4a0,roughness:.55,metalness:.02}),"
)

# 3b. Better shirt — richer color with slight sheen
src = src.replace(
    "shirt:new THREE.MeshStandardMaterial({color:0x1a55aa,roughness:.55}),",
    "shirt:new THREE.MeshStandardMaterial({color:0x1e5cb8,roughness:.48,metalness:.04}),"
)

# 3c. Better pants
src = src.replace(
    "pants:new THREE.MeshStandardMaterial({color:0x2a3545,roughness:.65}),",
    "pants:new THREE.MeshStandardMaterial({color:0x2d3a4d,roughness:.58}),"
)

# 3d. Better hair
src = src.replace(
    "hair:new THREE.MeshStandardMaterial({color:0x2a1a0a,roughness:.75}),",
    "hair:new THREE.MeshStandardMaterial({color:0x28180a,roughness:.68,metalness:.03}),"
)

# 3e. Replace entire createGolfer with higher poly, more organic proportions
old_golfer = '''/* ===== 3D GOLFER ===== */
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
arm.add(mkM(new THREE.CylinderGeometry(.032,.028,.2,6),M.shirt,0,-.1,0,true));
const fore=new THREE.Group();fore.name=name.replace('Arm','Fore');
fore.add(mkM(new THREE.CylinderGeometry(.028,.022,.18,6),M.skin,0,-.09,0,true));
fore.add(mkM(new THREE.SphereGeometry(.023,6,5),side<0?M.glove:M.skin,0,-.18,0,false));
fore.position.y=-.2;arm.add(fore);
arm.position.set(side*.16,.04,0);torso.add(arm);return{arm,fore}}
const la=mkArm('lArm',1),ra=mkArm('rArm',-1);
// Legs
function mkLeg(name,side){
const leg=new THREE.Group();leg.name=name;
leg.add(mkM(new THREE.CylinderGeometry(.048,.038,.26,6),M.pants,0,-.13,0,true));
const shin=new THREE.Group();shin.name=name.replace('Leg','Shin');
shin.add(mkM(new THREE.CylinderGeometry(.038,.032,.26,6),M.pants,0,-.13,0,true));
shin.add(mkM(new THREE.BoxGeometry(.048,.028,.09),M.shoes,0,-.27,.018,true));
shin.position.y=-.26;leg.add(shin);
leg.position.set(side*.065,0,0);hips.add(leg);return{leg,shin}}
const ll=mkLeg('lLeg',1),rl=mkLeg('rLeg',-1);
// Golf Club
const club=new THREE.Group();club.name='club';
const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.005,.005,.65,6),M.clubM);shaft.position.y=-.325;club.add(shaft);
club.add(mkM(new THREE.CylinderGeometry(.008,.007,.13,6),M.grip,0,0,0,false));
const ch=new THREE.Mesh(new THREE.BoxGeometry(.055,.018,.035),M.clubM);ch.position.y=-.65;ch.castShadow=true;club.add(ch);
club.position.set(0,-.18,0);la.fore.add(club);
// Shadow disc
const shd=new THREE.Mesh(new THREE.CircleGeometry(.2,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.22,depthWrite:false}));
shd.rotation.x=-Math.PI/2;shd.position.y=.003;g.add(shd);
g.userData={torso,hips,head,lArm:la.arm,lFore:la.fore,rArm:ra.arm,rFore:ra.fore,lLeg:ll.leg,lShin:ll.shin,rLeg:rl.leg,rShin:rl.shin,club,torsoBaseY:torso.position.y};
g.scale.set(1.8,1.8,1.8);
golfer=g;scene.add(g);golfer.visible=false;
return g}'''

new_golfer = '''/* ===== 3D GOLFER ===== */
function createGolfer(){
const g=new THREE.Group();
const SEG=12; // Higher poly for smoother look
const torso=new THREE.Group();torso.name='torso';
// Torso — slightly tapered, rounder
const torsoGeo=new THREE.CylinderGeometry(.135,.115,.40,SEG);
torso.add(Object.assign(new THREE.Mesh(torsoGeo,M.shirt),{castShadow:true}));
// Collar detail
const collar=new THREE.Mesh(new THREE.TorusGeometry(.12,.014,8,SEG),M.shirt);
collar.position.y=.19;collar.rotation.x=Math.PI/2;torso.add(collar);
// Shoulder pads for more natural silhouette
const lShd=new THREE.Mesh(new THREE.SphereGeometry(.048,8,6),M.shirt);lShd.position.set(.14,.16,0);lShd.scale.set(1,.7,1);torso.add(lShd);
const rShd=new THREE.Mesh(new THREE.SphereGeometry(.048,8,6),M.shirt);rShd.position.set(-.14,.16,0);rShd.scale.set(1,.7,1);torso.add(rShd);
torso.position.y=.82;g.add(torso);
// Hips + Belt
const hips=new THREE.Group();hips.name='hips';
hips.add(Object.assign(new THREE.Mesh(new THREE.CylinderGeometry(.115,.125,.13,SEG),M.pants),{castShadow:true}));
hips.position.y=.6;g.add(hips);
const belt=new THREE.Mesh(new THREE.TorusGeometry(.118,.012,8,20),new THREE.MeshStandardMaterial({color:0x3a2a1a,roughness:.5,metalness:.2}));
belt.rotation.x=Math.PI/2;belt.position.y=.665;g.add(belt);
// Belt buckle
const buckle=new THREE.Mesh(new THREE.BoxGeometry(.022,.018,.006),new THREE.MeshStandardMaterial({color:0xc0a040,roughness:.3,metalness:.6}));
buckle.position.set(0,.665,.12);g.add(buckle);
// Head + Face — rounder, more detailed
const head=new THREE.Group();head.name='head';
// Main head shape
const headGeo=new THREE.SphereGeometry(.092,14,12);
head.add(Object.assign(new THREE.Mesh(headGeo,M.skin),{castShadow:true}));
// Ears
for(const sx of[-.085,.085]){const ear=new THREE.Mesh(new THREE.SphereGeometry(.018,8,6),M.skin);ear.position.set(sx,-.01,.005);ear.scale.set(.6,1,.6);head.add(ear)}
// Eyes - with white sclera
for(const sx of[-.03,.03]){
const sclera=new THREE.Mesh(new THREE.SphereGeometry(.014,8,6),new THREE.MeshBasicMaterial({color:0xf8f8f8}));
sclera.position.set(sx,.006,.08);sclera.scale.set(1,.7,1);head.add(sclera);
const iris=new THREE.Mesh(new THREE.SphereGeometry(.007,6,4),new THREE.MeshBasicMaterial({color:0x2a1a0a}));
iris.position.set(sx,.006,.088);head.add(iris)}
// Eyebrows
for(const sx of[-.03,.03]){const brow=new THREE.Mesh(new THREE.BoxGeometry(.022,.005,.005),M.hair);brow.position.set(sx,.025,.082);head.add(brow)}
// Nose
const nose=new THREE.Mesh(new THREE.CylinderGeometry(.006,.01,.02,6),M.skin);
nose.position.set(0,-.008,.088);nose.rotation.x=-.3;head.add(nose);
// Mouth/smile line
const mouth=new THREE.Mesh(new THREE.TorusGeometry(.015,.003,4,8,Math.PI),new THREE.MeshBasicMaterial({color:0xc08060}));
mouth.position.set(0,-.028,.082);mouth.rotation.x=.1;head.add(mouth);
// Hair + Cap
const hairGeo=new THREE.SphereGeometry(.094,14,10,0,Math.PI*2,0,Math.PI*.48);
head.add(new THREE.Mesh(hairGeo,M.hair));
// Sideburns
for(const sx of[-.078,.078]){const sb=new THREE.Mesh(new THREE.BoxGeometry(.012,.03,.012),M.hair);sb.position.set(sx,-.02,.03);head.add(sb)}
const cap=new THREE.Mesh(new THREE.CylinderGeometry(.098,.098,.032,14),M.hat);cap.position.y=.062;cap.castShadow=true;head.add(cap);
const visor=new THREE.Mesh(new THREE.BoxGeometry(.09,.008,.065),M.hat);visor.position.set(0,.052,.085);head.add(visor);
// Cap logo dot
const logo=new THREE.Mesh(new THREE.CircleGeometry(.012,8),new THREE.MeshBasicMaterial({color:0x2255aa}));
logo.position.set(0,.045,.099);head.add(logo);
head.position.y=.33;torso.add(head);
// Arms — higher poly, natural taper
function mkArm(name,side){
const arm=new THREE.Group();arm.name=name;
arm.add(mkM(new THREE.CylinderGeometry(.035,.030,.21,SEG),M.shirt,0,-.105,0,true));
const fore=new THREE.Group();fore.name=name.replace('Arm','Fore');
fore.add(mkM(new THREE.CylinderGeometry(.030,.024,.19,SEG),M.skin,0,-.095,0,true));
// Wrist detail
fore.add(mkM(new THREE.CylinderGeometry(.025,.025,.015,8),M.skin,0,-.175,0,false));
// Hand — slightly bigger, more visible
const handMat=side<0?M.glove:M.skin;
fore.add(mkM(new THREE.SphereGeometry(.025,8,6),handMat,0,-.19,0,false));
fore.position.y=-.21;arm.add(fore);
arm.position.set(side*.165,.05,0);torso.add(arm);return{arm,fore}}
const la=mkArm('lArm',1),ra=mkArm('rArm',-1);
// Legs — thicker, more natural
function mkLeg(name,side){
const leg=new THREE.Group();leg.name=name;
leg.add(mkM(new THREE.CylinderGeometry(.052,.042,.27,SEG),M.pants,0,-.135,0,true));
const shin=new THREE.Group();shin.name=name.replace('Leg','Shin');
shin.add(mkM(new THREE.CylinderGeometry(.042,.035,.27,SEG),M.pants,0,-.135,0,true));
// Ankle
shin.add(mkM(new THREE.CylinderGeometry(.036,.036,.02,8),M.pants,0,-.26,0,false));
// Shoe — rounded box shape
const shoeGeo=new THREE.BoxGeometry(.052,.032,.10);shoeGeo.translate(0,0,.01);
shin.add(mkM(shoeGeo,M.shoes,0,-.28,.015,true));
shin.position.y=-.27;leg.add(shin);
leg.position.set(side*.068,0,0);hips.add(leg);return{leg,shin}}
const ll=mkLeg('lLeg',1),rl=mkLeg('rLeg',-1);
// Golf Club
const club=new THREE.Group();club.name='club';
const shaft=new THREE.Mesh(new THREE.CylinderGeometry(.005,.005,.65,8),M.clubM);shaft.position.y=-.325;club.add(shaft);
club.add(mkM(new THREE.CylinderGeometry(.009,.008,.14,8),M.grip,0,0,0,false));
const ch=new THREE.Mesh(new THREE.BoxGeometry(.058,.02,.038),M.clubM);ch.position.y=-.65;ch.castShadow=true;club.add(ch);
club.position.set(0,-.18,0);la.fore.add(club);
// Shadow disc — softer
const shd=new THREE.Mesh(new THREE.CircleGeometry(.22,16),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.18,depthWrite:false}));
shd.rotation.x=-Math.PI/2;shd.position.y=.003;g.add(shd);
g.userData={torso,hips,head,lArm:la.arm,lFore:la.fore,rArm:ra.arm,rFore:ra.fore,lLeg:ll.leg,lShin:ll.shin,rLeg:rl.leg,rShin:rl.shin,club,torsoBaseY:torso.position.y};
g.scale.set(1.8,1.8,1.8);
golfer=g;scene.add(g);golfer.visible=false;
return g}'''

src = src.replace(old_golfer, new_golfer)

# 3f. Improve idle animation — add weight shift and subtle head movement
old_idle_anim = '''// Golfer idle breathing
if(golfer&&golfer.visible&&G.state==='aim'&&!SA.active){
const b=Math.sin(elapsed*2)*.008;
golfer.userData.torso.position.y=golfer.userData.torsoBaseY+b}'''

new_idle_anim = '''// Golfer idle breathing + weight shift + head look
if(golfer&&golfer.visible&&G.state==='aim'&&!SA.active){
const u=golfer.userData;
const b=Math.sin(elapsed*1.8)*.008;
u.torso.position.y=u.torsoBaseY+b;
// Subtle weight shift side to side
const sw=Math.sin(elapsed*.7)*.012;
u.hips.rotation.z=sw;
u.torso.rotation.z=-sw*.5;
// Subtle head look toward hole
u.head.rotation.y=Math.sin(elapsed*.5)*.04;
u.head.rotation.x=.05+Math.sin(elapsed*1.2)*.015;
// Arms relax slightly
const ar=Math.sin(elapsed*1.4)*.01;
u.lArm.rotation.x=.08+ar;u.rArm.rotation.x=.08-ar}'''

src = src.replace(old_idle_anim, new_idle_anim)

# ============================================================
# ADDITIONAL POLISH
# ============================================================

# Add more trees to courses
src = src.replace(
    "const nTrees=12+Math.floor(rng()*12);",
    "const nTrees=18+Math.floor(rng()*14);"
)

# More flowers
src = src.replace(
    "for(let i=0;i<6+Math.floor(rng()*10);i++){",
    "for(let i=0;i<12+Math.floor(rng()*16);i++){"
)

# Update cache version in sw.js reference
# Also update the game version indicator
src = src.replace(
    "console.log('Park Golf Pro v9 initialized')",
    "console.log('Park Golf Pro v10 initialized')"
)

with open('/home/user/webapp/index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("All fixes applied successfully!")
print(f"File size: {len(src)} bytes")
