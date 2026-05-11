c = r'''
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),lerp=(a,b,t)=>a+(b-a)*t,rad=d=>d*Math.PI/180;
function mulberry32(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t^=t+Math.imul(t^t>>>7,61|t);return((t^t>>>14)>>>0)/4294967296}}
const TEX={
grass(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,'#2a7d2a');g.addColorStop(.3,'#237023');g.addColorStop(.6,'#1d631d');g.addColorStop(1,'#1a5a1a');x.fillStyle=g;x.fillRect(0,0,w,h);
for(let i=0;i<8000;i++){const bx=Math.random()*w,by=Math.random()*h,bl=2+Math.random()*10,a=-.5*Math.PI+(Math.random()-.5)*.4;
const s=Math.random();x.strokeStyle=s<.2?'#4cb84c':s<.5?'#358435':s<.8?'#1e6b1e':'#57c957';x.lineWidth=.4+Math.random()*.8;x.globalAlpha=.3+Math.random()*.5;
x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo(bx+Math.cos(a)*bl*.4,by+Math.sin(a)*bl*.5,bx+Math.cos(a)*bl*.2,by+Math.sin(a)*bl);x.stroke()}
x.globalAlpha=1;for(let i=0;i<20;i++){const px=Math.random()*w,py=Math.random()*h,pr=10+Math.random()*40;
const rg=x.createRadialGradient(px,py,0,px,py,pr);rg.addColorStop(0,'rgba(90,200,70,.08)');rg.addColorStop(1,'rgba(90,200,70,0)');x.fillStyle=rg;x.beginPath();x.arc(px,py,pr,0,Math.PI*2);x.fill()}
for(let i=0;i<12;i++){const px=Math.random()*w,py=Math.random()*h,pr=8+Math.random()*25;
const rg=x.createRadialGradient(px,py,0,px,py,pr);rg.addColorStop(0,'rgba(10,40,10,.1)');rg.addColorStop(1,'rgba(10,40,10,0)');x.fillStyle=rg;x.beginPath();x.arc(px,py,pr,0,Math.PI*2);x.fill()}
return new THREE.CanvasTexture(c)},
fairway(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#2e8b2e';x.fillRect(0,0,w,h);const sw=28;
for(let i=0;i<Math.ceil(w/sw);i++){x.fillStyle=i%2===0?'rgba(55,165,55,.18)':'rgba(22,105,22,.18)';x.fillRect(i*sw,0,sw,h)}
for(let i=0;i<5000;i++){x.strokeStyle=Math.random()>.5?'rgba(65,185,65,.25)':'rgba(28,115,28,.25)';x.lineWidth=.4;x.globalAlpha=.4+Math.random()*.4;
x.beginPath();const bx=Math.random()*w,by=Math.random()*h;x.moveTo(bx,by);x.lineTo(bx+(Math.random()-.5)*1.5,by-1.5-Math.random()*4);x.stroke()}
x.globalAlpha=1;return new THREE.CanvasTexture(c)},
green(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#3ab53a';x.fillRect(0,0,w,h);const cx=w/2,cy=h/2;
for(let r=5;r<w*.7;r+=4){x.strokeStyle=r%8<4?'rgba(55,195,55,.1)':'rgba(35,155,35,.1)';x.lineWidth=2;x.beginPath();x.arc(cx,cy,r,0,Math.PI*2);x.stroke()}
for(let i=0;i<1500;i++){x.fillStyle=Math.random()>.5?'rgba(65,210,65,.06)':'rgba(42,170,42,.06)';x.fillRect(Math.random()*w,Math.random()*h,.8,.8)}
return new THREE.CanvasTexture(c)},
sand(w=256,h=256){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#d4b978';x.fillRect(0,0,w,h);
for(let i=0;i<10000;i++){const v=Math.random();x.fillStyle=v<.3?'rgba(200,170,100,.35)':v<.6?'rgba(230,200,140,.25)':'rgba(180,150,80,.25)';x.fillRect(Math.random()*w,Math.random()*h,.8+Math.random(),1+Math.random())}
for(let y=0;y<h;y+=6+Math.random()*5){x.strokeStyle='rgba(180,150,80,.12)';x.lineWidth=.8;x.beginPath();x.moveTo(0,y);for(let xx=0;xx<w;xx+=8)x.quadraticCurveTo(xx+4,y+Math.random()*2-1,xx+8,y+Math.random()*1.5-.75);x.stroke()}
return new THREE.CanvasTexture(c)},
water(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,'#1a7090');g.addColorStop(.5,'#0d5575');g.addColorStop(1,'#0a4058');x.fillStyle=g;x.fillRect(0,0,w,h);
for(let i=0;i<50;i++){const cx=Math.random()*w,cy=Math.random()*h,cr=3+Math.random()*25;x.strokeStyle=`rgba(120,210,255,${.06+Math.random()*.08})`;x.lineWidth=.8;x.beginPath();x.arc(cx,cy,cr,0,Math.PI*2);x.stroke()}
for(let i=0;i<150;i++){x.fillStyle=`rgba(200,240,255,${.04+Math.random()*.08})`;x.beginPath();x.arc(Math.random()*w,Math.random()*h,.5+Math.random()*1.5,0,Math.PI*2);x.fill()}
return new THREE.CanvasTexture(c)},
dirt(w=256,h=256){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#8B7355';x.fillRect(0,0,w,h);for(let i=0;i<4000;i++){x.fillStyle=Math.random()<.5?'rgba(120,95,60,.25)':'rgba(160,130,90,.25)';x.fillRect(Math.random()*w,Math.random()*h,1+Math.random()*2,1+Math.random()*2)}
return new THREE.CanvasTexture(c)},
bark(){const c=document.createElement('canvas');c.width=128;c.height=256;const x=c.getContext('2d');
x.fillStyle='#5a3a1a';x.fillRect(0,0,128,256);for(let y=0;y<256;y+=2){x.fillStyle=`rgba(${55+Math.random()*35},${28+Math.random()*22},${8+Math.random()*12},${.15+Math.random()*.3})`;x.fillRect(0,y,128,2)}
return new THREE.CanvasTexture(c)},
rough(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#3a6a2a';x.fillRect(0,0,w,h);for(let i=0;i<6000;i++){x.strokeStyle=['#4a8a3a','#2a5a1a','#5aaa4a','#3a7a2a'][Math.floor(Math.random()*4)];
x.lineWidth=.4+Math.random();x.globalAlpha=.3+Math.random()*.5;x.beginPath();const bx=Math.random()*w,by=Math.random()*h;x.moveTo(bx,by);x.lineTo(bx+Math.random()*3-1.5,by-3-Math.random()*12);x.stroke()}
x.globalAlpha=1;return new THREE.CanvasTexture(c)},
sky(){const c=document.createElement('canvas');c.width=2048;c.height=1024;const x=c.getContext('2d');
const g=x.createLinearGradient(0,0,0,1024);g.addColorStop(0,'#0b1e40');g.addColorStop(.12,'#1a3d6e');g.addColorStop(.3,'#3d7fc4');g.addColorStop(.45,'#6aade0');g.addColorStop(.55,'#92c8ec');g.addColorStop(.65,'#b8dcf2');g.addColorStop(.72,'#dce8d8');g.addColorStop(.78,'#c8bc98');g.addColorStop(.84,'#8aaa60');g.addColorStop(1,'#4a7a30');
x.fillStyle=g;x.fillRect(0,0,2048,1024);
for(let i=0;i<45;i++){const cx=Math.random()*2048,cy=180+Math.random()*280,cw=60+Math.random()*250,ch=10+Math.random()*25;
for(let j=0;j<10;j++){const ox=cx+(Math.random()-.5)*cw,oy=cy+(Math.random()-.5)*ch,r=12+Math.random()*40;
const rg=x.createRadialGradient(ox,oy,0,ox,oy,r);rg.addColorStop(0,`rgba(255,255,255,${.15+Math.random()*.12})`);rg.addColorStop(.6,'rgba(255,255,255,.05)');rg.addColorStop(1,'rgba(255,255,255,0)');x.fillStyle=rg;x.beginPath();x.arc(ox,oy,r,0,Math.PI*2);x.fill()}}
const sg=x.createRadialGradient(1500,400,0,1500,400,250);sg.addColorStop(0,'rgba(255,245,210,.25)');sg.addColorStop(.4,'rgba(255,225,160,.1)');sg.addColorStop(1,'rgba(255,200,100,0)');x.fillStyle=sg;x.beginPath();x.arc(1500,400,250,0,Math.PI*2);x.fill();
const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;return t}
};
const COURSES=[
{name:'서울숲',city:'서울',par:[3,4,3,4,3,5,3,4,3],dist:[30,55,35,60,40,80,32,58,38],theme:'spring',wind:2,trees:'deciduous',water:[4,8]},
{name:'한강공원',city:'서울',par:[4,3,4,3,4,3,4,3,4],dist:[50,35,55,30,60,38,52,33,58],theme:'summer',wind:3,trees:'mixed',water:[2,5,8]},
{name:'월드컵공원',city:'서울',par:[3,4,3,5,3,4,3,4,3],dist:[28,48,32,72,36,56,30,50,34],theme:'autumn',wind:2,trees:'deciduous',water:[3,7]},
{name:'대구스타디움',city:'대구',par:[4,3,4,3,5,3,4,3,4],dist:[52,30,58,35,78,32,55,28,60],theme:'summer',wind:3,trees:'pine',water:[1,5]},
{name:'해운대',city:'부산',par:[3,4,3,4,3,4,3,5,3],dist:[35,60,38,55,40,58,36,75,32],theme:'coastal',wind:4,trees:'palm',water:[2,4,6,8]},
{name:'경주보문',city:'경주',par:[4,3,5,3,4,3,4,3,4],dist:[55,32,80,28,58,35,52,30,62],theme:'autumn',wind:2,trees:'mixed',water:[3,6]},
{name:'무등산',city:'광주',par:[3,3,4,3,4,3,5,3,3],dist:[32,28,56,35,52,30,76,38,34],theme:'mountain',wind:3,trees:'pine',water:[4,7]},
{name:'태백산',city:'태백',par:[4,3,3,4,3,5,3,4,3],dist:[58,35,30,55,38,82,32,56,36],theme:'mountain',wind:4,trees:'pine',water:[5,8]},
{name:'제주한라',city:'제주',par:[3,4,3,4,3,4,5,3,4],dist:[38,60,35,58,32,62,78,30,55],theme:'tropical',wind:5,trees:'palm',water:[1,3,5,7]},
{name:'남해독일마을',city:'남해',par:[4,3,4,3,5,3,3,4,3],dist:[52,28,56,35,76,30,32,58,38],theme:'coastal',wind:4,trees:'mixed',water:[2,4,7]}
];
const CLUBS=[{name:'드라이버',dist:85,loft:12,spin:.3},{name:'우드',dist:60,loft:18,spin:.4},{name:'아이언',dist:40,loft:28,spin:.6},{name:'퍼터',dist:18,loft:3,spin:.1}];
const SNAMES={'-3':'알바트로스','-2':'이글','-1':'버디','0':'파','+1':'보기','+2':'더블보기','+3':'트리플보기'};
const STO={key:'pg9',_d:null,load(){try{this._d=JSON.parse(localStorage.getItem(this.key))||{}}catch(e){this._d={}}
if(!this._d.name)this._d.name='플레이어';if(!this._d.vol)this._d.vol=80;if(!this._d.vib)this._d.vib=true;if(!this._d.records)this._d.records=[];if(!this._d.best)this._d.best={};return this._d},
save(){try{localStorage.setItem(this.key,JSON.stringify(this._d))}catch(e){}},get d(){if(!this._d)this.load();return this._d}};
const AUD={ctx:null,gain:null,init(){if(this.ctx)return;this.ctx=new(window.AudioContext||window.webkitAudioContext)();this.gain=this.ctx.createGain();this.gain.connect(this.ctx.destination);this.setVol(STO.d.vol/100)},
setVol(v){if(this.gain)this.gain.gain.value=clamp(v,0,1)},resume(){if(this.ctx&&this.ctx.state==='suspended')this.ctx.resume()},
play(type){if(!this.ctx)return;const t=this.ctx.currentTime;
const mk=(f,dur,tp='sine',vol=.3)=>{const o=this.ctx.createOscillator(),g=this.ctx.createGain();o.type=tp;o.frequency.value=f;g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);o.connect(g);g.connect(this.gain);o.start(t);o.stop(t+dur)};
const noise=(dur,vol=.1)=>{const sz=this.ctx.sampleRate*dur,buf=this.ctx.createBuffer(1,sz,this.ctx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<sz;i++)d[i]=(Math.random()*2-1)*vol;const s=this.ctx.createBufferSource(),g=this.ctx.createGain();s.buffer=buf;g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);s.connect(g);g.connect(this.gain);s.start(t);s.stop(t+dur)};
switch(type){case'hit':mk(800,.08,'square',.4);mk(400,.15,'sine',.3);noise(.1,.15);break;case'putt':mk(600,.06,'sine',.25);mk(300,.1,'sine',.15);break;
case'hole':mk(523,.15,'sine',.35);setTimeout(()=>mk(659,.15,'sine',.35),100);setTimeout(()=>mk(784,.3,'sine',.4),200);break;
case'splash':noise(.4,.2);mk(200,.3,'sine',.15);break;case'bounce':mk(500,.05,'square',.2);break;case'ob':mk(200,.3,'sawtooth',.2);mk(150,.4,'sawtooth',.15);break;
case'swing':mk(300,.1,'sine',.15);mk(600,.08,'sine',.1);noise(.08,.1);break;case'applause':for(let i=0;i<5;i++)setTimeout(()=>noise(.15,.08),i*60);break}}};
function vib(ms=20){if(STO.d.vib&&navigator.vibrate)navigator.vibrate(ms)}
'''
with open('/home/user/webapp/index.html','a') as f: f.write(c)
import os; print(f"P2: {os.path.getsize('/home/user/webapp/index.html')}b")
