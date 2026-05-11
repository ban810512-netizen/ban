# V8 Part 1: HTML shell + CSS + importmap
import os
content = r'''<!DOCTYPE html>
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
html,body{width:100%;height:100%;overflow:hidden;background:#000;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;touch-action:none;user-select:none}
#GC{position:fixed;top:0;left:0;width:100%;height:100%;overflow:hidden}
canvas{display:block;width:100%!important;height:100%!important}
/* Enhanced HUD - Golf King style */
#hud{position:absolute;top:0;left:0;width:100%;pointer-events:none;z-index:10}
#hudBar{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:linear-gradient(180deg,rgba(0,0,0,.75) 0%,rgba(0,0,0,.3) 80%,transparent 100%)}
.hd{display:flex;flex-direction:column;align-items:center;min-width:52px}
.hd .hl{font-size:9px;color:rgba(255,255,255,.6);text-transform:uppercase;letter-spacing:.5px;font-weight:600}
.hd .hv{font-size:15px;color:#fff;font-weight:700;text-shadow:0 1px 3px rgba(0,0,0,.5)}
#hHole .hv{color:#ffd700;font-size:18px}
#hDst .hv{color:#7eff7e}
#hWnd .hv{color:#87ceeb}
/* Club selector */
#clubBtn{position:absolute;top:58px;right:10px;pointer-events:auto;z-index:15;background:linear-gradient(135deg,rgba(40,40,40,.9),rgba(20,20,20,.95));color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:6px 14px;font-size:13px;font-weight:700;cursor:pointer;backdrop-filter:blur(8px);box-shadow:0 2px 8px rgba(0,0,0,.4)}
#clubBtn:active{transform:scale(.95);background:linear-gradient(135deg,rgba(60,60,60,.9),rgba(30,30,30,.95))}
/* Minimap */
#minimap{position:absolute;bottom:140px;right:8px;width:130px;height:130px;border-radius:12px;overflow:hidden;border:2px solid rgba(255,255,255,.25);z-index:12;pointer-events:none;box-shadow:0 2px 12px rgba(0,0,0,.5);backdrop-filter:blur(4px)}
#mmCvs{width:100%;height:100%}
/* Big message overlay */
#bigMsg{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;z-index:20;pointer-events:none;display:none}
.bm{font-size:42px;font-weight:900;color:#fff;text-shadow:0 0 20px rgba(255,215,0,.6),0 3px 6px rgba(0,0,0,.7);letter-spacing:2px;animation:popIn .4s cubic-bezier(.17,.67,.35,1.2)}
.bs{font-size:18px;color:rgba(255,255,255,.85);margin-top:6px;font-weight:500;text-shadow:0 2px 4px rgba(0,0,0,.5)}
@keyframes popIn{0%{transform:scale(0) rotate(-10deg);opacity:0}60%{transform:scale(1.15) rotate(2deg)}100%{transform:scale(1) rotate(0);opacity:1}}
/* Aim guide */
#aimGuide{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.7);font-size:12px;z-index:10;pointer-events:none;background:rgba(0,0,0,.35);padding:4px 14px;border-radius:12px;backdrop-filter:blur(4px);display:none}
/* Swing panel - Golf King style */
#swingPanel{position:absolute;bottom:0;left:0;width:100%;z-index:15;display:none;pointer-events:auto}
#swingInner{padding:10px 16px 20px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.6) 30%,rgba(0,0,0,.85))}
#swingTop{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
#swingLabel{color:rgba(255,255,255,.7);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px}
#swingVal{color:#ffd700;font-size:15px;font-weight:800}
/* Power bar */
#pwrWrap{position:relative;height:22px;border-radius:11px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.15);margin-bottom:8px}
#pwrFill{height:100%;width:0%;border-radius:11px;transition:none;background:linear-gradient(90deg,#2ecc40 0%,#f1c40f 50%,#e74c3c 80%,#c0392b 100%)}
#pwrMark{position:absolute;top:-2px;bottom:-2px;width:3px;background:#fff;border-radius:2px;box-shadow:0 0 6px rgba(255,255,255,.8);display:none;z-index:2}
/* Accuracy bar */
#accWrap{position:relative;height:22px;border-radius:11px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.15);margin-bottom:10px;display:none}
#accZone{position:absolute;height:100%;background:rgba(46,204,64,.25);border-left:2px solid rgba(46,204,64,.6);border-right:2px solid rgba(46,204,64,.6);border-radius:0}
#accPerf{position:absolute;height:100%;width:3px;background:#2ecc40;transform:translateX(-50%);z-index:1}
#accNdl{position:absolute;top:-2px;bottom:-2px;width:3px;background:#fff;border-radius:2px;box-shadow:0 0 8px rgba(255,255,255,.9);z-index:2;display:none}
/* Swing button */
#swBtn{width:100%;padding:12px;border:none;border-radius:12px;font-size:17px;font-weight:800;cursor:pointer;color:#fff;background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 3px 12px rgba(46,204,64,.4);letter-spacing:1px;text-transform:uppercase}
#swBtn:active{transform:scale(.97);filter:brightness(.9)}
/* Putt info */
#puttInfo{position:absolute;bottom:150px;left:50%;transform:translateX(-50%);color:#fff;font-size:12px;z-index:10;pointer-events:none;display:none;background:rgba(0,0,0,.5);padding:5px 14px;border-radius:10px;backdrop-filter:blur(4px)}
/* Flyover overlay */
#flyover{position:absolute;top:0;left:0;width:100%;height:100%;z-index:25;display:none;pointer-events:auto}
#flyInner{position:absolute;top:0;left:0;width:100%;padding:16px;background:linear-gradient(180deg,rgba(0,0,0,.8),rgba(0,0,0,.4) 60%,transparent)}
#flyH{font-size:28px;font-weight:900;color:#ffd700;text-shadow:0 2px 6px rgba(0,0,0,.6)}
#flyD{display:flex;gap:16px;margin-top:6px;flex-wrap:wrap}
#flyD span{font-size:13px;color:rgba(255,255,255,.85);font-weight:600}
#flyD span em{font-style:normal;color:#ffd700}
#flySk{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.5);color:rgba(255,255,255,.8);border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:8px 24px;font-size:13px;cursor:pointer;backdrop-filter:blur(4px)}
/* Scorecard */
#scoreScr,#resultScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:none;background:linear-gradient(135deg,rgba(0,40,0,.95),rgba(0,20,0,.97));overflow-y:auto;-webkit-overflow-scrolling:touch}
.scrInner{max-width:420px;margin:0 auto;padding:20px 16px}
.scrTitle{font-size:22px;font-weight:900;color:#ffd700;text-align:center;margin-bottom:4px}
.scrSub{font-size:13px;color:rgba(255,255,255,.6);text-align:center;margin-bottom:16px}
.scTbl{width:100%;border-collapse:collapse;margin-bottom:16px}
.scTbl th{background:rgba(255,215,0,.15);color:#ffd700;font-size:10px;padding:6px 4px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.scTbl td{text-align:center;padding:6px 4px;font-size:13px;color:#fff;border-bottom:1px solid rgba(255,255,255,.08)}
.scTbl .par{color:rgba(255,255,255,.5);font-size:11px}
.scTbl .eagle{color:#ffd700;font-weight:800}
.scTbl .birdie{color:#f44;font-weight:700}
.scTbl .bogey{color:#4af;font-weight:600}
.scTbl .dbogey{color:#88f}
.scTot{text-align:center;font-size:18px;font-weight:800;color:#fff;margin:12px 0;padding:10px;background:rgba(255,215,0,.1);border-radius:10px}
.scrBtn{display:block;width:100%;padding:13px;border:none;border-radius:12px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;margin-top:10px;text-align:center}
.scrBtn.primary{background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 3px 12px rgba(46,204,64,.3)}
.scrBtn.secondary{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2)}
/* Rank badge */
.rnk{display:inline-block;padding:3px 12px;border-radius:10px;font-size:12px;font-weight:700;margin-bottom:12px}
.rnk.s{background:linear-gradient(135deg,#ffd700,#ff8c00);color:#000}
.rnk.a{background:linear-gradient(135deg,#c0c0c0,#e0e0e0);color:#000}
.rnk.b{background:linear-gradient(135deg,#cd7f32,#b87333);color:#fff}
/* Menu */
#menuScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(180deg,rgba(0,60,0,.95),rgba(0,30,0,.98))}
#menuLogo{font-size:36px;font-weight:900;color:#ffd700;text-shadow:0 0 30px rgba(255,215,0,.4),0 3px 6px rgba(0,0,0,.6);margin-bottom:4px;letter-spacing:2px}
#menuSub{font-size:14px;color:rgba(255,255,255,.5);margin-bottom:30px}
#mPlayer{font-size:14px;color:rgba(255,255,255,.7);margin-bottom:24px}
.mBtn{display:block;width:220px;padding:14px;border:none;border-radius:14px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;margin:6px 0;text-align:center;letter-spacing:.5px}
#btnPlay{background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 4px 15px rgba(46,204,64,.4)}
#btnPrac{background:linear-gradient(135deg,#2980b9,#3498db);box-shadow:0 4px 15px rgba(52,152,219,.4)}
#btnRec{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2)}
#btnSet{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2)}
.mBtn:active{transform:scale(.96);filter:brightness(.85)}
/* Course select */
#courseScr,#recordScr,#settingScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:none;background:linear-gradient(135deg,rgba(0,40,0,.96),rgba(0,20,0,.98));overflow-y:auto;-webkit-overflow-scrolling:touch}
.pnlHdr{display:flex;align-items:center;padding:14px 16px;background:rgba(0,0,0,.3)}
.pnlHdr h2{flex:1;text-align:center;font-size:18px;color:#ffd700;font-weight:800}
.pnlBack{background:none;border:none;color:rgba(255,255,255,.7);font-size:24px;cursor:pointer;padding:4px 8px}
.cItem{display:flex;align-items:center;padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.06);cursor:pointer}
.cItem:active{background:rgba(255,255,255,.05)}
.cIcon{width:44px;height:44px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:22px;margin-right:14px;flex-shrink:0}
.cInfo{flex:1}
.cNm{font-size:15px;font-weight:700;color:#fff}
.cCity{font-size:11px;color:rgba(255,255,255,.5);margin-top:2px}
.cBest{font-size:12px;color:#ffd700;font-weight:600}
.rItem{padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.06)}
.rNm{font-size:14px;font-weight:700;color:#fff}
.rDt{font-size:11px;color:rgba(255,255,255,.4);margin-top:2px}
.rSc{font-size:13px;color:#ffd700;font-weight:600;margin-top:2px}
/* Settings */
.sRow{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.06)}
.sRow label{font-size:14px;color:#fff;font-weight:600}
.sRow input[type="text"]{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);color:#fff;padding:8px 12px;border-radius:8px;font-size:14px;width:140px}
.sRow input[type="range"]{width:120px;accent-color:#2ecc71}
.sToggle{position:relative;width:48px;height:26px;background:rgba(255,255,255,.2);border-radius:13px;cursor:pointer;transition:.3s}
.sToggle.on{background:#2ecc71}
.sToggle::after{content:'';position:absolute;top:3px;left:3px;width:20px;height:20px;background:#fff;border-radius:50%;transition:.3s}
.sToggle.on::after{left:25px}
/* Loading */
#loading{position:absolute;top:0;left:0;width:100%;height:100%;z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#0a1a0a}
#loading .ldTxt{color:#ffd700;font-size:16px;font-weight:700;margin-top:16px}
#loading .ldBar{width:200px;height:4px;background:rgba(255,255,255,.1);border-radius:2px;margin-top:10px;overflow:hidden}
#loading .ldFill{height:100%;width:0%;background:linear-gradient(90deg,#27ae60,#ffd700);border-radius:2px;transition:width .3s}
/* Shot trail */
.trail-dot{position:absolute;border-radius:50%;pointer-events:none;z-index:5}
/* Wind indicator */
#windArrow{position:absolute;top:56px;left:50%;transform:translateX(-50%);z-index:10;pointer-events:none}
</style>
</head>
<body>
<div id="GC">
 <div id="hud" style="display:none">
  <div id="hudBar">
   <div class="hd" id="hHole"><span class="hl">Hole</span><span class="hv">1</span></div>
   <div class="hd" id="hPar"><span class="hl">Par</span><span class="hv">4</span></div>
   <div class="hd" id="hCrs"><span class="hl">Course</span><span class="hv">-</span></div>
   <div class="hd" id="hStk"><span class="hl">Stroke</span><span class="hv">0</span></div>
   <div class="hd" id="hDst"><span class="hl">Dist</span><span class="hv">0m</span></div>
   <div class="hd" id="hWnd"><span class="hl">Wind</span><span class="hv">0</span></div>
  </div>
 </div>
 <button id="clubBtn" style="display:none">🏌️ Driver</button>
 <div id="minimap" style="display:none"><canvas id="mmCvs" width="160" height="160"></canvas></div>
 <div id="bigMsg"><div class="bm"></div><div class="bs"></div></div>
 <div id="aimGuide">◀ 드래그하여 조준 ▶</div>
 <div id="swingPanel">
  <div id="swingInner">
   <div id="swingTop"><span id="swingLabel">POWER</span><span id="swingVal">0%</span></div>
   <div id="pwrWrap"><div id="pwrFill"></div><div id="pwrMark"></div></div>
   <div id="accWrap"><div id="accZone"></div><div id="accPerf"></div><div id="accNdl"></div></div>
   <button id="swBtn">스윙</button>
  </div>
 </div>
 <div id="puttInfo"></div>
 <div id="flyover">
  <div id="flyInner">
   <div id="flyH">Hole 1</div>
   <div id="flyD"><span>Par <em>4</em></span><span>거리 <em>80m</em></span><span>바람 <em>2m/s</em></span></div>
  </div>
  <button id="flySk">건너뛰기 ▶</button>
 </div>
 <div id="scoreScr"><div class="scrInner"><div class="scrTitle" id="scNm"></div><div class="scrSub" id="scSub"></div><table class="scTbl" id="scTbl"></table><div class="scTot" id="scTot"></div><button class="scrBtn primary" id="scNxt">다음 홀 ▶</button></div></div>
 <div id="resultScr"><div class="scrInner"><div class="scrTitle" id="rsNm"></div><div class="scrSub" id="rsSub"></div><div id="rsRnk" style="text-align:center"></div><table class="scTbl" id="rsTbl"></table><div class="scTot" id="rsTot"></div><button class="scrBtn primary" id="rsMenu">메인 메뉴</button></div></div>
 <div id="menuScr">
  <div id="menuLogo">파크골프 프로</div>
  <div id="menuSub">전국투어 2026</div>
  <div id="mPlayer">플레이어</div>
  <button class="mBtn" id="btnPlay">🏆 전국투어</button>
  <button class="mBtn" id="btnPrac">🎯 연습라운드</button>
  <button class="mBtn" id="btnRec">📊 기록실</button>
  <button class="mBtn" id="btnSet">⚙️ 설정</button>
 </div>
 <div id="courseScr"><div class="pnlHdr"><button class="pnlBack" id="cBack">←</button><h2>코스 선택</h2><div style="width:36px"></div></div><div id="cList"></div></div>
 <div id="recordScr"><div class="pnlHdr"><button class="pnlBack" id="rBack">←</button><h2>기록실</h2><div style="width:36px"></div></div><div id="rList"></div></div>
 <div id="settingScr">
  <div class="pnlHdr"><button class="pnlBack" id="sBack">←</button><h2>설정</h2><div style="width:36px"></div></div>
  <div class="sRow"><label>이름</label><input type="text" id="sNm" maxlength="8" value="플레이어"></div>
  <div class="sRow"><label>볼륨</label><input type="range" id="sVol" min="0" max="100" value="80"></div>
  <div class="sRow"><label>진동</label><div class="sToggle on" id="sVib"></div></div>
  <div style="padding:16px"><button class="scrBtn primary" id="sSave">저장</button></div>
 </div>
 <div id="loading"><div style="font-size:40px">⛳</div><div class="ldTxt">로딩중...</div><div class="ldBar"><div class="ldFill" id="ldFill"></div></div></div>
</div>

<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js"}}</script>
<script type="module">
import * as THREE from 'three';
'''

with open('/home/user/webapp/index.html','w',encoding='utf-8') as f:
    f.write(content)
print(f"Part1 written: {os.path.getsize('/home/user/webapp/index.html')} bytes")
