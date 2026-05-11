# V8 Part 3: Scene + Materials + 3D Golfer Character + Course Builder
content = r'''
/* ====== SCENE GLOBALS ====== */
let scene,camera,renderer,clock;
let grp,grnC,grnR,teeP,holeP,flagM,bunks=[],waters=[],obB,fwPath=[];
let M={}; // materials
let golfer=null; // 3D golfer object
let sunLight,ambLight;

/* ====== SCENE INIT ====== */
function initScene(){
  scene=new THREE.Scene();
  camera=new THREE.PerspectiveCamera(50,window.innerWidth/window.innerHeight,.1,500);
  camera.position.set(0,8,12);
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});
  renderer.setSize(window.innerWidth,window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=1.2;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  document.getElementById('GC').prepend(renderer.domElement);
  clock=new THREE.Clock();
  // Lights
  sunLight=new THREE.DirectionalLight(0xfff5e0,2.5);
  sunLight.position.set(30,50,20);
  sunLight.castShadow=true;
  sunLight.shadow.mapSize.set(2048,2048);
  sunLight.shadow.camera.left=-60;sunLight.shadow.camera.right=60;
  sunLight.shadow.camera.top=60;sunLight.shadow.camera.bottom=-60;
  sunLight.shadow.camera.near=1;sunLight.shadow.camera.far=150;
  sunLight.shadow.bias=-.001;
  sunLight.shadow.normalBias=.02;
  scene.add(sunLight);
  ambLight=new THREE.AmbientLight(0x4488aa,.6);
  scene.add(ambLight);
  const hemi=new THREE.HemisphereLight(0x88bbff,0x445522,.5);
  scene.add(hemi);
  // Sky
  scene.background=TEX.sky();
  scene.environment=scene.background;
  scene.fog=new THREE.FogExp2(0xa8d4f0,.004);
  // Resize
  window.addEventListener('resize',()=>{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
  });
}

/* ====== MATERIALS ====== */
function initMaterials(){
  const gt=TEX.grass();gt.wrapS=gt.wrapT=THREE.RepeatWrapping;gt.repeat.set(12,12);
  const ft=TEX.fairway();ft.wrapS=ft.wrapT=THREE.RepeatWrapping;ft.repeat.set(2,8);
  const gnt=TEX.green();gnt.wrapS=gnt.wrapT=THREE.RepeatWrapping;
  const st=TEX.sand();st.wrapS=st.wrapT=THREE.RepeatWrapping;st.repeat.set(2,2);
  const wt=TEX.water();wt.wrapS=wt.wrapT=THREE.RepeatWrapping;wt.repeat.set(2,2);
  const dt=TEX.dirt();dt.wrapS=dt.wrapT=THREE.RepeatWrapping;dt.repeat.set(3,3);
  const bt=TEX.bark();bt.wrapS=bt.wrapT=THREE.RepeatWrapping;
  const rt=TEX.rough();rt.wrapS=rt.wrapT=THREE.RepeatWrapping;rt.repeat.set(6,6);
  M={
    grass:new THREE.MeshStandardMaterial({map:gt,roughness:.85,metalness:0}),
    fairway:new THREE.MeshStandardMaterial({map:ft,roughness:.7,metalness:0}),
    green:new THREE.MeshStandardMaterial({map:gnt,roughness:.5,metalness:0}),
    sand:new THREE.MeshStandardMaterial({map:st,roughness:.95,metalness:0}),
    water:new THREE.MeshStandardMaterial({map:wt,roughness:.1,metalness:.3,transparent:true,opacity:.85}),
    dirt:new THREE.MeshStandardMaterial({map:dt,roughness:.9,metalness:0}),
    bark:new THREE.MeshStandardMaterial({map:bt,roughness:.9,metalness:0}),
    rough:new THREE.MeshStandardMaterial({map:rt,roughness:.9,metalness:0}),
    white:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.3,metalness:.1}),
    red:new THREE.MeshStandardMaterial({color:0xcc2222,roughness:.5}),
    pole:new THREE.MeshStandardMaterial({color:0xeeeeee,roughness:.3,metalness:.5}),
    tee:new THREE.MeshStandardMaterial({color:0x44aa44,roughness:.6}),
    ob:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.5}),
    flower1:new THREE.MeshStandardMaterial({color:0xff6688,roughness:.6}),
    flower2:new THREE.MeshStandardMaterial({color:0xffaa33,roughness:.6}),
    flower3:new THREE.MeshStandardMaterial({color:0xaa44ff,roughness:.6}),
    rock:new THREE.MeshStandardMaterial({color:0x888888,roughness:.85,metalness:.05}),
    // Golfer materials
    skin:new THREE.MeshStandardMaterial({color:0xf5c6a0,roughness:.7,metalness:0}),
    shirt:new THREE.MeshStandardMaterial({color:0x2266cc,roughness:.6,metalness:0}),
    pants:new THREE.MeshStandardMaterial({color:0x334455,roughness:.7,metalness:0}),
    shoes:new THREE.MeshStandardMaterial({color:0x222222,roughness:.5,metalness:.1}),
    hat:new THREE.MeshStandardMaterial({color:0xffffff,roughness:.5,metalness:0}),
    glove:new THREE.MeshStandardMaterial({color:0xf0f0f0,roughness:.5,metalness:0}),
    club:new THREE.MeshStandardMaterial({color:0xaaaaaa,roughness:.2,metalness:.8}),
    clubGrip:new THREE.MeshStandardMaterial({color:0x333333,roughness:.8,metalness:0}),
    hair:new THREE.MeshStandardMaterial({color:0x3a2a1a,roughness:.8,metalness:0}),
  };
}

/* ====== 3D GOLFER CHARACTER ====== */
function createGolfer(){
  const g=new THREE.Group();
  g.name='golfer';
  // Scale: golfer height ~1.75m in world units (scale factor)
  const S=1;
  // Body parts as groups for animation
  // TORSO
  const torso=new THREE.Group();torso.name='torso';
  const torsoGeo=new THREE.CylinderGeometry(.14*S,.12*S,.4*S,8);
  const torsoM=new THREE.Mesh(torsoGeo,M.shirt);
  torsoM.castShadow=true;
  torso.add(torsoM);
  torso.position.y=.85*S;
  g.add(torso);
  // HIPS
  const hips=new THREE.Group();hips.name='hips';
  const hipsGeo=new THREE.CylinderGeometry(.12*S,.13*S,.12*S,8);
  const hipsM=new THREE.Mesh(hipsGeo,M.pants);
  hipsM.castShadow=true;
  hips.add(hipsM);
  hips.position.y=.62*S;
  g.add(hips);
  // HEAD
  const head=new THREE.Group();head.name='head';
  const headGeo=new THREE.SphereGeometry(.09*S,10,8);
  const headM=new THREE.Mesh(headGeo,M.skin);
  headM.castShadow=true;
  head.add(headM);
  // Hair
  const hairGeo=new THREE.SphereGeometry(.093*S,10,8,0,Math.PI*2,0,Math.PI*.55);
  const hairM=new THREE.Mesh(hairGeo,M.hair);
  hairM.position.y=.01*S;
  head.add(hairM);
  // Cap visor
  const capGeo=new THREE.CylinderGeometry(.1*S,.1*S,.03*S,10);
  const capM=new THREE.Mesh(capGeo,M.hat);
  capM.position.y=.06*S;
  capM.castShadow=true;
  head.add(capM);
  const visorGeo=new THREE.BoxGeometry(.08*S,.01*S,.06*S);
  const visorM=new THREE.Mesh(visorGeo,M.hat);
  visorM.position.set(0,.05*S,.08*S);
  head.add(visorM);
  head.position.y=1.15*S;
  torso.add(head);
  // LEFT ARM (front arm in stance)
  const lArm=new THREE.Group();lArm.name='leftArm';
  const lUpperGeo=new THREE.CylinderGeometry(.035*S,.03*S,.22*S,6);
  const lUpperM=new THREE.Mesh(lUpperGeo,M.shirt);
  lUpperM.position.y=-.11*S;lUpperM.castShadow=true;
  lArm.add(lUpperM);
  const lForearm=new THREE.Group();lForearm.name='leftForearm';
  const lForeGeo=new THREE.CylinderGeometry(.03*S,.025*S,.2*S,6);
  const lForeM=new THREE.Mesh(lForeGeo,M.skin);
  lForeM.position.y=-.1*S;lForeM.castShadow=true;
  lForearm.add(lForeM);
  // Left hand
  const lHandGeo=new THREE.SphereGeometry(.025*S,6,6);
  const lHandM=new THREE.Mesh(lHandGeo,M.glove);
  lHandM.position.y=-.2*S;
  lForearm.add(lHandM);
  lForearm.position.y=-.22*S;
  lArm.add(lForearm);
  lArm.position.set(.17*S,.05*S,0);
  torso.add(lArm);
  // RIGHT ARM (back arm)
  const rArm=new THREE.Group();rArm.name='rightArm';
  const rUpperGeo=new THREE.CylinderGeometry(.035*S,.03*S,.22*S,6);
  const rUpperM=new THREE.Mesh(rUpperGeo,M.shirt);
  rUpperM.position.y=-.11*S;rUpperM.castShadow=true;
  rArm.add(rUpperM);
  const rForearm=new THREE.Group();rForearm.name='rightForearm';
  const rForeGeo=new THREE.CylinderGeometry(.03*S,.025*S,.2*S,6);
  const rForeM=new THREE.Mesh(rForeGeo,M.skin);
  rForeM.position.y=-.1*S;rForeM.castShadow=true;
  rForearm.add(rForeM);
  const rHandGeo=new THREE.SphereGeometry(.025*S,6,6);
  const rHandM=new THREE.Mesh(rHandGeo,M.skin);
  rHandM.position.y=-.2*S;
  rForearm.add(rHandM);
  rForearm.position.y=-.22*S;
  rArm.add(rForearm);
  rArm.position.set(-.17*S,.05*S,0);
  torso.add(rArm);
  // LEFT LEG
  const lLeg=new THREE.Group();lLeg.name='leftLeg';
  const lThighGeo=new THREE.CylinderGeometry(.05*S,.04*S,.28*S,6);
  const lThighM=new THREE.Mesh(lThighGeo,M.pants);
  lThighM.position.y=-.14*S;lThighM.castShadow=true;
  lLeg.add(lThighM);
  const lShin=new THREE.Group();lShin.name='leftShin';
  const lShinGeo=new THREE.CylinderGeometry(.04*S,.035*S,.28*S,6);
  const lShinM=new THREE.Mesh(lShinGeo,M.pants);
  lShinM.position.y=-.14*S;lShinM.castShadow=true;
  lShin.add(lShinM);
  const lFootGeo=new THREE.BoxGeometry(.05*S,.03*S,.1*S);
  const lFootM=new THREE.Mesh(lFootGeo,M.shoes);
  lFootM.position.set(0,-.29*S,.02*S);lFootM.castShadow=true;
  lShin.add(lFootM);
  lShin.position.y=-.28*S;
  lLeg.add(lShin);
  lLeg.position.set(.07*S,0,0);
  hips.add(lLeg);
  // RIGHT LEG
  const rLeg=new THREE.Group();rLeg.name='rightLeg';
  const rThighGeo=new THREE.CylinderGeometry(.05*S,.04*S,.28*S,6);
  const rThighM=new THREE.Mesh(rThighGeo,M.pants);
  rThighM.position.y=-.14*S;rThighM.castShadow=true;
  rLeg.add(rThighM);
  const rShin=new THREE.Group();rShin.name='rightShin';
  const rShinGeo=new THREE.CylinderGeometry(.04*S,.035*S,.28*S,6);
  const rShinM=new THREE.Mesh(rShinGeo,M.pants);
  rShinM.position.y=-.14*S;rShinM.castShadow=true;
  rShin.add(rShinM);
  const rFootGeo=new THREE.BoxGeometry(.05*S,.03*S,.1*S);
  const rFootM=new THREE.Mesh(rFootGeo,M.shoes);
  rFootM.position.set(0,-.29*S,.02*S);rFootM.castShadow=true;
  rShin.add(rFootM);
  rShin.position.y=-.28*S;
  rLeg.add(rShin);
  rLeg.position.set(-.07*S,0,0);
  hips.add(rLeg);
  // GOLF CLUB (attached to hands)
  const clubGrp=new THREE.Group();clubGrp.name='golfClub';
  // Shaft
  const shaftGeo=new THREE.CylinderGeometry(.006*S,.006*S,.7*S,6);
  const shaftM=new THREE.Mesh(shaftGeo,M.club);
  shaftM.position.y=-.35*S;
  clubGrp.add(shaftM);
  // Grip
  const gripGeo=new THREE.CylinderGeometry(.009*S,.008*S,.15*S,6);
  const gripM=new THREE.Mesh(gripGeo,M.clubGrip);
  gripM.position.y=0;
  clubGrp.add(gripM);
  // Club head
  const headG=new THREE.Group();
  const chGeo=new THREE.BoxGeometry(.06*S,.02*S,.04*S);
  const chM=new THREE.Mesh(chGeo,M.club);
  chM.castShadow=true;
  headG.add(chM);
  headG.position.y=-.7*S;
  headG.rotation.z=Math.PI*.05;
  clubGrp.add(headG);
  clubGrp.position.set(0,-.2*S,0);
  // Attach club to left forearm
  lForearm.add(clubGrp);
  // Shadow on ground
  const shadowGeo=new THREE.CircleGeometry(.2*S,12);
  const shadowMat=new THREE.MeshBasicMaterial({color:0x000000,transparent:true,opacity:.25,depthWrite:false});
  const shadowM=new THREE.Mesh(shadowGeo,shadowMat);
  shadowM.rotation.x=-Math.PI/2;
  shadowM.position.y=.005;
  shadowM.name='golferShadow';
  g.add(shadowM);
  // Store references for animation
  g.userData={
    torso,hips,head,
    lArm,lForearm,rArm,rForearm,
    lLeg,lShin,rLeg,rShin,
    clubGrp,
    // Animation state
    animPhase:'idle', // idle, address, backswing, downswing, impact, followthrough
    animTime:0,
    animSpeed:1,
    swingPower:0,
  };
  g.scale.set(1.8,1.8,1.8);
  return g;
}

/* ====== GOLFER POSE FUNCTIONS ====== */
const POSE={
  idle(g){
    const u=g.userData;
    u.torso.rotation.set(0,0,0);
    u.hips.rotation.set(0,0,0);
    u.lArm.rotation.set(.1,0,0);
    u.lForearm.rotation.set(0,0,0);
    u.rArm.rotation.set(.1,0,0);
    u.rForearm.rotation.set(0,0,0);
    u.lLeg.rotation.set(0,0,0);
    u.lShin.rotation.set(0,0,0);
    u.rLeg.rotation.set(0,0,0);
    u.rShin.rotation.set(0,0,0);
    u.clubGrp.visible=true;
  },
  address(g){
    const u=g.userData;
    // Slight forward bend, club down
    u.torso.rotation.set(.2,0,0);
    u.hips.rotation.set(.05,0,0);
    u.lArm.rotation.set(.6,0,.15);
    u.lForearm.rotation.set(.2,0,0);
    u.rArm.rotation.set(.6,0,-.15);
    u.rForearm.rotation.set(.2,0,0);
    u.lLeg.rotation.set(-.05,0,-.03);
    u.lShin.rotation.set(.08,0,0);
    u.rLeg.rotation.set(-.05,0,.03);
    u.rShin.rotation.set(.08,0,0);
    u.clubGrp.visible=true;
  },
  backswing(g,t){
    // t: 0-1 progress of backswing
    const u=g.userData;
    const T=clamp(t,0,1);
    u.torso.rotation.set(.15-T*.1, T*.6, T*.05);
    u.hips.rotation.set(.05, T*.15, 0);
    // Arms go up and back
    u.lArm.rotation.set(.5-T*.8, T*.3, .15+T*.2);
    u.lForearm.rotation.set(.2+T*1.2, 0, 0);
    u.rArm.rotation.set(.5+T*.3, -T*.4, -.15-T*.3);
    u.rForearm.rotation.set(.2+T*.8, 0, 0);
    // Weight shift
    u.lLeg.rotation.set(-.05+T*.05, 0, -.03);
    u.lShin.rotation.set(.08, 0, 0);
    u.rLeg.rotation.set(-.05-T*.08, 0, .03);
    u.rShin.rotation.set(.08+T*.1, 0, 0);
    u.head.rotation.set(0, -T*.2, 0);
  },
  downswing(g,t){
    // t: 0-1 progress of downswing (fast)
    const u=g.userData;
    const T=clamp(t,0,1);
    // Reverse backswing rapidly
    const bk=1-T; // remaining backswing
    u.torso.rotation.set(.15-.1*bk+T*.15, .6*bk-T*.3, .05*bk);
    u.hips.rotation.set(.05, .15*bk-T*.2, 0);
    u.lArm.rotation.set(.5-.8*bk+T*.5, .3*bk-T*.1, .15+.2*bk-T*.1);
    u.lForearm.rotation.set(.2+1.2*bk-T*1.0, 0, 0);
    u.rArm.rotation.set(.5+.3*bk-T*.5, -.4*bk+T*.2, -.15-.3*bk+T*.2);
    u.rForearm.rotation.set(.2+.8*bk-T*.6, 0, 0);
    u.lLeg.rotation.set(-.05+.05*bk-T*.03, 0, -.03);
    u.rLeg.rotation.set(-.05-.08*bk+T*.05, 0, .03);
    u.head.rotation.set(0, -.2*bk+T*.1, 0);
  },
  impact(g){
    const u=g.userData;
    u.torso.rotation.set(.3, -.3, 0);
    u.hips.rotation.set(.05, -.2, 0);
    u.lArm.rotation.set(1.0, -.1, .05);
    u.lForearm.rotation.set(.2, 0, 0);
    u.rArm.rotation.set(.2, .2, .05);
    u.rForearm.rotation.set(.2, 0, 0);
    u.lLeg.rotation.set(-.08, 0, -.03);
    u.rLeg.rotation.set(.0, 0, .03);
    u.head.rotation.set(0, .1, 0);
  },
  followthrough(g,t){
    const u=g.userData;
    const T=clamp(t,0,1);
    u.torso.rotation.set(.1+T*.1, -.3-T*.5, -T*.05);
    u.hips.rotation.set(.0, -.2-T*.3, 0);
    u.lArm.rotation.set(1.0-T*1.5, -.1-T*.3, .05-T*.2);
    u.lForearm.rotation.set(.2+T*.5, 0, 0);
    u.rArm.rotation.set(.2-T*.8, .2+T*.4, .05+T*.3);
    u.rForearm.rotation.set(.2+T*.6, 0, 0);
    u.lLeg.rotation.set(-.08+T*.1, 0, -.03+T*.03);
    u.rLeg.rotation.set(.0-T*.15, 0, .03);
    u.rShin.rotation.set(.08+T*.2,0,0);
    u.head.rotation.set(-T*.1, .1+T*.3, 0);
  },
  putt_address(g){
    const u=g.userData;
    u.torso.rotation.set(.25,0,0);
    u.hips.rotation.set(.08,0,0);
    u.lArm.rotation.set(.5,0,.08);
    u.lForearm.rotation.set(.15,0,0);
    u.rArm.rotation.set(.5,0,-.08);
    u.rForearm.rotation.set(.15,0,0);
    u.lLeg.rotation.set(-.03,0,-.04);
    u.rLeg.rotation.set(-.03,0,.04);
    u.head.rotation.set(.1,0,0);
  },
  putt_stroke(g,t){
    // t: -1 to 1 (back to forward)
    const u=g.userData;
    u.torso.rotation.set(.25,0,0);
    u.lArm.rotation.set(.5+t*.2,0,.08);
    u.lForearm.rotation.set(.15-t*.1,0,0);
    u.rArm.rotation.set(.5+t*.2,0,-.08);
    u.rForearm.rotation.set(.15-t*.1,0,0);
  }
};

/* ====== SWING ANIMATION CONTROLLER ====== */
const SWING_ANIM={
  active:false,
  phase:'idle',
  time:0,
  power:0,
  isPutt:false,
  callback:null,
  durations:{backswing:.6,downswing:.18,impact:.05,followthrough:.8},
  start(power,isPutt,cb){
    this.active=true;
    this.phase=isPutt?'putt_back':'backswing';
    this.time=0;
    this.power=power;
    this.isPutt=isPutt;
    this.callback=cb;
    if(!isPutt){
      AUD.play('swing');
    }
  },
  update(dt){
    if(!this.active||!golfer)return;
    this.time+=dt;
    if(this.isPutt){
      this._updatePutt();
    }else{
      this._updateFull();
    }
  },
  _updateFull(){
    const d=this.durations;
    switch(this.phase){
      case'backswing':{
        const t=this.time/d.backswing;
        POSE.backswing(golfer,t);
        if(t>=1){this.phase='downswing';this.time=0;}
        break;
      }
      case'downswing':{
        const t=this.time/d.downswing;
        POSE.downswing(golfer,t);
        if(t>=1){
          this.phase='impact';this.time=0;
          // Fire ball at impact
          if(this.callback){this.callback();this.callback=null;}
          vib(30);
        }
        break;
      }
      case'impact':{
        const t=this.time/d.impact;
        POSE.impact(golfer);
        if(t>=1){this.phase='followthrough';this.time=0;}
        break;
      }
      case'followthrough':{
        const t=this.time/d.followthrough;
        POSE.followthrough(golfer,t);
        if(t>=1){this.active=false;this.phase='idle';}
        break;
      }
    }
  },
  _updatePutt(){
    const totalDur=.6;
    const t=this.time/totalDur;
    if(t<.4){
      // Back stroke
      POSE.putt_stroke(golfer,-(t/.4));
    }else if(t<.6){
      // Forward through impact
      const ft=(t-.4)/.2;
      POSE.putt_stroke(golfer,-1+ft*2);
      if(t>=.5&&this.callback){this.callback();this.callback=null;vib(15);}
    }else if(t<1){
      const ft=(t-.6)/.4;
      POSE.putt_stroke(golfer,1-ft);
    }else{
      this.active=false;this.phase='idle';
      POSE.putt_address(golfer);
    }
  },
  reset(){
    this.active=false;this.phase='idle';this.time=0;
  }
};

/* ====== COURSE BUILDER ====== */
function mkTree(type,x,z,scale=1){
  const g=new THREE.Group();
  const s=(.7+Math.random()*.6)*scale;
  if(type==='palm'){
    // Palm tree
    const pts=[];
    for(let i=0;i<=10;i++){
      const t=i/10;
      pts.push(new THREE.Vector3(Math.sin(t*1.5)*.3*s,t*3*s,Math.cos(t*.5)*.1*s));
    }
    const curve=new THREE.CatmullRomCurve3(pts);
    const trunk=new THREE.Mesh(new THREE.TubeGeometry(curve,12,0.06*s,6,false),M.bark);
    trunk.castShadow=true;g.add(trunk);
    for(let i=0;i<7;i++){
      const a=i/7*Math.PI*2;
      const len=1.2*s+Math.random()*.5*s;
      const shape=new THREE.Shape();
      shape.moveTo(0,0);shape.quadraticCurveTo(len*.3,.15*s,len,-.1*s);
      shape.quadraticCurveTo(len*.3,-.05*s,0,0);
      const frond=new THREE.Mesh(new THREE.ShapeGeometry(shape),new THREE.MeshStandardMaterial({color:0x228833,roughness:.7,side:THREE.DoubleSide}));
      frond.position.copy(pts[10]);
      frond.rotation.set(-.3+Math.random()*.3,a,Math.random()*.2-.1);
      frond.castShadow=true;g.add(frond);
    }
  }else if(type==='pine'){
    const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.04*s,.06*s,2*s,6),M.bark);
    trunk.position.y=s;trunk.castShadow=true;g.add(trunk);
    for(let i=0;i<4;i++){
      const y=.8*s+i*.5*s;
      const r=(.7-i*.12)*s;
      const h=.6*s;
      const cone=new THREE.Mesh(new THREE.ConeGeometry(r,h,8),new THREE.MeshStandardMaterial({color:new THREE.Color().setHSL(.28+Math.random()*.05,.6,.25+i*.05),roughness:.8}));
      cone.position.y=y+h/2;cone.castShadow=true;cone.receiveShadow=true;g.add(cone);
    }
  }else{
    // Deciduous
    const trunk=new THREE.Mesh(new THREE.CylinderGeometry(.04*s,.07*s,1.5*s,6),M.bark);
    trunk.position.y=.75*s;trunk.castShadow=true;g.add(trunk);
    const canopyColors=[0x2d8a2d,0x3a9a3a,0x228822,0x44aa44];
    for(let i=0;i<5;i++){
      const r=(.4+Math.random()*.3)*s;
      const sphere=new THREE.Mesh(new THREE.SphereGeometry(r,8,6),new THREE.MeshStandardMaterial({color:canopyColors[i%canopyColors.length],roughness:.75}));
      sphere.position.set((Math.random()-.5)*.3*s,1.5*s+Math.random()*.5*s,(Math.random()-.5)*.3*s);
      sphere.castShadow=true;sphere.receiveShadow=true;g.add(sphere);
    }
  }
  g.position.set(x,0,z);
  return g;
}

function mkMountains(){
  const g=new THREE.Group();
  for(let layer=0;layer<2;layer++){
    const dist=80+layer*40;
    const color=layer===0?0x3a6a3a:0x5a8a5a;
    const peaks=8+layer*4;
    const verts=[],indices=[];
    for(let i=0;i<=peaks;i++){
      const angle=(i/peaks)*Math.PI*2;
      const r=dist+Math.random()*10;
      const x=Math.cos(angle)*r,z=Math.sin(angle)*r;
      const h=(8+Math.random()*15)*(layer===0?1:.7);
      verts.push(x,0,z,x,h,z);
      if(i<peaks){
        const b=i*2;
        indices.push(b,b+1,b+2,b+1,b+3,b+2);
      }
    }
    const geo=new THREE.BufferGeometry();
    geo.setAttribute('position',new THREE.Float32BufferAttribute(verts,3));
    geo.setIndex(indices);geo.computeVertexNormals();
    const mat=new THREE.MeshStandardMaterial({color,roughness:.85,flatShading:true});
    const mesh=new THREE.Mesh(geo,mat);
    mesh.receiveShadow=true;g.add(mesh);
  }
  return g;
}

function buildCourse(ci,hi){
  if(grp){scene.remove(grp)}
  grp=new THREE.Group();
  bunks=[];waters=[];fwPath=[];
  const c=COURSES[ci],seed=ci*100+hi;
  const rng=mulberry32(seed);
  const par=c.par[hi],dist=c.dist[hi];
  // Tee and hole positions
  teeP=new THREE.Vector3(0,0,0);
  const angle=rng()*Math.PI*.4-.2;
  holeP=new THREE.Vector3(Math.sin(angle)*dist*.3,0,-dist*.3);
  // Ground plane with gentle undulation
  const gndSize=120;
  const gndSeg=60;
  const gndGeo=new THREE.PlaneGeometry(gndSize,gndSize,gndSeg,gndSeg);
  const posArr=gndGeo.attributes.position.array;
  for(let i=0;i<posArr.length;i+=3){
    const gx=posArr[i],gy=posArr[i+1];
    posArr[i+2]=Math.sin(gx*.05)*Math.cos(gy*.05)*.3+Math.sin(gx*.12+gy*.08)*.15;
  }
  gndGeo.computeVertexNormals();
  const gnd=new THREE.Mesh(gndGeo,M.grass);
  gnd.rotation.x=-Math.PI/2;
  gnd.receiveShadow=true;
  grp.add(gnd);
  // Fairway path - curved
  const midX=(teeP.x+holeP.x)/2+(rng()-.5)*dist*.15;
  const midZ=(teeP.z+holeP.z)/2;
  const pts=20;
  for(let i=0;i<=pts;i++){
    const t=i/pts;
    const t2=t*t,t3=t2*t;
    const x=teeP.x*(1-t)*(1-t)+2*midX*t*(1-t)+holeP.x*t*t;
    const z=teeP.z*(1-t)+holeP.z*t;
    fwPath.push(new THREE.Vector3(x,0.01,z));
  }
  // Fairway as thick strip
  const fwW=2.5+dist*.015;
  for(let i=0;i<fwPath.length-1;i++){
    const p1=fwPath[i],p2=fwPath[i+1];
    const dx=p2.x-p1.x,dz=p2.z-p1.z;
    const len=Math.sqrt(dx*dx+dz*dz);
    const fw=new THREE.Mesh(new THREE.PlaneGeometry(fwW,len),M.fairway);
    fw.rotation.x=-Math.PI/2;
    fw.rotation.z=-Math.atan2(dz,dx)+Math.PI/2;
    fw.position.set((p1.x+p2.x)/2,.015,(p1.z+p2.z)/2);
    fw.receiveShadow=true;grp.add(fw);
    // Rough borders
    for(const side of[-1,1]){
      const rw=new THREE.Mesh(new THREE.PlaneGeometry(fwW*.6,len),M.rough);
      const nx=-dz/len*side,nz=dx/len*side;
      rw.rotation.x=-Math.PI/2;
      rw.rotation.z=-Math.atan2(dz,dx)+Math.PI/2;
      rw.position.set((p1.x+p2.x)/2+nx*(fwW*.5+fwW*.3),.012,(p1.z+p2.z)/2+nz*(fwW*.5+fwW*.3));
      rw.receiveShadow=true;grp.add(rw);
    }
  }
  // Tee box
  const teeBox=new THREE.Mesh(new THREE.PlaneGeometry(2,2.5),M.tee);
  teeBox.rotation.x=-Math.PI/2;teeBox.position.set(teeP.x,.02,teeP.z);
  teeBox.receiveShadow=true;grp.add(teeBox);
  // Tee markers
  for(const sx of[-.6,.6]){
    const marker=new THREE.Mesh(new THREE.SphereGeometry(.06,8,6),M.white);
    marker.position.set(teeP.x+sx,.06,teeP.z+.8);
    marker.castShadow=true;grp.add(marker);
  }
  // Green
  grnR=2.5+dist*.01;
  grnC=holeP.clone();
  const greenMesh=new THREE.Mesh(new THREE.CircleGeometry(grnR,32),M.green);
  greenMesh.rotation.x=-Math.PI/2;greenMesh.position.set(grnC.x,.025,grnC.z);
  greenMesh.receiveShadow=true;grp.add(greenMesh);
  // Fringe
  const fringe=new THREE.Mesh(new THREE.RingGeometry(grnR,grnR+.5,32),M.fairway);
  fringe.rotation.x=-Math.PI/2;fringe.position.set(grnC.x,.018,grnC.z);
  fringe.receiveShadow=true;grp.add(fringe);
  // Hole cup
  const cup=new THREE.Mesh(new THREE.CylinderGeometry(.054,.054,.05,16),new THREE.MeshStandardMaterial({color:0x111111}));
  cup.position.set(holeP.x,.0,holeP.z);grp.add(cup);
  // Flag
  const pole=new THREE.Mesh(new THREE.CylinderGeometry(.008,.008,1.2,6),M.pole);
  pole.position.set(holeP.x,.6,holeP.z);pole.castShadow=true;grp.add(pole);
  const flagShape=new THREE.Shape();
  flagShape.moveTo(0,0);flagShape.lineTo(.3,-.08);flagShape.lineTo(0,-.16);
  flagM=new THREE.Mesh(new THREE.ShapeGeometry(flagShape),M.red);
  flagM.position.set(holeP.x+.008,1.18,holeP.z);
  flagM.castShadow=true;grp.add(flagM);
  // Bunkers
  const hasBunker=rng()>.3;
  if(hasBunker){
    const nb=1+Math.floor(rng()*2);
    for(let i=0;i<nb;i++){
      const bt=.5+rng()*.4;
      const bp=new THREE.Vector3();
      bp.lerpVectors(teeP,holeP,bt);
      const off=(rng()-.5)*fwW*1.5;
      const bpx=bp.x+off,bpz=bp.z+(rng()-.5)*2;
      const br=.8+rng()*.8;
      const bMesh=new THREE.Mesh(new THREE.CircleGeometry(br,16),M.sand);
      bMesh.rotation.x=-Math.PI/2;bMesh.position.set(bpx,.022,bpz);
      bMesh.receiveShadow=true;grp.add(bMesh);
      // Lip
      const lip=new THREE.Mesh(new THREE.TorusGeometry(br,.06,6,24),new THREE.MeshStandardMaterial({color:0xc4a44a,roughness:.8}));
      lip.rotation.x=-Math.PI/2;lip.position.set(bpx,.05,bpz);
      lip.castShadow=true;grp.add(lip);
      bunks.push({x:bpx,z:bpz,r:br});
    }
  }
  // Water hazards
  const hasWater=c.water.includes(hi+1);
  if(hasWater){
    const wt=.3+rng()*.4;
    const wp=new THREE.Vector3();wp.lerpVectors(teeP,holeP,wt);
    const woff=(rng()>.5?1:-1)*(fwW*.8+rng()*2);
    const wx=wp.x+woff,wz=wp.z+(rng()-.5)*3;
    const ww=3+rng()*3,wh=2+rng()*2;
    const wMesh=new THREE.Mesh(new THREE.PlaneGeometry(ww,wh),M.water);
    wMesh.rotation.x=-Math.PI/2;wMesh.position.set(wx,.01,wz);
    wMesh.receiveShadow=true;wMesh.name='water';grp.add(wMesh);
    waters.push({x:wx,z:wz,w:ww/2,h:wh/2,mesh:wMesh});
    // Rocks around water
    for(let i=0;i<6;i++){
      const ra=rng()*Math.PI*2;
      const rd=Math.max(ww,wh)/2+.2+rng()*.5;
      const rock=new THREE.Mesh(new THREE.DodecahedronGeometry(.15+rng()*.2,0),M.rock);
      rock.position.set(wx+Math.cos(ra)*rd,.1,wz+Math.sin(ra)*rd);
      rock.rotation.set(rng(),rng(),rng());
      rock.castShadow=true;grp.add(rock);
    }
  }
  // Trees
  const treeType=c.trees==='mixed'?(rng()>.5?'deciduous':'pine'):c.trees;
  const nTrees=10+Math.floor(rng()*10);
  for(let i=0;i<nTrees;i++){
    const ta=rng()*Math.PI*2;
    const td=5+rng()*40;
    const tx=Math.cos(ta)*td,tz=-dist*.15+Math.sin(ta)*td;
    // Don't place on fairway
    let onFw=false;
    for(const fp of fwPath){if(Math.hypot(tx-fp.x,tz-fp.z)<fwW*1.2){onFw=true;break}}
    if(onFw)continue;
    const tt=c.trees==='mixed'?(['deciduous','pine','palm'][Math.floor(rng()*3)]):treeType;
    grp.add(mkTree(tt,tx,tz,.8+rng()*.4));
  }
  // Flowers
  const nFlowers=5+Math.floor(rng()*8);
  for(let i=0;i<nFlowers;i++){
    const fa=rng()*Math.PI*2;
    const fd=4+rng()*20;
    const fx=Math.cos(fa)*fd,fz=-dist*.15+Math.sin(fa)*fd;
    const fMats=[M.flower1,M.flower2,M.flower3];
    const flower=new THREE.Mesh(new THREE.SphereGeometry(.08+rng()*.06,6,4),fMats[Math.floor(rng()*3)]);
    flower.position.set(fx,.08+rng()*.05,fz);
    flower.castShadow=true;grp.add(flower);
    // Stem
    const stem=new THREE.Mesh(new THREE.CylinderGeometry(.008,.008,.1,4),new THREE.MeshStandardMaterial({color:0x228822}));
    stem.position.set(fx,.04,fz);grp.add(stem);
  }
  // Cart path
  const cpGeo=new THREE.PlaneGeometry(.6,dist*.35);
  const cp=new THREE.Mesh(cpGeo,M.dirt);
  cp.rotation.x=-Math.PI/2;
  cp.position.set(teeP.x+fwW+1.5,.013,(teeP.z+holeP.z)/2);
  cp.receiveShadow=true;grp.add(cp);
  // OB markers
  obB=15+dist*.12;
  for(let a=0;a<Math.PI*2;a+=Math.PI/6){
    const ox=Math.cos(a)*obB,oz=-dist*.15+Math.sin(a)*obB;
    const obM=new THREE.Mesh(new THREE.CylinderGeometry(.02,.02,.4,4),M.ob);
    obM.position.set(ox,.2,oz);grp.add(obM);
  }
  // Mountains
  grp.add(mkMountains());
  scene.add(grp);
}

'''

with open('/home/user/webapp/index.html','a',encoding='utf-8') as f:
    f.write(content)
import os
print(f"Part3 appended. Total: {os.path.getsize('/home/user/webapp/index.html')} bytes")
