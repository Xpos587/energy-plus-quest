import { chromium } from 'playwright';
import { mkdir, writeFile, copyFile } from 'node:fs/promises';
const stage=process.argv[2];
if(!['current','blender','final','gate'].includes(stage)) throw Error('Use current|blender|final|gate');
const root='.tmp-work/scene4-final-render';
const out=`${root}/${stage}`;
await mkdir(out,{recursive:true});
const browser=await chromium.launch();
const checks=[];
try {
 for(const [width,height] of [[1440,900],[390,844]]){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:1,serviceWorkers:'block',reducedMotion:'reduce'});
  const page=await context.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const way of stage==='gate'?['choice']:['choice','remote','rush','petr']){
   await page.goto('http://127.0.0.1:4175/scenes.html?scene=crane&parcel=camera&recipient=alva');
   await page.locator('[data-hotspot]').first().waitFor({state:'attached'});
   const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
   for(let n=0;n<20&&await next.isVisible();n++)await next.click();
   if(await page.locator('[data-hotspot]').count()!==3)throw Error('Expected exactly three choices');
   if(way!=='choice'){
    await page.locator(`[data-hotspot="${way}"]`).click();
    await page.locator('[data-choice-confirm]').click();
    await page.locator('[data-result-reader]').waitFor();
   }
   await page.locator('img').evaluateAll(images=>Promise.all(images.map(i=>i.decode())));
   await page.addStyleTag({content:'[data-barge-ripple]{animation:none!important;transform:none!important;opacity:.8!important}'});
   if(way==='choice')await page.waitForFunction(()=>getComputedStyle(document.querySelector('[data-barge-art]>div')).visibility==='visible');
   await page.screenshot({path:`${out}/${way}-${width}x${height}.png`});
   const data=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),art:document.querySelector('[data-barge-art]')?.getAttribute('data-barge-art'),result:!!document.querySelector('[data-result-reader]')}));
   if(data.overflow||data.broken.length||errors.length)throw Error(JSON.stringify({data,errors}));
   checks.push({width,height,way,...data});
  }
  await context.close();
 }
 for(const [name,width,height] of [['wide',1942,809],['desk',1536,1024],['mid',1402,1122],['tall',1024,1536]].filter(([name])=>stage!=='gate'||['wide','tall'].includes(name))){
  const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:2,serviceWorkers:'block',reducedMotion:'reduce'});
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:4175/scenes.html?scene=crane&parcel=camera&recipient=alva');
  await page.locator('[data-hotspot]').first().waitFor({state:'attached'});
  const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
  for(let n=0;n<20&&await next.isVisible();n++)await next.click();
  await page.addStyleTag({content:`[data-barge-art]{position:fixed!important;left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;z-index:9999}[data-barge-art]>div{left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;transition:none!important}[data-barge-art] button,[data-barge-ripple]{display:none!important}`});
  await page.locator(`[data-barge-art="${name}"]`).waitFor();
  await page.locator('[data-barge-art] img').evaluateAll(images=>Promise.all(images.map(i=>i.decode())));
  await page.waitForFunction(()=>getComputedStyle(document.querySelector('[data-barge-art]>div')).visibility==='visible');
  await page.screenshot({path:`${out}/art-${name}.png`,clip:{x:0,y:0,width,height}});
  await context.close();
 }
 for(const way of stage==='gate'?[]:['remote','rush','petr']) for(const suffix of ['','-rail','-portrait']) await copyFile(`public/scene-art/barge-v5/outcome-${way}${suffix}.webp`,`${out}/outcome-${way}${suffix}.webp`);
 await writeFile(`${out}/checks.json`,JSON.stringify(checks,null,2)+'\n');
 console.log(stage,stage==='gate'?': 2 choice viewports and wide/tall native art; other formats/outcomes not in this gate':': 8 runtime cases, all four clean native 2x artwork inputs, all nine live crop-contract outcome samples');
} finally {await browser.close();}
