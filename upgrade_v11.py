import re

with open('/home/user/webapp/index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ============================================================
# GOLF KING STYLE UPGRADE — HUD + Aiming + Camera + Landing Zone
# ============================================================

# 1. REPLACE HUD CSS — Golf King style panels
old_hud_css = '''#hud{position:absolute;top:0;left:0;width:100%;pointer-events:none;z-index:10;display:none}
#hudBar{display:flex;justify-content:space-between;padding:6px 10px;background:linear-gradient(180deg,rgba(0,0,0,.7),transparent)}
.hd{text-align:center;min-width:48px}.hd .hl{font-size:8px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.5px}
.hd .hv{font-size:14px;color:#fff;font-weight:700}
#clubBtn{position:absolute;top:52px;right:8px;pointer-events:auto;z-index:15;background:rgba(0,0,0,.7);color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:5px 12px;font-size:12px;font-weight:700;cursor:pointer;display:none}
#minimap{position:absolute;bottom:130px;right:6px;width:120px;height:120px;border-radius:10px;border:1.5px solid rgba(255,255,255,.2);z-index:12;pointer-events:none;overflow:hidden;display:none}'''

new_hud_css = '''#hud{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:10;display:none}
/* Golf King — Top Left Info Panel */
#infoPanel{position:absolute;top:8px;left:8px;z-index:15;pointer-events:auto}
.ipBox{background:rgba(0,0,0,.72);border-radius:10px;padding:6px 11px;margin-bottom:4px;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,.08)}
#ipCrs{display:flex;align-items:center;gap:7px}
#ipCrs .cNm{font-size:12px;font-weight:800;color:#ffd700}
#ipCrs .cHl{font-size:11px;color:rgba(255,255,255,.85)}
#ipClub .clR{display:flex;align-items:center;gap:8px}
.clIco{width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#2266aa,#44aadd);display:flex;align-items:center;justify-content:center;font-size:15px;color:#fff;font-weight:900}
.clNm{font-size:13px;font-weight:700;color:#fff}
.clLv{font-size:8px;color:#ffd700;background:rgba(255,215,0,.15);padding:1px 5px;border-radius:3px;margin-left:4px}
.clDst{font-size:10px;color:rgba(255,255,255,.55);margin-top:1px}
#ipWind{display:flex;align-items:center;gap:6px}
.wIco{font-size:13px}
.wSpd{font-size:15px;font-weight:800;color:#ff9944}
.wU{font-size:9px;color:rgba(255,255,255,.4)}
.wArr{display:inline-block;font-size:16px;color:#ff9944;transition:transform .3s}
/* Top Right Boxes */
#topR{position:absolute;top:8px;right:8px;display:flex;gap:4px;z-index:15}
.trB{background:rgba(0,0,0,.72);border-radius:10px;padding:5px 10px;text-align:center;backdrop-filter:blur(4px);min-width:46px;border:1px solid rgba(255,255,255,.08)}
.trB .tl{font-size:7px;color:rgba(255,255,255,.4);letter-spacing:.5px;text-transform:uppercase}
.trB .tv{font-size:14px;color:#fff;font-weight:800}
.trB .tv.gd{color:#ffd700}
/* Club Button — bottom right circle */
#clubBtn{position:absolute;bottom:145px;right:10px;pointer-events:auto;z-index:15;background:rgba(0,0,0,.8);color:#fff;border:2px solid rgba(46,204,113,.4);border-radius:50%;width:50px;height:50px;font-size:9px;font-weight:700;cursor:pointer;display:none;text-align:center;line-height:1.2;backdrop-filter:blur(4px)}
/* Minimap */
#minimap{position:absolute;top:56px;right:8px;width:105px;height:105px;border-radius:10px;border:1px solid rgba(255,255,255,.12);z-index:12;pointer-events:none;overflow:hidden;display:none;background:rgba(0,35,0,.6);backdrop-filter:blur(2px)}
/* Center distance display */
#distPin{position:absolute;bottom:140px;left:50%;transform:translateX(-50%);z-index:14;pointer-events:none;display:none;text-align:center}
#distPin .dv{font-size:30px;font-weight:900;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.8)}
#distPin .du{font-size:11px;color:rgba(255,255,255,.5)}'''

src = src.replace(old_hud_css, new_hud_css)

# 2. REPLACE HUD HTML
old_hud_html = '''<div id="hud"><div id="hudBar">
<div class="hd"><span class="hl">코스</span><span class="hv" id="hCrs">-</span></div>
<div class="hd"><span class="hl">홀</span><span class="hv" id="hHole">1</span></div>
<div class="hd"><span class="hl">파</span><span class="hv" id="hPar">4</span></div>
<div class="hd"><span class="hl">타수</span><span class="hv" id="hStk">0</span></div>
<div class="hd"><span class="hl">거리</span><span class="hv" id="hDst">0m</span></div>
<div class="hd"><span class="hl">바람</span><span class="hv" id="hWnd">0<span id="hWndArr" style="display:inline-block;font-size:10px">↑</span></span></div>
</div></div>
<button id="clubBtn">드라이버</button>'''

new_hud_html = '''<div id="hud">
<div id="infoPanel">
<div class="ipBox" id="ipCrs"><span class="cNm" id="hCrs">서울숲</span><span class="cHl" id="hHole">1홀</span><span class="cHl">·</span><span class="cHl" id="hPar">PAR 4</span></div>
<div class="ipBox" id="ipClub"><div class="clR"><div class="clIco" id="clIco">D</div><div><div style="display:flex;align-items:center"><span class="clNm" id="clNm">드라이버</span><span class="clLv">LV.1</span></div><div class="clDst" id="clDst">비거리 ~40m</div></div></div></div>
<div class="ipBox" id="ipWind"><span class="wIco">💨</span><span class="wSpd" id="wSpd">0.0</span><span class="wU">m/s</span><span class="wArr" id="hWndArr">↑</span></div>
</div>
<div id="topR"><div class="trB"><span class="tl">타수</span><span class="tv" id="hStk">0</span></div><div class="trB"><span class="tl">거리</span><span class="tv gd" id="hDst">0m</span></div></div>
<div id="distPin"><div class="dv" id="dpV">0</div><div class="du">홀까지 거리(m)</div></div>
</div>
<button id="clubBtn">클럽<br>변경</button>'''

src = src.replace(old_hud_html, new_hud_html)

# 3. REPLACE updHUD function
old_updHUD = '''function updHUD(){
const c=COURSES[G.ci],h=c.par[G.hi];
$('hCrs').textContent=c.name;
$('hHole').textContent=`${G.hi+1}홀`;
$('hPar').textContent=`PAR ${h}`;
$('hStk').textContent=`${G.stroke}타`;
const d=holeP?Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z):0;
$('hDst').textContent=`${d.toFixed(1)}m`;
$('hWnd').innerHTML=`${G.wind.spd.toFixed(1)}<span id="hWndArr" style="display:inline-block;font-size:10px;transform:rotate(${Math.round(G.wind.dir*180/Math.PI)}deg)">↑</span>`;
$('clubBtn').textContent=CLUBS[G.ci_].name;
}'''

new_updHUD = '''function updHUD(){
const c=COURSES[G.ci],h=c.par[G.hi];
$('hCrs').textContent=c.name;
$('hHole').textContent=`${G.hi+1}홀`;
$('hPar').textContent=`PAR ${h}`;
$('hStk').textContent=G.stroke;
const d=holeP?Math.hypot(G.ball.x-holeP.x,G.ball.z-holeP.z):0;
$('hDst').textContent=d.toFixed(1)+'m';
$('wSpd').textContent=G.wind.spd.toFixed(1);
$('hWndArr').style.transform='rotate('+Math.round(G.wind.dir*180/Math.PI)+'deg)';
const club=CLUBS[G.ci_];
$('clNm').textContent=club.name;
$('clIco').textContent=['D','W','I','P'][G.ci_];
$('clDst').textContent='비거리 ~'+(club.power*2.5).toFixed(0)+'m';
$('dpV').textContent=d.toFixed(1);
if($('distPin'))$('distPin').style.display=(G.state==='aim')?'block':'none';
}'''

src = src.replace(old_updHUD, new_updHUD)

# 4. Update showScr for new elements
src = src.replace(
    "else if(name==='game'){$('hud').style.display='block';$('clubBtn').style.display='block';$('minimap').style.display='block'}",
    "else if(name==='game'){$('hud').style.display='block';$('clubBtn').style.display='block';$('minimap').style.display='block';if($('distPin'))$('distPin').style.display='block'}"
)
src = src.replace(
    "else if(name==='swing'){$('hud').style.display='block';$('minimap').style.display='block';$('swingPanel').style.display='block'}",
    "else if(name==='swing'){$('hud').style.display='block';$('minimap').style.display='block';$('swingPanel').style.display='block';if($('distPin'))$('distPin').style.display='none'}"
)

# 5. Add distPin to SCREENS
src = src.replace(
    "const SCREENS=['hud','clubBtn','minimap','swingPanel','flyover','scoreScr','resultScr','menuScr','courseScr','recordScr','settingScr','loading'];",
    "const SCREENS=['hud','clubBtn','minimap','swingPanel','flyover','scoreScr','resultScr','menuScr','courseScr','recordScr','settingScr','loading','distPin'];"
)

# 6. REPLACE AIMING — Blue curved line + landing zone like Golf King
old_aim = '''let ballM,ballShadow,aimLine,aimDot,trailLine,trailPts=[],particles=[];
function mkBall(){ballM=new THREE.Mesh(new THREE.SphereGeometry(.021,16,12),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.22,metalness:.05}));ballM.castShadow=true;ballM.scale.set(3,3,3);scene.add(ballM);
ballShadow=new THREE.Mesh(new THREE.CircleGeometry(.05,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.28,depthWrite:false}));ballShadow.rotation.x=-Math.PI/2;scene.add(ballShadow)}
function updBM(){if(!ballM)return;ballM.position.set(G.ball.x,G.ball.y,G.ball.z);ballShadow.position.set(G.ball.x,.004,G.ball.z);const h=Math.max(0,G.ball.y-.063);ballShadow.scale.setScalar(1+h*2);ballShadow.material.opacity=.28/(1+h*3)}
function mkAim(){const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(60*3),3));
aimLine=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xffff44,transparent:true,opacity:.65}));scene.add(aimLine);
aimDot=new THREE.Mesh(new THREE.SphereGeometry(.035,8,6),new THREE.MeshBasicMaterial({color:0xffff00,transparent:true,opacity:.55}));scene.add(aimDot)}
function updAim(pwr){if(!aimLine||!G)return;const club=CLUBS[G.ci],maxD=club.power*(pwr/100)*2.5,loft=rad(club.loft),dir=G.aim;
const pts=aimLine.geometry.attributes.position.array,n=20,dx=Math.sin(dir),dz=-Math.cos(dir);
for(let i=0;i<n;i++){const t=i/(n-1),d=maxD*t*.3,h=Math.sin(t*Math.PI)*maxD*Math.sin(loft)*.06;pts[i*3]=G.ball.x+dx*d;pts[i*3+1]=.063+h;pts[i*3+2]=G.ball.z+dz*d}
for(let i=n;i<60;i++)pts[i*3]=pts[i*3+1]=pts[i*3+2]=0;aimLine.geometry.attributes.position.needsUpdate=true;
aimDot.position.set(G.ball.x+dx*maxD*.3,.063,G.ball.z+dz*maxD*.3);aimDot.visible=true}
function hideAim(){if(aimLine)aimLine.visible=false;if(aimDot)aimDot.visible=false}
function showAimL(){if(aimLine)aimLine.visible=true;if(aimDot)aimDot.visible=true}'''

new_aim = '''let ballM,ballShadow,aimLine,aimDot,landZone,landRing,trailLine,trailPts=[],particles=[];
function mkBall(){ballM=new THREE.Mesh(new THREE.SphereGeometry(.021,16,12),new THREE.MeshStandardMaterial({color:0xffffff,roughness:.22,metalness:.05}));ballM.castShadow=true;ballM.scale.set(3,3,3);scene.add(ballM);
ballShadow=new THREE.Mesh(new THREE.CircleGeometry(.05,12),new THREE.MeshBasicMaterial({color:0,transparent:true,opacity:.28,depthWrite:false}));ballShadow.rotation.x=-Math.PI/2;scene.add(ballShadow)}
function updBM(){if(!ballM)return;ballM.position.set(G.ball.x,G.ball.y,G.ball.z);ballShadow.position.set(G.ball.x,.004,G.ball.z);const h=Math.max(0,G.ball.y-.063);ballShadow.scale.setScalar(1+h*2);ballShadow.material.opacity=.28/(1+h*3)}
function mkAim(){
// Golf King style — white/blue arc trajectory
const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(90*3),3));
aimLine=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xeeffff,transparent:true,opacity:.85}));scene.add(aimLine);
// Landing zone — green/yellow circle on ground
landZone=new THREE.Mesh(new THREE.RingGeometry(.5,.9,32),new THREE.MeshBasicMaterial({color:0x66cc44,transparent:true,opacity:.25,side:THREE.DoubleSide,depthWrite:false}));
landZone.rotation.x=-Math.PI/2;landZone.position.y=.035;scene.add(landZone);
landRing=new THREE.Mesh(new THREE.RingGeometry(.85,.95,32),new THREE.MeshBasicMaterial({color:0xffcc00,transparent:true,opacity:.45,side:THREE.DoubleSide,depthWrite:false}));
landRing.rotation.x=-Math.PI/2;landRing.position.y=.04;scene.add(landRing);
// Center dot
aimDot=new THREE.Mesh(new THREE.SphereGeometry(.05,10,8),new THREE.MeshBasicMaterial({color:0x44aaff,transparent:true,opacity:.65}));scene.add(aimDot)}
function updAim(pwr){if(!aimLine||!G)return;
const club=CLUBS[G.ci_||0],maxD=club.power*(pwr/100)*2.5,loft=rad(club.loft),dir=G.aim;
const pts=aimLine.geometry.attributes.position.array,n=30,dx=Math.sin(dir),dz=-Math.cos(dir),ld=maxD*.3;
for(let i=0;i<n;i++){const t=i/(n-1),d=ld*t,h=Math.sin(t*Math.PI)*maxD*Math.sin(loft)*.07;
pts[i*3]=G.ball.x+dx*d;pts[i*3+1]=.063+h;pts[i*3+2]=G.ball.z+dz*d}
for(let i=n;i<90;i++)pts[i*3]=pts[i*3+1]=pts[i*3+2]=0;
aimLine.geometry.attributes.position.needsUpdate=true;
const lx=G.ball.x+dx*ld,lz=G.ball.z+dz*ld,sc=.4+maxD*.018;
if(landZone){landZone.position.set(lx,.035,lz);landZone.scale.set(sc,sc,sc);landZone.visible=true}
if(landRing){landRing.position.set(lx,.04,lz);landRing.scale.set(sc,sc,sc);landRing.visible=true}
if(aimDot){aimDot.position.set(lx,.07,lz);aimDot.visible=true}}
function hideAim(){if(aimLine)aimLine.visible=false;if(aimDot)aimDot.visible=false;if(landZone)landZone.visible=false;if(landRing)landRing.visible=false}
function showAimL(){if(aimLine)aimLine.visible=true;if(aimDot)aimDot.visible=true;if(landZone)landZone.visible=true;if(landRing)landRing.visible=true}'''

src = src.replace(old_aim, new_aim)

# 7. Landing zone pulse animation in game loop
old_water_anim = '''// Water animation
waters.forEach(w=>{if(w.mesh)w.mesh.position.y=w.mesh.userData.baseY+Math.sin(elapsed*1.5+w.x*.1)*.05});'''

new_water_anim = '''// Water animation
waters.forEach(w=>{if(w.mesh)w.mesh.position.y=w.mesh.userData.baseY+Math.sin(elapsed*1.5+w.x*.1)*.05});
// Landing zone pulse
if(landZone&&landZone.visible){landZone.material.opacity=.2+Math.sin(elapsed*3)*.08;if(landRing)landRing.material.opacity=.35+Math.sin(elapsed*4)*.15}'''

src = src.replace(old_water_anim, new_water_anim)

# 8. Update club button handler to also update aim
src = src.replace(
    "$('clubBtn').onclick=function(){\nG.ci_=(G.ci_+1)%4;G.putting=G.ci_===3;\nupdHUD();AUD.play('click')};",
    "$('clubBtn').onclick=function(){\nG.ci_=(G.ci_+1)%4;G.putting=G.ci_===3;\nupdHUD();updAim(70);AUD.play('click')};"
)

# 9. Version update
src = src.replace("console.log('Park Golf Pro v10 initialized')", "console.log('Park Golf Pro v11 initialized')")

with open('/home/user/webapp/index.html', 'w', encoding='utf-8') as f:
    f.write(src)

# Also update sw.js
with open('/home/user/webapp/sw.js', 'r') as f:
    sw = f.read()
sw = sw.replace('parkgolf-v90', 'parkgolf-v11')
with open('/home/user/webapp/sw.js', 'w') as f:
    f.write(sw)

print("Golf King style upgrade complete!")
print(f"File size: {len(src)} bytes")
