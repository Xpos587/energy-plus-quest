import {fitMap,placeTargets} from './fit-map.mjs';
const base='/review/map-geometry/pass-07/';
const map=document.querySelector('.map'),scene=document.querySelector('.scene'),video=document.querySelector('video'),poster=document.querySelector('.poster'),motion=document.querySelector('.motion'),status=document.querySelector('.media-status');
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let data,view,format,fit,phase=0,pendingPhase=0,ready=false,wantsMotion=!reduced.matches,token=0,frameCallback;
const targets=[],choices=[];
function select(n){
 for(const button of [...targets,...choices])button.setAttribute('aria-pressed',String(Number(button.dataset.number)===n));
 document.querySelector('.selection').textContent=`Выбран грузовик №${n}. Это демонстрация, баллы не начисляются.`;
}
for(let n=1;n<=4;n++){
 for(const [container,isTarget] of [[document.querySelector('.targets'),true],[document.querySelector('.choices'),false]]){
  const b=document.createElement('button');b.type='button';b.dataset.number=n;b.className=isTarget?'target':'choice';b.setAttribute('aria-label',`Выбрать грузовик №${n}`);b.setAttribute('aria-pressed','false');
  const span=document.createElement('span');span.textContent=n;b.append(span);container.append(b);(isTarget?targets:choices).push(b);
  if(!isTarget){b.addEventListener('click',()=>select(n));continue;}
  let press;
  b.addEventListener('pointerdown',e=>{if(!e.isPrimary||e.button!==0)return;press={id:e.pointerId,x:e.clientX,y:e.clientY};b.setPointerCapture(e.pointerId);});
  b.addEventListener('pointermove',e=>{if(press&&Math.hypot(e.clientX-press.x,e.clientY-press.y)>=10)press.dragged=true;});
  b.addEventListener('pointerup',e=>{if(press?.id===e.pointerId&&!press.dragged&&Math.hypot(e.clientX-press.x,e.clientY-press.y)<10)select(n);press=null;});
  b.addEventListener('pointercancel',()=>{press=null;});
  b.addEventListener('click',e=>{if(e.detail===0)select(n);});
 }
}
document.querySelector('.automatic').onclick=()=>select(1+Math.floor(Math.random()*4));
function paint(time=phase){
 if(!view||!fit)return;
 const frame=Math.floor((time%32)*data.fps+1e-4)%data.frames;
 const anchors=view.tracks[frame].map(([x,y])=>[fit.x+x*fit.scale,fit.y+y*fit.scale]);
 placeTargets(anchors,map.clientWidth,map.clientHeight).forEach(([x,y],i)=>{targets[i].style.left=`${x}px`;targets[i].style.top=`${y}px`;});
 map.dataset.frame=frame;
}
function updateMotion(){const playing=!video.paused&&ready;motion.textContent=playing?'Остановить движение':'Запустить движение';motion.setAttribute('aria-pressed',String(playing));}
function track(){
 if(!video.requestVideoFrameCallback)return;
 if(frameCallback)video.cancelVideoFrameCallback(frameCallback);
 frameCallback=video.requestVideoFrameCallback((_,metadata)=>{if(ready){phase=metadata.mediaTime;paint();}track();});
}
async function play(){if(!ready||!wantsMotion||document.hidden)return;try{await video.play();status.textContent='';}catch{status.textContent='Автозапуск недоступен. Нажмите «Запустить движение».';}updateMotion();}
function fallback(){ready=false;video.pause();video.hidden=true;poster.hidden=false;phase=0;pendingPhase=0;paint(0);status.textContent='Движение недоступно. Выбор работает на неподвижной карте.';updateMotion();}
function resize(){
 if(!data)return;
 const next=map.clientWidth/map.clientHeight>=1.2?'desktop':'mobile';
 view=data.views[next];fit=fitMap(view,map.clientWidth,map.clientHeight);
 scene.style.width=`${view.width}px`;scene.style.height=`${view.height}px`;scene.style.transform=`translate(${fit.x}px,${fit.y}px) scale(${fit.scale})`;
 if(next!==format){
  const saved=ready?video.currentTime:pendingPhase;pendingPhase=saved;format=next;map.dataset.format=format;ready=false;video.pause();video.hidden=true;poster.hidden=false;poster.src=base+format+'-poster.jpg';phase=0;paint(0);
  const current=++token;
  video.onloadedmetadata=()=>{if(current!==token)return;video.currentTime=Math.min(saved,video.duration-.001);};
  video.onseeked=()=>{if(current!==token)return;video.onseeked=null;ready=true;phase=video.currentTime;video.hidden=false;poster.hidden=true;paint();play();};
  video.src=base+format+'-motion.mp4';video.load();
 }else paint(ready?video.currentTime:0);
}
video.addEventListener('error',fallback);
video.addEventListener('pause',updateMotion);video.addEventListener('play',updateMotion);
video.addEventListener('timeupdate',()=>{if(ready&&!video.requestVideoFrameCallback){phase=video.currentTime;paint();}});
video.addEventListener('seeked',()=>{if(ready){phase=video.currentTime;paint();}});
motion.onclick=()=>{wantsMotion=video.paused;if(wantsMotion){if(!ready){format=null;resize();}else play();}else video.pause();};
reduced.addEventListener('change',()=>{wantsMotion=!reduced.matches;if(!wantsMotion)video.pause();else play();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause();else play();});
try{const response=await fetch(base+'tracks.json');if(!response.ok)throw Error('tracks');data=await response.json();new ResizeObserver(resize).observe(map);resize();track();}catch{status.textContent='Не удалось загрузить карту. Обновите страницу.';targets.forEach(b=>b.hidden=true);}
