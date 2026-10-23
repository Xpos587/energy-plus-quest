import {chromium,expect} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const root='docs/reviews/barge-2026-10-17/revision-3';await mkdir(`${root}/frames`,{recursive:true});
const browser=await chromium.launch(),receipt=[];
const parcels=process.env.BARGE_PARCELS?.split(',')||['boat','camera','socks'];
for(const viewport of [{width:320,height:568},{width:390,height:844},{width:844,height:390},{width:1440,height:900}]){
const page=await browser.newPage({viewport});
for(const v of ['a','b','c'])for(const parcel of parcels){
await page.goto('file://'+process.cwd()+`/${root}/prototype.html?v=${v}&parcel=${parcel}`);
await expect(page.locator('.condition')).toBeVisible();
let parts=[];while(await page.locator('.condition').count()){
await page.locator('.condition img').evaluate(i=>i.decode());await page.evaluate(async()=>{await document.fonts.ready;const bg=new Image();bg.src=document.body.dataset.parcel==='boat'?'action-boat-v1.png':'action-sheet-v1.png';await bg.decode();});
parts.push(await page.locator('.condition .intro-copy').innerText());await expect(page.locator('.condition button')).toBeInViewport({ratio:1});
if(parcel==='boat'&&v==='b')await page.screenshot({path:`${root}/frames/intro-${viewport.width}-${parts.length}.png`});
await page.locator('.condition button').click();}
expect(parts.join(' ')).toContain('три часа');expect(parts.join(' ')).toContain('Крановщик Иван');
for(const state of ['choice','remote','rush','wait','petr']){
await page.goto('file://'+process.cwd()+`/${root}/prototype.html?v=${v}&parcel=${parcel}&state=${state==='choice'?'':state}&active=rush`);
await page.locator('img').evaluateAll(async imgs=>Promise.all(imgs.map(i=>i.decode())));await page.evaluate(async()=>{await document.fonts.ready;const bg=new Image();bg.src=document.body.dataset.parcel==='boat'?'action-boat-v1.png':'action-sheet-v1.png';await bg.decode();});
const m=await page.evaluate(()=>({scrollX:document.documentElement.scrollWidth>innerWidth,scrollY:document.documentElement.scrollHeight>innerHeight,items:[...document.querySelectorAll('button,.reading,.rail h1,.context p:last-child')].map(e=>{const r=e.getBoundingClientRect();return {text:e.textContent,inside:r.x>=0&&r.y>=0&&r.right<=innerWidth+.5&&r.bottom<=innerHeight+.5,unclipped:e.scrollHeight<=e.clientHeight+1};}),source:[...document.images].filter(i=>i.classList.contains('outcome-sheet')).map(i=>({src:i.currentSrc,natural:[i.naturalWidth,i.naturalHeight],frame:[i.parentElement.clientWidth,i.parentElement.clientHeight]}))}));receipt.push({viewport,v,parcel,state,...m});
if(parcel==='boat'||(v==='b'&&viewport.width===390))await page.screenshot({path:`${root}/frames/${v}-${viewport.width}-${state}-${parcel}.png`});
if(state==='remote'){if((await page.locator('[data-next]').innerText()).includes('Читать дальше'))await page.locator('[data-next]').click();await expect(page.locator('.reading')).toContainText('Такие системы');if(parcel==='boat')await page.screenshot({path:`${root}/frames/${v}-${viewport.width}-remote-part2.png`});}
if(state==='petr'){await expect(page.locator('.reading')).toContainText('Петр выручил');await expect(page.locator('.reading')).toContainText('Петр согласился');}
if(state!=='choice'){await page.locator('[data-revise]').click();await expect(page.locator('main')).toHaveAttribute('data-state','choice');}
}
}
await page.close();}
await writeFile(`${root}/geometry${parcels.length===1?'-boat':''}.json`,JSON.stringify(receipt,null,2));
const failed=receipt.filter(r=>r.scrollX||r.scrollY||r.items.some(x=>!x.inside||!x.unclipped));console.log(JSON.stringify({cases:receipt.length,failed:failed.map(r=>({viewport:r.viewport,v:r.v,parcel:r.parcel,state:r.state,scroll:r.scrollY,bad:r.items.filter(x=>!x.inside||!x.unclipped).map(x=>x.text)}))},null,2));await browser.close();
