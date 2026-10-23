import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const dir=new URL('.',import.meta.url).pathname;
const browser=await chromium.launch({headless:true});
const records=[];
const nextArt = process.env.PILOT_ART; const branch=process.env.PILOT_BRANCH; if(!nextArt||!branch)throw Error('Missing branch/art');
for(const [device,width,height] of [['desktop',1440,900],['mobile',390,844],['small',320,568]]){
 for(const version of ['before','after']){
  const page=await browser.newPage({viewport:{width,height}});
  await page.route(new RegExp('inventory-barge-style-v6|inventory-'+branch+'-v8'),async route=>{
   const outcome=route.request().url().includes(branch);
   const file=version==='before'?(outcome?`family-boat/baseline/inventory-${branch}-v8.webp`:'baseline/warehouse.webp'):outcome?nextArt:'warehouse-master-v3-final.png';
   await route.fulfill({path:dir+file,contentType:version==='before'?'image/webp':'image/png'});
  });
  await page.goto('http://127.0.0.1:4173/scenes.html?scene=inventory&parcel=boat&recipient=alva');
  for(let n=0;n<30;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}
  await page.locator('[data-choice-id="'+branch+'"][data-hotspot]').click();
  await page.locator('[data-choice-confirm]').click();
  const copy=await page.locator('[data-testid="result-copy"]').innerText();
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  if(version==='after'){
   await page.addStyleTag({content:`
    [data-scene="inventory"] [data-result] {background:#fff!important;box-shadow:none!important;}
    @media(max-width:750px){
     [data-scene="inventory"] [data-result]{position:fixed!important;inset:auto 12px 12px!important;transform:none!important;translate:none!important;width:auto!important;height:calc(100dvh - 88px - min(56.25vw,44dvh))!important;max-height:calc(100dvh - 88px - min(56.25vw,44dvh))!important;overflow:hidden!important;}
    }
    [data-scene-consequence="inventory-${branch}"]{position:fixed!important;top:var(--pilot-top)!important;left:0!important;width:100%!important;height:var(--pilot-height)!important;overflow:hidden!important;cursor:default!important;background:#e8edf0;}
    [data-scene-consequence="inventory-${branch}"] picture{display:block!important;width:100%!important;min-width:0!important;height:100%!important;}
    [data-scene-consequence="inventory-${branch}"] img{width:100%!important;min-width:0!important;height:100%!important;object-fit:contain!important;}
   `});
   await page.evaluate(()=>{
    const measure=()=>{const head=document.querySelector('[data-scene="inventory"] > header').getBoundingClientRect();const panel=document.querySelector('[data-result]').getBoundingClientRect();document.documentElement.style.setProperty('--pilot-top',`${head.bottom+8}px`);document.documentElement.style.setProperty('--pilot-height',`${Math.max(0,panel.top-head.bottom-16)}px`);};
    measure(); window.addEventListener('resize',measure); new ResizeObserver(measure).observe(document.querySelector('[data-result]'));
   });
  }
  await page.screenshot({path:dir+`natural-faces/${branch}-${device}-${version}.png`});
  const metrics=await page.evaluate(()=>{
   const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}};
   const reader=document.querySelector('[data-result-reading]');
   return {art:rect('[data-scene-consequence]'),panel:rect('[data-result]'),reader:{height:reader.clientHeight,scrollHeight:reader.scrollHeight},overflow:document.documentElement.scrollWidth>innerWidth};
  });
  const readPages=[];
  for(let n=0;n<40;n++){
   readPages.push(await page.locator('[data-testid="result-copy"]').innerText());
   const next=page.getByRole('button',{name:'Читать дальше',exact:true});
   if(!await next.isVisible())break;
   await next.click();
   if(n===39)throw Error('Reading loop exceeded');
  }
  if(!await page.getByRole('button',{name:'Продолжить',exact:true}).isVisible())throw Error('Narrative end not reached');
  if(version==='after'){
   for(let n=0;n<40;n++){const back=page.getByRole('button',{name:'Назад по рассказу',exact:true});if(!await back.isVisible())break;await back.click();}
   await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
   for(let n=0;n<30;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}
   await page.locator('[data-choice-id="'+branch+'"]').first().waitFor();
  }
  records.push({device,version,copy,readPages,...metrics});
  await page.close();
 }
}
await browser.close();
for(const device of ['desktop','mobile','small']){
 const pair=records.filter(r=>r.device===device);
 const normalize=r=>r.readPages.join(' ').replace(/\s+/g,' ').trim();
 if(normalize(pair[0])!==normalize(pair[1]))throw Error('Before/after full narrative mismatch');
}
await fs.writeFile(dir+`natural-faces/${branch}-capture-receipt.json`,JSON.stringify(records,null,2));
console.log('6 screenshots; full paginated copy and return to choices verified. Preview-only layout.');
