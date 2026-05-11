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
html,body{width:100%;height:100%;overflow:hidden;background:#000;font-family:'Segoe UI',system-ui,sans-serif;touch-action:none;user-select:none}
#GC{position:fixed;top:0;left:0;width:100%;height:100%}
canvas{display:block;width:100%!important;height:100%!important}
#hud{position:absolute;top:0;left:0;width:100%;pointer-events:none;z-index:10}
#hudBar{display:flex;justify-content:space-between;padding:6px 10px;background:linear-gradient(180deg,rgba(0,0,0,.7),transparent)}
.hd{text-align:center;min-width:48px}.hd .hl{font-size:8px;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.5px}
.hd .hv{font-size:14px;color:#fff;font-weight:700}
#clubBtn{position:absolute;top:52px;right:8px;pointer-events:auto;z-index:15;background:rgba(0,0,0,.7);color:#fff;border:1px solid rgba(255,255,255,.2);border-radius:16px;padding:5px 12px;font-size:12px;font-weight:700;cursor:pointer}
#minimap{position:absolute;bottom:130px;right:6px;width:120px;height:120px;border-radius:10px;border:1.5px solid rgba(255,255,255,.2);z-index:12;pointer-events:none;overflow:hidden}
#mmCvs{width:100%;height:100%}
#bigMsg{position:absolute;top:45%;left:50%;transform:translate(-50%,-50%);text-align:center;z-index:20;pointer-events:none;display:none}
.bm{font-size:38px;font-weight:900;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,.5),0 2px 4px rgba(0,0,0,.8);animation:pop .35s ease-out}
.bs{font-size:15px;color:rgba(255,255,255,.8);margin-top:4px;text-shadow:0 1px 3px rgba(0,0,0,.6)}
@keyframes pop{0%{transform:scale(0);opacity:0}70%{transform:scale(1.15)}100%{transform:scale(1);opacity:1}}
#aimGuide{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);color:rgba(255,255,255,.6);font-size:11px;z-index:10;pointer-events:none;background:rgba(0,0,0,.3);padding:3px 12px;border-radius:10px;display:none}
#swingPanel{position:absolute;bottom:0;left:0;width:100%;z-index:15;display:none;pointer-events:auto}
#swingInner{padding:8px 14px 16px;background:linear-gradient(180deg,transparent,rgba(0,0,0,.7) 40%,rgba(0,0,0,.9))}
#swingTop{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
#swingLabel{color:rgba(255,255,255,.6);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px}
#swingVal{color:#ffd700;font-size:14px;font-weight:800}
#pwrWrap{position:relative;height:20px;border-radius:10px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.12);margin-bottom:6px}
#pwrFill{height:100%;width:0%;border-radius:10px;background:linear-gradient(90deg,#2ecc40,#f1c40f 50%,#e74c3c 85%)}
#pwrMark{position:absolute;top:-1px;bottom:-1px;width:3px;background:#fff;border-radius:2px;box-shadow:0 0 6px #fff;display:none;z-index:2}
#accWrap{position:relative;height:20px;border-radius:10px;overflow:hidden;background:rgba(0,0,0,.5);border:1px solid rgba(255,255,255,.12);margin-bottom:8px;display:none}
#accZone{position:absolute;height:100%;background:rgba(46,204,64,.2);border-left:2px solid rgba(46,204,64,.5);border-right:2px solid rgba(46,204,64,.5)}
#accPerf{position:absolute;height:100%;width:2px;background:#2ecc40;transform:translateX(-50%);z-index:1}
#accNdl{position:absolute;top:-1px;bottom:-1px;width:3px;background:#fff;border-radius:2px;box-shadow:0 0 8px #fff;z-index:2;display:none}
#swBtn{width:100%;padding:11px;border:none;border-radius:10px;font-size:16px;font-weight:800;cursor:pointer;color:#fff;background:linear-gradient(135deg,#27ae60,#2ecc71);box-shadow:0 3px 10px rgba(46,204,64,.35);letter-spacing:1px}
#puttInfo{position:absolute;bottom:145px;left:50%;transform:translateX(-50%);color:#fff;font-size:11px;z-index:10;pointer-events:none;display:none;background:rgba(0,0,0,.4);padding:4px 12px;border-radius:8px}
#flyover{position:absolute;top:0;left:0;width:100%;height:100%;z-index:25;display:none;pointer-events:auto}
#flyTop{position:absolute;top:0;left:0;width:100%;padding:14px;background:linear-gradient(180deg,rgba(0,0,0,.75),transparent)}
#flyH{font-size:26px;font-weight:900;color:#ffd700}
#flyD{display:flex;gap:14px;margin-top:4px}#flyD span{font-size:12px;color:rgba(255,255,255,.8)}#flyD em{font-style:normal;color:#ffd700}
#flySk{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.4);color:rgba(255,255,255,.7);border:1px solid rgba(255,255,255,.15);border-radius:16px;padding:7px 22px;font-size:12px;cursor:pointer}
#scoreScr,#resultScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:none;background:linear-gradient(135deg,rgba(0,35,0,.96),rgba(0,18,0,.98));overflow-y:auto;-webkit-overflow-scrolling:touch}
.si{max-width:400px;margin:0 auto;padding:18px 14px}
.st{font-size:20px;font-weight:900;color:#ffd700;text-align:center;margin-bottom:3px}
.ss{font-size:12px;color:rgba(255,255,255,.5);text-align:center;margin-bottom:14px}
.tb{width:100%;border-collapse:collapse;margin-bottom:14px}
.tb th{background:rgba(255,215,0,.12);color:#ffd700;font-size:9px;padding:5px 3px;font-weight:700;text-transform:uppercase}
.tb td{text-align:center;padding:5px 3px;font-size:12px;color:#fff;border-bottom:1px solid rgba(255,255,255,.06)}
.tb .par{color:rgba(255,255,255,.4);font-size:10px}
.tb .eg{color:#ffd700;font-weight:800}.tb .bi{color:#f44;font-weight:700}.tb .bo{color:#4af}.tb .db{color:#88f}
.tot{text-align:center;font-size:16px;font-weight:800;color:#fff;margin:10px 0;padding:8px;background:rgba(255,215,0,.08);border-radius:8px}
.btn{display:block;width:100%;padding:12px;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;color:#fff;margin-top:8px;text-align:center}
.btn.p{background:linear-gradient(135deg,#27ae60,#2ecc71)}.btn.s{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15)}
.rk{display:inline-block;padding:2px 10px;border-radius:8px;font-size:11px;font-weight:700;margin-bottom:10px}
.rk.rs{background:linear-gradient(135deg,#ffd700,#ff8c00);color:#000}.rk.ra{background:linear-gradient(135deg,#c0c0c0,#e0e0e0);color:#000}.rk.rb{background:linear-gradient(135deg,#cd7f32,#b87333);color:#fff}
#menuScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(180deg,rgba(0,50,0,.95),rgba(0,25,0,.98))}
#menuLogo{font-size:34px;font-weight:900;color:#ffd700;text-shadow:0 0 25px rgba(255,215,0,.35);margin-bottom:3px;letter-spacing:2px}
#menuSub{font-size:13px;color:rgba(255,255,255,.4);margin-bottom:26px}
#mPlayer{font-size:13px;color:rgba(255,255,255,.6);margin-bottom:20px}
.mb{display:block;width:200px;padding:12px;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;color:#fff;margin:5px 0;text-align:center}
#btnPlay{background:linear-gradient(135deg,#27ae60,#2ecc71)}#btnPrac{background:linear-gradient(135deg,#2980b9,#3498db)}
#btnRec,#btnSet{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15)}
.mb:active{transform:scale(.96);filter:brightness(.85)}
#courseScr,#recordScr,#settingScr{position:absolute;top:0;left:0;width:100%;height:100%;z-index:30;display:none;background:linear-gradient(135deg,rgba(0,35,0,.97),rgba(0,18,0,.98));overflow-y:auto;-webkit-overflow-scrolling:touch}
.ph{display:flex;align-items:center;padding:12px 14px;background:rgba(0,0,0,.25)}.ph h2{flex:1;text-align:center;font-size:16px;color:#ffd700;font-weight:800}
.pb{background:none;border:none;color:rgba(255,255,255,.6);font-size:22px;cursor:pointer;padding:3px 6px}
.ci{display:flex;align-items:center;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05);cursor:pointer}
.ci:active{background:rgba(255,255,255,.04)}
.ck{width:40px;height:40px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px;margin-right:12px}
.cn{font-size:14px;font-weight:700;color:#fff}.cc{font-size:10px;color:rgba(255,255,255,.4);margin-top:1px}.cb{font-size:11px;color:#ffd700;font-weight:600}
.ri{padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.sr{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.sr label{font-size:13px;color:#fff;font-weight:600}
.sr input[type="text"]{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);color:#fff;padding:7px 10px;border-radius:7px;font-size:13px;width:130px}
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
<div id="hud" style="display:none"><div id="hudBar">
<div class="hd" id="hHole"><span class="hl">Hole</span><span class="hv">1</span></div>
<div class="hd" id="hPar"><span class="hl">Par</span><span class="hv">4</span></div>
<div class="hd" id="hCrs"><span class="hl">Course</span><span class="hv">-</span></div>
<div class="hd" id="hStk"><span class="hl">Stroke</span><span class="hv">0</span></div>
<div class="hd" id="hDst"><span class="hl">Dist</span><span class="hv">0m</span></div>
<div class="hd" id="hWnd"><span class="hl">Wind</span><span class="hv">0</span></div>
</div></div>
<button id="clubBtn" style="display:none">Driver</button>
<div id="minimap" style="display:none"><canvas id="mmCvs" width="160" height="160"></canvas></div>
<div id="bigMsg"><div class="bm"></div><div class="bs"></div></div>
<div id="aimGuide">◀ 드래그하여 조준 ▶</div>
<div id="swingPanel"><div id="swingInner">
<div id="swingTop"><span id="swingLabel">POWER</span><span id="swingVal">0%</span></div>
<div id="pwrWrap"><div id="pwrFill"></div><div id="pwrMark"></div></div>
<div id="accWrap"><div id="accZone"></div><div id="accPerf"></div><div id="accNdl"></div></div>
<button id="swBtn">스윙</button>
</div></div>
<div id="puttInfo"></div>
<div id="flyover"><div id="flyTop"><div id="flyH">Hole 1</div><div id="flyD"></div></div><button id="flySk">건너뛰기 ▶</button></div>
<div id="scoreScr"><div class="si"><div class="st" id="scNm"></div><div class="ss" id="scSub"></div><table class="tb" id="scTbl"></table><div class="tot" id="scTot"></div><button class="btn p" id="scNxt">다음 홀</button></div></div>
<div id="resultScr"><div class="si"><div class="st" id="rsNm"></div><div class="ss" id="rsSub"></div><div id="rsRnk" style="text-align:center"></div><table class="tb" id="rsTbl"></table><div class="tot" id="rsTot"></div><button class="btn p" id="rsMenu">메인 메뉴</button></div></div>
<div id="menuScr"><div id="menuLogo">파크골프 프로</div><div id="menuSub">전국투어 2026</div><div id="mPlayer">플레이어</div>
<button class="mb" id="btnPlay">🏆 전국투어</button><button class="mb" id="btnPrac">🎯 연습라운드</button><button class="mb" id="btnRec">📊 기록실</button><button class="mb" id="btnSet">⚙️ 설정</button></div>
<div id="courseScr"><div class="ph"><button class="pb" id="cBack">←</button><h2>코스 선택</h2><div style="width:32px"></div></div><div id="cList"></div></div>
<div id="recordScr"><div class="ph"><button class="pb" id="rBack">←</button><h2>기록실</h2><div style="width:32px"></div></div><div id="rList"></div></div>
<div id="settingScr"><div class="ph"><button class="pb" id="sBack">←</button><h2>설정</h2><div style="width:32px"></div></div>
<div class="sr"><label>이름</label><input type="text" id="sNm" maxlength="8" value="플레이어"></div>
<div class="sr"><label>볼륨</label><input type="range" id="sVol" min="0" max="100" value="80"></div>
<div class="sr"><label>진동</label><div class="tg on" id="sVib"></div></div>
<div style="padding:14px"><button class="btn p" id="sSave">저장</button></div></div>
<div id="loading"><div style="font-size:36px">⛳</div><div class="lt">로딩중...</div><div class="lb"><div class="lf" id="ldFill"></div></div></div>
</div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js"}}</script>
<script type="module">
import * as THREE from 'three';
'''
with open('/home/user/webapp/index.html','w',encoding='utf-8') as f:
    f.write(content)
import os; print(f"P1: {os.path.getsize('/home/user/webapp/index.html')}b")
