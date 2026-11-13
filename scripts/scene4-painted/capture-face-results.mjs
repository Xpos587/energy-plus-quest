import { chromium } from 'playwright';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
// Real-time browser verification; no clock fast-forward (result text animates separately).
const root=resolve(import.meta.dirname,'../..');
const [base='http://127.0.0.1:4175',dir=resolve(root,'.tmp-work/scene4-faces/reviews')]=process.argv.slice(2);
await mkdir(dir,{recursive:true});
const browser=await chromium.launch(),checks=[];
try {for(const [width,height] of [[1440,900],[390,844]])for(const way of ['remote','rush','petr']){
 const context=await browser.newContext({viewport:{width,height},deviceScaleFactor:2,serviceWorkers:'block'}),page=await context.newPage();
 await page.goto(new URL('/scenes.html?scene=crane&parcel=camera&recipient=alva',base).href);
 await page.locator('[data-hotspot]').first().waitFor({state:'attached'});
 const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});
 for(let n=0;n<20&&await next.isVisible();n++)await next.click();
 if(await page.locator('[data-hotspot]').count()!==3)throw Error('Expected exactly three choices');
 await page.locator('[data-barge-art][data-artwork-ready=true]').waitFor({state:'visible'});
 await page.locator('[data-barge-art] img').evaluateAll(images=>Promise.all(images.map(image=>image.decode())));
 if(await page.locator('[data-layer=ivan]').count())throw Error('Duplicate legacy Ivan overlay');
 if(way==='remote')await page.screenshot({path:`${dir}/choice-${width}.png`,animations:'disabled'});
 await page.locator(`[data-hotspot=${way}]`).click();
 await page.locator('[data-choice-confirm]').click();
 const result=page.locator(`[data-scene-consequence=crane-${way}] img`);
 await result.waitFor({state:'visible',timeout:20000});await result.evaluate(i=>i.decode());
 await page.getByTestId('result-copy').waitFor({state:'visible'});
 await page.waitForFunction(()=>{const p=document.querySelector('[data-testid=result-copy]');return p&&p.textContent.trim().length>30;});
 const row=await result.evaluate(i=>({src:i.currentSrc,width:i.naturalWidth,height:i.naturalHeight,alt:i.alt}));
 const suffix=width===1440?'-rail':'-portrait';
 if(!new URL(row.src).pathname.endsWith(`/outcome-${way}${suffix}.webp`))throw Error(JSON.stringify(row));
 const state=await page.evaluate(()=>({broken:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),loading:!!document.querySelector('[data-artwork-status]'),overflow:document.documentElement.scrollWidth>innerWidth,copy:document.querySelector('[data-testid=result-copy]')?.textContent}));
 if(state.broken.length||state.loading||state.overflow)throw Error(JSON.stringify(state));
 await page.screenshot({path:`${dir}/${way}-${width}-RESULT.png`,animations:'disabled'});
 checks.push({way,viewport:{width,height},dpr:2,choices:3,legacyIvanLayers:0,...row,...state});await context.close();
 }await writeFile(`${dir}/result-runtime.json`,JSON.stringify(checks,null,2)+'\n');console.log(checks);
}finally{await browser.close();}
