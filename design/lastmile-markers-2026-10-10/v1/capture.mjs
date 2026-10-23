import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const stage='v1';
const root='design/lastmile-markers-2026-10-10/v1/screens';
await mkdir(root,{recursive:true});
const browser=await chromium.launch({args:['--disable-gpu']});
const records=[];
for(const [width,height] of [[320,568],[393,650],[393,852],[820,1180],[1440,900]]){
 const page=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});
 await page.addInitScript(()=>{const scope='quest-barge-final';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'professional',recipient:'arseniy',parcel:'socks',carrier:'crew'}}));localStorage.setItem(scope+':intro-seen','true');localStorage.setItem(scope+':remaining','true');localStorage.setItem(scope+':scenes',JSON.stringify({progress:{sceneIndex:3,phase:'choice',finished:false,answers:{compact:'auto',inventory:'wms',crane:'remote'}}}));});
 const errors=[]; page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4173/');
 await page.locator('[data-world-scene="lastmile"]').waitFor();
 const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let i=0;i<30&&await next.isVisible();i++)await next.click();
 await page.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 const numbers=await page.locator('button[data-hotspot]').evaluateAll(es=>es.map(e=>({id:e.getAttribute('data-hotspot'),number:e.innerText.trim(),rect:e.getBoundingClientRect().toJSON(),badgeInset:getComputedStyle(e,'::before').top,radius:getComputedStyle(e,'::before').borderRadius})));
 for(const m of numbers){if(m.rect.width<44||m.rect.height<44||m.radius==='50%')throw Error('Bad marker '+m.id);}
 await page.screenshot({path:`${root}/${stage}-${width}x${height}.png`});
 if(height<=700)await page.screenshot({path:`${root}/v1-full-${width}x${height}.png`,fullPage:true});
 records.push({width,height,errors,text:await page.locator('body').innerText(),geometry:await page.locator('[data-world-plane],[data-hotspot]').evaluateAll(es=>es.map(e=>({tag:e.tagName,id:e.getAttribute('data-hotspot'),rect:e.getBoundingClientRect().toJSON()}))),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
 for(const id of ['helicopter','rover','robot','pipe-carrier']){
  await page.locator(`[data-scene-choice="${id}"]`).click();
  await page.locator('[data-inspecting="true"]').waitFor();
  await page.screenshot({path:`${root}/v1-selected-${id}-${width}x${height}.png`});
  const active=page.locator('[data-lastmile-object][data-active="true"] [data-lastmile-zone]');
  const style=await active.evaluate(e=>{const s=getComputedStyle(e);return{stroke:s.stroke,strokeWidth:s.strokeWidth,fillOpacity:s.fillOpacity}});
  if(Number(style.fillOpacity)<.1||Number.parseFloat(style.strokeWidth)<1.5)throw Error('Invisible selection '+id);
  await page.getByRole('button',{name:'К вариантам',exact:true}).click();
 }
 for(const [id,wide,tall] of [
  ['helicopter',[1042,138],[408,515]],['rover',[925,582],[354,874]],['robot',[1185,662],[530,922]],['pipe-carrier',[635,581],[180,876]]]){
  await page.evaluate(()=>scrollTo(0,0));
  const plane=page.locator('[data-world-plane]');
  const target=await plane.evaluate((e,coords)=>{const r=e.getBoundingClientRect();const w=Number(e.querySelector('img').getAttribute('width'));return{x:r.x+coords[0]*r.width/w,y:r.y+coords[1]*r.width/w};},await plane.locator('img').getAttribute('width')==='1983'?wide:tall);
  await page.mouse.click(target.x,target.y);
  await page.locator(`[data-lastmile-selection="${id}"]`).waitFor();
  await page.getByRole('button',{name:'К вариантам',exact:true}).click();
 }
 await page.close();
}
await browser.close(); await writeFile(`design/lastmile-markers-2026-10-10/v1/check.json`,JSON.stringify(records,null,2));console.log(records.map(({width,errors,overflow})=>({width,errors,overflow})));
