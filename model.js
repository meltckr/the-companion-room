/** Architectural concept viewer. Dimensions are metres; layout remains conceptual. */
export function createSpaViewer(canvas, options = {}) {
  const gl = canvas.getContext('webgl2', { antialias: true, alpha: false, preserveDrawingBuffer: true });
  if (!gl) {
    canvas.dataset.ready = 'false';
    const error = new Error('The interactive tour needs a browser with WebGL 2 enabled.');
    options.onError?.(error);
    return { setView() {}, setSeason() {}, setFutureBay() {}, resize() {}, capture: () => null, exportScene: () => null, destroy() {} };
  }
  let disposed = false, frame = 0, view = 'overview', future = false, season = 'winter';
  let yaw = .57, pitch = .74, radius = 13.5;
  let eye = [0, 1.65, 2.9], heading = 0, tilt = -.08;
  const target = [0, .45, -.1], points = [], items = [], removers = [];
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const add = (a, b) => a.map((v, i) => v + b[i]);
  const sub = (a, b) => a.map((v, i) => v - b[i]);
  const dot = (a, b) => a.reduce((v, n, i) => v + n * b[i], 0);
  const cross = (a, b) => [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const norm = a => { const d = Math.hypot(...a) || 1; return a.map(v => v / d); };
  const color = hex => [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16) / 255);
  const C = { stone: color('d7d0bf'), wall: color('ece8dd'), oak: color('b18b61'), green: color('405b50'), dark: color('263c34'), steel: color('aebbb6'), white: color('f4f2e9'), gold: color('bfaa78'), mat: color('6b7167'), black: color('303b36'), light: color('fff1c7') };
  function multiply(a,b) { const out = new Float32Array(16); for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)out[c*4+r]+=a[k*4+r]*b[c*4+k]; return out; }
  function lookAt(e,t,up=[0,1,0]) { const z=norm(sub(e,t)),x=norm(cross(up,z)),y=cross(z,x); return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,e),-dot(y,e),-dot(z,e),1]); }
  function perspective(fov,aspect,near,far) { const f=1/Math.tan(fov/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]); }
  function ortho(l,r,b,t,n,f) {return new Float32Array([2/(r-l),0,0,0,0,2/(t-b),0,0,0,0,-2/(f-n),0,-(r+l)/(r-l),-(t+b)/(t-b),-(f+n)/(f-n),1]);}
  function vertex(p,n,c,rough=.7,kind=0) {points.push(...p,...n,...c,rough,kind);}
  function tri(a,b,c,col,rough=.7,kind=0) { const n=norm(cross(sub(b,a),sub(c,a))); vertex(a,n,col,rough,kind);vertex(b,n,col,rough,kind);vertex(c,n,col,rough,kind); }
  let group='all';
  function object(fn) { const start=points.length/11;fn();items.push({start,count:points.length/11-start,group}); }
  function box(x,y,z,w,h,d,col,rough=.7,kind=0) {
    object(()=>{const x0=x-w/2,x1=x+w/2,y0=y-h/2,y1=y+h/2,z0=z-d/2,z1=z+d/2;
      const faces=[[[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],[[x1,y0,z0],[x0,y0,z0],[x0,y1,z0],[x1,y1,z0]],[[x0,y0,z0],[x0,y0,z1],[x0,y1,z1],[x0,y1,z0]],[[x1,y0,z1],[x1,y0,z0],[x1,y1,z0],[x1,y1,z1]],[[x0,y1,z1],[x1,y1,z1],[x1,y1,z0],[x0,y1,z0]],[[x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1]]];
      for(const [a,b,c,d] of faces){tri(a,b,c,col,rough,kind);tri(a,c,d,col,rough,kind);}
    });
  }
  function rod(a,b,r,col,segments=12,rough=.3) {object(()=>{const axis=norm(sub(b,a)),u=norm(cross(axis,Math.abs(axis[1])>.9?[1,0,0]:[0,1,0])),v=cross(axis,u);
    for(let i=0;i<segments;i++){const p=i/segments*Math.PI*2,q=(i+1)/segments*Math.PI*2;const off=t=>u.map((n,k)=>r*(n*Math.cos(t)+v[k]*Math.sin(t)));const a0=add(a,off(p)),a1=add(a,off(q)),b0=add(b,off(p)),b1=add(b,off(q));tri(a0,a1,b1,col,rough);tri(a0,b1,b0,col,rough);tri(a,a1,a0,col,rough);tri(b,b0,b1,col,rough);}
  });}
  function hose(cx,y,cz,r=.25) { for(let i=0;i<24;i++){const a=i/24*Math.PI*1.8,b=(i+1)/24*Math.PI*1.8;rod([cx+r*Math.cos(a),y+r*Math.sin(a),cz],[cx+r*Math.cos(b),y+r*Math.sin(b),cz],.018,C.black,6);}}
  function bottle(x,y,z,c=C.green) {rod([x,y,z],[x,y+.18,z],.045,c,12,.45);rod([x,y+.18,z],[x,y+.225,z],.018,C.black,8);box(x+.025,y+.235,z,.08,.02,.025,C.black);}
  function animalRamp(x,z,width=.68) {
    // Schematic animal-access ramp; final slope, grip and gate require equipment review.
    const left=x-width/2,right=x+width/2,back=z+.43,front=z+1.7,high=.50,low=.035;
    object(()=>{
      const a=[left,high,back],b=[right,high,back],c=[right,low,front],d=[left,low,front];
      tri(a,d,c,C.mat,.95);tri(a,c,b,C.mat,.95);
      tri([left,.02,back],[left,.02,front],d,C.steel,.5);tri([left,.02,back],d,a,C.steel,.5);
      tri([right,.02,back],b,c,C.steel,.5);tri([right,.02,back],c,[right,.02,front],C.steel,.5);
    });
    for(let i=1;i<11;i++){const t=i/11;box(x,high+(low-high)*t+.009,back+(front-back)*t,width-.05,.018,.025,C.black);}
    rod([left,high+.035,back],[left,low+.035,front],.025,C.steel);
    rod([right,high+.035,back],[right,low+.035,front],.025,C.steel);
  }
  function dryerHose(x,z) {
    const path=[[x+.56,1.44,z-.31],[x+.65,1.22,z-.25],[x+.61,.96,z-.18],[x+.42,.87,z-.06],[x+.22,.98,z+.08],[x+.3,1.19,z+.14]];
    for(let i=0;i<path.length-1;i++){
      const a=path[i],b=path[i+1];rod(a,b,.037,C.black,10,.7);
      const length=Math.hypot(...sub(b,a)),sections=Math.ceil(length/.034);
      for(let j=0;j<sections;j++){const t=j/sections,u=Math.min(1,t+.018/length);rod(a.map((v,k)=>v+(b[k]-v)*t),a.map((v,k)=>v+(b[k]-v)*u),.043,C.dark,10,.65);}
    }
    rod([x+.3,1.19,z+.14],[x+.22,1.26,z+.32],.055,C.black,14,.45);
    rod([x+.22,1.26,z+.32],[x+.2,1.28,z+.37],.044,C.black,14,.45);
    box(x+.56,1.45,z-.37,.12,.14,.12,C.dark,.55);
  }
  function tub(x,z,w=1.65) {
    // Generic integrated wash/dry unit: schematic, not a branded equipment model.
    box(x,.24,z,w,.43,.84,C.green,.55);
    box(x,.47,z,w+.06,.08,.91,C.steel,.22);
    box(x,.515,z,w-.13,.04,.73,C.white,.35);
    box(x-w/2+.045,.81,z,.09,.64,.9,C.steel,.22);
    box(x+w/2-.045,.81,z,.09,.64,.9,C.steel,.22);
    box(x,1.0,z-.405,w,1.02,.09,C.steel,.22);
    // Open entry between front splash wings; a manufacturer-approved gate is to be selected.
    const wing=(w-.70)/2;
    for(const sign of [-1,1])box(x+sign*(.35+wing/2),.81,z+.405,wing,.64,.09,C.steel,.22);
    box(x,.54,z,w-.2,.015,.62,C.mat,.8);
    for(let i=-3;i<=3;i++)box(x+i*.15,.553,z,.016,.008,.59,C.black);
    // Separate thin wash spray and thick dark dryer hose, both within reach of the basin.
    rod([x-.52,1.12,z-.3],[x-.52,1.38,z-.3],.022,C.steel);
    rod([x-.52,1.38,z-.3],[x-.52,1.38,z-.06],.022,C.steel);
    hose(x-.42,1.2,z-.28,.18);
    rod([x-.25,1.22,z-.23],[x-.25,1.38,z-.23],.026,C.steel);
    dryerHose(x,z);
    // Rear controls use four distinct physical buttons with a stop indicator.
    box(x,1.42,z-.325,.48,.27,.075,C.dark,.4);
    for(let i=0;i<4;i++)rod([x-.15+i*.1,1.41,z-.28],[x-.15+i*.1,1.41,z-.265],.028,i===3?color('bb765b'):C.gold,14,.4);
    box(x,1.5,z-.28,.32,.025,.008,C.light,.1,5);
    // Side service hatch and small ventilation slots.
    box(x+w/2+.008,.25,z,.025,.31,.59,C.dark,.6);
    for(let i=0;i<5;i++)box(x+w/2+.026,.17+i*.035,z,.012,.012,.35,C.black,.7);
    rod([x+w/2+.03,.32,z+.19],[x+w/2+.04,.32,z+.19],.014,C.gold,8);
    for(const sign of [-1,1])box(x+sign*.52,.25,z+.43,.28,.32,.025,C.green);
    animalRamp(x,z);
  }
  function plant(x,z) {
    rod([x,.04,z],[x,.43,z],.2,C.stone,20,.9);
    for(let i=0;i<7;i++){const a=i*2.4;const top=[x+Math.cos(a)*.28,.9+(i%3)*.12,z+Math.sin(a)*.28];rod([x,.42,z],top,.015,C.green,6);rod(top,add(top,[Math.cos(a)*.14,.18,Math.sin(a)*.14]),.09,C.green,8,.9);}
  }
  // Room shell. Front wall is omitted as a presentation cutaway.
  box(0,-.19,0,7.6,.3,6.99,C.dark);
  box(0,-.025,0,7.3152,.08,6.7056,C.stone,.85,1);
  group='back';box(0,1.5,-3.4,7.52,3,.16,C.wall,.9,3);
  box(0,.08,-3.3,7.3,.15,.025,C.stone);
  group='left';box(-3.72,1.5,0,.15,3,6.8,C.wall,.9,3);
  group='right';box(3.72,.55,0,.15,1.1,6.8,C.wall,.9,3);box(3.72,2.8,0,.15,.4,6.8,C.wall);
  box(3.72,1.9,-2.4,.15,1.8,1.9,C.wall);box(3.72,1.9,2.7,.15,1.8,1.4,C.wall);
  box(3.65,1.85,.5,.05,1.55,3.2,color('c4d6d0'),.2,4);
  for(const z of [-1.15,.45,2.1])box(3.57,1.87,z,.08,1.72,.055,C.dark);
  box(3.57,1.02,.46,.22,.07,3.4,C.oak,.7,2);
  group='all';
  // Back-wall oak panels and warm linear lighting.
  box(-1.02,1.95,-3.285,4.65,1.6,.035,C.oak,.75,2);
  for(let i=0;i<48;i++)box(-3.24+i*.096,1.95,-3.25,.034,1.6,.05,color('c1a27b'),.8,2);
  box(-1.02,2.77,-3.16,4.65,.04,.14,C.light,.1,5);
  tub(-2.05,-2.5);tub(.15,-2.5);
  for(const x of [-2.75,.85]){box(x,1.72,-3.13,.16,.28,.1,C.white,.4);box(x,1.64,-3.06,.09,.04,.06,C.dark);}
  // Bay partition: solid splash panel with open slats above.
  box(-.95,1.0,-2.28,.09,1.9,1.5,C.green,.55);
  for(let i=0;i<7;i++)box(-.95,2.18,-2.92+i*.2,.07,.6,.045,C.oak,.7,2);
  // Quick paw rinse, with low threshold and handheld sprayer.
  box(-2.8,.12,1.55,1.12,.22,1.12,C.steel,.3);
  box(-2.8,.24,1.55,.95,.04,.95,C.mat);
  box(-3.31,.55,1.55,.08,.8,1.1,C.steel);
  box(-2.8,.38,1.04,1.12,.42,.08,C.steel);
  box(-2.8,.38,2.06,1.12,.42,.08,C.steel);
  rod([-3.26,.7,1.5],[-3.26,1.2,1.5],.025,C.steel);hose(-3.26,1.05,1.9,.2);
  box(-2.0,.014,1.55,.5,.025,.95,C.mat);
  // Locked cleaning and towel cabinet.
  box(-3.03,1.1,-.35,1.08,2.2,.75,C.green,.6);
  box(-3.03,1.1,.04,.025,2.1,.02,C.dark);
  rod([-3.11,1.05,.065],[-3.11,1.28,.065],.015,C.gold);
  rod([-2.95,1.05,.065],[-2.95,1.28,.065],.015,C.gold);
  box(-3.03,2.23,-.35,1.13,.06,.8,C.oak,.7,2);
  // Flat towel-and-brush counter; all powered drying is integrated at the wash bays.
  box(2.92,.43,.25,1.04,.82,2.05,C.green,.6);
  box(2.9,.88,.25,1.14,.08,2.14,C.stone,.65);
  for(const z of [.95,.45])for(let i=0;i<3;i++)box(2.98,.95+i*.055,z,.60,.05,.28,C.white);
  // A brush lying flat on the stone counter, with handle and visible short bristles.
  rod([2.72,.95,-.38],[2.72,.985,-.38],.085,C.oak,16,.8);
  box(2.72,.966,-.23,.05,.035,.2,C.oak,.75,2);
  for(let ix=-2;ix<=2;ix++)for(let iz=-2;iz<=2;iz++){
    if(ix*ix+iz*iz<7)rod([2.72+ix*.026,.985,-.38+iz*.026],[2.72+ix*.026,1.012,-.38+iz*.026],.003,C.black,4,.9);
  }
  box(3.22,.935,-.55,.22,.025,.18,C.green,.8);
  // Front waiting bench, coat hooks and convenience shelf.
  box(1.55,.49,2.85,1.05,.14,.52,C.oak,.7,2);
  for(const x of [1.12,1.98])box(x,.22,2.85,.08,.46,.38,C.dark);
  // Optional retail niche. Essentials remain at the wash bays and towel cabinet.
  box(2.93,.43,2.72,.78,.84,.48,C.green,.6);
  box(2.93,1.46,2.88,.78,1.18,.12,C.dark,.45);
  for(const x of [2.56,3.3])box(x,1.46,2.68,.045,1.18,.48,C.green,.5);
  for(const y of [.9,1.26,1.63,2.04])box(2.93,y,2.68,.78,.035,.48,C.oak,.7,2);
  for(const y of [.92,1.28,1.65])for(let i=0;i<3;i++)bottle(2.71+i*.2,y,2.57,i===1?C.gold:C.green);
  box(2.93,2.09,2.69,.78,.05,.48,C.green);
  box(2.93,1.97,2.43,.62,.025,.025,C.light,.1,5);
  box(-1.55,1.25,3.1,1.08,.06,.2,C.oak,.7,2);
  for(let i=0;i<3;i++)rod([-2.0+i*.35,1.55,3.15],[-2.0+i*.35,1.55,2.99],.025,C.gold);
  box(0,.012,2.9,1.5,.02,.7,C.mat);
  // Narrow drains, floor lighting and ceiling track, kept out of overview sightlines.
  for(const x of [-2.05,.15]) {box(x,.018,-1.25,1.58,.015,.07,C.steel);for(let i=0;i<18;i++)box(x-.73+i*.085,.028,-1.25,.025,.004,.055,C.dark);}
  group='interior';
  for(const x of [-2.15,.4,2.5]) {box(x,2.94,-.25,.055,.08,5.7,C.dark);for(const z of [-2,0,1.9]){rod([x,2.92,z],[x,2.7,z],.045,C.dark);rod([x,2.7,z],[x,2.64,z],.085,C.light,18,.1);}}
  group='flex';
  box(2.7,.05,-2.25,1.45,.08,1.45,color('b5bba8'),.9);
  box(2.7,.45,-2.87,1.45,.09,.35,C.oak,.7,2);
  for(const x of [2.1,3.3])box(x,.23,-2.87,.06,.42,.26,C.dark);
  plant(3.05,-1.9);
  group='future';tub(2.7,-2.5,1.48);
  group='all';
  const scenePoints=options.geometry?.vertices||points;
  const sceneItems=options.geometry?.items||items;
  const stride=options.geometry?.stride||11;
  if(stride!==11&&stride!==12&&stride!==14)throw new Error(`Unsupported scene vertex stride: ${stride}`);
  canvas.dataset.vertexCount=String(scenePoints.length/stride);
  canvas.dataset.drawGroups=String(sceneItems.length);
  const vs = `#version 300 es
  precision highp float; layout(location=0) in vec3 aPosition; layout(location=1) in vec3 aNormal; layout(location=2) in vec3 aColor; layout(location=3) in float aRough; layout(location=4) in float aKind;layout(location=5) in float aAO;layout(location=6) in vec2 aLightUV;
  uniform mat4 uVP;uniform mat4 uLight;out vec3 vWorld;out vec3 vNormal;out vec3 vColor;out float vRough;out float vKind;out float vAO;out vec2 vLightUV;out vec4 vShadow;
  void main(){vWorld=aPosition;vNormal=aNormal;vColor=aColor;vRough=aRough;vKind=aKind;vAO=aAO;vLightUV=aLightUV;vShadow=uLight*vec4(aPosition,1.);gl_Position=uVP*vec4(aPosition,1.);}`;
  const fs = `#version 300 es
  precision highp float;
  in vec3 vWorld;in vec3 vNormal;in vec3 vColor;in float vRough;in float vKind;in float vAO;in vec2 vLightUV;in vec4 vShadow;
  uniform vec3 uEye;uniform vec3 uSky;uniform sampler2D uDepth;uniform sampler2D uReflection;uniform bool uReflectionsReady;uniform sampler2D uLightmap;uniform bool uLightingReady;uniform sampler2D uOak;uniform sampler2D uStone;uniform vec2 uMaterialReady;uniform bool uShadows;out vec4 frag;
  float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
  float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1)),f.x),f.y),f.z);}
  vec3 stoneSample(vec2 uv){
    vec2 tileInterior=vec2(.18,.18);
    return textureGrad(uStone,vec2(.49,.24)+fract(uv)*tileInterior,dFdx(uv)*tileInterior,dFdy(uv)*tileInterior).rgb;
  }
  vec3 surfacePhoto(vec3 n,bool wood){
    vec3 weights=pow(abs(n),vec3(8.));weights/=max(dot(weights,vec3(1.)),.0001);
    if(wood){
      // Side faces keep grain upright. Horizontal slabs run grain along their X axis.
      vec3 x=texture(uOak,vWorld.zy*vec2(.82,.58)).rgb;
      vec3 y=texture(uOak,vWorld.zx*vec2(.82,.58)).rgb;
      vec3 z=texture(uOak,vWorld.xy*vec2(.82,.58)).rgb;
      return x*weights.x+y*weights.y+z*weights.z;
    }
    return stoneSample(vWorld.zy*.65)*weights.x+stoneSample(vWorld.xz*.65)*weights.y+stoneSample(vWorld.xy*.65)*weights.z;
  }
  float softShadow(vec3 n,vec3 l){
    vec3 p=vShadow.xyz/vShadow.w*.5+.5;
    if(!uShadows||p.x<=0.||p.x>=1.||p.y<=0.||p.y>=1.||p.z>=1.||p.z<=0.)return 1.;
    float bias=max(.0012*(1.-dot(n,l)),.00038),blocked=0.;
    for(int x=0;x<4;x++)for(int y=0;y<4;y++){
      vec2 offset=(vec2(x,y)-1.5)*1.65/1536.;
      blocked+=step(texture(uDepth,p.xy+offset).r,p.z-bias);
    }
    return 1.-blocked/16.;
  }
  // A compact microfacet highlight; broad source lobes keep steel from looking plastic.
  vec3 lightBRDF(vec3 n,vec3 v,vec3 l,vec3 base,float rough,float metal,vec3 radiance){
    float nl=max(dot(n,l),0.),nv=max(dot(n,v),.001);vec3 h=normalize(v+l);
    float nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);
    float a=max(.075,rough*rough),a2=a*a,d=nh*nh*(a2-1.)+1.;
    float distribution=a2/(3.14159*d*d);
    float k=(rough+1.)*(rough+1.)*.125;
    float geometry=(nv/(nv*(1.-k)+k))*(nl/(nl*(1.-k)+k));
    vec3 f0=mix(vec3(.04),base,metal),f=f0+(1.-f0)*pow(1.-vh,5.);
    vec3 spec=distribution*geometry*f/max(4.*nv*nl,.001);
    return ((1.-f)*(1.-metal)*base/3.14159+spec)*radiance*nl;
  }
  void main(){
    vec3 n=normalize(vNormal),v=normalize(uEye-vWorld),base=vColor;
    float rough=clamp(vRough,.12,.96);
    float detail=1.-smoothstep(.025,.13,length(fwidth(vWorld)));
    float broad=noise(vWorld*2.7),fine=noise(vWorld*95.);
    if((vKind>.5&&vKind<1.5)||(vKind<.5&&vRough>.46&&vRough<.7&&min(base.r,min(base.g,base.b))>.5)){
      if(uMaterialReady.y>.5){
        vec3 photo=surfacePhoto(n,false);
        float luminance=dot(photo,vec3(.2126,.7152,.0722));
        base*=clamp(luminance/.72,.62,1.18);
      }
      float vein=sin(vWorld.x*3.3+vWorld.z*2.1+broad*5.);
      base*=.965+.035*broad-.024*pow(abs(vein),12.);
      rough=clamp(rough+(fine-.5)*.10*detail,.3,.85);
    }
    if(vKind>1.5&&vKind<2.5){
      if(uMaterialReady.x>.5){
        vec3 photo=surfacePhoto(n,true);
        base=mix(base,photo*vec3(1.03,1.01,.97),.92);
      }
      float along=abs(n.y)>.7?vWorld.z:vWorld.y;
      float across=abs(n.x)>.7?vWorld.z:vWorld.x;
      float grain=sin(across*170.+noise(vec3(across*8.,along*.6,0.))*13.);
      base*=.93+.10*broad+.035*grain*detail;
      rough=clamp(rough+.055*grain*detail,.32,.7);
    }
    if(vKind>2.5&&vKind<3.5)base*=.99+.02*(fine-.5)*detail;
    // Low-roughness neutral or brass geometry is the exported metal family.
    float neutralMetal=step(.4,base.r)*(1.-step(.13,max(base.r,max(base.g,base.b))-min(base.r,min(base.g,base.b))));
    float brassMetal=step(base.b,base.g)*step(base.g,base.r)*step(base.r,base.g*1.4)*step(base.g,base.b*1.8);
    float metal=vKind<.5?(1.-smoothstep(.35,.46,vRough))*max(neutralMetal,brassMetal)*.88:0.;
    if(metal>.5){float brushing=sin((vWorld.x+vWorld.z)*740.);rough=clamp(rough+.025*brushing*detail,.18,.5);}
    vec3 daylight=normalize(vec3(-5.,11.,7.));
    float visibility=softShadow(n,daylight);
    float ao=clamp(vAO,.08,1.);
    float hemi=mix(.31,.57,n.y*.5+.5);
    vec3 ambient=mix(vec3(.42,.36,.27),vec3(.70,.78,.87),n.y*.5+.5);
    vec3 c=base*ambient*hemi*mix(.22,1.,ao)*(1.-metal*.68);
    c+=lightBRDF(n,v,daylight,base,rough,metal,vec3(2.65,2.78,2.86))*(.18+.82*visibility);
    vec3 ceiling=vec3(.1,3.05,-.6)-vWorld;
    float ceilingFalloff=1./(1.+dot(ceiling,ceiling)*.095);
    c+=lightBRDF(n,v,normalize(ceiling),base,max(rough,.28),metal,vec3(2.1,1.55,1.02))*ceilingFalloff*mix(.35,1.,ao);
    // Warm indirect cove and floor bounce balance the cool window source.
    float cove=exp(-abs(vWorld.y-2.65)*1.3)*(.5+.5*max(n.y,0.));
    c+=base*vec3(.22,.14,.075)*cove*ao;
    c+=base*vec3(.065,.052,.035)*max(-n.y,0.)*ao;
    vec3 r=reflect(-v,n);
    vec3 environment=mix(vec3(.16,.13,.095),vec3(.69,.76,.81),smoothstep(-.3,.9,r.y));
    float windowLobe=pow(max(dot(r,normalize(vec3(-.75,.45,.48))),0.),mix(48.,4.,rough));
    float strip=pow(max(1.-abs(r.y-.65),0.),mix(65.,9.,rough));
    environment+=vec3(.82,.91,1.)*windowLobe*.8+vec3(1.,.77,.47)*strip*.25;
    if(uReflectionsReady){
      // Panorama centre faces world -Z; image rows are uploaded in top-origin order.
      vec2 reflectionUV=vec2(.5+atan(r.x,-r.z)/6.2831853,.5-asin(clamp(r.y,-1.,1.))/3.14159265);
      vec3 encoded=textureLod(uReflection,reflectionUV,rough*5.5).rgb;
      vec3 room=mix(encoded/12.92,pow((encoded+.055)/1.055,vec3(2.4)),step(vec3(.04045),encoded));
      environment=mix(environment,room*1.25,.88);
    }
    vec3 f0=mix(vec3(.04),base,metal),fresnel=f0+(1.-f0)*pow(1.-max(dot(n,v),0.),5.);
    c+=environment*fresnel*(1.-rough*.72)*mix(.35,1.,ao);
    if(uLightingReady&&vLightUV.x>=0.&&vLightUV.y>=0.&&vKind<3.5&&metal<.5){
      vec3 encoded=texture(uLightmap,vLightUV).rgb;
      vec3 baked=mix(encoded/12.92,pow((encoded+.055)/1.055,vec3(2.4)),step(vec3(.04045),encoded));
      // The atlas already contains diffuse color and indirect illumination. Add only view-dependent sheen.
      vec3 sheen=environment*fresnel*(1.-rough*.72)*.35;
      sheen+=lightBRDF(n,v,normalize(ceiling),vec3(0.),max(rough,.28),0.,vec3(.45,.34,.23))*ceilingFalloff;
      c=baked+sheen;
    }
    if(vKind>3.5&&vKind<4.5)c=mix(c,uSky,.72)+vec3(.08)*pow(1.-max(dot(n,v),0.),3.);
    if(vKind>4.5)c=base*1.65;
    // Gentle highlight compression preserves warm whites without clipping luminaires.
    c=max(c,vec3(0.));c=c/(vec3(1.)+c*.30);
    c=pow(c,vec3(1./2.2));
    frag=vec4(clamp(c,0.,1.),1.);
  }`;
  function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
  const resources=[];
  function program(v,f){const p=gl.createProgram(),a=shader(gl.VERTEX_SHADER,v),b=shader(gl.FRAGMENT_SHADER,f);gl.attachShader(p,a);gl.attachShader(p,b);gl.linkProgram(p);gl.deleteShader(a);gl.deleteShader(b);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(p));resources.push(['program',p]);return p;}
  let main,depthProgram;
  try {main=program(vs,fs);depthProgram=program(`#version 300 es\nprecision highp float;layout(location=0) in vec3 aPosition;uniform mat4 uVP;void main(){gl_Position=uVP*vec4(aPosition,1.);}`,`#version 300 es\nprecision highp float;out vec4 frag;void main(){frag=vec4(1.);}`);} catch(error){options.onError?.(error);throw error;}
  const vao=gl.createVertexArray();gl.bindVertexArray(vao);resources.push(['vertexArray',vao]);
  const buffer=gl.createBuffer();resources.push(['buffer',buffer]);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(scenePoints),gl.STATIC_DRAW);
  for(const [loc,size,offset] of [[0,3,0],[1,3,3],[2,3,6],[3,1,9],[4,1,10]]){gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,stride*4,offset*4);}
  if(stride>=12){gl.enableVertexAttribArray(5);gl.vertexAttribPointer(5,1,gl.FLOAT,false,stride*4,44);}else{gl.disableVertexAttribArray(5);gl.vertexAttrib1f(5,1);}
  if(stride===14){gl.enableVertexAttribArray(6);gl.vertexAttribPointer(6,2,gl.FLOAT,false,stride*4,48);}else{gl.disableVertexAttribArray(6);gl.vertexAttrib2f(6,-1,-1);}
  let shadowDirty=true;
  const depth=gl.createTexture();resources.push(['texture',depth]);gl.bindTexture(gl.TEXTURE_2D,depth);gl.texImage2D(gl.TEXTURE_2D,0,gl.DEPTH_COMPONENT24,1536,1536,0,gl.DEPTH_COMPONENT,gl.UNSIGNED_INT,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  const fbo=gl.createFramebuffer();resources.push(['framebuffer',fbo]);gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.TEXTURE_2D,depth,0);gl.drawBuffers([gl.NONE]);gl.readBuffer(gl.NONE);const shadows=gl.checkFramebufferStatus(gl.FRAMEBUFFER)===gl.FRAMEBUFFER_COMPLETE;gl.bindFramebuffer(gl.FRAMEBUFFER,null);
  const uniforms=Object.fromEntries(['uVP','uLight','uEye','uSky','uDepth','uShadows','uOak','uStone','uMaterialReady','uLightmap','uLightingReady','uReflection','uReflectionsReady'].map(n=>[n,gl.getUniformLocation(main,n)]));
  const materialReady=[0,0],materialLoads=[];
  canvas.dataset.materialsReady='false';
  const anisotropy=gl.getExtension('EXT_texture_filter_anisotropic');
  const materialTextures=['oak','stone'].map((name,index)=>{
    const texture=gl.createTexture();resources.push(['texture',texture]);
    gl.activeTexture(gl.TEXTURE0+index+1);gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([255,255,255,255]));
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.REPEAT);
    const image=new Image();materialLoads.push(image);image.crossOrigin='anonymous';
    image.onload=()=>{
      if(disposed||gl.isContextLost())return;
      try{
        gl.activeTexture(gl.TEXTURE0+index+1);gl.bindTexture(gl.TEXTURE_2D,texture);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,image);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
        if(anisotropy)gl.texParameterf(gl.TEXTURE_2D,anisotropy.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(4,gl.getParameter(anisotropy.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
        materialReady[index]=1;canvas.dataset.materialsReady=String(materialReady.every(Boolean));schedule();
      }catch{ /* Keep the procedural surface if this device cannot upload the photograph. */ }
    };
    image.onerror=()=>{image.onload=image.onerror=null;};
    image.src=window.ROOM_MATERIALS?.[name]||`assets/master-v4/${name}.jpg`;
    return texture;
  });
  let lightingReady=false;
  canvas.dataset.lightingReady='false';
  const lightmap=gl.createTexture();resources.push(['texture',lightmap]);
  gl.activeTexture(gl.TEXTURE3);gl.bindTexture(gl.TEXTURE_2D,lightmap);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,1,1,0,gl.RGB,gl.UNSIGNED_BYTE,new Uint8Array([255,255,255]));
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  if(stride===14){
    const image=new Image();materialLoads.push(image);image.crossOrigin='anonymous';
    image.onload=()=>{
      if(disposed||gl.isContextLost())return;
      try{
        gl.activeTexture(gl.TEXTURE3);gl.bindTexture(gl.TEXTURE_2D,lightmap);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,image);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
        lightingReady=true;canvas.dataset.lightingReady='true';schedule();
      }catch{gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);}
    };
    image.onerror=()=>{image.onload=image.onerror=null;};
    image.src=window.ROOM_LIGHTMAP||'assets/master-v4/lighting.png';
  }
  let reflectionsReady=false;
  canvas.dataset.reflectionsReady='false';
  const reflection=gl.createTexture();resources.push(['texture',reflection]);
  gl.activeTexture(gl.TEXTURE4);gl.bindTexture(gl.TEXTURE_2D,reflection);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,1,1,0,gl.RGB,gl.UNSIGNED_BYTE,new Uint8Array([128,128,128]));
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
  {
    const image=new Image();materialLoads.push(image);image.crossOrigin='anonymous';
    image.onload=()=>{
      if(disposed||gl.isContextLost())return;
      try{
        gl.activeTexture(gl.TEXTURE4);gl.bindTexture(gl.TEXTURE_2D,reflection);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,image);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);
        reflectionsReady=true;canvas.dataset.reflectionsReady='true';schedule();
      }catch{ /* Synthetic reflection remains available until a room map can upload. */ }
    };
    image.onerror=()=>{image.onload=image.onerror=null;};
    image.src=window.ROOM_REFLECTION||'assets/master-v4/reflections.jpg';
  }
  const depthVP=gl.getUniformLocation(depthProgram,'uVP');
  const lightVP=multiply(ortho(-6.8,6.8,-6.8,6.8,.1,30),lookAt([-5,11,7],[0,0,0]));
  function visible(item){return !(item.group==='future'&&!future||item.group==='flex'&&future||item.group==='right'&&(view==='overview'||view==='plan')||item.group==='interior'&&(view==='overview'||view==='plan'));}
  function drawItems(){for(const item of sceneItems)if(visible(item))gl.drawArrays(gl.TRIANGLES,item.start,item.count);}
  function camera(){const aspect=canvas.width/canvas.height;if(view==='overview'){const distance=radius*Math.max(1,1.25/aspect);const e=[Math.sin(yaw)*Math.cos(pitch)*distance,Math.sin(pitch)*distance,Math.cos(yaw)*Math.cos(pitch)*distance];return {e,mat:multiply(perspective(.72,aspect,.1,60),lookAt(e,target))};}if(view==='plan'){const span=4.6;const w=aspect>=1?span*aspect:span;const h=aspect>=1?span:span/aspect;return {e:[0,12,0],mat:multiply(ortho(-w,w,-h,h,.1,40),lookAt([0,12,0],[0,0,0],[0,0,-1]))};}const dir=[Math.sin(heading)*Math.cos(tilt),Math.sin(tilt),-Math.cos(heading)*Math.cos(tilt)];return {e:eye,mat:multiply(perspective(1.12,aspect,.06,40),lookAt(eye,add(eye,dir)))};}
  function render(){frame=0;if(disposed)return;const rect=canvas.getBoundingClientRect(),dpr=Math.min(window.devicePixelRatio||1,2),w=Math.max(1,Math.round(rect.width*dpr)),h=Math.max(1,Math.round(rect.height*dpr));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.bindVertexArray(vao);
    if(shadows&&shadowDirty){gl.bindFramebuffer(gl.FRAMEBUFFER,fbo);gl.viewport(0,0,1536,1536);gl.clear(gl.DEPTH_BUFFER_BIT);gl.useProgram(depthProgram);gl.uniformMatrix4fv(depthVP,false,lightVP);drawItems();gl.bindFramebuffer(gl.FRAMEBUFFER,null);shadowDirty=false;}
    gl.viewport(0,0,w,h);gl.clearColor(.895,.899,.87,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.useProgram(main);const c=camera();gl.uniformMatrix4fv(uniforms.uVP,false,c.mat);gl.uniformMatrix4fv(uniforms.uLight,false,lightVP);gl.uniform3fv(uniforms.uEye,c.e);const skies={winter:[.78,.86,.9],spring:[.7,.82,.69],summer:[.61,.79,.79],fall:[.84,.72,.53]};gl.uniform3fv(uniforms.uSky,skies[season]||skies.winter);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,depth);gl.uniform1i(uniforms.uDepth,0);gl.uniform1i(uniforms.uShadows,shadows?1:0);for(let i=0;i<2;i++){gl.activeTexture(gl.TEXTURE1+i);gl.bindTexture(gl.TEXTURE_2D,materialTextures[i]);}gl.uniform1i(uniforms.uOak,1);gl.uniform1i(uniforms.uStone,2);gl.uniform2fv(uniforms.uMaterialReady,materialReady);gl.activeTexture(gl.TEXTURE3);gl.bindTexture(gl.TEXTURE_2D,lightmap);gl.uniform1i(uniforms.uLightmap,3);gl.uniform1i(uniforms.uLightingReady,lightingReady&&!future?1:0);gl.activeTexture(gl.TEXTURE4);gl.bindTexture(gl.TEXTURE_2D,reflection);gl.uniform1i(uniforms.uReflection,4);gl.uniform1i(uniforms.uReflectionsReady,reflectionsReady?1:0);drawItems();canvas.dataset.ready='true';canvas.dataset.view=view;canvas.dataset.futureBay=String(future);canvas.dataset.season=season;}
  function schedule(){if(!frame&&!disposed)frame=requestAnimationFrame(render);}
  function listen(name,fn,opts){canvas.addEventListener(name,fn,opts);removers.push(()=>canvas.removeEventListener(name,fn,opts));}
  let pointer=null;
  listen('pointerdown',e=>{if(e.button!==0)return;pointer={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);canvas.focus({preventScroll:true});});
  listen('pointermove',e=>{if(!pointer||e.pointerId!==pointer.id)return;const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;pointer.x=e.clientX;pointer.y=e.clientY;if(view==='overview'){yaw-=dx*.006;pitch=clamp(pitch+dy*.005,.18,1.4);}else if(view!=='plan'){heading-=dx*.005;tilt=clamp(tilt-dy*.004,-1.05,1.05);}schedule();});
  const end=e=>{if(pointer?.id===e.pointerId)pointer=null;};listen('pointerup',end);listen('pointercancel',end);listen('lostpointercapture',()=>{pointer=null;});
  listen('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();if(view==='overview'){radius=clamp(radius+e.deltaY*.008,6,19);}else if(view!=='plan'){move(e.deltaY>0?-.15:.15,0);}schedule();},{passive:false});
  function move(forward,side){
    const nx=clamp(eye[0]+Math.sin(heading)*forward+Math.cos(heading)*side,-3.35,3.35);
    const nz=clamp(eye[2]-Math.cos(heading)*forward+Math.sin(heading)*side,-3.05,3.05);
    const obstacles=[[-3.4,-2.25,-.95,.35],[-3.5,-2.05,.8,2.3],[-3.2,-1.0,-3.2,-1.25],[-.98,1.25,-3.2,-1.25],[-2.64,-1.46,-1.3,-.55],[-.44,.74,-1.3,-.55],[2.1,3.5,-.98,1.55],[2.3,3.5,2.05,3.2],[.9,2.2,2.4,3.2]];
    if(future)obstacles.push([1.65,3.5,-3.2,-1.25],[2.1,3.3,-1.3,-.55]);else obstacles.push([1.75,3.5,-3.2,-2.55]);
    const clear=(x,z)=>!obstacles.some(([x0,x1,z0,z1])=>x>x0&&x<x1&&z>z0&&z<z1);
    const x=clear(nx,eye[2])?nx:eye[0];eye=[x,1.65,clear(x,nz)?nz:eye[2]];
  }
  listen('keydown',e=>{if(!['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','w','a','s','d','W','A','S','D','+','-'].includes(e.key))return;e.preventDefault();if(view==='overview'){if(['ArrowLeft','a','A'].includes(e.key))yaw-=.09;if(['ArrowRight','d','D'].includes(e.key))yaw+=.09;if(['ArrowUp','w','W','+'].includes(e.key))radius=clamp(radius-.4,6,19);if(['ArrowDown','s','S','-'].includes(e.key))radius=clamp(radius+.4,6,19);}else if(view!=='plan'){const k=e.key.toLowerCase();const forward=(k==='w'||k==='arrowup')?.2:(k==='s'||k==='arrowdown')?-.2:0;const side=(k==='a'||k==='arrowleft')?-.2:(k==='d'||k==='arrowright')?.2:0;move(forward,side);}schedule();});
  if(!canvas.hasAttribute('tabindex'))canvas.tabIndex=0;
  if(!canvas.hasAttribute('aria-label'))canvas.setAttribute('aria-label','Interactive pet spa concept. Drag to look around. Focus and use arrow keys to move; choose a camera view using the controls.');
  const oldTouch=canvas.style.touchAction;canvas.style.touchAction='none';
  listen('webglcontextlost',e=>{e.preventDefault();canvas.dataset.ready='false';options.onError?.(new Error('The 3D graphics context was interrupted. Reload to restore the tour.'));});
  const observer=new ResizeObserver(schedule);observer.observe(canvas);
  render();options.onReady?.();
  return {
    setView(name){if(!['overview','entrance','wash','dry','plan'].includes(name))return;shadowDirty=true;view=name;if(name==='overview'){yaw=.57;pitch=.74;radius=13.5;}if(name==='entrance'){eye=[0,1.65,2.9];heading=0;tilt=-.1;}if(name==='wash'){eye=[-.7,1.65,.05];heading=-.23;tilt=-.23;}if(name==='dry'){eye=[.5,1.65,1.8];heading=1.0;tilt=-.17;}schedule();},
    setSeason(name){if(['winter','spring','summer','fall'].includes(name)){season=name;schedule();}},
    setFutureBay(enabled){future=Boolean(enabled);shadowDirty=true;schedule();},
    resize:schedule,
    exportScene(){return {stride,vertices:Array.from(scenePoints),items:sceneItems.map(item=>({...item}))};},
    capture(){if(disposed)return null;render();return canvas.toDataURL('image/png');},
    destroy(){disposed=true;for(const image of materialLoads){image.onload=image.onerror=null;image.src='';}canvas.dataset.materialsReady='false';canvas.dataset.lightingReady='false';canvas.dataset.reflectionsReady='false';if(frame)cancelAnimationFrame(frame);observer.disconnect();removers.forEach(fn=>fn());canvas.style.touchAction=oldTouch;for(const [type,value] of resources){const method={program:'deleteProgram',buffer:'deleteBuffer',texture:'deleteTexture',framebuffer:'deleteFramebuffer',vertexArray:'deleteVertexArray'}[type];gl[method](value);}canvas.dataset.ready='false';}
  };
}
