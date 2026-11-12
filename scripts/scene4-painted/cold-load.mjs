import { chromium } from 'playwright';
import { mkdir, rename, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
const out=process.argv[2]||'/home/michael/Github/energy-plus-quest/.tmp-work/scene4-final-render/cold-load-after';
await mkdir(out,{recursive:true});
const browser=await chromium.launch();
for(const mode of ['no-preference','reduce']){
 const ctx=await browser.newContext({viewport:{width:1440,height:900},serviceWorkers:'block',reducedMotion:mode,recordVideo:{dir:`${out}/raw-${mode}`,size:{width:1440,height:900}}});
 const page=await ctx.newPage(),t0=Date.now();
 await page.addInitScript(()=>{
  window.sceneSamples=[];
  function sample(){
   const stage=document.querySelector('[data-barge-art]');
   if(stage){const q=s=>{const e=stage.querySelector(s),r=e?.getBoundingClientRect();return e?{src:e.currentSrc,complete:e.complete,w:e.naturalWidth,rect:r&&[r.x,r.y,r.width,r.height],opacity:getComputedStyle(e).opacity,visibility:getComputedStyle(e).visibility}:null};window.sceneSamples.push({time:Date.now(),format:stage.getAttribute('data-barge-art'),visibility:getComputedStyle(stage.firstElementChild).visibility,loading:document.querySelector('[data-artwork-status]')?.getAttribute('data-artwork-status'),broken:[...stage.querySelectorAll('img')].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),barge:q('[data-layer=barge]'),near:q('[data-layer=top] img'),far:q('[data-layer=far]')});}
   requestAnimationFrame(sample);
  } requestAnimationFrame(sample);
 });
 await page.goto('http://127.0.0.1:4175/scenes.html?scene=crane&parcel=camera&recipient=alva');
 await page.locator('[data-hotspot]').first().waitFor({state:'attached'});
 const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
 for(let n=0;n<20&&await next.isVisible();n++)await next.click();
 const choiceAt=Date.now()-t0;
 await page.waitForTimeout(3800);
 const samples=await page.evaluate(()=>window.sceneSamples);
 const visible=samples.filter(s=>s.visibility==='visible');
 if(visible.length<30 || visible.some(s=>s.broken.length))throw Error('Incomplete first paint or insufficient post-reveal frames');
 await page.screenshot({path:`${out}/${mode}-settled.png`});
 const video=await page.video().path();await ctx.close();
 await rename(video,`${out}/${mode}.webm`);
 await writeFile(`${out}/${mode}.json`,JSON.stringify({t0,choiceAt,samples},null,2));

 execFileSync('ffmpeg',['-v','error','-y','-i',`${out}/${mode}.webm`,'-vf','fps=10,scale=360:-1,tile=8x8','-frames:v','1',`${out}/${mode}-sheet.jpg`]);
 console.log(mode,{choiceAt,samples:samples.length,visibleFrames:visible.length,loadingMs:visible[0].time-samples[0].time,incompleteVisibleFrames:visible.filter(s=>s.broken.length).length});
}
await browser.close();
