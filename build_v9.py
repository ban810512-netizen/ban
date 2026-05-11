#!/usr/bin/env python3
"""Build Park Golf Pro v9 - Part 1: HTML + CSS + HTML Elements"""
f = open('/home/user/webapp/index.html', 'w')
f.write(r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#1a5c1a">
<link rel="manifest" href="./manifest.json">
<link rel="icon" href="./assets/icons/icon-192.png">
<title>파크골프 프로</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{width:100%;height:100%;overflow:hidden;background:#000;font-family:'Segoe UI',system-ui,sans-serif;touch-action:none;user-select:none}
#GC{position:fixed;top:0;left:0;width:100%;height:100%}
canvas{display:block;width:100%!important;height:100%!important}
#hud{position:absolute;top:0;left:0;width:100%;pointer-events:none;z-index:10;display:none}
#hudBar{display:flex;justify-content:space-between;padding:6px 10px;background:linear-gradient(180deg,rgba(0,0,0,.7),transparent)}
.hd{text-align:center;min-width:48px}.hd .hl{font-size:8px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.5px}
.hd .hv{font-size:14px;color:#fff;font-weight:700}
#clubBtn{position:absolute;top:52px;right:8px;pointer-events:auto;z-index:15;background:rgba(0,0,0,.7);color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:5px 12px;font-size:12px;font-weight:700;cursor:pointer;display:none}
#minimap{position:absolute;bottom:130px;right:6px;width:120px;height:120px;border-radius:10px;border:1.5px solid rgba(255,255,255,.2);z-index:12;pointer-events:none;overflow:hidden;display:none}
#bigMsg{position:absolute;top:40%;left:50%;transform:translate(-50%,-50%);text-align:center;z-index:20;pointer-events:none;display:none;font-size:38px;font-weight:900;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,.5),0 2px 4px rgba(0,0,0,.8)}
#swingPanel{position:absolute;bottom:0;left:0;width:100%;z-index:18;display:none;pointer-events:auto}
#swingInner{padding:10px 16px 18px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.75) 30%,rgba(0,0,0,.92))}
.barWrap{position:relative;height:22px;border-radius:11px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.12);margin-bottom:8px}
#pwrFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#2ecc40,#f1c40f 50%,#e74c3c 85%);transition:none}
#accWrap{display:none}
#accFill{height:100%;width:0%;border-radius:11px;background:linear-gradient(90deg,#e74c3c,#2ecc40 45%,#2ecc40 55%,#e74c3c);transition:none}
#swBtn{width:100%;padding:12px;border:none;border-radius:10px;font-size:16px;font-weight:800;cursor:pointer;color:#fff;background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 3px 12px rgba(46,204,64,.35);letter-spacing:1px}
#flyover{position:absolute;top:0;left:0;width:100%;height:100%;z-index:25;display:none;pointer-events:auto}
#flyTop{position:absolute;top:0;left:0;width:100%;padding:14px;background:linear-gradient(180deg,rgba(0,0,0,.75),transparent)}
#flyH{font-size:26px;font-weight:900;color:#ffd700}
#flyInfo{display:flex;gap:14px;margin-top:4px;font-size:12px;color:rgba(255,255,255,.8)}
#flyInfo em{font-style:normal;color:#ffd700}
#flySk{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.4);color:rgba(255,255,255,.7);border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:7px 22px;font-size:12px;cursor:pointer}
.scrFull{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:none;overflow-y:auto;-webkit-overflow-scrolling:touch}
#scoreScr,#resultScr{background:linear-gradient(135deg,rgba(0,35,0,.96),rgba(0,18,0,.98))}
.si{max-width:420px;margin:0 auto;padding:18px 14px}
.st{font-size:22px;font-weight:900;color:#ffd700;text-align:center;margin-bottom:4px}
.ss{font-size:12px;color:rgba(255,255,255,.5);text-align:center;margin-bottom:14px}
.scTbl{width:100%;border-collapse:collapse;margin-bottom:14px}
.scTbl th{background:rgba(255,215,0,.12);color:#ffd700;font-size:9px;padding:5px 3px;font-weight:700}
.scTbl td{text-align:center;padding:5px 3px;font-size:12px;color:#fff;border-bottom:1px solid rgba(255,255,255,.06)}
.eagle{color:#ffd700!important;font-weight:800}.birdie{color:#ff4444!important;font-weight:700}.par{color:rgba(255,255,255,.5)}.bogey{color:#4af}.dbogey{color:#88f}
.tot{text-align:center;font-size:16px;font-weight:800;color:#fff;margin:10px 0;padding:8px;background:rgba(255,215,0,.08);border-radius:8px}
.btn{display:block;width:100%;padding:12px;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;color:#fff;margin-top:8px;text-align:center}
.btn.p{background:linear-gradient(135deg,#27ae60,#2ecc71)}.btn.s{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15)}
.btn:active{transform:scale(.97);filter:brightness(.85)}
.resHole{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.06);font-size:13px;color:#fff}
#menuScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(180deg,rgba(0,50,0,.95),rgba(0,25,0,.98))}
#menuLogo{font-size:34px;font-weight:900;color:#ffd700;text-shadow:0 0 25px rgba(255,215,0,.35);margin-bottom:3px;letter-spacing:2px}
#menuSub{font-size:13px;color:rgba(255,255,255,.4);margin-bottom:26px}
.mb{display:block;width:220px;padding:13px;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;color:#fff;margin:5px 0;text-align:center}
.mb:active{transform:scale(.96);filter:brightness(.85)}
#btnPlay{background:linear-gradient(135deg,#27ae60,#2ecc71)}
#btnRec{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15)}
#btnSet{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15)}
#courseScr,#recordScr,#settingScr{background:linear-gradient(135deg,rgba(0,35,0,.97),rgba(0,18,0,.98))}
.ph{display:flex;align-items:center;padding:12px 14px;background:rgba(0,0,0,.25)}
.ph h2{flex:1;text-align:center;font-size:16px;color:#ffd700;font-weight:800}
.pb{background:none;border:none;color:rgba(255,255,255,.6);font-size:22px;cursor:pointer;padding:3px 6px}
.ci{display:flex;align-items:center;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05);cursor:pointer}
.ci:active{background:rgba(255,255,255,.04)}
.cn{font-size:14px;font-weight:700;color:#fff}.cc{font-size:10px;color:rgba(255,255,255,.4);margin-top:1px}
.sr{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.sr label{font-size:13px;color:#fff;font-weight:600}
.sr input[type="range"]{width:110px;accent-color:#2ecc71}
.tg{position:relative;width:44px;height:24px;background:rgba(255,255,255,.15);border-radius:12px;cursor:pointer;transition:.3s}
.tg.on{background:#2ecc71}.tg::after{content:'';position:absolute;top:2px;left:2px;width:20px;height:20px;background:#fff;border-radius:50%;transition:.3s}.tg.on::after{left:22px}
#loading{position:absolute;top:0;left:0;width:100%;height:100%;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0a1a0a}
.lt{color:#ffd700;font-size:15px;font-weight:700;margin-top:14px}
.lb{width:180px;height:3px;background:rgba(255,255,255,.08);border-radius:2px;margin-top:8px;overflow:hidden}
.lf{height:100%;width:0%;background:linear-gradient(90deg,#27ae60,#ffd700);border-radius:2px;transition:width .3s}
</style>
</head>
<body>
<div id="GC">
<!-- HUD -->
<div id="hud"><div id="hudBar">
<div class="hd"><span class="hl">코스</span><span class="hv" id="hCrs">-</span></div>
<div class="hd"><span class="hl">홀</span><span class="hv" id="hHole">1</span></div>
<div class="hd"><span class="hl">파</span><span class="hv" id="hPar">4</span></div>
<div class="hd"><span class="hl">타수</span><span class="hv" id="hStk">0</span></div>
<div class="hd"><span class="hl">거리</span><span class="hv" id="hDst">0m</span></div>
<div class="hd"><span class="hl">바람</span><span class="hv" id="hWnd">0<span id="hWndArr" style="display:inline-block;font-size:10px">↑</span></span></div>
</div></div>
<button id="clubBtn">드라이버</button>
<div id="minimap"><canvas id="mmCvs" width="160" height="160"></canvas></div>
<div id="bigMsg"></div>
<!-- Swing Panel -->
<div id="swingPanel"><div id="swingInner">
<div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="color:rgba(255,255,255,.5);font-size:10px;font-weight:700">파워</span><span id="swVal" style="color:#ffd700;font-size:13px;font-weight:800">0%</span></div>
<div class="barWrap" id="pwrWrap"><div id="pwrFill"></div></div>
<div class="barWrap" id="accWrap"><div id="accFill"></div></div>
<button id="swBtn" ontouchstart="onSwTap(event)" onclick="onSwTap(event)">스윙!</button>
</div></div>
<!-- Flyover -->
<div id="flyover"><div id="flyTop"><div id="flyH">1홀</div><div id="flyInfo"><span>PAR <em id="flyPar">4</em></span><span><em id="flyDist">50</em>m</span></div></div><button id="flySk" ontouchstart="endFly()" onclick="endFly()">건너뛰기 ▶</button></div>
<!-- Scorecard -->
<div id="scoreScr" class="scrFull"><div class="si"><div class="st" id="scTitle">스코어카드</div><div class="ss" id="scSub"></div><table class="scTbl" id="scTbl"></table><div class="tot" id="scTot"></div><button class="btn p" id="scNext" onclick="nextHole()">다음 홀</button></div></div>
<!-- Result -->
<div id="resultScr" class="scrFull"><div class="si"><div class="st" id="rsTitle">라운드 결과</div><div class="ss" id="rsSub"></div><div id="rsBody"></div><div class="tot" id="rsTot"></div><button class="btn p" onclick="startRound(G.ci)">다시 플레이</button><button class="btn s" onclick="showMenu()" style="margin-top:6px">메인 메뉴</button></div></div>
<!-- Menu -->
<div id="menuScr"><div id="menuLogo">파크골프 프로</div><div id="menuSub">전국투어 2026</div>
<button class="mb" id="btnPlay" onclick="openCourseSelect()">🏆 전국투어</button>
<button class="mb" id="btnRec" onclick="openRecords()">📊 기록실</button>
<button class="mb" id="btnSet" onclick="openSettings()">⚙️ 설정</button></div>
<!-- Course Select -->
<div id="courseScr" class="scrFull"><div class="ph"><button class="pb" onclick="showMenu()">←</button><h2>코스 선택</h2><div style="width:32px"></div></div><div id="cList"></div></div>
<!-- Records -->
<div id="recordScr" class="scrFull"><div class="ph"><button class="pb" onclick="showMenu()">←</button><h2>기록실</h2><div style="width:32px"></div></div><div id="rList"></div></div>
<!-- Settings -->
<div id="settingScr" class="scrFull"><div class="ph"><button class="pb" onclick="showMenu()">←</button><h2>설정</h2><div style="width:32px"></div></div>
<div class="sr"><label>볼륨</label><input type="range" id="sVol" min="0" max="100" value="80"></div>
<div class="sr"><label>진동</label><div class="tg on" id="sVib" onclick="this.classList.toggle('on')"></div></div>
</div>
<!-- Loading -->
<div id="loading"><div style="font-size:36px">⛳</div><div class="lt">로딩중...</div><div class="lb"><div class="lf" id="ldFill"></div></div></div>
</div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js"}}</script>
<script type="module">
import * as THREE from 'three';
window.THREE = THREE;

/* ===== UTILITIES ===== */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const rad=d=>d*Math.PI/180;
function mulberry32(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t^=t+Math.imul(t^t>>>7,61|t);return((t^t>>>14)>>>0)/4294967296}}
''')
f.close()
print(f"Part 1 done: {__import__('os').path.getsize('/home/user/webapp/index.html')} bytes")
