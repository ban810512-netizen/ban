#!/usr/bin/env python3
"""Park Golf Pro v7 - Photorealistic Three.js game with procedural textures."""

html_part1 = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1a5c1a">
<title>파크골프 프로</title>
<link rel="manifest" href="manifest.json">
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent;user-select:none}
html,body{width:100%;height:100%;overflow:hidden;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;color:#fff;touch-action:none;background:#000}
#gameContainer{position:fixed;inset:0;z-index:0}
canvas{display:block}
.scr{position:fixed;inset:0;z-index:50;display:none;flex-direction:column;align-items:center;justify-content:center;padding:20px;overflow-y:auto}
.scr.on{display:flex}
#menuScr{background:linear-gradient(160deg,rgba(10,31,10,.95),rgba(20,48,20,.92),rgba(13,27,42,.95));gap:14px}
#menuScr h1{font-size:42px;font-weight:900;background:linear-gradient(135deg,#66bb6a,#fdd835,#fff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-1px}
#menuScr .sub{font-size:11px;color:#66bb6a;letter-spacing:8px;margin:-6px 0 20px;font-weight:300}
#menuScr .pname{font-size:13px;color:#aaa;margin-bottom:8px}
.btn{width:100%;max-width:300px;padding:16px;border-radius:16px;border:none;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;color:#fff;background:rgba(255,255,255,.06);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.08);margin:4px 0;transition:all .15s;letter-spacing:1px}
.btn:active{transform:scale(.96);opacity:.8}
.btn.primary{background:linear-gradient(135deg,#2e7d32,#66bb6a);box-shadow:0 6px 24px rgba(76,175,80,.35);border:none}
#courseScr,#recordScr,#settingScr{background:linear-gradient(160deg,rgba(10,31,10,.97),rgba(13,27,42,.97));justify-content:flex-start;padding-top:max(44px,env(safe-area-inset-top))}
#courseScr h2,#recordScr h2,#settingScr h2{font-size:22px;font-weight:800;margin-bottom:16px}
.courseList{width:100%;max-width:360px;max-height:65vh;overflow-y:auto;-webkit-overflow-scrolling:touch}
.courseItem{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:14px 16px;margin-bottom:8px;cursor:pointer;transition:all .15s}
.courseItem:active{background:rgba(255,255,255,.12);transform:scale(.98)}
.courseItem .cn{font-size:15px;font-weight:700}.courseItem .ci{font-size:11px;color:#999;margin-top:2px}.courseItem .cb{font-size:11px;color:#66bb6a;font-weight:600;margin-top:2px}
.settRow{display:flex;justify-content:space-between;align-items:center;width:100%;max-width:300px;padding:12px 0;border-bottom:1px solid rgba(255,255,255,.06)}
.settRow label{font-size:14px;color:#ccc}
.settRow input[type=text]{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:10px;color:#fff;padding:8px 12px;width:120px;font-size:14px;font-family:inherit}
.settRow input[type=range]{width:120px;accent-color:#66bb6a}
.settRow input[type=checkbox]{width:20px;height:20px;accent-color:#66bb6a}
#hud{position:fixed;top:0;left:0;right:0;z-index:10;pointer-events:none;display:none}
#hud>*{pointer-events:auto}
#hudBar{display:flex;justify-content:space-between;align-items:center;padding:8px 14px;padding-top:max(8px,env(safe-area-inset-top));background:linear-gradient(180deg,rgba(0,0,0,.7),rgba(0,0,0,.25),transparent)}
.hudL,.hudR{display:flex;flex-direction:column;gap:2px}
.hudL{align-items:flex-start}.hudR{align-items:flex-end}
.holeNum{font-size:22px;font-weight:900;color:#fdd835;line-height:1}
.parInfo{font-size:11px;color:#b0b0b0}
.courseName{font-size:10px;color:#888;text-align:center;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.strokeCnt{font-size:14px;font-weight:700}
.distInfo{font-size:14px;font-weight:700;color:#4fc3f7}
.windInfo{font-size:11px;color:#81d4fa}
#clubBtn{position:fixed;top:max(60px,calc(env(safe-area-inset-top)+52px));right:12px;z-index:12;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.18);border-radius:22px;padding:8px 18px;font-size:13px;font-weight:700;cursor:pointer;color:#fff;backdrop-filter:blur(6px);display:none}
#bigMsg{position:fixed;top:28%;left:50%;transform:translate(-50%,-50%);z-index:30;display:none;text-align:center;pointer-events:none}
#bigMsg .bm{font-size:52px;font-weight:900;text-shadow:0 4px 30px rgba(0,0,0,.9),0 0 60px rgba(255,215,0,.3)}
#bigMsg .bs{font-size:16px;color:#fdd835;margin-top:6px;font-weight:600}
@keyframes popIn{0%{transform:translate(-50%,-50%) scale(0) rotate(-8deg);opacity:0}50%{transform:translate(-50%,-50%) scale(1.15) rotate(2deg)}100%{transform:translate(-50%,-50%) scale(1) rotate(0);opacity:1}}
#aimGuide{position:fixed;bottom:185px;left:50%;transform:translateX(-50%);z-index:11;font-size:12px;color:rgba(255,255,255,.35);display:none;text-align:center;pointer-events:none;letter-spacing:4px}
#swingPanel{position:fixed;bottom:0;left:0;width:100%;z-index:20;display:none;flex-direction:column;padding:10px 20px;padding-bottom:max(16px,env(safe-area-inset-bottom));background:linear-gradient(0deg,rgba(0,0,0,.92),rgba(0,0,0,.4),transparent)}
#powerBar{width:100%;height:38px;background:rgba(255,255,255,.05);border-radius:19px;position:relative;overflow:hidden;margin-bottom:8px;border:1px solid rgba(255,255,255,.05)}
#powerFill{height:100%;width:0%;background:linear-gradient(90deg,#43a047 0%,#66bb6a 25%,#fdd835 50%,#ff9800 75%,#e53935 100%);border-radius:19px}
#powerMark{position:absolute;top:-2px;height:42px;width:5px;background:#fff;border-radius:3px;box-shadow:0 0 14px rgba(255,255,255,.9),0 0 6px #fff;left:0%;display:none;z-index:2}
#accBar{width:100%;height:30px;background:rgba(255,255,255,.05);border-radius:15px;position:relative;overflow:hidden;margin-bottom:10px;display:none;border:1px solid rgba(255,255,255,.05)}
#accZone{position:absolute;left:28%;width:44%;height:100%;background:rgba(76,175,80,.15);border-left:2px solid rgba(76,175,80,.3);border-right:2px solid rgba(76,175,80,.3)}
#accPerfect{position:absolute;left:45%;width:10%;height:100%;background:rgba(253,216,53,.12);border-left:2px solid rgba(253,216,53,.25);border-right:2px solid rgba(253,216,53,.25)}
#accNeedle{position:absolute;top:-1px;height:32px;width:5px;background:#ff5722;border-radius:3px;box-shadow:0 0 12px rgba(255,87,34,.9);left:0%;z-index:2}
#swingBtn{width:100%;padding:18px;border:none;border-radius:20px;font-size:22px;font-weight:900;cursor:pointer;font-family:inherit;background:linear-gradient(135deg,#2e7d32,#43a047);color:#fff;box-shadow:0 6px 24px rgba(76,175,80,.4);letter-spacing:4px}
#swingBtn:active{transform:scale(.97)}
#puttInfo{position:fixed;bottom:195px;left:14px;z-index:12;display:none;background:rgba(0,0,0,.6);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:8px 14px;font-size:12px;backdrop-filter:blur(6px)}
#flyover{position:fixed;inset:0;z-index:25;display:none;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:70px;pointer-events:none}
#flyover>*{pointer-events:auto}
.flyHole{font-size:64px;font-weight:900;text-shadow:0 4px 30px rgba(0,0,0,.8);line-height:1}
.flyName{font-size:13px;color:#ccc;margin-top:6px}
.flyInfo{font-size:20px;font-weight:700;color:#fdd835;margin-top:8px;margin-bottom:18px}
.flyProgWrap{width:55%;max-width:220px;height:3px;background:rgba(255,255,255,.1);border-radius:2px;margin-bottom:18px;overflow:hidden}
.flyProgBar{height:100%;background:linear-gradient(90deg,#66bb6a,#fdd835);width:0%}
.flySkip{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.18);color:#fff;padding:8px 28px;border-radius:22px;font-size:13px;cursor:pointer;font-family:inherit;backdrop-filter:blur(6px)}
#scoreScr,#resultScr{background:rgba(0,0,0,.94);z-index:40;gap:12px;backdrop-filter:blur(16px)}
#scoreScr h2,#resultScr h2{font-size:22px;font-weight:800}
.stbl{border-collapse:collapse;font-size:12px;width:100%;max-width:360px}
.stbl th,.stbl td{border:1px solid rgba(255,255,255,.06);padding:6px 4px;text-align:center}
.stbl th{background:rgba(255,255,255,.03);font-size:10px;color:#999;font-weight:600}
.un{color:#66bb6a;font-weight:700}.ov{color:#ef5350;font-weight:700}
#loading{position:fixed;inset:0;z-index:100;background:#0a1f0a;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;transition:opacity .5s}
#loading .spinner{width:40px;height:40px;border:3px solid rgba(255,255,255,.1);border-top:3px solid #66bb6a;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#loading p{color:#66bb6a;font-size:13px;letter-spacing:2px}
</style>
</head>
<body>
<div id="loading"><div class="spinner"></div><p>LOADING...</p></div>
<div id="gameContainer"></div>
<div id="hud">
<div id="hudBar">
<div class="hudL"><span class="holeNum" id="hHole">H1</span><span class="parInfo" id="hPar">Par 3</span></div>
<span class="courseName" id="hCourse"></span>
<div class="hudR"><span class="strokeCnt" id="hStrokes">0</span><span class="distInfo" id="hDist"></span><span class="windInfo" id="hWind"></span></div>
</div>
</div>
<div id="clubBtn">Driver</div>
<div id="bigMsg"><div class="bm"></div><div class="bs"></div></div>
<div id="aimGuide">DRAG TO AIM</div>
<div id="swingPanel">
<div id="powerBar"><div id="powerFill"></div><div id="powerMark"></div></div>
<div id="accBar"><div id="accZone"></div><div id="accPerfect"></div><div id="accNeedle"></div></div>
<button id="swingBtn">SWING</button>
</div>
<div id="puttInfo"></div>
<div id="flyover">
<div class="flyHole" id="flyHole"></div>
<div class="flyName" id="flyName"></div>
<div class="flyInfo" id="flyInfo"></div>
<div class="flyProgWrap"><div class="flyProgBar" id="flyProg"></div></div>
<button class="flySkip" id="flySkip">SKIP</button>
</div>
<div id="scoreScr" class="scr">
<h2>Scorecard</h2>
<div id="scName" style="font-size:13px;color:#aaa;margin-bottom:8px"></div>
<table id="scTable" class="stbl"></table>
<div id="scTotal" style="margin-top:8px;font-size:14px"></div>
<button class="btn primary" id="scNext" style="margin-top:12px">Next Hole</button>
</div>
<div id="resultScr" class="scr">
<h2>Round Complete</h2>
<div id="rsName" style="font-size:14px;margin-bottom:4px"></div>
<table id="rsTable" class="stbl"></table>
<div id="rsTotal" style="margin-top:8px;font-size:14px"></div>
<div id="rsRank" style="font-size:28px;margin:10px 0"></div>
<button class="btn primary" id="rsMenu">Main Menu</button>
</div>
<div id="menuScr" class="scr on">
<h1>PARK GOLF</h1>
<p class="sub">PARK GOLF PRO</p>
<p class="pname" id="menuPlayer"></p>
<button class="btn primary" id="btnPlay">PLAY</button>
<button class="btn" id="btnPractice">PRACTICE</button>
<button class="btn" id="btnRecords">RECORDS</button>
<button class="btn" id="btnSettings">SETTINGS</button>
</div>
<div id="courseScr" class="scr">
<h2>Select Course</h2>
<div class="courseList" id="courseList"></div>
<button class="btn" id="courseBack">Back</button>
</div>
<div id="recordScr" class="scr">
<h2>Records</h2>
<div id="recordList" style="width:100%;max-width:360px;max-height:65vh;overflow-y:auto"></div>
<button class="btn" id="recordBack">Back</button>
</div>
<div id="settingScr" class="scr">
<h2>Settings</h2>
<div class="settRow"><label>Name</label><input id="setName" type="text" maxlength="10"></div>
<div class="settRow"><label>Volume</label><input id="setVol" type="range" min="0" max="100"></div>
<div class="settRow"><label>Vibrate</label><input id="setVib" type="checkbox" checked></div>
<button class="btn primary" id="setSave" style="margin-top:14px">Save</button>
<button class="btn" id="setBack">Back</button>
</div>

<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js"}}
</script>
<script type="module">
import * as THREE from 'three';
'''

js_code = r'''
// ══════════════════════════════════════════════════════════════════
// PARK GOLF PRO v7 — Photorealistic Three.js WebGL
// ══════════════════════════════════════════════════════════════════

// ─── SEEDED RNG ─────────────────────────────────────────────
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

// ─── COURSE DATA ────────────────────────────────────────────
const COURSES=[
{name:"일산 킨텍스",city:"고양",par:[3,4,3,5,3,4,3,4,3],dist:[32,58,28,82,35,65,30,55,25],theme:"plains",wind:1.2,trees:"mixed",water:[4,7]},
{name:"제주 서귀포",city:"서귀포",par:[3,3,4,3,5,4,3,4,3],dist:[30,35,62,28,78,55,32,60,26],theme:"coastal",wind:1.8,trees:"palm",water:[2,5,8]},
{name:"부산 해운대",city:"부산",par:[4,3,3,5,3,4,3,3,4],dist:[52,30,28,85,33,60,25,35,58],theme:"coastal",wind:1.5,trees:"mixed",water:[3,6]},
{name:"강릉 경포대",city:"강릉",par:[3,4,3,4,5,3,3,4,3],dist:[28,55,32,60,80,30,27,58,24],theme:"forest",wind:1.0,trees:"dense",water:[5]},
{name:"남해 독일마을",city:"남해",par:[3,3,5,4,3,4,3,3,4],dist:[25,30,75,58,32,62,28,33,55],theme:"hills",wind:1.3,trees:"mixed",water:[3,7]},
{name:"순천만 에코",city:"순천",par:[4,3,3,4,3,5,4,3,3],dist:[55,28,32,60,30,82,58,25,30],theme:"wetland",wind:1.1,trees:"sparse",water:[1,3,6,8]},
{name:"춘천 의암호",city:"춘천",par:[3,4,3,3,5,4,3,4,3],dist:[30,58,25,32,78,55,28,62,27],theme:"lake",wind:0.9,trees:"dense",water:[2,5,7]},
{name:"경주 보문",city:"경주",par:[4,3,4,3,3,5,3,4,3],dist:[52,30,58,28,35,80,25,62,30],theme:"plains",wind:1.0,trees:"mixed",water:[4,6]},
{name:"여수 엑스포",city:"여수",par:[3,3,4,5,3,3,4,3,4],dist:[28,32,55,78,30,25,60,33,58],theme:"coastal",wind:1.6,trees:"sparse",water:[2,4,8]},
{name:"평창 알펜시아",city:"평창",par:[3,5,3,4,3,4,3,3,4],dist:[25,80,30,62,28,58,32,27,55],theme:"mountain",wind:1.4,trees:"pine",water:[3]}
];
const CLUBS=[
{name:"Driver",maxDist:85,loft:12,spin:0.3},
{name:"Wood",maxDist:60,loft:18,spin:0.5},
{name:"Iron",maxDist:40,loft:28,spin:0.8},
{name:"Putter",maxDist:18,loft:4,spin:0.1}
];
const SCORE_NAMES={'-4':'Condor!','-3':'Albatross!','-2':'Eagle!','-1':'Birdie!','0':'Par','1':'Bogey','2':'D.Bogey','3':'T.Bogey'};

// ─── STORAGE ────────────────────────────────────────────────
const STO={_k:'pg7',_d:null,
  df(){return{name:'Player',vol:80,vib:true,records:[]}},
  load(){try{const s=localStorage.getItem(this._k);this._d=s?JSON.parse(s):this.df()}catch(e){this._d=this.df()}return this._d},
  save(){try{localStorage.setItem(this._k,JSON.stringify(this._d))}catch(e){}},
  get d(){if(!this._d)this.load();return this._d}
};

// ─── AUDIO ──────────────────────────────────────────────────
const AUD={ctx:null,vol:0.8,
  init(){if(this.ctx)return;this.ctx=new(window.AudioContext||window.webkitAudioContext)()},
  resume(){if(this.ctx&&this.ctx.state==='suspended')this.ctx.resume()},
  play(t){
    if(!this.ctx)return;this.resume();const now=this.ctx.currentTime;
    const g=this.ctx.createGain();g.connect(this.ctx.destination);
    if(t==='hit'){
      const o=this.ctx.createOscillator();o.type='sine';o.frequency.setValueAtTime(900,now);
      o.frequency.exponentialRampToValueAtTime(150,now+0.18);
      g.gain.setValueAtTime(this.vol*0.5,now);g.gain.exponentialRampToValueAtTime(0.001,now+0.22);
      o.connect(g);o.start(now);o.stop(now+0.22);
      const b=this.ctx.createBufferSource();const buf=this.ctx.createBuffer(1,this.ctx.sampleRate*0.03,this.ctx.sampleRate);
      const d=buf.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,6);
      b.buffer=buf;const g2=this.ctx.createGain();g2.gain.value=this.vol*0.7;b.connect(g2);g2.connect(this.ctx.destination);b.start(now)
    }else if(t==='putt'){
      const o=this.ctx.createOscillator();o.type='sine';o.frequency.value=500;
      g.gain.setValueAtTime(this.vol*0.3,now);g.gain.exponentialRampToValueAtTime(0.001,now+0.08);
      o.connect(g);o.start(now);o.stop(now+0.08)
    }else if(t==='hole'){
      [523,659,784,1047].forEach((f,i)=>{const o=this.ctx.createOscillator();o.type='sine';o.frequency.value=f;
        const gn=this.ctx.createGain();gn.gain.setValueAtTime(0,now+i*0.1);
        gn.gain.linearRampToValueAtTime(this.vol*0.35,now+i*0.1+0.02);
        gn.gain.exponentialRampToValueAtTime(0.001,now+i*0.1+0.4);
        o.connect(gn);gn.connect(this.ctx.destination);o.start(now+i*0.1);o.stop(now+i*0.1+0.4)})
    }else if(t==='splash'){
      const b=this.ctx.createBufferSource();const buf=this.ctx.createBuffer(1,this.ctx.sampleRate*0.5,this.ctx.sampleRate);
      const d=buf.getChannelData(0);for(let i=0;i<d.length;i++){const tt=i/this.ctx.sampleRate;d[i]=(Math.random()*2-1)*Math.exp(-tt*6)*0.6}
      b.buffer=buf;g.gain.value=this.vol*0.5;b.connect(g);b.start(now)
    }else if(t==='bounce'){
      const o=this.ctx.createOscillator();o.type='sine';o.frequency.setValueAtTime(350,now);
      o.frequency.exponentialRampToValueAtTime(80,now+0.06);g.gain.setValueAtTime(this.vol*0.2,now);
      g.gain.exponentialRampToValueAtTime(0.001,now+0.08);o.connect(g);o.start(now);o.stop(now+0.08)
    }else if(t==='ob'){
      const o=this.ctx.createOscillator();o.type='square';o.frequency.value=180;
      g.gain.setValueAtTime(this.vol*0.3,now);g.gain.exponentialRampToValueAtTime(0.001,now+0.35);
      o.connect(g);o.start(now);o.stop(now+0.35)
    }
  }
};
function vibrate(ms){if(STO.d.vib&&navigator.vibrate)navigator.vibrate(ms)}

// ─── DOM ────────────────────────────────────────────────────
const $=id=>document.getElementById(id);
const EL={};
['hud','hudBar','hHole','hPar','hCourse','hStrokes','hDist','hWind','clubBtn',
'bigMsg','aimGuide','swingPanel','powerFill','powerMark','accBar','accNeedle','swingBtn','puttInfo',
'flyover','flyHole','flyName','flyInfo','flyProg','flySkip',
'scoreScr','scName','scTable','scTotal','scNext',
'resultScr','rsName','rsTable','rsTotal','rsRank','rsMenu',
'menuScr','menuPlayer','btnPlay','btnPractice','btnRecords','btnSettings',
'courseScr','courseList','courseBack',
'recordScr','recordList','recordBack',
'settingScr','setName','setVol','setVib','setSave','setBack',
'gameContainer','loading'].forEach(id=>{EL[id]=$(id)});

// ─── PROCEDURAL TEXTURES ────────────────────────────────────
function makeGrassTexture(baseR,baseG,baseB,detail){
  const sz=512,c=document.createElement('canvas');c.width=c.height=sz;
  const ctx=c.getContext('2d');
  // base gradient
  const grd=ctx.createLinearGradient(0,0,sz,sz);
  grd.addColorStop(0,`rgb(${baseR-10},${baseG-5},${baseB})`);
  grd.addColorStop(0.5,`rgb(${baseR},${baseG},${baseB})`);
  grd.addColorStop(1,`rgb(${baseR+8},${baseG+5},${baseB-3})`);
  ctx.fillStyle=grd;ctx.fillRect(0,0,sz,sz);
  // noise
  for(let i=0;i<8000;i++){
    const x=Math.random()*sz,y=Math.random()*sz;
    const v=Math.random()*20-10;
    ctx.fillStyle=`rgba(${baseR+v},${baseG+v+5},${baseB+v},0.4)`;
    ctx.fillRect(x,y,2,2);
  }
  // grass blades
  if(detail){
    ctx.lineWidth=1;
    for(let i=0;i<3000;i++){
      const x=Math.random()*sz,y=Math.random()*sz;
      const h=3+Math.random()*8;
      const lean=(Math.random()-0.5)*4;
      const bright=Math.floor(Math.random()*40-20);
      ctx.strokeStyle=`rgba(${baseR+bright-10},${baseG+bright+15},${baseB+bright-5},0.5)`;
      ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+lean,y-h);ctx.stroke();
    }
  }
  const tex=new THREE.CanvasTexture(c);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
  tex.repeat.set(8,8);
  tex.colorSpace=THREE.SRGBColorSpace;
  return tex;
}

function makeSandTexture(){
  const sz=256,c=document.createElement('canvas');c.width=c.height=sz;
  const ctx=c.getContext('2d');
  ctx.fillStyle='#e0c878';ctx.fillRect(0,0,sz,sz);
  for(let i=0;i<12000;i++){
    const x=Math.random()*sz,y=Math.random()*sz;
    const v=Math.random()*30-15;
    ctx.fillStyle=`rgba(${224+v},${200+v},${120+v},0.5)`;
    ctx.fillRect(x,y,1.5,1.5);
  }
  const tex=new THREE.CanvasTexture(c);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(3,3);
  tex.colorSpace=THREE.SRGBColorSpace;
  return tex;
}

function makeWaterNormalMap(){
  const sz=256,c=document.createElement('canvas');c.width=c.height=sz;
  const ctx=c.getContext('2d');
  ctx.fillStyle='rgb(128,128,255)';ctx.fillRect(0,0,sz,sz);
  for(let i=0;i<2000;i++){
    const x=Math.random()*sz,y=Math.random()*sz;
    const r=128+Math.floor((Math.random()-0.5)*30);
    const g=128+Math.floor((Math.random()-0.5)*30);
    ctx.fillStyle=`rgb(${r},${g},255)`;
    ctx.beginPath();ctx.arc(x,y,1+Math.random()*3,0,Math.PI*2);ctx.fill();
  }
  const tex=new THREE.CanvasTexture(c);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(4,4);
  return tex;
}

function makeDirtTexture(){
  const sz=256,c=document.createElement('canvas');c.width=c.height=sz;
  const ctx=c.getContext('2d');
  ctx.fillStyle='#8B7355';ctx.fillRect(0,0,sz,sz);
  for(let i=0;i<6000;i++){
    const x=Math.random()*sz,y=Math.random()*sz;
    const v=Math.random()*30-15;
    ctx.fillStyle=`rgba(${139+v},${115+v},${85+v},0.5)`;
    ctx.fillRect(x,y,2,2);
  }
  const tex=new THREE.CanvasTexture(c);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;tex.repeat.set(4,4);
  tex.colorSpace=THREE.SRGBColorSpace;
  return tex;
}

function makeBarkTexture(){
  const sz=128,c=document.createElement('canvas');c.width=sz;c.height=sz*2;
  const ctx=c.getContext('2d');
  ctx.fillStyle='#5a3a1a';ctx.fillRect(0,0,sz,sz*2);
  for(let y=0;y<sz*2;y+=3){
    ctx.strokeStyle=`rgba(${60+Math.random()*40},${30+Math.random()*20},${10+Math.random()*15},0.6)`;
    ctx.lineWidth=1+Math.random()*2;
    ctx.beginPath();ctx.moveTo(0,y+Math.random()*2);
    ctx.lineTo(sz,y+Math.random()*2);ctx.stroke();
  }
  const tex=new THREE.CanvasTexture(c);
  tex.wrapS=tex.wrapT=THREE.RepeatWrapping;
  tex.colorSpace=THREE.SRGBColorSpace;
  return tex;
}

// ─── THREE.JS SETUP ─────────────────────────────────────────
let scene,camera,renderer,clock;

function initThree(){
  scene=new THREE.Scene();
  camera=new THREE.PerspectiveCamera(50,window.innerWidth/window.innerHeight,0.1,600);
  camera.position.set(0,8,15);

  renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});
  renderer.setSize(window.innerWidth,window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.15;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  EL.gameContainer.appendChild(renderer.domElement);

  // Sun
  const sun=new THREE.DirectionalLight(0xfff0d0,2.5);
  sun.position.set(50,80,40);
  sun.castShadow=true;
  sun.shadow.mapSize.width=2048;sun.shadow.mapSize.height=2048;
  sun.shadow.camera.near=1;sun.shadow.camera.far=250;
  sun.shadow.camera.left=-80;sun.shadow.camera.right=80;
  sun.shadow.camera.top=80;sun.shadow.camera.bottom=-80;
  sun.shadow.bias=-0.0005;sun.shadow.normalBias=0.02;
  scene.add(sun);scene._sun=sun;

  scene.add(new THREE.AmbientLight(0x5577aa,0.6));
  scene.add(new THREE.HemisphereLight(0x88bbee,0x445522,0.8));

  clock=new THREE.Clock();
  window.addEventListener('resize',()=>{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
  });
}

// ─── MATERIALS ──────────────────────────────────────────────
let MAT={};
function initMaterials(){
  const fairwayTex=makeGrassTexture(60,140,50,true);
  const greenTex=makeGrassTexture(50,165,55,true);
  const roughTex=makeGrassTexture(75,115,45,true);
  const bgTex=makeGrassTexture(70,130,55,false);
  const sandTex=makeSandTexture();
  const dirtTex=makeDirtTexture();
  const barkTex=makeBarkTexture();
  const waterNorm=makeWaterNormalMap();

  MAT={
    fairway:new THREE.MeshStandardMaterial({map:fairwayTex,roughness:0.85,metalness:0}),
    green:new THREE.MeshStandardMaterial({map:greenTex,roughness:0.65,metalness:0}),
    rough:new THREE.MeshStandardMaterial({map:roughTex,roughness:0.95,metalness:0}),
    bg:new THREE.MeshStandardMaterial({map:bgTex,roughness:0.95,metalness:0}),
    tee:new THREE.MeshStandardMaterial({map:fairwayTex,roughness:0.7,metalness:0}),
    sand:new THREE.MeshStandardMaterial({map:sandTex,roughness:0.95,metalness:0}),
    dirt:new THREE.MeshStandardMaterial({map:dirtTex,roughness:0.9,metalness:0}),
    water:new THREE.MeshStandardMaterial({color:0x1a6a8a,roughness:0.05,metalness:0.4,transparent:true,opacity:0.8,normalMap:waterNorm,normalScale:new THREE.Vector2(0.3,0.3)}),
    bark:new THREE.MeshStandardMaterial({map:barkTex,roughness:0.9,metalness:0}),
    leaves:new THREE.MeshStandardMaterial({color:0x2a7a2a,roughness:0.75,metalness:0,side:THREE.DoubleSide}),
    leavesDk:new THREE.MeshStandardMaterial({color:0x1a5a1a,roughness:0.8,metalness:0,side:THREE.DoubleSide}),
    palm:new THREE.MeshStandardMaterial({color:0x2a8a2a,roughness:0.7,metalness:0,side:THREE.DoubleSide}),
    pine:new THREE.MeshStandardMaterial({color:0x1a5a28,roughness:0.8,metalness:0}),
    flag:new THREE.MeshStandardMaterial({color:0xee1111,roughness:0.4,metalness:0.1,side:THREE.DoubleSide}),
    pole:new THREE.MeshStandardMaterial({color:0xdddddd,roughness:0.2,metalness:0.7}),
    ball:new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.2,metalness:0.05,envMapIntensity:0.5}),
    obW:new THREE.MeshStandardMaterial({color:0xffffff,roughness:0.6}),
    obR:new THREE.MeshStandardMaterial({color:0xff0000,roughness:0.5}),
    path:new THREE.MeshStandardMaterial({map:dirtTex,roughness:0.85,metalness:0,color:0xc8b896}),
    rock:new THREE.MeshStandardMaterial({color:0x777777,roughness:0.9,metalness:0.1}),
    flower:[
      new THREE.MeshStandardMaterial({color:0xff5588,roughness:0.6}),
      new THREE.MeshStandardMaterial({color:0xffcc22,roughness:0.6}),
      new THREE.MeshStandardMaterial({color:0xcc66ff,roughness:0.6}),
      new THREE.MeshStandardMaterial({color:0xff8844,roughness:0.6}),
    ],
    mountain:new THREE.MeshStandardMaterial({color:0x6a8a5a,roughness:0.95,metalness:0}),
    snow:new THREE.MeshStandardMaterial({color:0xeeeeff,roughness:0.7,metalness:0.1}),
    cloud:new THREE.MeshStandardMaterial({color:0xffffff,roughness:1,metalness:0,transparent:true,opacity:0.65}),
  };
}

// ─── SKYDOME ────────────────────────────────────────────────
function buildSky(theme){
  const colors={
    plains:['#5b9bd5','#87CEEB','#b5d9e8'],
    coastal:['#4a8ab5','#7ec8e3','#c5dde8'],
    forest:['#5a9ab0','#6eb5c0','#a8d0c8'],
    hills:['#6a9ac0','#8ecae6','#c5dde8'],
    wetland:['#5a9a88','#80c5a8','#b5d8c0'],
    lake:['#4a7ab0','#7bbcd5','#aad0e0'],
    mountain:['#7090b0','#9dc5e0','#ccdde8']
  };
  const cols=colors[theme]||colors.plains;
  
  // Skydome
  const skyGeo=new THREE.SphereGeometry(280,32,15,0,Math.PI*2,0,Math.PI*0.5);
  const skyC=document.createElement('canvas');skyC.width=64;skyC.height=256;
  const skyCtx=skyC.getContext('2d');
  const grd=skyCtx.createLinearGradient(0,0,0,256);
  grd.addColorStop(0,cols[0]);grd.addColorStop(0.4,cols[1]);grd.addColorStop(0.85,cols[2]);grd.addColorStop(1,'#f0e8d0');
  skyCtx.fillStyle=grd;skyCtx.fillRect(0,0,64,256);
  const skyTex=new THREE.CanvasTexture(skyC);
  skyTex.colorSpace=THREE.SRGBColorSpace;
  const skyMat=new THREE.MeshBasicMaterial({map:skyTex,side:THREE.BackSide,fog:false});
  const sky=new THREE.Mesh(skyGeo,skyMat);
  sky.position.y=-5;
  return sky;
}

// ─── COURSE BUILDER ─────────────────────────────────────────
let courseGroup=null;
let greenCenter=new THREE.Vector3(),greenRadius=0;
let teePos=new THREE.Vector3(),holePos=new THREE.Vector3();
let flagMesh=null;
let bunkers=[],waterAreas=[];
let obBounds={minX:-30,maxX:30,minZ:-100,maxZ:10};
let fairwayPath=[];
let terrainData=null;

function buildCourse(ci,hi){
  if(courseGroup){scene.remove(courseGroup);courseGroup.traverse(c=>{if(c.geometry)c.geometry.dispose();})}
  courseGroup=new THREE.Group();
  bunkers=[];waterAreas=[];fairwayPath=[];

  const C=COURSES[ci],dist=C.dist[hi],par=C.par[hi];
  const hasWater=C.water&&C.water.includes(hi+1);
  const rng=mulberry32(ci*100+hi);

  // Sky
  const sky=buildSky(C.theme);
  courseGroup.add(sky);

  // Fog
  const fogC=new THREE.Color(C.theme==='coastal'?0x7ec8e3:C.theme==='forest'?0x6eb5c0:C.theme==='mountain'?0x9dc5e0:0x87CEEB);
  scene.fog=new THREE.FogExp2(fogC,0.0025);
  scene.background=fogC;

  // ── TERRAIN ──
  const terrW=200,terrH=200,terrSeg=80;
  const terrGeo=new THREE.PlaneGeometry(terrW,terrH,terrSeg,terrSeg);
  terrGeo.rotateX(-Math.PI/2);
  const pos=terrGeo.attributes.position;
  terrainData={w:terrW,h:terrH,seg:terrSeg,data:new Float32Array(pos.count)};
  
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i),z=pos.getZ(i);
    // rolling hills
    let y=Math.sin(x*0.05)*0.8+Math.cos(z*0.04)*0.6+Math.sin((x+z)*0.03)*0.4;
    // flatten fairway area
    const closestFwDist=100; // will refine below
    pos.setY(i,y);
    terrainData.data[i]=y;
  }
  
  // Build fairway path first to know where to flatten
  const numSeg=16;
  const curveAmt=(rng()-0.5)*dist*0.2;
  const midCurve=(rng()-0.5)*dist*0.12;
  for(let i=0;i<=numSeg;i++){
    const t=i/numSeg;
    const z=-t*dist;
    const x=Math.sin(t*Math.PI)*curveAmt+Math.sin(t*Math.PI*2)*midCurve*0.3;
    const w=3.5+Math.sin(t*Math.PI)*2+(par>=4?1.5:0);
    fairwayPath.push({x,z,w});
  }
  
  // Flatten terrain near fairway
  for(let i=0;i<pos.count;i++){
    const px=pos.getX(i),pz=pos.getZ(i);
    let minDist=Infinity;
    for(const fp of fairwayPath){
      const d=Math.sqrt((px-fp.x)**2+(pz-fp.z)**2);
      if(d<minDist)minDist=d;
    }
    const flatR=8;
    if(minDist<flatR){
      const factor=minDist/flatR;
      const curY=pos.getY(i);
      pos.setY(i,curY*factor*factor);
      terrainData.data[i]=curY*factor*factor;
    }
  }
  terrGeo.computeVertexNormals();

  // Paint terrain with vertex colors
  const colors=new Float32Array(pos.count*3);
  const fwColor=new THREE.Color(0x3a8c35);
  const roughColor=new THREE.Color(0x5a7a38);
  const bgColor=new THREE.Color(0x5a9a48);
  for(let i=0;i<pos.count;i++){
    const px=pos.getX(i),pz=pos.getZ(i);
    let minDist=Infinity,nearW=5;
    for(const fp of fairwayPath){
      const d=Math.sqrt((px-fp.x)**2+(pz-fp.z)**2);
      if(d<minDist){minDist=d;nearW=fp.w}
    }
    let col;
    if(minDist<nearW)col=fwColor;
    else if(minDist<nearW+3)col=roughColor;
    else col=bgColor;
    colors[i*3]=col.r;colors[i*3+1]=col.g;colors[i*3+2]=col.b;
  }
  terrGeo.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
  
  const terrMat=new THREE.MeshStandardMaterial({
    vertexColors:true,roughness:0.85,metalness:0,
    map:makeGrassTexture(60,130,48,true)
  });
  const terrain=new THREE.Mesh(terrGeo,terrMat);
  terrain.position.set(0,0,-dist/2);
  terrain.receiveShadow=true;
  terrain.castShadow=false;
  courseGroup.add(terrain);

  // ── Tee Box ──
  teePos.set(0,getTerrainY(0,0,dist),0);
  const teeGeo=new THREE.BoxGeometry(3.5,0.06,4);
  const tee=new THREE.Mesh(teeGeo,MAT.tee);
  tee.position.set(0,teePos.y+0.03,0);tee.receiveShadow=true;
  courseGroup.add(tee);
  // tee markers
  const tmGeo=new THREE.SphereGeometry(0.08,8,6);
  [-1,1].forEach(s=>{const m=new THREE.Mesh(tmGeo,MAT.flag);m.position.set(s*0.9,teePos.y+0.1,1);courseGroup.add(m)});

  // ── Fairway overlay strips ──
  const fwVerts=[],fwIdx=[],fwUvs=[];
  for(let i=0;i<fairwayPath.length;i++){
    const p=fairwayPath[i];
    const yl=getTerrainY(p.x-p.w,p.z,dist);
    const yr=getTerrainY(p.x+p.w,p.z,dist);
    fwVerts.push(p.x-p.w,yl+0.02,p.z, p.x+p.w,yr+0.02,p.z);
    fwUvs.push(0,i/fairwayPath.length, 1,i/fairwayPath.length);
    if(i>0){const b=(i-1)*2;fwIdx.push(b,b+1,b+2,b+1,b+3,b+2)}
  }
  const fwGeo=new THREE.BufferGeometry();
  fwGeo.setAttribute('position',new THREE.Float32BufferAttribute(fwVerts,3));
  fwGeo.setAttribute('uv',new THREE.Float32BufferAttribute(fwUvs,2));
  fwGeo.setIndex(fwIdx);fwGeo.computeVertexNormals();
  const fwMesh=new THREE.Mesh(fwGeo,MAT.fairway);
  fwMesh.receiveShadow=true;courseGroup.add(fwMesh);

  // ── Green ──
  const lastFw=fairwayPath[fairwayPath.length-1];
  greenRadius=3.5+par*0.8;
  greenCenter.set(lastFw.x,getTerrainY(lastFw.x,lastFw.z-greenRadius*0.3,dist),lastFw.z-greenRadius*0.3);
  const gGeo=new THREE.CircleGeometry(greenRadius,36);
  const gMesh=new THREE.Mesh(gGeo,MAT.green);
  gMesh.rotation.x=-Math.PI/2;
  gMesh.position.set(greenCenter.x,greenCenter.y+0.025,greenCenter.z);
  gMesh.receiveShadow=true;courseGroup.add(gMesh);
  
  // green fringe
  const frGeo=new THREE.RingGeometry(greenRadius,greenRadius+1.0,36);
  const frMesh=new THREE.Mesh(frGeo,MAT.fairway);
  frMesh.rotation.x=-Math.PI/2;frMesh.position.set(greenCenter.x,greenCenter.y+0.02,greenCenter.z);
  frMesh.receiveShadow=true;courseGroup.add(frMesh);

  // ── Hole & Flag ──
  const hOff=(rng()-0.5)*greenRadius*0.35;
  holePos.set(greenCenter.x+hOff,greenCenter.y,greenCenter.z+(rng()-0.5)*greenRadius*0.35);
  
  const cupGeo=new THREE.CylinderGeometry(0.054,0.054,0.08,16);
  const cupMat=new THREE.MeshStandardMaterial({color:0x111111});
  courseGroup.add(new THREE.Mesh(cupGeo,cupMat).translateX(holePos.x).translateY(holePos.y-0.01).translateZ(holePos.z));
  
  // pole
  const polGeo=new THREE.CylinderGeometry(0.018,0.018,2.2,8);
  const pol=new THREE.Mesh(polGeo,MAT.pole);
  pol.position.set(holePos.x,holePos.y+1.1,holePos.z);pol.castShadow=true;courseGroup.add(pol);
  
  // flag
  const flagPts=[new THREE.Vector2(0,0),new THREE.Vector2(0.8,0.12),new THREE.Vector2(0.8,0.25),new THREE.Vector2(0,0.38)];
  const flagShape=new THREE.Shape(flagPts);
  const fGeo=new THREE.ShapeGeometry(flagShape);
  flagMesh=new THREE.Mesh(fGeo,MAT.flag);
  flagMesh.position.set(holePos.x+0.02,holePos.y+1.82,holePos.z);
  flagMesh.castShadow=true;courseGroup.add(flagMesh);

  // ── Bunkers ──
  const nBnk=par>=4?2+(rng()>0.5?1:0):1;
  for(let b=0;b<nBnk;b++){
    const bT=0.4+rng()*0.4;
    const bFw=fairwayPath[Math.floor(bT*(fairwayPath.length-1))];
    const bSide=rng()>0.5?1:-1;
    const bR=1.5+rng()*1.8;
    const bx=bFw.x+bSide*(bFw.w+rng()*1.5);
    const bz=bFw.z+(rng()-0.5)*4;
    const by=getTerrainY(bx,bz,dist);
    bunkers.push({center:new THREE.Vector3(bx,by,bz),radius:bR});
    
    // sunken sand
    const bGeo=new THREE.CircleGeometry(bR,20);
    const bMesh=new THREE.Mesh(bGeo,MAT.sand);
    bMesh.rotation.x=-Math.PI/2;bMesh.position.set(bx,by-0.08,bz);bMesh.receiveShadow=true;
    courseGroup.add(bMesh);
    
    // raised lip
    const lipGeo=new THREE.TorusGeometry(bR,0.2,6,24);
    const lip=new THREE.Mesh(lipGeo,MAT.dirt);
    lip.rotation.x=-Math.PI/2;lip.position.set(bx,by+0.05,bz);lip.castShadow=true;
    courseGroup.add(lip);
  }

  // ── Water ──
  if(hasWater){
    const wT=0.3+rng()*0.3;
    const wFw=fairwayPath[Math.floor(wT*(fairwayPath.length-1))];
    const wSide=rng()>0.5?1:-1;
    const ww=5+rng()*6,wh=4+rng()*4;
    const wx=wFw.x+wSide*(wFw.w+ww*0.35);
    const wz=wFw.z;
    const wy=getTerrainY(wx,wz,dist)-0.15;
    waterAreas.push({center:new THREE.Vector3(wx,wy,wz),size:{x:ww,z:wh}});
    
    // water surface
    const wGeo=new THREE.PlaneGeometry(ww,wh,8,8);
    const wMesh=new THREE.Mesh(wGeo,MAT.water);
    wMesh.rotation.x=-Math.PI/2;wMesh.position.set(wx,wy,wz);
    wMesh.receiveShadow=true;wMesh.name='water';
    courseGroup.add(wMesh);
    
    // edge decoration: reeds, rocks
    for(let r=0;r<12;r++){
      const a=rng()*Math.PI*2;
      const rad=Math.max(ww,wh)*0.5+rng()*1.0;
      const rx=wx+Math.cos(a)*rad;
      const rz=wz+Math.sin(a)*rad*(wh/ww);
      if(rng()>0.4){
        // rock
        const rGeo=new THREE.DodecahedronGeometry(0.2+rng()*0.3,0);
        const rock=new THREE.Mesh(rGeo,MAT.rock);
        const sc=0.5+rng();rock.scale.set(sc,sc*0.4,sc);
        rock.position.set(rx,wy+0.1,rz);rock.rotation.set(rng(),rng(),rng());
        rock.castShadow=true;courseGroup.add(rock);
      }else{
        // reed cluster
        for(let rd=0;rd<3;rd++){
          const reedGeo=new THREE.CylinderGeometry(0.01,0.015,0.5+rng()*0.5,4);
          const reed=new THREE.Mesh(reedGeo,new THREE.MeshStandardMaterial({color:0x5a7a3a}));
          reed.position.set(rx+(rng()-0.5)*0.2,wy+0.3,rz+(rng()-0.5)*0.2);
          reed.rotation.set((rng()-0.5)*0.2,0,(rng()-0.5)*0.2);
          courseGroup.add(reed);
        }
      }
    }
  }

  // ── TREES ──
  const density={sparse:8,mixed:16,dense:24,palm:10,pine:18};
  const nTrees=density[C.trees]||12;
  for(let t=0;t<nTrees;t++){
    const tz=-(rng()*dist*1.3)-4;
    const side=rng()>0.5?1:-1;
    const tx=side*(5+rng()*30);
    // skip fairway
    let skip=false;
    for(const fp of fairwayPath){if(Math.abs(fp.z-tz)<dist/fairwayPath.length*1.5&&Math.abs(tx-fp.x)<fp.w+2){skip=true;break}}
    if(skip)continue;
    const ty=getTerrainY(tx,tz,dist);
    buildTree(courseGroup,tx,ty,tz,C.trees,rng);
  }
  
  // Background trees (far away, silhouettes)
  for(let t=0;t<30;t++){
    const angle=rng()*Math.PI*2;
    const rad=50+rng()*50;
    const tx=Math.cos(angle)*rad;
    const tz=-dist/2+Math.sin(angle)*rad;
    const ty=getTerrainY(tx,tz,dist);
    buildTree(courseGroup,tx,ty,tz,C.trees,rng,true);
  }

  // ── Cart Path ──
  const cpVerts=[],cpIdx=[];
  for(let i=0;i<fairwayPath.length;i++){
    const p=fairwayPath[i];
    const px=p.x+p.w+3;
    const py1=getTerrainY(px-0.6,p.z,dist);
    const py2=getTerrainY(px+0.6,p.z,dist);
    cpVerts.push(px-0.6,py1+0.01,p.z, px+0.6,py2+0.01,p.z);
    if(i>0){const b=(i-1)*2;cpIdx.push(b,b+1,b+2,b+1,b+3,b+2)}
  }
  const cpGeo=new THREE.BufferGeometry();
  cpGeo.setAttribute('position',new THREE.Float32BufferAttribute(cpVerts,3));
  cpGeo.setIndex(cpIdx);cpGeo.computeVertexNormals();
  courseGroup.add(new THREE.Mesh(cpGeo,MAT.path));

  // ── OB Markers ──
  obBounds={minX:-30,maxX:30,minZ:-(dist+25),maxZ:10};
  const obGeo=new THREE.CylinderGeometry(0.035,0.035,0.8,6);
  const obTopGeo=new THREE.SphereGeometry(0.06,6,4);
  for(let i=0;i<24;i++){
    let mx,mz;
    if(i<6){mx=obBounds.minX;mz=obBounds.minZ+i*(dist+35)/5}
    else if(i<12){mx=obBounds.maxX;mz=obBounds.minZ+(i-6)*(dist+35)/5}
    else if(i<18){mz=obBounds.minZ;mx=obBounds.minX+(i-12)*60/5}
    else{mz=obBounds.maxZ;mx=obBounds.minX+(i-18)*60/5}
    const my=getTerrainY(mx,mz,dist);
    const post=new THREE.Mesh(obGeo,MAT.obW);post.position.set(mx,my+0.4,mz);post.castShadow=true;courseGroup.add(post);
    const top=new THREE.Mesh(obTopGeo,MAT.obR);top.position.set(mx,my+0.82,mz);courseGroup.add(top);
  }

  // ── Flowers & grass tufts ──
  const flGeo=new THREE.SphereGeometry(0.08,5,4);
  for(let f=0;f<40;f++){
    const fz=-(rng()*dist*0.9)-3;
    const fx=(rng()>0.5?1:-1)*(3+rng()*25);
    const fy=getTerrainY(fx,fz,dist);
    const fl=new THREE.Mesh(flGeo,MAT.flower[Math.floor(rng()*4)]);
    fl.position.set(fx,fy+0.08,fz);fl.scale.set(1+rng(),0.6,1+rng());
    courseGroup.add(fl);
  }
  // grass tufts on rough
  const tuftGeo=new THREE.ConeGeometry(0.08,0.25,4);
  for(let g=0;g<60;g++){
    const gz=-(rng()*dist)-2;
    const gx=(rng()>0.5?1:-1)*(4+rng()*20);
    const gy=getTerrainY(gx,gz,dist);
    const tuft=new THREE.Mesh(tuftGeo,MAT.leaves);
    tuft.position.set(gx,gy+0.12,gz);
    tuft.rotation.set((rng()-0.5)*0.3,rng()*Math.PI,(rng()-0.5)*0.3);
    courseGroup.add(tuft);
  }

  // ── Mountains ──
  buildMountains(courseGroup,C.theme,dist,rng);

  // ── Clouds ──
  const clGeo=new THREE.SphereGeometry(1,6,4);
  for(let c=0;c<10;c++){
    const cg=new THREE.Group();
    const nPuffs=3+Math.floor(rng()*3);
    for(let p=0;p<nPuffs;p++){
      const cm=new THREE.Mesh(clGeo,MAT.cloud);
      cm.position.set((rng()-0.5)*4,rng()*0.8,(rng()-0.5)*2);
      cm.scale.set(2+rng()*3,0.5+rng()*0.4,1+rng()*1);
      cg.add(cm);
    }
    cg.position.set((rng()-0.5)*120,35+rng()*25,-dist/2+(rng()-0.5)*100);
    cg._speed=(0.3+rng()*0.5)*(rng()>0.5?1:-1);
    courseGroup.add(cg);
  }

  scene.add(courseGroup);
}

function getTerrainY(x,z,dist){
  const cx=x,cz=z+dist/2;// offset to terrain center
  let y=Math.sin(cx*0.05)*0.8+Math.cos(cz*0.04)*0.6+Math.sin((cx+cz)*0.03)*0.4;
  // flatten near fairway
  let minD=Infinity;
  for(const fp of fairwayPath){const d=Math.sqrt((x-fp.x)**2+(z-fp.z)**2);if(d<minD)minD=d}
  if(minD<8){const f=minD/8;y*=f*f}
  return y;
}

function buildTree(group,x,y,z,type,rng,bg){
  const scale=bg?0.6+rng()*0.4:1;
  const h=(2.5+rng()*3)*scale;
  
  if(type==='palm'){
    const pts=[new THREE.Vector3(0,0,0),new THREE.Vector3(rng()*0.5,h*0.4,rng()*0.3),
      new THREE.Vector3(rng()*0.3,h*0.8,rng()*0.2),new THREE.Vector3(0,h,0)];
    const curve=new THREE.CatmullRomCurve3(pts);
    const trunkGeo=new THREE.TubeGeometry(curve,8,0.08*scale,6);
    const trunk=new THREE.Mesh(trunkGeo,MAT.bark);
    trunk.position.set(x,y,z);trunk.castShadow=true;group.add(trunk);
    for(let f=0;f<7;f++){
      const a=(f/7)*Math.PI*2;
      const shape=new THREE.Shape();
      shape.moveTo(0,0);shape.quadraticCurveTo(1.2*scale,0.25*scale,2.5*scale,0.08*scale);
      shape.quadraticCurveTo(1.2*scale,-0.25*scale,0,0);
      const fGeo=new THREE.ShapeGeometry(shape);
      const frond=new THREE.Mesh(fGeo,MAT.palm);
      frond.position.set(x,y+h,z);frond.rotation.set(-0.6+rng()*0.2,a,0);
      frond.castShadow=true;group.add(frond);
    }
  }else if(type==='pine'){
    const tGeo=new THREE.CylinderGeometry(0.06*scale,0.1*scale,h*0.4,6);
    const trunk=new THREE.Mesh(tGeo,MAT.bark);
    trunk.position.set(x,y+h*0.2,z);trunk.castShadow=true;group.add(trunk);
    for(let l=0;l<4;l++){
      const ly=h*0.35+l*h*0.18;
      const lr=(1.4-l*0.3)*scale;
      const cGeo=new THREE.ConeGeometry(lr,h*0.3,8);
      const cone=new THREE.Mesh(cGeo,MAT.pine);
      cone.position.set(x,y+ly,z);cone.castShadow=true;cone.receiveShadow=true;
      group.add(cone);
    }
  }else{
    // deciduous
    const tGeo=new THREE.CylinderGeometry(0.05*scale,0.1*scale,h*0.5,6);
    const trunk=new THREE.Mesh(tGeo,MAT.bark);
    trunk.position.set(x,y+h*0.25,z);trunk.castShadow=true;group.add(trunk);
    // multi-sphere canopy
    const mat=rng()>0.5?MAT.leaves:MAT.leavesDk;
    const nSpheres=bg?2:3+Math.floor(rng()*2);
    for(let s=0;s<nSpheres;s++){
      const sr=(0.7+rng()*0.6)*scale;
      const sGeo=new THREE.SphereGeometry(sr,8,6);
      const sphere=new THREE.Mesh(sGeo,mat);
      sphere.position.set(x+(rng()-0.5)*0.6*scale,y+h*0.55+rng()*0.6*scale,z+(rng()-0.5)*0.6*scale);
      sphere.scale.set(1,0.65+rng()*0.3,1);
      sphere.castShadow=true;sphere.receiveShadow=true;
      group.add(sphere);
    }
  }
}

function buildMountains(group,theme,dist,rng){
  const mColor=theme==='mountain'?0x7a8a7a:theme==='coastal'?0x5a8a9a:0x5a8a5a;
  const hasSnow=theme==='mountain';
  
  for(let ring=0;ring<2;ring++){
    const mDist=100+ring*50;
    const nPeaks=8+ring*4;
    for(let i=0;i<nPeaks;i++){
      const angle=(i/nPeaks)*Math.PI*1.2-Math.PI*0.1+rng()*0.3;
      const x=Math.sin(angle)*mDist+(rng()-0.5)*20;
      const z=-dist/2-Math.cos(angle)*mDist;
      const h=15+rng()*(ring===0?30:20);
      const w=8+rng()*12;
      
      const mGeo=new THREE.ConeGeometry(w,h,6+Math.floor(rng()*3));
      const mMat=new THREE.MeshStandardMaterial({
        color:new THREE.Color(mColor).offsetHSL(rng()*0.05-0.025,0,rng()*0.1-0.05),
        roughness:0.95,metalness:0,fog:true
      });
      const mountain=new THREE.Mesh(mGeo,mMat);
      mountain.position.set(x,h*0.3,z);
      mountain.rotation.set(0,rng()*Math.PI,0);
      mountain.scale.set(1+rng()*0.3,1,1+rng()*0.3);
      group.add(mountain);
      
      if(hasSnow&&h>25){
        const sGeo=new THREE.ConeGeometry(w*0.3,h*0.15,6);
        const snow=new THREE.Mesh(sGeo,MAT.snow);
        snow.position.set(x,h*0.75,z);group.add(snow);
      }
    }
  }
}

// ─── BALL ───────────────────────────────────────────────────
let ballMesh,ballShadow;
let ballPos=new THREE.Vector3(),ballVel=new THREE.Vector3();
let ballOnGround=true,ballInWater=false,ballOB=false;

function createBall(){
  const geo=new THREE.SphereGeometry(0.021,20,14);
  ballMesh=new THREE.Mesh(geo,MAT.ball);
  ballMesh.castShadow=true;ballMesh.scale.set(3.5,3.5,3.5);
  scene.add(ballMesh);
  const shGeo=new THREE.CircleGeometry(0.15,12);
  const shMat=new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:0.25,depthWrite:false});
  ballShadow=new THREE.Mesh(shGeo,shMat);ballShadow.rotation.x=-Math.PI/2;
  scene.add(ballShadow);
}
function resetBall(x,y,z){
  ballPos.set(x,y,z);ballVel.set(0,0,0);
  ballOnGround=true;ballInWater=false;ballOB=false;updBallMesh();
}
function updBallMesh(){
  if(!ballMesh)return;
  ballMesh.position.set(ballPos.x,ballPos.y+0.075,ballPos.z);
  ballShadow.position.set(ballPos.x,getTerrainY(ballPos.x,ballPos.z,G.dist)+0.01,ballPos.z);
  ballShadow.material.opacity=Math.max(0,0.25-ballPos.y*0.01);
}

// ─── AIM LINE ───────────────────────────────────────────────
let aimLine,aimDot,aimAngle=0;
function createAimLine(){
  const mat=new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:0.5});
  const geo=new THREE.BufferGeometry();
  const pts=new Float32Array(60*3);
  geo.setAttribute('position',new THREE.BufferAttribute(pts,3));
  aimLine=new THREE.Line(geo,mat);scene.add(aimLine);
  
  // dashed segments for better visibility
  const dotGeo=new THREE.SphereGeometry(0.12,8,6);
  const dotMat=new THREE.MeshBasicMaterial({color:0xfdd835,transparent:true,opacity:0.8});
  aimDot=new THREE.Mesh(dotGeo,dotMat);scene.add(aimDot);
}
function updAimLine(power){
  if(!aimLine)return;
  const club=CLUBS[G.clubIdx];
  const maxD=club.maxDist*(power||0.5);
  const dir=new THREE.Vector3(Math.sin(aimAngle),0,-Math.cos(aimAngle));
  const pos=aimLine.geometry.attributes.position.array;
  const steps=20;
  for(let i=0;i<steps;i++){
    const t=i/(steps-1);const d=t*maxD;
    const h=Math.sin(t*Math.PI)*club.loft*0.15*(power||0.5);
    const px=ballPos.x+dir.x*d;
    const pz=ballPos.z+dir.z*d;
    const py=getTerrainY(px,pz,G.dist)+0.15+h;
    pos[i*3]=px;pos[i*3+1]=py;pos[i*3+2]=pz;
  }
  for(let i=steps;i<20;i++){pos[i*3]=pos[(steps-1)*3];pos[i*3+1]=pos[(steps-1)*3+1];pos[i*3+2]=pos[(steps-1)*3+2]}
  aimLine.geometry.attributes.position.needsUpdate=true;
  aimLine.geometry.setDrawRange(0,steps);
  aimDot.position.set(ballPos.x+dir.x*maxD,getTerrainY(ballPos.x+dir.x*maxD,ballPos.z+dir.z*maxD,G.dist)+0.2,ballPos.z+dir.z*maxD);
  aimLine.visible=aimDot.visible=true;
}
function hideAim(){if(aimLine)aimLine.visible=false;if(aimDot)aimDot.visible=false}

// ─── PARTICLES ──────────────────────────────────────────────
let particles=[];
function spawnPtc(pos,n,col,spread,spd){
  for(let i=0;i<n;i++){
    const geo=new THREE.SphereGeometry(0.04+Math.random()*0.06,4,3);
    const mat=new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:1});
    const m=new THREE.Mesh(geo,mat);m.position.copy(pos);scene.add(m);
    particles.push({m,v:new THREE.Vector3((Math.random()-0.5)*spread,Math.random()*spd,(Math.random()-0.5)*spread),life:1,dec:0.5+Math.random()*0.5});
  }
}
function updPtc(dt){
  for(let i=particles.length-1;i>=0;i--){
    const p=particles[i];p.v.y-=9.8*dt;
    p.m.position.add(p.v.clone().multiplyScalar(dt));
    p.life-=p.dec*dt;p.m.material.opacity=Math.max(0,p.life);
    if(p.life<=0){scene.remove(p.m);p.m.geometry.dispose();p.m.material.dispose();particles.splice(i,1)}
  }
}

// ─── CAMERA ─────────────────────────────────────────────────
const CAM={
  tgt:new THREE.Vector3(),cur:new THREE.Vector3(),
  lk:new THREE.Vector3(),clk:new THREE.Vector3(),
  behind(inst){
    const d=new THREE.Vector3(Math.sin(aimAngle),0,-Math.cos(aimAngle));
    this.tgt.set(ballPos.x-d.x*5,ballPos.y+3.2,ballPos.z+d.z*4+3);
    this.lk.set(ballPos.x+d.x*10,ballPos.y,ballPos.z+d.z*-10);
    if(inst){this.cur.copy(this.tgt);this.clk.copy(this.lk);camera.position.copy(this.cur);camera.lookAt(this.clk)}
  },
  follow(){
    const bk=ballVel.clone().normalize().multiplyScalar(-6);bk.y=0;
    this.tgt.set(ballPos.x+bk.x,Math.max(ballPos.y+3,3),ballPos.z+bk.z+2);
    this.lk.copy(ballPos);
  },
  flyover(t,dist){
    const mid=fairwayPath[Math.floor(fairwayPath.length/2)];
    const cx=mid?mid.x:0;
    const z=2+(-(dist+5)-2)*t;
    this.tgt.set(cx+Math.sin(t*Math.PI)*10,10+Math.sin(t*Math.PI)*8,z+8);
    this.lk.set(cx,0,z-8);
  },
  result(){this.tgt.set(holePos.x+3,holePos.y+2.5,holePos.z+3);this.lk.copy(holePos)},
  upd(dt){
    const s=3.5;
    this.cur.lerp(this.tgt,1-Math.exp(-s*dt));
    this.clk.lerp(this.lk,1-Math.exp(-s*dt));
    camera.position.copy(this.cur);camera.lookAt(this.clk);
  }
};

// ─── PHYSICS ────────────────────────────────────────────────
const PHY={grav:9.8,air:0.02,bounce:0.35,rollFric:0.92,greenFric:0.88,sandFric:0.72,stop:0.04};

function physicsTick(dt){
  if(ballOnGround&&ballVel.lengthSq()<PHY.stop*PHY.stop){ballVel.set(0,0,0);return'stopped'}
  const sub=4,sd=dt/sub;
  for(let s=0;s<sub;s++){
    if(!ballOnGround){ballVel.y-=PHY.grav*sd;
      const spd=ballVel.length();if(spd>0.1){ballVel.add(ballVel.clone().normalize().multiplyScalar(-PHY.air*spd*spd*sd))}
    }
    ballVel.x+=G.wind.x*sd*(ballOnGround?0.05:0.4);
    ballVel.z+=G.wind.z*sd*(ballOnGround?0.05:0.4);
    ballPos.add(ballVel.clone().multiplyScalar(sd));
    
    const gy=getTerrainY(ballPos.x,ballPos.z,G.dist);
    if(ballPos.y<=gy){
      ballPos.y=gy;
      if(!ballOnGround&&ballVel.y<-0.4){
        ballVel.y=-ballVel.y*PHY.bounce;ballVel.x*=0.8;ballVel.z*=0.8;
        AUD.play('bounce');
        if(Math.abs(ballVel.y)<0.25){ballOnGround=true;ballVel.y=0}
      }else{ballOnGround=true;ballVel.y=0}
    }else{ballOnGround=false}
    
    if(ballOnGround){
      const og=isOnGreen(),ib=isInBunker();
      let f=og?PHY.greenFric:PHY.rollFric;
      if(ib)f=PHY.sandFric;
      ballVel.x*=Math.pow(f,sd*60);ballVel.z*=Math.pow(f,sd*60);
      if(og){
        const th=new THREE.Vector3(holePos.x-ballPos.x,0,holePos.z-ballPos.z);
        const sd2=th.length();
        if(sd2>0.3&&sd2<greenRadius){th.normalize().multiplyScalar(0.12*sd);ballVel.add(th)}
      }
      // terrain slope
      const slopeX=(getTerrainY(ballPos.x+0.5,ballPos.z,G.dist)-getTerrainY(ballPos.x-0.5,ballPos.z,G.dist));
      const slopeZ=(getTerrainY(ballPos.x,ballPos.z+0.5,G.dist)-getTerrainY(ballPos.x,ballPos.z-0.5,G.dist));
      ballVel.x+=slopeX*2*sd;ballVel.z+=slopeZ*2*sd;
    }
    
    for(const w of waterAreas){
      if(Math.abs(ballPos.x-w.center.x)<w.size.x/2&&Math.abs(ballPos.z-w.center.z)<w.size.z/2&&ballPos.y<w.center.y+0.15){
        ballInWater=true;ballVel.set(0,0,0);AUD.play('splash');return'water';
      }
    }
    if(ballPos.x<obBounds.minX||ballPos.x>obBounds.maxX||ballPos.z<obBounds.minZ||ballPos.z>obBounds.maxZ){
      ballOB=true;ballVel.set(0,0,0);AUD.play('ob');return'ob';
    }
    if(ballOnGround&&isOnGreen()){
      const dh=Math.sqrt((ballPos.x-holePos.x)**2+(ballPos.z-holePos.z)**2);
      const spd=Math.sqrt(ballVel.x**2+ballVel.z**2);
      if(dh<0.15&&spd<3){ballPos.set(holePos.x,holePos.y,holePos.z);ballVel.set(0,0,0);return'holed'}
    }
  }
  updBallMesh();
  return ballOnGround&&ballVel.lengthSq()<PHY.stop*PHY.stop?'stopped':'flying';
}

function isOnGreen(){const dx=ballPos.x-greenCenter.x,dz=ballPos.z-greenCenter.z;return dx*dx+dz*dz<greenRadius*greenRadius}
function isInBunker(){for(const b of bunkers){const dx=ballPos.x-b.center.x,dz=ballPos.z-b.center.z;if(dx*dx+dz*dz<b.radius*b.radius)return true}return false}
function distToHole(){return Math.sqrt((ballPos.x-holePos.x)**2+(ballPos.z-holePos.z)**2)}

// ─── GAME STATE ─────────────────────────────────────────────
const G={state:'menu',courseIdx:0,holeIdx:0,clubIdx:0,strokes:0,scores:[],par:0,dist:0,
  wind:{x:0,z:0,speed:0,dir:0},power:0,accuracy:0,pDir:1,aDir:1,pSpd:1.8,aSpd:2.5,
  practice:false,flyT:0,prevBall:new THREE.Vector3(),maxStr:8,windSnd:null};

function newWind(ci){
  const str=COURSES[ci].wind*(0.5+Math.random()*0.5);
  const dir=Math.random()*Math.PI*2;
  G.wind={x:Math.cos(dir)*str*0.5,z:Math.sin(dir)*str*0.5,speed:str,dir};
}
function autoClub(){const d=distToHole();G.clubIdx=d<5?3:d<25?2:d<50?1:0}

// ─── UI ─────────────────────────────────────────────────────
function showScr(el){document.querySelectorAll('.scr').forEach(s=>s.classList.remove('on'));if(el)el.classList.add('on')}
function showHUD(v){EL.hud.style.display=v?'block':'none';EL.clubBtn.style.display=v?'block':'none'}
function updHUD(){
  EL.hHole.textContent='H'+(G.holeIdx+1);EL.hPar.textContent='Par '+G.par;
  EL.hCourse.textContent=COURSES[G.courseIdx].name;
  EL.hStrokes.textContent=G.strokes+' / '+G.par;
  EL.hDist.textContent=distToHole().toFixed(1)+'m';
  const wd=['N','NE','E','SE','S','SW','W','NW'];
  EL.hWind.textContent=wd[Math.round(((G.wind.dir*180/Math.PI)%360+360)%360/45)%8]+' '+G.wind.speed.toFixed(1)+'m/s';
  EL.clubBtn.textContent=CLUBS[G.clubIdx].name;
}
function showBig(m,s,dur){
  EL.bigMsg.querySelector('.bm').textContent=m;
  EL.bigMsg.querySelector('.bs').textContent=s||'';
  EL.bigMsg.style.display='block';EL.bigMsg.style.animation='popIn 0.4s ease-out forwards';
  if(dur)setTimeout(()=>{EL.bigMsg.style.display='none'},dur);
}
function showSwing(v){EL.swingPanel.style.display=v?'flex':'none';if(!v){EL.accBar.style.display='none';EL.powerMark.style.display='none';EL.powerFill.style.width='0%'}}
function showFly(v){EL.flyover.style.display=v?'flex':'none'}

function buildSC(tbl,scores,pars){
  let h='<tr><th>H</th>';for(let i=0;i<scores.length;i++)h+='<th>'+(i+1)+'</th>';
  h+='<th>T</th></tr><tr><td>P</td>';let tp=0;
  for(let i=0;i<scores.length;i++){h+='<td>'+pars[i]+'</td>';tp+=pars[i]}
  h+='<td>'+tp+'</td></tr><tr><td>S</td>';let t=0;
  for(let i=0;i<scores.length;i++){const d=scores[i]-pars[i];const c=d<0?'un':d>0?'ov':'';h+='<td class="'+c+'">'+scores[i]+'</td>';t+=scores[i]}
  h+='<td><b>'+t+'</b></td></tr>';tbl.innerHTML=h;return{t,tp};
}
function scoreName(s,p){const d=s-p;return SCORE_NAMES[String(d)]||(d>0?'+'+d:''+d)}
function rank(d){return d<=-9?'SS':d<=-5?'S':d<=-2?'A':d<=1?'B':d<=5?'C':'D'}

// ─── GAME FLOW ──────────────────────────────────────────────
function startRound(ci,prac){
  AUD.init();G.courseIdx=ci;G.practice=prac;G.holeIdx=0;G.scores=[];showScr(null);startHole();
}
function startHole(){
  const C=COURSES[G.courseIdx];
  G.par=C.par[G.holeIdx];G.dist=C.dist[G.holeIdx];G.strokes=0;
  newWind(G.courseIdx);
  buildCourse(G.courseIdx,G.holeIdx);
  if(!ballMesh)createBall();if(!aimLine)createAimLine();
  resetBall(0,getTerrainY(0,0,G.dist),0);
  aimAngle=Math.atan2(greenCenter.x-ballPos.x,-(greenCenter.z-ballPos.z));
  autoClub();
  G.state='flyover';G.flyT=0;
  showScr(null);showHUD(false);showSwing(false);hideAim();showFly(true);
  EL.flyHole.textContent='H'+(G.holeIdx+1);
  EL.flyName.textContent=C.name;
  EL.flyInfo.textContent='Par '+G.par+' | '+G.dist+'m';
  EL.flyProg.style.width='0%';
  ballMesh.visible=false;if(aimLine)aimLine.visible=false;if(aimDot)aimDot.visible=false;
}
function endFlyover(){
  G.state='aim';showFly(false);showHUD(true);showSwing(true);
  EL.aimGuide.style.display='block';EL.puttInfo.style.display='none';
  ballMesh.visible=true;updHUD();CAM.behind(true);updAimLine(0.5);
}
function doSwing(pwr,acc){
  G.strokes++;const club=CLUBS[G.clubIdx];
  const accErr=(acc-0.5)*2;const angErr=accErr*0.25;
  const ang=aimAngle+angErr;const d=club.maxDist*pwr;
  const lR=club.loft*Math.PI/180;const spd=d*0.7;
  ballVel.set(Math.sin(ang)*Math.cos(lR)*spd+accErr*club.spin*2,Math.sin(lR)*spd,-Math.cos(ang)*Math.cos(lR)*spd);
  ballOnGround=false;G.prevBall.copy(ballPos);
  G.state='flying';hideAim();showSwing(false);EL.aimGuide.style.display='none';
  AUD.play(club.name==='Putter'?'putt':'hit');vibrate(30);updHUD();
}
function onStop(res){
  if(res==='holed'){
    const sn=scoreName(G.strokes,G.par);
    showBig(sn,G.strokes===1?'HOLE IN ONE!':G.strokes+' strokes',2500);
    AUD.play('hole');vibrate([100,50,100,50,200]);
    spawnPtc(holePos.clone().add(new THREE.Vector3(0,0.5,0)),30,0xfdd835,3,5);
    spawnPtc(holePos.clone().add(new THREE.Vector3(0,0.3,0)),20,0xff6644,2,4);
    G.scores.push(G.strokes);CAM.result();
    setTimeout(()=>{EL.bigMsg.style.display='none';showSC()},2800);
    G.state='result';return;
  }
  if(res==='water'){
    showBig('WATER','+1 penalty',1800);vibrate(200);G.strokes++;
    spawnPtc(ballPos.clone().add(new THREE.Vector3(0,0.2,0)),15,0x4488ff,2,3);
    setTimeout(()=>{EL.bigMsg.style.display='none';resetBall(G.prevBall.x,getTerrainY(G.prevBall.x,G.prevBall.z,G.dist),G.prevBall.z);goAim()},2000);
    G.state='penalty';return;
  }
  if(res==='ob'){
    showBig('O.B.','+1 penalty',1800);vibrate(200);G.strokes++;
    setTimeout(()=>{EL.bigMsg.style.display='none';resetBall(G.prevBall.x,getTerrainY(G.prevBall.x,G.prevBall.z,G.dist),G.prevBall.z);goAim()},2000);
    G.state='penalty';return;
  }
  if(G.strokes>=G.maxStr){showBig('MAX',G.maxStr+' strokes',1800);G.scores.push(G.maxStr);setTimeout(()=>{EL.bigMsg.style.display='none';showSC()},2000);G.state='result';return}
  goAim();
}
function goAim(){
  G.state='aim';aimAngle=Math.atan2(holePos.x-ballPos.x,-(holePos.z-ballPos.z));autoClub();
  showHUD(true);showSwing(true);updHUD();CAM.behind(false);updAimLine(0.5);
  EL.aimGuide.style.display='block';
  if(isOnGreen()){EL.puttInfo.innerHTML='Green '+distToHole().toFixed(1)+'m';EL.puttInfo.style.display='block'}
  else EL.puttInfo.style.display='none';
}
function showSC(){
  const C=COURSES[G.courseIdx];EL.scName.textContent=C.name;
  const{t,tp}=buildSC(EL.scTable,G.scores,C.par.slice(0,G.scores.length));
  EL.scTotal.textContent=t+' ('+(t-tp>=0?'+':'')+(t-tp)+')';
  EL.scNext.textContent=G.holeIdx>=8?'View Results':'Next Hole';
  showScr(EL.scoreScr);showHUD(false);G.state='scorecard';
}
function nextHole(){showScr(null);G.holeIdx++;if(G.holeIdx>=9){showResult();return}startHole()}
function showResult(){
  const C=COURSES[G.courseIdx];EL.rsName.textContent=C.name;
  const{t,tp}=buildSC(EL.rsTable,G.scores,C.par);
  const d=t-tp;EL.rsTotal.textContent=t+' ('+(d>=0?'+':'')+d+')';
  EL.rsRank.textContent='Rank: '+rank(d);
  if(!G.practice){
    STO.d.records.push({course:G.courseIdx,name:C.name,scores:[...G.scores],total:t,diff:d,date:new Date().toISOString().split('T')[0]});
    if(STO.d.records.length>50)STO.d.records=STO.d.records.slice(-50);STO.save();
  }
  showScr(EL.resultScr);showHUD(false);G.state='roundResult';
}

// ─── INPUT ──────────────────────────────────────────────────
let txS=0,isDrag=false;
function initInput(){
  const cv=renderer.domElement;
  cv.addEventListener('pointerdown',e=>{if(G.state!=='aim')return;txS=e.clientX;isDrag=true});
  cv.addEventListener('pointermove',e=>{if(!isDrag||G.state!=='aim')return;aimAngle-=(e.clientX-txS)*0.004;txS=e.clientX;CAM.behind(false);updAimLine(0.5);updHUD()});
  cv.addEventListener('pointerup',()=>{isDrag=false});
  cv.addEventListener('pointercancel',()=>{isDrag=false});
  
  EL.swingBtn.addEventListener('pointerdown',e=>{
    e.stopPropagation();AUD.resume();
    if(G.state==='aim'){G.state='swingPower';G.power=0;G.pDir=1;EL.aimGuide.style.display='none';EL.swingBtn.textContent='POWER!'}
    else if(G.state==='swingPower'){G.state='swingAccuracy';G.accuracy=0;G.aDir=1;EL.powerMark.style.display='block';EL.powerMark.style.left=(G.power*100)+'%';EL.accBar.style.display='block';EL.swingBtn.textContent='SWING!'}
    else if(G.state==='swingAccuracy'){doSwing(G.power,G.accuracy)}
  });
  EL.clubBtn.addEventListener('click',()=>{if(G.state!=='aim')return;G.clubIdx=(G.clubIdx+1)%CLUBS.length;EL.clubBtn.textContent=CLUBS[G.clubIdx].name;updAimLine(0.5);vibrate(10)});
  EL.flySkip.addEventListener('click',()=>{if(G.state==='flyover')endFlyover()});
  EL.scNext.addEventListener('click',()=>{if(G.state==='scorecard')nextHole()});
  EL.rsMenu.addEventListener('click',()=>{showScr(EL.menuScr);showHUD(false);G.state='menu'});
  EL.btnPlay.addEventListener('click',()=>{AUD.init();showCourses(false)});
  EL.btnPractice.addEventListener('click',()=>{AUD.init();showCourses(true)});
  EL.btnRecords.addEventListener('click',showRecs);
  EL.btnSettings.addEventListener('click',showSets);
  EL.courseBack.addEventListener('click',()=>{showScr(EL.menuScr);G.state='menu'});
  EL.recordBack.addEventListener('click',()=>{showScr(EL.menuScr);G.state='menu'});
  EL.setBack.addEventListener('click',()=>{showScr(EL.menuScr);G.state='menu'});
  EL.setSave.addEventListener('click',()=>{
    STO.d.name=EL.setName.value||'Player';STO.d.vol=parseInt(EL.setVol.value);STO.d.vib=EL.setVib.checked;
    AUD.vol=STO.d.vol/100;STO.save();showScr(EL.menuScr);EL.menuPlayer.textContent=STO.d.name;G.state='menu';
  });
}
function showCourses(prac){
  G.practice=prac;EL.courseList.innerHTML='';
  COURSES.forEach((c,i)=>{
    const d=document.createElement('div');d.className='courseItem';
    const tp=c.par.reduce((a,b)=>a+b,0);
    const best=STO.d.records.filter(r=>r.course===i).reduce((b,r)=>Math.min(b,r.total),Infinity);
    d.innerHTML='<div class="cn">'+c.name+'</div><div class="ci">'+c.city+' | Par '+tp+' | 9H</div><div class="cb">'+(best<Infinity?'Best: '+best:'NEW')+'</div>';
    d.addEventListener('click',()=>startRound(i,prac));EL.courseList.appendChild(d);
  });
  showScr(EL.courseScr);G.state='courseSelect';
}
function showRecs(){
  const r=STO.d.records;
  if(!r.length){EL.recordList.innerHTML='<p style="color:#888;text-align:center;padding:20px">No records</p>'}
  else{let h='';[...r].reverse().slice(0,20).forEach(r=>{const d=r.diff;const c=d<0?'un':d>0?'ov':'';
    h+='<div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:10px 14px;margin-bottom:6px"><div style="font-size:14px;font-weight:700">'+(r.name||COURSES[r.course].name)+'</div><div style="font-size:12px;color:#999">'+r.date+'</div><div class="'+c+'" style="font-size:16px;font-weight:800">'+r.total+' ('+(d>=0?'+':'')+d+')</div></div>'});
    EL.recordList.innerHTML=h}
  showScr(EL.recordScr);G.state='records';
}
function showSets(){
  EL.setName.value=STO.d.name;EL.setVol.value=STO.d.vol;EL.setVib.checked=STO.d.vib;
  showScr(EL.settingScr);G.state='settings';
}

// ─── MAIN LOOP ──────────────────────────────────────────────
let wTime=0;
function loop(){
  requestAnimationFrame(loop);
  const dt=Math.min(clock.getDelta(),0.05);
  wTime+=dt;
  
  // water animation
  if(MAT.water){
    MAT.water.opacity=0.7+Math.sin(wTime*1.5)*0.08;
    if(MAT.water.normalMap){MAT.water.normalMap.offset.x=wTime*0.02;MAT.water.normalMap.offset.y=wTime*0.015}
  }
  // flag wave
  if(flagMesh)flagMesh.rotation.y=Math.sin(wTime*3)*0.2;
  // cloud drift
  if(courseGroup)courseGroup.children.forEach(c=>{if(c._speed)c.position.x+=c._speed*dt});

  switch(G.state){
    case'flyover':
      G.flyT+=dt*0.3;EL.flyProg.style.width=Math.min(100,G.flyT*100)+'%';
      CAM.flyover(Math.min(G.flyT,1),G.dist);
      if(G.flyT>=1)endFlyover();break;
    case'aim':CAM.behind(false);break;
    case'swingPower':
      G.power+=G.pDir*G.pSpd*dt;if(G.power>=1){G.power=1;G.pDir=-1}if(G.power<=0){G.power=0;G.pDir=1}
      EL.powerFill.style.width=(G.power*100)+'%';updAimLine(G.power);break;
    case'swingAccuracy':
      G.accuracy+=G.aDir*G.aSpd*dt;if(G.accuracy>=1){G.accuracy=1;G.aDir=-1}if(G.accuracy<=0){G.accuracy=0;G.aDir=1}
      EL.accNeedle.style.left=(G.accuracy*100)+'%';break;
    case'flying':
      const res=physicsTick(dt);CAM.follow();
      if(res==='stopped'||res==='holed'||res==='water'||res==='ob')onStop(res);break;
  }
  updPtc(dt);CAM.upd(dt);renderer.render(scene,camera);
}

// ─── INIT ───────────────────────────────────────────────────
function init(){
  STO.load();AUD.vol=STO.d.vol/100;
  EL.menuPlayer.textContent=STO.d.name;
  initThree();initMaterials();
  createBall();createAimLine();
  ballMesh.visible=false;aimLine.visible=false;aimDot.visible=false;
  initInput();
  showScr(EL.menuScr);showHUD(false);showSwing(false);G.state='menu';
  // menu bg
  buildCourse(0,0);
  CAM.tgt.set(5,10,8);CAM.lk.set(0,0,-15);CAM.cur.copy(CAM.tgt);CAM.clk.copy(CAM.lk);
  EL.loading.style.opacity='0';setTimeout(()=>{EL.loading.style.display='none'},500);
  loop();
  if('serviceWorker' in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{});
}
init();
'''

html_end = '''
</script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_part1)
    f.write(js_code)
    f.write(html_end)

import os
size = os.path.getsize('index.html')
print(f"Written {size} bytes to index.html")
print("Done!")
