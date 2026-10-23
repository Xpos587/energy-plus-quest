import {chromium} from '@playwright/test';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch(),root='docs/reviews/barge-2026-10-17/revision-3',receipt=[];
for(const width of [390,1440])for(const dpr of [1,2]){
const page=await browser.newPage({viewport:{width,height:width===390?844:900},deviceScaleFactor:dpr});await page.goto('file://'+process.cwd()+`/${root}/prototype.html?v=b&state=petr&parcel=camera`);await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(i=>i.decode())));await page.evaluate(()=>document.fonts.ready);
receipt.push(await page.evaluate(()=>{const img=document.querySelector('.outcome-sheet'),frame=img.parentElement.getBoundingClientRect();return {viewport:[innerWidth,innerHeight],dpr:devicePixelRatio,src:img.currentSrc,sheet:[img.naturalWidth,img.naturalHeight],effective:[img.naturalWidth/2,img.naturalHeight/2],display:[frame.width,frame.height],neededAtDpr:[frame.width*devicePixelRatio,frame.height*devicePixelRatio]};}));
if(width===390&&dpr===2)await page.screenshot({path:`${root}/frames/b-390-petr-camera-dpr2.png`});await page.close();}
console.log(JSON.stringify(receipt));await writeFile(`${root}/dpr.json`,JSON.stringify(receipt,null,2));await browser.close();
