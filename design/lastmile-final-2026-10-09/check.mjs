import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const root='design/lastmile-final-2026-10-09';await mkdir(root+'/screens',{recursive:true});
const browser=await chromium.launch({args:['--disable-gpu']});const records=[];
for(const [width,height] of [[320,568],[393,852],[820,1180],[1440,900]]) for(const parcel of ['camera','socks','boat']) for(const choice of ['rover','robot','pipe-carrier','helicopter']){
 const id=`${width}-${parcel}-${choice}`,p=await browser.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(`http://127.0.0.1:4173/scenes.html?scene=lastmile&parcel=${parcel}&recipient=alva`);
 const brief=p.getByRole('button',{name:/^(Далее|К выбору)$/});for(let i=0;i<30&&await brief.isVisible();i++)await brief.click();
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 if(choice==='rover'&&parcel==='camera')await p.screenshot({path:`${root}/screens/${width}-choice.png`});
 await p.locator(`[data-scene-choice="${choice}"]`).click();await p.locator('[data-choice-confirm]').click();await p.locator('[data-result-reader]').waitFor();
 let pages=0;const sources=[];for(;pages<30;pages++){
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 const img=await p.locator('[data-result-art] img,[data-outcome-scene] img').evaluateAll(es=>es.map(e=>e.currentSrc));sources.push(...img);
 if(pages===0||(choice==='helicopter'&&await p.locator('[data-delivery-leg="ground"]').count()))await p.screenshot({path:`${root}/screens/${id}-p${pages}.png`});
 const next=p.getByRole('button',{name:'Читать дальше',exact:true});if(!await next.isVisible())break;await next.click();}
 const metrics=await p.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(e=>!e.complete||!e.naturalWidth).map(e=>e.src),offscreen:[...document.querySelectorAll('[data-result-reader] button')].filter(e=>{const r=e.getBoundingClientRect();return r.width&& (r.left<0||r.right>innerWidth+1||r.bottom>innerHeight+1)}).map(e=>e.textContent)}));
 if(choice==='rover'&&parcel==='camera'){
 await p.getByRole('button',{name:'К вручению подарка',exact:true}).click();await p.locator('[data-journey-ending]').waitFor();await p.screenshot({path:`${root}/screens/${width}-mission.png`});
 await p.getByRole('button',{name:'Узнать, какой вы логист'}).click();await p.locator('[data-logist-certificate]').waitFor();await p.screenshot({path:`${root}/screens/${width}-certificate.png`});}
 records.push({id,pages:pages+1,sources:[...new Set(sources)],errors,...metrics});await p.close();
}
await browser.close();await writeFile(root+'/check.json',JSON.stringify(records,null,2));console.log(JSON.stringify({cases:records.length,failures:records.filter(r=>r.errors.length||r.overflow||r.broken.length||r.offscreen.length)}));
