import {chromium} from '@playwright/test';
const b=await chromium.launch({args:['--disable-gpu']});
for(const [width,height] of [[1440,900],[1920,1080],[1024,768]]){
 const p=await b.newPage({viewport:{width,height}});
 await p.goto('http://127.0.0.1:4173/scenes.html?scene=crane&parcel=camera&recipient=alva');
 const next=p.getByRole('button',{name:/^(Далее|К выбору)$/});for(let i=0;i<20&&await next.isVisible();i++)await next.click();
 await p.locator('[data-scene-choice="petr"]').click();await p.locator('[data-choice-confirm]').click();
 await p.addStyleTag({content:`
 @media(min-width:901px) and (min-height:501px){
 [data-layout="result"]:has([data-scene-consequence="crane-petr"]){grid-template-columns:minmax(0,1fr) 320px!important;grid-template-rows:minmax(0,1fr)!important}
 [data-layout="result"]:has([data-scene-consequence="crane-petr"]) > [data-result]{grid-column:2!important;grid-row:1!important}
 [data-scene-consequence="crane-petr"] img{object-position:65% center!important}
 [data-layout="result"]:has([data-scene-consequence="crane-petr"]) footer{grid-template-columns:1fr 1fr!important;gap:8px!important}
 [data-layout="result"]:has([data-scene-consequence="crane-petr"]) [data-result-feedback]{grid-column:1/-1!important;grid-row:1!important}
 [data-layout="result"]:has([data-scene-consequence="crane-petr"]) footer button{grid-row:2!important;font-size:16px!important}
 }`});
 console.log(await p.locator('[data-layout]').evaluate(e=>({html:e.outerHTML.slice(0,400),cols:getComputedStyle(e).gridTemplateColumns,match:!!e.querySelector('[data-scene-consequence="crane-petr"]')})));await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));await p.screenshot({path:`design/media-audit-2026-10-05/petr-trial-${width}.png`});await p.close();
}await b.close();
