import {chromium} from '@playwright/test';
const root='docs/reviews/barge-2026-10-17/revision-3',browser=await chromium.launch();
for(const viewport of [{width:320,height:568},{width:390,height:844},{width:844,height:390},{width:1440,height:900}]){
const page=await browser.newPage({viewport});for(const v of ['a','b','c']){
await page.goto('file://'+process.cwd()+`/${root}/prototype.html?v=${v}&state=&parcel=boat`);await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(i=>i.decode())));await page.evaluate(async()=>{await document.fonts.ready;const bg=new Image();bg.src=document.body.dataset.parcel==='boat'?'action-boat-v1.png':'action-sheet-v1.png';await bg.decode();});await page.screenshot({path:`${root}/frames/${v}-${viewport.width}-neutral.png`});
for(const id of ['remote','rush','wait','petr']){await page.locator(`[data-option=${id}]`).focus();if(v==='b'||id==='petr')await page.screenshot({path:`${root}/frames/${v}-${viewport.width}-focus-${id}.png`});}
}
if([320,390,1440].includes(viewport.width)){await page.goto('file://'+process.cwd()+`/docs/reviews/barge-2026-10-17/revision-2/prototype.html?v=b&parcel=boat`);await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(i=>i.decode())));await page.evaluate(async()=>{await document.fonts.ready;const bg=new Image();bg.src=document.body.dataset.parcel==='boat'?'action-boat-v1.png':'action-sheet-v1.png';await bg.decode();});await page.screenshot({path:`${root}/frames/before-R2-first-${viewport.width}.png`});}
await page.close();}await browser.close();
