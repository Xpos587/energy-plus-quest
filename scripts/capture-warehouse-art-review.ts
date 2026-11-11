import { chromium } from '@playwright/test';
import { openInventory } from '../tests/inventory-fixture';
import { mkdir, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const out=process.argv[2]??'.tmp-work/r24-warehouse-a-runtime';
await mkdir(out,{recursive:true});
const browser=await chromium.launch();
const receipts=[];
try {
 for(const [width,height] of [[1440,900],[390,844]]) {
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1,baseURL:process.env.INVENTORY_TEST_URL??'http://127.0.0.1:4199',reducedMotion:'reduce'});
  const errors:string[]=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
  // Actual runtime only: no request interception, DOM/image replacement or synthetic screenshots.
  await openInventory(page);
  const img=page.locator('[data-world-plane] picture img');
  const currentSrc=await img.evaluate((i:HTMLImageElement)=>i.currentSrc);
  assert.ok(currentSrc.endsWith(`inventory-master-v16${width===390?'-tall':''}.webp`),currentSrc);
  const markers=await page.locator('[data-hotspot]').evaluateAll(nodes=>nodes.map(n=>({id:(n as HTMLElement).dataset.hotspot,rect:n.getBoundingClientRect().toJSON()})));
  assert.equal(markers.length,4);
  await page.screenshot({path:`${out}/choice-${width}x${height}.png`,scale:'css'});
  receipts.push({width,height,kind:'choice',currentSrc,markers});
  for(const [id,parcel] of [['entrance','boat'],['alphabet','boat'],['alphabet','camera'],['alphabet','socks'],['keeper','boat'],['wms','boat']]) {
   await openInventory(page,parcel);
   await page.locator(`[data-hotspot="${id}"]`).click();
   await page.locator('[data-choice-confirm]').click();
   const result=page.locator('[data-outcome-scene] img');
   await result.evaluate((i:HTMLImageElement)=>i.decode());
   const src=await result.evaluate((i:HTMLImageElement)=>i.currentSrc);
   assert.ok(src.endsWith(`/warehouse-results-v3/outcome-${id==='alphabet'?`alphabet-${parcel}`:id}.webp`),src);
   await page.screenshot({path:`${out}/${id}-${parcel}-${width}x${height}.png`,scale:'css'});
   receipts.push({width,height,kind:'result',id,parcel,currentSrc:src});
  }
  assert.deepEqual(errors,[]);
  receipts.push({width,height,errors});
  await page.close();
 }
} finally {await browser.close();}
await writeFile(`${out}/browser.json`,JSON.stringify({requestInterception:false,receipts},null,2));
console.log('Verified 14 actual-runtime captures (2 choices + 12 results), no page/HTTP errors.');
