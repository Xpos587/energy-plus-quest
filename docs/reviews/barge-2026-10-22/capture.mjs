import {chromium,expect} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const D='docs/reviews/barge-2026-10-22',P='docs/reviews/barge-2026-10-17/revision-3';
const b=await chromium.launch(),rows=[];
async function shot(page,name,meta){await page.evaluate(()=>document.fonts.ready);await page.locator('img').evaluateAll(is=>Promise.all(is.map(i=>i.decode())));await page.evaluate(async()=>{if(window.PROTOTYPE){const i=new Image();i.src=document.body.dataset.parcel==='boat'?'action-boat-v1.png':'action-sheet-v1.png';await i.decode();}});await page.screenshot({path:`${D}/frames/${name}.png`,animations:'disabled'});const metrics=await page.evaluate(()=>({overflow:[document.documentElement.scrollWidth>innerWidth,document.documentElement.scrollHeight>innerHeight],buttons:[...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width).map(e=>{const r=e.getBoundingClientRect();return{text:e.textContent,inside:r.x>=0&&r.y>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,unclipped:e.scrollHeight<=e.clientHeight+1};}),images:[...document.images].map(i=>({currentSrc:i.currentSrc,natural:[i.naturalWidth,i.naturalHeight],display:[i.clientWidth,i.clientHeight]}))}));rows.push({...meta,file:`frames/${name}.png`,...metrics});}
try{for(const viewport of [{width:390,height:844},{width:1440,height:900}]){
const size=viewport.width===390?'mobile':'desktop';
for(const v of ['a','b','c'])for(const parcel of ['boat','camera','socks']){
const page=await b.newPage({viewport,reducedMotion:'reduce'});
await page.goto('file://'+process.cwd()+`/${P}/prototype.html?v=${v}&parcel=${parcel}`);
let parts=0;while(await page.locator('.condition').count()){await expect(page.locator('.condition button')).toBeInViewport({ratio:1});await page.locator('.condition button').click();parts++;}
for(const state of ['choice','remote','rush','wait','petr']){if(state!=='choice')await page.locator(`[data-option=${state}]`).click();
await shot(page,`${size}-${v}-${parcel}-${state}`,{surface:'prototype',variant:v,parcel,state,viewport,introParts:parts});
if(state!=='choice'){await page.locator('[data-revise]').click();await expect(page.locator('main')).toHaveAttribute('data-state','choice');}}
await page.close();}
for(const parcel of ['boat','camera','socks']){const page=await b.newPage({viewport,reducedMotion:'reduce'});await page.goto('http://127.0.0.1:4344/');await page.evaluate(({parcel})=>{localStorage.clear();const s='quest-area-review';localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope:s,state:{step:'outcome',profile:'student',recipient:'alva',parcel,carrier:'old'}}));localStorage.setItem(s+':remaining','true');localStorage.setItem(s+':scenes',JSON.stringify({progress:{sceneIndex:2,phase:'choice',answers:{compact:'place-1',inventory:'wms'},finished:false},briefed:['compact','inventory','crane','lastmile']}));},{parcel});await page.reload();await page.locator('[data-scene-choice=remote]').waitFor();
for(const state of ['choice','remote','rush','wait','petr']){if(state!=='choice'){await page.locator(`[data-scene-choice=${state}]`).click();await expect(page.locator('[data-result-reader]')).toBeVisible();}await shot(page,`${size}-runtime-${parcel}-${state}`,{surface:'runtime4344',parcel,state,viewport});if(state!=='choice')await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();}await page.close();}
}
await writeFile(`${D}/readback.json`,JSON.stringify(rows,null,2));console.log(JSON.stringify({cases:rows.length,overflow:rows.filter(r=>r.overflow.some(Boolean)).map(r=>r.file),clippedButtons:rows.filter(r=>r.buttons.some(t=>!t.inside||!t.unclipped)).map(r=>r.file)}));}finally{await b.close();}
