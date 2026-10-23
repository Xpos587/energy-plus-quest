import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const root='design/lastmile-final-2026-10-09/v5';await mkdir(root+'/screens',{recursive:true});
const b=await chromium.launch({args:['--disable-gpu']});const records=[];
for(const [width,height] of [[320,568],[393,852],[820,1180],[1440,900]])for(const parcel of ['boat','camera','socks'])for(const option of ['rover','robot','pipe-carrier','helicopter']){
 const p=await b.newPage({viewport:{width,height},reducedMotion:'reduce'});const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.addInitScript(parcel=>{const scope='quest-lastmile-final';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope,state:{step:'outcome',profile:'professional',recipient:'alva',parcel,carrier:'crew'}}));localStorage.setItem(scope+':intro-seen','true');localStorage.setItem(scope+':remaining','true');localStorage.setItem(scope+':scenes',JSON.stringify({progress:{sceneIndex:3,phase:'choice',finished:false,answers:{compact:'auto',inventory:'wms',crane:'remote'}}}));},parcel);
 await p.goto('http://127.0.0.1:4173/');await p.locator('[data-world-scene="lastmile"]').waitFor();const next=p.getByRole('button',{name:/^(Далее|К выбору)$/});for(let i=0;i<30&&await next.isVisible();i++)await next.click();
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 const choice=await p.locator('[data-world-scene="lastmile"] img').getAttribute('src');if(!choice.includes('-v9.webp'))throw Error(choice);
 if(parcel==='boat'&&option==='rover')await p.screenshot({path:`${root}/screens/${width}-choice.png`});
 await p.locator(`[data-scene-choice="${option}"]`).click();await p.locator('[data-choice-confirm]').click();await p.locator('[data-result-reader]').waitFor();
 const sources=[];let pages=0;for(;pages<30;pages++){
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 sources.push(...await p.locator('[data-result-art] img,[data-outcome-scene] img').evaluateAll(es=>es.map(e=>e.currentSrc)));
 if(pages===0)await p.screenshot({path:`${root}/screens/${width}-${parcel}-${option}.png`});
 if(option==='helicopter'&&await p.locator('[data-delivery-leg="ground"]').count())await p.screenshot({path:`${root}/screens/${width}-${parcel}-${option}-ground.png`});
 const read=p.getByRole('button',{name:'Читать дальше',exact:true});if(!await read.isVisible())break;await read.click();
 }
 const expected={rover:`rusak-${parcel==='boat'?'boat':'parcel'}-final-v5`,robot:`robot-${parcel==='boat'?'boat-result-v3':'parcel-result-v1'}`,'pipe-carrier':'pipecarrier-return-swim-v5',helicopter:`helicopter-ground-${parcel==='boat'?'boat':'parcel'}-final-v5`}[option];if(!sources.some(s=>s.includes(expected)))throw Error(`${width}/${parcel}/${option}: ${sources}`);
 const metrics=await p.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,broken:[...document.images].filter(e=>!e.complete||!e.naturalWidth).map(e=>e.src)}));records.push({width,height,parcel,option,choice,sources:[...new Set(sources)],pages:pages+1,errors,...metrics});await p.close();
}
await b.close();await writeFile(root+'/check.json',JSON.stringify(records,null,2));console.log(JSON.stringify({cases:records.length,failures:records.filter(r=>r.errors.length||r.overflow||r.broken.length)}));
