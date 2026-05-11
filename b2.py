#!/usr/bin/env python3
"""v9 Part 2: Textures, Course Data, Audio, Storage"""
f = open('/home/user/webapp/index.html', 'a')
f.write(r'''
/* ===== TEXTURES ===== */
const TEX={
grass(w=1024,h=1024){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
for(let y=0;y<h;y+=2){const b=.22+Math.sin(y*.01)*.03;
x.fillStyle=`hsl(${110+Math.random()*15},${55+Math.random()*15}%,${(b+Math.random()*.04)*100}%)`;x.fillRect(0,y,w,2)}
for(let i=0;i<12000;i++){const bx=Math.random()*w,by=Math.random()*h,bl=4+Math.random()*12;
x.strokeStyle=`hsla(${100+Math.random()*30},${40+Math.random()*30}%,${18+Math.random()*22}%,${.3+Math.random()*.4})`;
x.lineWidth=.4+Math.random()*.8;x.beginPath();x.moveTo(bx,by);x.quadraticCurveTo(bx+(Math.random()-.5)*3,by-bl*.5,bx+(Math.random()-.5)*2,by-bl);x.stroke()}
for(let i=0;i<25;i++){const px=Math.random()*w,py=Math.random()*h,pr=20+Math.random()*50;
const rg=x.createRadialGradient(px,py,0,px,py,pr);rg.addColorStop(0,`rgba(${80+Math.random()*40},${140+Math.random()*60},${40+Math.random()*30},${.06+Math.random()*.06})`);
rg.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=rg;x.fillRect(px-pr,py-pr,pr*2,pr*2)}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(15,15);t.anisotropy=4;return t},
fairway(w=1024,h=1024){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#2a8a2a';x.fillRect(0,0,w,h);const sw=48;
for(let i=0;i<w;i+=sw){x.fillStyle=Math.floor(i/sw)%2===0?'rgba(20,90,20,.18)':'rgba(50,150,50,.15)';x.fillRect(i,0,sw,h)}
for(let i=0;i<8000;i++){const bx=Math.random()*w,by=Math.random()*h;
x.strokeStyle=`hsla(${110+Math.random()*20},${50+Math.random()*20}%,${25+Math.random()*20}%,.25)`;
x.lineWidth=.3+Math.random()*.5;x.beginPath();x.moveTo(bx,by);x.lineTo(bx+(Math.random()-.5)*1.5,by-2-Math.random()*5);x.stroke()}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(3,10);t.anisotropy=4;return t},
green(w=1024,h=1024){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
const g=x.createRadialGradient(w/2,h/2,0,w/2,h/2,w*.7);g.addColorStop(0,'#3dbf3d');g.addColorStop(.7,'#35a835');g.addColorStop(1,'#2d9a2d');
x.fillStyle=g;x.fillRect(0,0,w,h);
for(let r=8;r<w*.65;r+=5){x.strokeStyle=r%10<5?'rgba(55,195,55,.08)':'rgba(35,155,35,.08)';x.lineWidth=2.5;x.beginPath();x.arc(w/2,h/2,r,0,Math.PI*2);x.stroke()}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=4;return t},
sand(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#d4be8a';x.fillRect(0,0,w,h);
for(let i=0;i<15000;i++){const v=Math.random();x.fillStyle=v<.3?'rgba(210,185,130,.3)':v<.6?'rgba(240,215,160,.25)':'rgba(185,160,100,.25)';x.fillRect(Math.random()*w,Math.random()*h,.8+Math.random()*1.5,.8+Math.random()*1.5)}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(2,2);return t},
water(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
const g=x.createLinearGradient(0,0,w,h);g.addColorStop(0,'#0d5575');g.addColorStop(.5,'#0a4060');g.addColorStop(1,'#073050');
x.fillStyle=g;x.fillRect(0,0,w,h);
for(let i=0;i<50;i++){const cx=Math.random()*w,cy=Math.random()*h,cr=4+Math.random()*25;
x.strokeStyle=`rgba(80,180,240,${.06+Math.random()*.08})`;x.lineWidth=.8;x.beginPath();x.arc(cx,cy,cr,0,Math.PI*2);x.stroke()}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(2,2);return t},
dirt(){const c=document.createElement('canvas');c.width=256;c.height=256;const x=c.getContext('2d');
x.fillStyle='#8B7355';x.fillRect(0,0,256,256);
for(let i=0;i<5000;i++){x.fillStyle=Math.random()>.5?'rgba(120,95,60,.25)':'rgba(160,130,90,.25)';x.fillRect(Math.random()*256,Math.random()*256,1+Math.random()*2,1+Math.random()*2)}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(4,4);return t},
bark(){const c=document.createElement('canvas');c.width=128;c.height=256;const x=c.getContext('2d');
x.fillStyle='#5a3a1a';x.fillRect(0,0,128,256);
for(let y=0;y<256;y+=1.5){x.fillStyle=`rgba(${55+Math.random()*25},${30+Math.random()*18},${10+Math.random()*10},${.15+Math.random()*.25})`;x.fillRect(0,y,128,1.5)}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;return t},
rough(w=512,h=512){const c=document.createElement('canvas');c.width=w;c.height=h;const x=c.getContext('2d');
x.fillStyle='#3a6a2a';x.fillRect(0,0,w,h);
for(let i=0;i<8000;i++){x.strokeStyle=`hsla(${100+Math.random()*35},${40+Math.random()*25}%,${20+Math.random()*25}%,.35)`;
x.lineWidth=.4+Math.random()*1;x.beginPath();const bx=Math.random()*w,by=Math.random()*h;x.moveTo(bx,by);x.lineTo(bx+(Math.random()-.5)*5,by-5-Math.random()*14);x.stroke()}
const t=new THREE.CanvasTexture(c);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(8,8);return t},
sky(){const c=document.createElement('canvas');c.width=4096;c.height=2048;const x=c.getContext('2d');
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
const t=new THREE.CanvasTexture(c);t.mapping=THREE.EquirectangularReflectionMapping;return t}
};

/* ===== COURSE DATA ===== */
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
const CLUBS=[
{name:'드라이버',power:16,loft:12},{name:'우드',power:11,loft:18},
{name:'아이언',power:7.5,loft:28},{name:'퍼터',power:3.5,loft:3}
];

/* ===== STORAGE ===== */
const STO={key:'pg9',_d:null,
load(){try{this._d=JSON.parse(localStorage.getItem(this.key))||{}}catch(e){this._d={}}
if(!this._d.vol)this._d.vol=80;if(this._d.vib===undefined)this._d.vib=true;if(!this._d.best)this._d.best={};return this._d},
save(d){if(d)this._d=d;try{localStorage.setItem(this.key,JSON.stringify(this._d))}catch(e){}},
get d(){if(!this._d)this.load();return this._d}};

/* ===== AUDIO ===== */
const AUD={ctx:null,gain:null,
init(){if(this.ctx)return;this.ctx=new(window.AudioContext||window.webkitAudioContext)();this.gain=this.ctx.createGain();this.gain.connect(this.ctx.destination);this.gain.gain.value=STO.d.vol/100},
resume(){if(this.ctx&&this.ctx.state==='suspended')this.ctx.resume()},
play(type){if(!this.ctx)return;this.resume();const t=this.ctx.currentTime;
const mk=(f,dur,tp='sine',vol=.3)=>{const o=this.ctx.createOscillator(),g=this.ctx.createGain();o.type=tp;o.frequency.value=f;g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);o.connect(g);g.connect(this.gain);o.start(t);o.stop(t+dur)};
const noise=(dur,vol=.1)=>{const sz=this.ctx.sampleRate*dur,buf=this.ctx.createBuffer(1,sz,this.ctx.sampleRate),d=buf.getChannelData(0);for(let i=0;i<sz;i++)d[i]=(Math.random()*2-1)*vol;const s=this.ctx.createBufferSource(),g=this.ctx.createGain();s.buffer=buf;g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);s.connect(g);g.connect(this.gain);s.start(t);s.stop(t+dur)};
switch(type){
case'hit':mk(800,.08,'square',.4);mk(400,.15,'sine',.3);noise(.1,.15);break;
case'putt':mk(600,.06,'sine',.25);mk(300,.1,'sine',.15);break;
case'hole':mk(523,.15,'sine',.35);setTimeout(()=>mk(659,.15,'sine',.35),100);setTimeout(()=>mk(784,.3,'sine',.4),200);break;
case'splash':noise(.4,.2);mk(200,.3,'sine',.15);break;
case'bounce':mk(500,.05,'square',.2);break;
case'ob':mk(200,.3,'sawtooth',.2);mk(150,.4,'sawtooth',.15);break;
case'swing':mk(300,.1,'sine',.15);mk(600,.08,'sine',.1);noise(.08,.1);break;
case'click':mk(1000,.03,'sine',.15);break}}};
function vib(ms=20){try{if(STO.d.vib&&navigator.vibrate)navigator.vibrate(ms)}catch(e){}}
''')
f.close()
print(f"Part 2 done: {__import__('os').path.getsize('/home/user/webapp/index.html')} bytes")
