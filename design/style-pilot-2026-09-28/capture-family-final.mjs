import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const dir=new URL('.',import.meta.url).pathname;
const out=dir+'family-final-check/';
await fs.mkdir(out,{recursive:true});
const exists=async p=>fs.access(dir+p).then(()=>true,()=>false);
const assets={
 'inventory-barge-style-v6':'clean-colors/warehouse-v4.png',
 'inventory-entrance-v8':'clean-colors/entrance-v3.png',
 'inventory-alphabet-boat-v8':'clean-colors/alphabet-v12.png',
 'inventory-keeper-v8':await exists('clean-colors/keeper-v7.png')?'clean-colors/keeper-v7.png':'clean-colors/keeper-v6.png',
 'inventory-wms-v8':await exists('clean-colors/wms-v11.png')?'clean-colors/wms-v11.png':'clean-colors/wms-v10.png',
};
for(const file of Object.values(assets))if(!await exists(file))throw Error('Missing '+file);
const browser=await chromium.launch({headless:true});
const records=[];
async function ready(page){await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});await page.waitForTimeout(250);}
async function briefing(page){for(let n=0;n<40;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});if(!await b.isVisible())return;await b.click();}throw Error('Briefing loop exceeded');}
async function metrics(page){return page.evaluate(()=>{
 const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
 const art=document.querySelector('[data-scene-consequence]');const panel=document.querySelector('[data-result]');const a=rect(art),p=rect(panel);
 const images=[...document.images].map(i=>({src:i.currentSrc,loaded:i.complete&&i.naturalWidth>0,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,rect:rect(i),objectFit:getComputedStyle(i).objectFit}));
 return {viewport:{width:innerWidth,height:innerHeight},overflowX:document.documentElement.scrollWidth>innerWidth,overflowY:document.documentElement.scrollHeight>innerHeight,art:a,panel:p,overlap:a&&p?{width:Math.max(0,Math.min(a.right,p.right)-Math.max(a.x,p.x)),height:Math.max(0,Math.min(a.bottom,p.bottom)-Math.max(a.y,p.y))}:null,reader:rect(document.querySelector('[data-result-reading]')),images};
});}
try{
 for(const [device,width,height] of [['desktop',1440,900],['tablet',820,1180],['mobile',390,844],['small',320,568]]){
  const page=await browser.newPage({viewport:{width,height}});const errors=[];const routed=[];
  page.on('pageerror',e=>errors.push(String(e)));
  await page.route(/inventory-(?:barge-style-v6|entrance-v8|alphabet-boat-v8|keeper-v8|wms-v8)/,async route=>{const key=Object.keys(assets).find(k=>route.request().url().includes(k));routed.push({url:route.request().url(),asset:assets[key]});await route.fulfill({path:dir+assets[key],contentType:'image/png'});});
  const response=await page.goto('http://127.0.0.1:4173/scenes.html?scene=inventory&parcel=boat&recipient=alva');
  if(response.status()!==200)throw Error('HTTP '+response.status());
  await briefing(page);await ready(page);
  await page.screenshot({path:out+`${device}-choices.png`});
  records.push({device,stage:'choices',metrics:await metrics(page)});
  for(const branch of ['entrance','alphabet','keeper','wms']){
   await page.locator(`[data-choice-id="${branch}"][data-hotspot]`).focus();await page.locator(`[data-choice-id="${branch}"][data-hotspot]`).press('Enter');await page.locator('[data-choice-confirm]').click();await ready(page);
   const pages=[];
   for(let n=0;n<40;n++){
    pages.push({copy:await page.locator('[data-testid="result-copy"]').innerText(),metrics:await metrics(page)});
    await page.screenshot({path:out+`${device}-${branch}-${n+1}.png`});
    const next=page.getByRole('button',{name:'Читать дальше',exact:true});if(!await next.isVisible())break;await next.click();await ready(page);
    if(n===39)throw Error('Reader loop exceeded');
   }
   if(!await page.getByRole('button',{name:'Продолжить',exact:true}).isVisible())throw Error('Narrative end not reached');
   for(let n=0;n<40;n++){const back=page.getByRole('button',{name:'Назад по рассказу',exact:true});if(!await back.isVisible())break;await back.click();await ready(page);if(n===39)throw Error('Back loop exceeded');}
   await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();await briefing(page);await page.locator(`[data-choice-id="${branch}"][data-hotspot]`).waitFor();
   records.push({device,stage:branch,pages,returnVerified:true,selectionMethod:'hotspot keyboard focus + Enter',errors:[...errors],routed:[...routed]});
   await fs.writeFile(out+'receipt.json',JSON.stringify({assets,records},null,2));
  }
  await page.close();
 }
 const checks=[];
 for(const branch of ['entrance','alphabet','keeper','wms']){
  const rows=records.filter(r=>r.stage===branch);const narrative=r=>r.pages.map(p=>p.copy).join(' ').replace(/\s+/g,' ').trim();
  checks.push({branch,textSameAcrossViewports:rows.every(r=>narrative(r)===narrative(rows[0]))});
 }
 const report={assets,checks,pageErrors:records.flatMap(r=>r.errors??[]),overflow:records.flatMap(r=>(r.pages??[{metrics:r.metrics}]).filter(p=>p.metrics.overflowX||p.metrics.overflowY).map(p=>({device:r.device,stage:r.stage,...p.metrics}))),records};
 await fs.writeFile(out+'receipt.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify({assets,checks,pageErrors:report.pageErrors,overflowCount:report.overflow.length,records:records.length},null,2));
}finally{await browser.close();}
