import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const dir = new URL('.', import.meta.url).pathname;
const browser = await chromium.launch({headless:true});
const records=[];
for (const [device,width,height] of [['desktop',1440,900],['mobile',390,844],['small',320,568]]) {
 const page=await browser.newPage({viewport:{width,height}});
 const intercepted=[];
 await page.route(/inventory-barge-style-v6|inventory-alphabet-boat-v8/,async route=>{
  intercepted.push(route.request().url());
  await route.fulfill({path:dir+(route.request().url().includes('alphabet')?'outcome-v2.png':'warehouse-master-v2.png'),contentType:'image/png'});
 });
 await page.goto('http://127.0.0.1:4173/scenes.html?scene=inventory&parcel=boat&recipient=alva');
 for(let n=0;n<30;n++) {const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}
 const snap=async name=>{await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});await page.screenshot({path:dir+device+'-'+name+'.png'});};
 await snap('warehouse');
 await page.locator('[data-choice-id="alphabet"]').first().click();
 await page.locator('[data-choice-confirm]').click();
 await snap('outcome');
 records.push({device,intercepted,images:await page.locator('img').evaluateAll(a=>a.map(i=>({src:i.currentSrc,loaded:i.complete&&i.naturalWidth>0}))),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});
 await page.close();
}
await browser.close();
await fs.writeFile(dir+'capture-receipt.json',JSON.stringify(records,null,2));
console.log('Captured 6 pilot screens; production files unchanged.');
