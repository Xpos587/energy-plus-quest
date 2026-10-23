import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const dir=new URL('.',import.meta.url).pathname;
const browser=await chromium.launch({headless:true});
const records=[];
const nextArt=process.env.PILOT_ART || 'outcome-v4-final.png';
for(const [device,width,height] of [['desktop',1440,900],['mobile',390,844],['small',320,568]]){
 for(const version of ['before','after']){
  const page=await browser.newPage({viewport:{width,height}});
  await page.route(/inventory-barge-style-v6|inventory-alphabet-boat-v8/,async route=>{
   const outcome=route.request().url().includes('alphabet');
   const file=version==='before'?`baseline/${outcome?'outcome':'warehouse'}.webp`:outcome?(width<=750&&height>=700?'outcome-mobile-v4-final.png':nextArt):'warehouse-master-v3-final.png';
   await route.fulfill({path:dir+file,contentType:version==='before'?'image/webp':'image/png'});
  });
  await page.goto('http://127.0.0.1:4173/scenes.html?scene=inventory&parcel=boat&recipient=alva');
  for(let n=0;n<30;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}
  await page.locator('[data-choice-id="alphabet"]').first().click();
  await page.locator('[data-choice-confirm]').click();
  const copy=await page.locator('[data-testid="result-copy"]').innerText();
  await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  if(version==='after'){
   await page.addStyleTag({content:`
    [data-scene="inventory"] [data-result] {background:#fff!important;box-shadow:none!important;}
    @media(max-width:750px){
     [data-scene="inventory"] [data-result]{max-height:calc(100dvh - 120px - 60vw)!important;overflow:hidden!important;}
    }
    [data-scene-consequence="inventory-alphabet-boat"]{position:fixed!important;top:var(--pilot-top)!important;left:0!important;width:100%!important;height:var(--pilot-height)!important;overflow:hidden!important;cursor:default!important;background:#e8edf0;}
    [data-scene-consequence="inventory-alphabet-boat"] picture{display:block!important;width:100%!important;min-width:0!important;height:100%!important;}
    [data-scene-consequence="inventory-alphabet-boat"] img{width:100%!important;min-width:0!important;height:100%!important;object-fit:contain!important;}
   `});
   await page.evaluate(()=>{
    const measure=()=>{const head=document.querySelector('[data-scene="inventory"] > header').getBoundingClientRect();const panel=document.querySelector('[data-result]').getBoundingClientRect();document.documentElement.style.setProperty('--pilot-top',`${head.bottom+8}px`);document.documentElement.style.setProperty('--pilot-height',`${Math.max(0,panel.top-head.bottom-16)}px`);};
    measure(); window.addEventListener('resize',measure); new ResizeObserver(measure).observe(document.querySelector('[data-result]'));
   });
  }
  await page.screenshot({path:dir+`${device}-${version}-v4.png`});
  const metrics=await page.evaluate(()=>{
   const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom}};
   const reader=document.querySelector('[data-result-reading]');
   return {art:rect('[data-scene-consequence]'),panel:rect('[data-result]'),reader:{height:reader.clientHeight,scrollHeight:reader.scrollHeight},overflow:document.documentElement.scrollWidth>innerWidth};
  });
  if(version==='after'){
   await page.locator('[data-result-reading]').evaluate(el=>{el.scrollTop=el.scrollHeight;});
   const reachedEnd=await page.locator('[data-result-reading]').evaluate(el=>el.scrollHeight-el.clientHeight-el.scrollTop<2);
   if(!reachedEnd)throw Error('Full copy is not accessible');
   if(await page.locator('[data-testid="result-copy"]').innerText()!==copy)throw Error('Copy changed');
   await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
   for(let n=0;n<30;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}
   await page.locator('[data-choice-id="alphabet"]').first().waitFor();
  }
  records.push({device,version,copy,...metrics});
  await page.close();
 }
}
await browser.close();
for(const device of ['desktop','mobile','small']){
 const pair=records.filter(r=>r.device===device);
 if(pair[0].copy!==pair[1].copy)throw Error('Before/after copy mismatch');
}
await fs.writeFile(dir+'capture-v4-receipt.json',JSON.stringify(records,null,2));
console.log('6 screenshots; full copy, scrolling and return to choices verified. Preview-only layout.');
