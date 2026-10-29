import {capacity, defaults} from './capacity.mjs';
const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const zones={
wash:['01','WASH AND DRY IN PLACE','One bay for the full routine.','Two integrated wash/dry bays combine hand sprays, metered shampoo and a dedicated dryer hose. Residents can complete powered drying in the same basin. The illustration is generic; confirm equipment access, entry ramp and service clearances with the supplier and architect.'],
rinse:['02','THE QUICK STOP','Paws first. Then upstairs.','A low paw-rinse zone near entry gives residents a convenient stop after snow, salt or mud. Keep splash and towel drying within the wet area. Its use is separate from the full-bath capacity model.'],
dry:['03','THE FINISHING COUNTER','Towels, brushing, and a final check.','Powered drying happens at the wash bays. This separate flat counter holds clean towels and brushes, with used-towel return below. It is a finishing area; confirm an appropriate approach and support surface before equipment selection.'],
supplies:['04','THE OPERATING BACKBONE','A place for the essentials.','Provide metered shampoo at each wash bay, clean towels, used-towel return and a waste-bag dispenser. Keep maintenance chemicals in locked storage, separate from supplies residents can access.'],
future:['05','ROOM TO ADAPT','Preserve the third-bay option.','Use this alcove flexibly at opening. Reserve a route for future service connections where feasible. If demand calls for another full wash bay, redesign this zone and review clearances, ventilation and servicing. Expansion equipment and MEP work are excluded from the base allowance.'],
retail:['06','OPTIONAL RETAIL','A considered place for vending.','A compact built-in niche can hold an optional take-home product dispenser or contactless vending unit. Keep essentials included. Confirm a supplier and service arrangement before buying equipment. The model illustrates the reserved cabinet only.']};
function selectZone(key){const z=zones[key];if(!z)return;$('#zone-number').textContent=z[0];$('#zone-kicker').textContent=z[1];$('#zone-title').textContent=z[2];$('#zone-body').textContent=z[3];$$('[data-zone]').forEach(el=>el.classList.toggle('selected',el.dataset.zone===key));$$('[data-zone-button]').forEach(el=>{const active=el.dataset.zoneButton===key;el.classList.toggle('active',active);el.setAttribute('aria-pressed',active)});}
$$('[data-zone-button]').forEach(el=>el.addEventListener('click',()=>selectZone(el.dataset.zoneButton)));
$$('[data-zone]').forEach(el=>{el.addEventListener('click',()=>selectZone(el.dataset.zone));el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectZone(el.dataset.zone)}})});
const inputKeys=Object.keys(defaults);
const suffix={dogShare:'%',baths:'',cycle:' min',peakShare:'%',peakHours:' hr',availability:'%',target:'%'};
function readInputs(){return Object.fromEntries(inputKeys.map(k=>[k,Number($('#'+k).value)]));}
function updateCapacity(){const input=readInputs();for(const k of inputKeys)$('#'+k+'-value').textContent=(k==='baths'?input[k].toFixed(1):input[k])+(suffix[k]||'');const result=capacity(input);$('#result-bays').textContent=result.recommended;$('#result-monthly').textContent=Math.round(result.monthly).toLocaleString();$('#result-utilization').textContent=Math.round(result.utilization)+'%';$('#util-fill').style.width=Math.min(100,result.utilization)+'%';$('#util-fill').style.background=result.utilization>input.target?'#e3b482':'#c3d2ac';$('#result-note').textContent=result.recommended===2?'Retain two bays and preserve the expansion alcove.':result.recommended===3?'The third-bay option becomes useful under these assumptions.':'This scenario calls for a larger suite or a revised operating plan.';}
inputKeys.forEach(k=>$('#'+k).addEventListener('input',()=>{updateCapacity();$$('[data-scenario]').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-pressed','false')})}));
const scenarios={base:defaults,low:{...defaults,units:300,dogShare:15,baths:.5},stress:{...defaults,units:500,dogShare:35,baths:1.5,peakShare:80,availability:80},long:{...defaults,units:500,dogShare:35,baths:1.5,peakShare:80,availability:80,cycle:60}};
$$('[data-scenario]').forEach(el=>el.addEventListener('click',()=>{for(const [k,v]of Object.entries(scenarios[el.dataset.scenario]))$('#'+k).value=v;updateCapacity();$$('[data-scenario]').forEach(b=>{const on=b===el;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)})}));updateCapacity();
const seasons={winter:['Snow outside. A warm rinse inside.','Place the paw-rinse zone along the conditioned return path from outdoor pet access. Contain snowmelt and salt residue near entry, then provide towel drying before residents head upstairs.','Operations focus: entry mats, frequent wet-floor checks, towel replenishment and a clear path to the lifts.'],spring:['A quick stop after a muddy walk.','Make the low rinse convenient for paws and lower legs. Use washable wall protection around the spray zone and provide space to towel off before leaving.','Operations focus: mud capture, drain-strainer checks, surface cleaning and keeping clean towels separate from used ones.'],summer:['A comfortable place for a full wash.','Keep the indoor amenity conditioned and ventilated. Give residents straightforward controls for washing and powered drying in each bay, with a separate towel-and-brushing counter.','Operations focus: ventilation checks, water temperature controls, equipment service and restocking metered supplies.'],fall:['Leaves, rain and a simple reset.','Keep a clear entry sequence as wet coats and fallen leaves return indoors. Place hooks and a phone shelf within easy reach of the rinse area.','Operations focus: entrance cleanup, waste bags, towel turnover and reviewing the operating plan before winter.']};
let viewer, panorama, modelPromise, panoramaPromise;
let activeMode='cinematic', tourStarted=false, currentStop='entrance';
const stopOrder=['entrance','wash','dry'];
const stops={
 entrance:{title:'The arrival',kicker:'01 / AFTER THE WALK',heading:'A useful stop on the way home.',body:'A low paw rinse near entry, a place for coats and supplies, and a clear route to the full wash bays.'},
 wash:{title:'Wash + dry',kicker:'02 / THE FULL ROUTINE',heading:'Keep washing and drying in one bay.',body:'Two integrated bays provide a washing hand spray, compatible metered products and a separate dryer hose. The finishing counter stays available for towels and brushing.'},
 dry:{title:'The finishing counter',kicker:'03 / READY TO HEAD UPSTAIRS',heading:'A place to finish comfortably.',body:'A flat counter, clean towels and brushes make the last part of the routine easier. Keep used towels separate and supplies maintained by a named operator.'}
};
function updateStop(name){currentStop=name;const t=stops[name];const index=stopOrder.indexOf(name);$('#stop-number').textContent=`0${index+1} / 03`;$('#stop-title').textContent=t.title;$('#tour-caption-kicker').textContent=t.kicker;$('#tour-caption-title').textContent=t.heading;$('#tour-caption-body').textContent=t.body;$('#tour-next').textContent=index===2?'Back to arrival ↩':`Next: ${stops[stopOrder[index+1]].title.toLowerCase()} →`;$$('[data-cinema-view]').forEach(b=>{const on=b.dataset.cinemaView===name;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});}
function cinemaReady(){
 $('#cinema-status').classList.add('hidden');$('#tour-poster').classList.add('tour-open');
 for(const id of ['tour-stamp','tour-gesture','tour-stops','tour-next'])$('#'+id).classList.remove('hidden');
 if(document.fullscreenEnabled)$('#cinema-fullscreen').classList.remove('hidden');
 $('#start-tour').disabled=false;updateStop(currentStop);
}
async function ensurePanorama(){
 if(panorama)return panorama;if(panoramaPromise)return panoramaPromise;
 panoramaPromise=(async()=>{const {createPanoramaViewer}=await import('./panorama.js?v=3');
  const mobile=matchMedia('(max-width:800px)').matches;
  const assets=window.CINEMATIC_ASSETS||Object.fromEntries(['entrance','wash','dry'].map(name=>[name,`assets/master/${name}${mobile?'-mobile':''}.jpg`]));
  panorama=createPanoramaViewer($('#cinema-canvas'),{assets,onReady:cinemaReady,onError(error){$('#cinema-status').textContent='The tour could not load. You can still explore the room images and plans below.';$('#start-tour').disabled=false;console.warn('Room tour:',error)},onViewChange:updateStop});
  window.spaPanorama=panorama;return panorama;
 })();try{return await panoramaPromise}catch(error){panoramaPromise=null;throw error}
}
async function startTour(){
 tourStarted=true;$('#start-tour').disabled=true;$('#cinema-status').classList.remove('hidden');
 try{await ensurePanorama()}catch(error){$('#cinema-status').textContent='The tour could not load. Please try again.';$('#start-tour').disabled=false;console.warn(error)}
}
$('#start-tour').addEventListener('click',startTour);
$('#tour-next').addEventListener('click',()=>panorama?.setView(stopOrder[(stopOrder.indexOf(currentStop)+1)%3]));
$$('[data-cinema-view]').forEach(b=>b.addEventListener('click',()=>panorama?.setView(b.dataset.cinemaView)));
async function ensureModel(){
 if(viewer)return viewer;if(modelPromise)return modelPromise;
 modelPromise=(async()=>{
  const [{createSpaViewer},{loadMasterGeometry}]=await Promise.all([import('./model.js?v=3'),import('./master-loader.mjs?v=3')]);
  const geometry=await loadMasterGeometry();
  viewer=createSpaViewer($('#spa-canvas'),{geometry,onReady(){ $('#viewer-status').classList.add('hidden');$('#save-view').disabled=false; },onError(error){$('#viewer-status').textContent='The layout model is unavailable. The rendered tour and room plans remain available.';console.warn(error)}});
  window.spaViewer=viewer;return viewer;
 })();try{return await modelPromise}catch(error){modelPromise=null;$('#viewer-status').textContent='The layout model could not load. The rendered tour and plans remain available.';throw error}
}
async function setQuality(mode,userAction=false){
 activeMode=mode;const model=mode==='model';$('.cinema-wrap').classList.toggle('hidden',model);$('.canvas-wrap').classList.toggle('hidden',!model);$('.viewer-toolbar').classList.toggle('hidden',!model);$('.viewer-footer').classList.toggle('hidden',!model);$('.tour-caption').classList.toggle('hidden',model);
 $$('[data-quality]').forEach(b=>{const on=b.dataset.quality===mode;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});
 $('#mode-explanation').textContent=model?'Premium 528 sq ft room · Move freely and explore the third-bay option.':'Premium 528 sq ft room · Three rendered viewpoints.';
 try{if(model){await ensureModel();requestAnimationFrame(()=>viewer.resize())}else{if(userAction&&!tourStarted)await startTour();requestAnimationFrame(()=>panorama?.resize())}}catch(error){console.warn(error)}
}
$$('[data-quality]').forEach(b=>b.addEventListener('click',()=>setQuality(b.dataset.quality,true)));
function activateView(name){viewer?.setView(name);$('.walk-controls').classList.toggle('hidden',name==='overview'||name==='plan');$$('button[data-view]').forEach(b=>{const on=b.dataset.view===name;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on)});}
$$('button[data-view]').forEach(b=>b.addEventListener('click',()=>activateView(b.dataset.view)));
$$('[data-walk]').forEach(b=>b.addEventListener('click',()=>$('#spa-canvas').dispatchEvent(new KeyboardEvent('keydown',{key:b.dataset.walk,bubbles:true}))));
$('#future-bay').addEventListener('change',e=>{const on=e.target.checked;viewer?.setFutureBay(on);$('#bay-note').textContent=on?'Three-bay study · Expansion cost separate':'Two integrated bays + expansion alcove';$('#future-plan').setAttribute('fill',on?'#a8bda4':'#e3e4d7');selectZone('future')});
$$('button[data-season]').forEach(b=>b.addEventListener('click',()=>{const name=b.dataset.season;const t=seasons[name];$('#season-title').textContent=t[0];$('#season-body').textContent=t[1];$('#season-operation').textContent=t[2];$$('button[data-season]').forEach(el=>{const on=el===b;el.classList.toggle('active',on);el.setAttribute('aria-pressed',on)});viewer?.setSeason(name)}));
$$('[data-layout]').forEach(b=>b.addEventListener('click',()=>{const premium=b.dataset.layout==='premium';$('#premium-layout').classList.toggle('hidden',!premium);$('#compact-layout').classList.toggle('hidden',premium);$$('[data-layout]').forEach(el=>{const on=el===b;el.classList.toggle('active',on);el.setAttribute('aria-pressed',on)});$('#layout-choice').textContent=premium?'Premium plan selected':'Compact plan selected';$('#layout-tradeoff').textContent=premium?'Reserve 528 sq ft if the floorplate supports it; preserve an option for a third bay.':'Use 360 sq ft for the same opening bay count; expansion would require another location or a revised plan.';}));
let toastTimer;
function announce(message){$('#share-status').textContent=message;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{$('#share-status').textContent=''},6500)}
async function fullscreen(){try{if(document.fullscreenElement)await document.exitFullscreen();else await $('.viewer-shell').requestFullscreen()}catch{announce('Full screen is unavailable here. The inline tour still works.')}}
$('#fullscreen').addEventListener('click',fullscreen);$('#cinema-fullscreen').addEventListener('click',fullscreen);
if(!document.fullscreenEnabled){$('#fullscreen').hidden=true;$('#cinema-fullscreen').hidden=true;}
function download(url,name){const link=document.createElement('a');link.href=url;link.download=name;link.click()}
$('#save-view').addEventListener('click',()=>{try{const image=viewer?.capture();if(image)download(image,'companion-room-layout.png')}catch{announce('Image export is unavailable in this browser.')}});
const printStates=new Map();
window.addEventListener('beforeprint',()=>{document.querySelectorAll('details').forEach(d=>{printStates.set(d,d.open);d.open=true})});
window.addEventListener('afterprint',()=>{for(const [d,open]of printStates)d.open=open;printStates.clear()});
$$('.print').forEach(b=>b.addEventListener('click',()=>window.print()));
$$('.share-action').forEach(b=>b.addEventListener('click',async()=>{const url='https://meltckr.github.io/the-companion-room/?v=3';try{if(navigator.share){await navigator.share({title:'The Companion Room',text:'A considered resident pet-spa concept for East Lansing.',url});return}await navigator.clipboard.writeText(url);announce('Link copied. Paste it into iMessage.')}catch(error){if(error.name!=='AbortError')announce(url)}}));
setQuality('cinematic');
