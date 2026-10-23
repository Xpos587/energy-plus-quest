import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const stage='v4';
const root='design/barge-choice-2026-10-10/screens';
await mkdir(root,{recursive:true});
const browser=await chromium.launch({args:['--disable-gpu']});
const records=[];
for(const [width,height] of [[320,568],[393,650],[393,852],[820,1180],[1440,900]]){
 const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});
 await page.addInitScript(()=>{const scope='quest-barge-final';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'professional',recipient:'alva',parcel:'boat',carrier:'crew'}}));localStorage.setItem(scope+':intro-seen','true');localStorage.setItem(scope+':remaining','true');localStorage.setItem(scope+':scenes',JSON.stringify({progress:{sceneIndex:2,phase:'choice',finished:false,answers:{compact:'auto',inventory:'wms'}}}));});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4173/');
 await page.locator('[data-world-scene="crane"]').waitFor();
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let i=0;i<30&&await next.isVisible();i++)await next.click();
 await page.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 await page.screenshot({path:`${root}/${stage}-${width}x${height}.png`});
 if(height<=700)await page.screenshot({path:`${root}/v4-full-${width}x${height}.png`,fullPage:true});
 records.push({width,height,errors,text:await page.locator('body').innerText(),geometry:await page.locator('[data-world-plane],[data-hotspot]').evaluateAll(es=>es.map(e=>({tag:e.tagName,id:e.getAttribute('data-hotspot'),rect:e.getBoundingClientRect().toJSON()}))),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
 for(const id of ['rush','petr','remote']){
  await page.locator(`[data-scene-choice="${id}"]`).click();
  await page.locator('[data-inspecting="true"]').waitFor();
  await page.screenshot({path:`${root}/v4-selected-${id}-${width}x${height}.png`});
  const active=page.locator('[data-crane-zone][data-active="true"]');
  const style=await active.evaluate(e=>{const s=getComputedStyle(e);return{stroke:s.stroke,strokeWidth:s.strokeWidth,fillOpacity:s.fillOpacity}});
  if(Number(style.fillOpacity)<.1||Number.parseFloat(style.strokeWidth)<1.5)throw Error('Invisible selection '+id);
  await page.getByRole('button',{name:'К вариантам',exact:true}).click();
 }
 await page.close();
}
await browser.close(); await writeFile(`design/barge-choice-2026-10-10/${stage}.json`,JSON.stringify(records,null,2));console.log(records.map(({width,errors,overflow})=>({width,errors,overflow})));
