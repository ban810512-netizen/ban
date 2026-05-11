# V8 Part 2: Textures + Data + Audio + Storage + Utilities
content = r'''
/* ====== UTILITIES ====== */
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const rand=(a=0,b=1)=>Math.random()*(b-a)+a;
const deg=r=>r*180/Math.PI;
const rad=d=>d*Math.PI/180;
function mulberry32(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t^=t+Math.imul(t^t>>>7,61|t);return((t^t>>>14)>>>0)/4294967296}}

/* ====== PROCEDURAL TEXTURES (PBR Quality) ====== */
const TEX={
  grass(w=512,h=512){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    // Base gradient
    const g=x.createLinearGradient(0,0,0,h);
    g.addColorStop(0,'#2d7a2d');g.addColorStop(.5,'#1e6b1e');g.addColorStop(1,'#1a5a1a');
    x.fillStyle=g;x.fillRect(0,0,w,h);
    // Individual grass blades - dense
    for(let i=0;i<6000;i++){
      const bx=Math.random()*w,by=Math.random()*h;
      const bl=3+Math.random()*8,bw=.5+Math.random()*1;
      const angle=-Math.PI/2+(.3*Math.random()-.15);
      const shade=Math.random();
      if(shade<.3)x.strokeStyle='#3a9a3a';
      else if(shade<.6)x.strokeStyle='#2a7a2a';
      else if(shade<.85)x.strokeStyle='#1d6a1d';
      else x.strokeStyle='#4aaa3a';
      x.lineWidth=bw;x.beginPath();
      x.moveTo(bx,by);
      x.quadraticCurveTo(bx+Math.random()*3-1.5,by-bl*.6,bx+Math.random()*2-1,by-bl);
      x.stroke();
    }
    // Light patches
    for(let i=0;i<15;i++){
      const px=Math.random()*w,py=Math.random()*h,pr=15+Math.random()*30;
      const rg=x.createRadialGradient(px,py,0,px,py,pr);
      rg.addColorStop(0,'rgba(80,180,60,.12)');rg.addColorStop(1,'rgba(80,180,60,0)');
      x.fillStyle=rg;x.fillRect(px-pr,py-pr,pr*2,pr*2);
    }
    return new THREE.CanvasTexture(c);
  },
  fairway(w=512,h=512){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    // Base
    x.fillStyle='#2e8b2e';x.fillRect(0,0,w,h);
    // Mowing stripes - prominent
    const sw=32;
    for(let i=0;i<w;i+=sw){
      x.fillStyle=(Math.floor(i/sw)%2===0)?'rgba(50,160,50,.2)':'rgba(20,100,20,.2)';
      x.fillRect(i,0,sw,h);
    }
    // Fine grass texture
    for(let i=0;i<4000;i++){
      const bx=Math.random()*w,by=Math.random()*h;
      x.strokeStyle=Math.random()>.5?'rgba(60,180,60,.3)':'rgba(30,120,30,.3)';
      x.lineWidth=.5;x.beginPath();
      x.moveTo(bx,by);x.lineTo(bx+Math.random()*2-1,by-2-Math.random()*4);
      x.stroke();
    }
    return new THREE.CanvasTexture(c);
  },
  green(w=512,h=512){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    x.fillStyle='#3aaf3a';x.fillRect(0,0,w,h);
    // Smooth putting surface with subtle grain
    for(let i=0;i<2000;i++){
      x.fillStyle=Math.random()>.5?'rgba(60,200,60,.08)':'rgba(40,160,40,.08)';
      x.fillRect(Math.random()*w,Math.random()*h,1,1);
    }
    // Circular mowing pattern
    const cx=w/2,cy=h/2;
    for(let r=10;r<w*.7;r+=6){
      x.strokeStyle=r%12<6?'rgba(50,190,50,.12)':'rgba(30,150,30,.12)';
      x.lineWidth=3;x.beginPath();x.arc(cx,cy,r,0,Math.PI*2);x.stroke();
    }
    return new THREE.CanvasTexture(c);
  },
  sand(w=256,h=256){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    x.fillStyle='#d4b978';x.fillRect(0,0,w,h);
    for(let i=0;i<8000;i++){
      const v=Math.random();
      x.fillStyle=v<.3?'rgba(200,170,100,.4)':v<.6?'rgba(230,200,140,.3)':'rgba(180,150,80,.3)';
      x.fillRect(Math.random()*w,Math.random()*h,1+Math.random(),1+Math.random());
    }
    // Ripple marks
    for(let y=0;y<h;y+=8+Math.random()*4){
      x.strokeStyle='rgba(180,150,80,.15)';x.lineWidth=1;
      x.beginPath();x.moveTo(0,y);
      for(let xx=0;xx<w;xx+=10)x.quadraticCurveTo(xx+5,y+Math.random()*3-1.5,xx+10,y+Math.random()*2-1);
      x.stroke();
    }
    return new THREE.CanvasTexture(c);
  },
  water(w=512,h=512){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    const g=x.createLinearGradient(0,0,0,h);
    g.addColorStop(0,'#1a6b8a');g.addColorStop(.5,'#0d5070');g.addColorStop(1,'#0a3a50');
    x.fillStyle=g;x.fillRect(0,0,w,h);
    // Caustic patterns
    for(let i=0;i<40;i++){
      const cx=Math.random()*w,cy=Math.random()*h,cr=5+Math.random()*20;
      x.strokeStyle='rgba(100,200,255,.12)';x.lineWidth=1;
      x.beginPath();x.arc(cx,cy,cr,0,Math.PI*2);x.stroke();
    }
    // Sparkles
    for(let i=0;i<100;i++){
      x.fillStyle=`rgba(200,240,255,${.05+Math.random()*.1})`;
      x.beginPath();x.arc(Math.random()*w,Math.random()*h,Math.random()*2,0,Math.PI*2);x.fill();
    }
    return new THREE.CanvasTexture(c);
  },
  dirt(w=256,h=256){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    x.fillStyle='#8B7355';x.fillRect(0,0,w,h);
    for(let i=0;i<3000;i++){
      const v=Math.random();
      x.fillStyle=v<.4?'rgba(120,95,60,.3)':'rgba(160,130,90,.3)';
      x.fillRect(Math.random()*w,Math.random()*h,1+Math.random()*2,1+Math.random()*2);
    }
    return new THREE.CanvasTexture(c);
  },
  bark(w=128,h=256){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    x.fillStyle='#5a3a1a';x.fillRect(0,0,w,h);
    for(let y=0;y<h;y+=2){
      x.fillStyle=`rgba(${60+Math.random()*30},${30+Math.random()*20},${10+Math.random()*10},${.2+Math.random()*.3})`;
      x.fillRect(0,y,w,2);
    }
    for(let i=0;i<200;i++){
      x.fillStyle='rgba(40,20,5,.2)';
      x.fillRect(Math.random()*w,Math.random()*h,1,2+Math.random()*4);
    }
    return new THREE.CanvasTexture(c);
  },
  rough(w=512,h=512){
    const c=document.createElement('canvas');c.width=w;c.height=h;
    const x=c.getContext('2d');
    x.fillStyle='#3a6a2a';x.fillRect(0,0,w,h);
    for(let i=0;i<5000;i++){
      const shade=Math.random();
      x.strokeStyle=shade<.3?'#4a8a3a':shade<.6?'#2a5a1a':'#5aaa4a';
      x.lineWidth=.5+Math.random();x.beginPath();
      const bx=Math.random()*w,by=Math.random()*h;
      x.moveTo(bx,by);x.lineTo(bx+Math.random()*4-2,by-4-Math.random()*10);
      x.stroke();
    }
    return new THREE.CanvasTexture(c);
  },
  sky(){
    const c=document.createElement('canvas');c.width=2048;c.height=1024;
    const x=c.getContext('2d');
    // Sky gradient - warm atmosphere
    const g=x.createLinearGradient(0,0,0,1024);
    g.addColorStop(0,'#0a1a3a');g.addColorStop(.15,'#1a3a6a');
    g.addColorStop(.35,'#4a8ace');g.addColorStop(.5,'#7ab8e8');
    g.addColorStop(.6,'#a8d4f0');g.addColorStop(.7,'#d0e8f8');
    g.addColorStop(.78,'#e8dcc0');g.addColorStop(.85,'#c0a878');
    g.addColorStop(1,'#5a8a3a');
    x.fillStyle=g;x.fillRect(0,0,2048,1024);
    // Wispy clouds
    for(let i=0;i<35;i++){
      const cx=Math.random()*2048,cy=200+Math.random()*300;
      const cw=80+Math.random()*200,ch=15+Math.random()*30;
      for(let j=0;j<8;j++){
        const ox=cx+Math.random()*cw-cw/2,oy=cy+Math.random()*ch-ch/2;
        const r=15+Math.random()*35;
        const rg=x.createRadialGradient(ox,oy,0,ox,oy,r);
        rg.addColorStop(0,'rgba(255,255,255,.25)');rg.addColorStop(.5,'rgba(255,255,255,.1)');
        rg.addColorStop(1,'rgba(255,255,255,0)');
        x.fillStyle=rg;x.fillRect(ox-r,oy-r,r*2,r*2);
      }
    }
    // Sun glow
    const sg=x.createRadialGradient(1400,420,0,1400,420,200);
    sg.addColorStop(0,'rgba(255,240,200,.3)');sg.addColorStop(.3,'rgba(255,220,150,.15)');
    sg.addColorStop(1,'rgba(255,200,100,0)');
    x.fillStyle=sg;x.fillRect(1100,220,600,400);
    const t=new THREE.CanvasTexture(c);
    t.mapping=THREE.EquirectangularReflectionMapping;
    return t;
  }
};

/* ====== COURSE DATA ====== */
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
  {name:'드라이버',dist:85,loft:12,spin:.3,icon:'🏌️'},
  {name:'우드',dist:60,loft:18,spin:.4,icon:'🪵'},
  {name:'아이언',dist:40,loft:28,spin:.6,icon:'⛳'},
  {name:'퍼터',dist:18,loft:3,spin:.1,icon:'🎯'}
];

const SNAMES={'-3':'알바트로스','-2':'이글','-1':'버디','0':'파','+1':'보기','+2':'더블보기','+3':'트리플보기'};

/* ====== STORAGE ====== */
const STO={
  key:'pg8',
  _d:null,
  load(){try{this._d=JSON.parse(localStorage.getItem(this.key))||{}}catch(e){this._d={}}
    if(!this._d.name)this._d.name='플레이어';
    if(!this._d.vol)this._d.vol=80;
    if(!this._d.vib)this._d.vib=true;
    if(!this._d.records)this._d.records=[];
    if(!this._d.best)this._d.best={};
    return this._d;
  },
  save(){try{localStorage.setItem(this.key,JSON.stringify(this._d))}catch(e){}},
  get d(){if(!this._d)this.load();return this._d}
};

/* ====== AUDIO (Procedural Web Audio) ====== */
const AUD={
  ctx:null,gain:null,
  init(){
    if(this.ctx)return;
    this.ctx=new(window.AudioContext||window.webkitAudioContext)();
    this.gain=this.ctx.createGain();
    this.gain.connect(this.ctx.destination);
    this.setVol(STO.d.vol/100);
  },
  setVol(v){if(this.gain)this.gain.gain.value=clamp(v,0,1)},
  resume(){if(this.ctx&&this.ctx.state==='suspended')this.ctx.resume()},
  play(type){
    if(!this.ctx)return;
    const t=this.ctx.currentTime;
    const mk=(f,dur,tp='sine',vol=.3)=>{
      const o=this.ctx.createOscillator(),g=this.ctx.createGain();
      o.type=tp;o.frequency.value=f;g.gain.setValueAtTime(vol,t);
      g.gain.exponentialRampToValueAtTime(.001,t+dur);
      o.connect(g);g.connect(this.gain);o.start(t);o.stop(t+dur);
    };
    const noise=(dur,vol=.1)=>{
      const sz=this.ctx.sampleRate*dur,buf=this.ctx.createBuffer(1,sz,this.ctx.sampleRate);
      const d=buf.getChannelData(0);for(let i=0;i<sz;i++)d[i]=(Math.random()*2-1)*vol;
      const s=this.ctx.createBufferSource(),g=this.ctx.createGain();
      s.buffer=buf;g.gain.setValueAtTime(vol,t);g.gain.exponentialRampToValueAtTime(.001,t+dur);
      s.connect(g);g.connect(this.gain);s.start(t);s.stop(t+dur);
    };
    switch(type){
      case'hit':mk(800,.08,'square',.4);mk(400,.15,'sine',.3);noise(.1,.15);break;
      case'putt':mk(600,.06,'sine',.25);mk(300,.1,'sine',.15);break;
      case'hole':mk(523,.15,'sine',.35);setTimeout(()=>mk(659,.15,'sine',.35),100);setTimeout(()=>mk(784,.3,'sine',.4),200);break;
      case'splash':noise(.4,.2);mk(200,.3,'sine',.15);break;
      case'bounce':mk(500,.05,'square',.2);break;
      case'ob':mk(200,.3,'sawtooth',.2);mk(150,.4,'sawtooth',.15);break;
      case'wind':noise(.5,.05);break;
      case'swing':mk(300,.1,'sine',.15);mk(600,.08,'sine',.1);noise(.08,.1);break;
      case'applause':for(let i=0;i<5;i++)setTimeout(()=>noise(.15,.08),i*60);break;
    }
  }
};

function vib(ms=20){if(STO.d.vib&&navigator.vibrate)navigator.vibrate(ms)}

'''

with open('/home/user/webapp/index.html','a',encoding='utf-8') as f:
    f.write(content)
import os
print(f"Part2 appended. Total: {os.path.getsize('/home/user/webapp/index.html')} bytes")
