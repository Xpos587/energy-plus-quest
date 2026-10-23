import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const browser=await chromium.launch();
try {
 const page=await browser.newPage(); const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,390,320]){
  await page.setViewportSize({width,height:1000});
  await page.goto('http://127.0.0.1:4173/review/scene-concepts-2026-09-23/compact-style/art-review.html');
  for(const title of ['Новая проработка','Исходная схема']){
   await page.getByRole('button',{name:title,exact:true}).click();
   await page.locator('#art').evaluate(i=>i.decode());
   assert(await page.locator('#art').evaluate(i=>i.naturalWidth>0));
   assert.equal(await page.locator('#art').getAttribute('src'),await page.locator('#full').getAttribute('href'));
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  }
  await page.getByRole('button',{name:'Новая проработка',exact:true}).click();
  await page.locator('#art').evaluate(i=>i.decode());
  await page.screenshot({path:`design/scene-world/compact-style-2026-09-23/review-${width}.png`,fullPage:true});
 }
 assert.deepEqual(errors,[]);
 console.log('PASS: loading review at 1440/390/320, both images decode, image links switch with the selected version, no horizontal overflow or runtime errors.');
} finally { await browser.close(); }
