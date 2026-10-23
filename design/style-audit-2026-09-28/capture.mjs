import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const out = new URL('./captures/', import.meta.url).pathname;
const browser=await chromium.launch({headless:true});
const records=[];
for(const [device,width,height] of [['desktop',1440,900],['mobile',390,844]]){
 const context=await browser.newContext({viewport:{width,height}});const page=await context.newPage();
 const snap=async(name)=>{await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});await page.screenshot({path:`${out}${device}-${name}.png`});records.push({device,name,images:await page.locator('img').evaluateAll(a=>a.map(i=>({src:i.getAttribute('src'),alt:i.alt}))),overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)});};
 const advance=async()=>{for(let n=0;n<35;n++){const b=page.getByRole('button',{name:/^(Далее|К выбору)$/});if(!await b.isVisible())break;await b.click();}};
 await page.goto('http://127.0.0.1:4173/');await snap('profile');await page.locator('[data-choice="student"]').click();await snap('recipient');await page.locator('[data-choice="alva"]').click();await snap('parcel');await page.locator('[data-choice="camera"]').click();await snap('carrier-briefing');await advance();await snap('carrier');
 for(const scene of ['compact','inventory','crane','lastmile']){
  await page.goto(`http://127.0.0.1:4173/scenes.html?scene=${scene}&parcel=camera&recipient=alva`);await snap(`${scene}-briefing`);await advance();await snap(scene);
  const choices=await page.locator('[data-choice-id]').evaluateAll(a=>a.map(x=>x.getAttribute('data-choice-id')));
  for(const id of [...new Set(choices)]){
   await page.locator(`[data-choice-id="${id}"]`).first().click();const confirm=page.locator('[data-choice-confirm]');if(await confirm.isVisible()){if(id===choices[0])await snap(`${scene}-inspection`);await confirm.click();}
   await snap(`${scene}-result-${id}`);
   if(scene==='lastmile'&&id===choices.at(-1)){await page.getByRole('button',{name:'Завершить',exact:true}).click();await snap('final');break;}
   const back=page.getByRole('button',{name:device==='mobile'?'Назад':'Изменить выбор',exact:true});await back.click();await advance();
  }
 }
 await context.close();
}
await fs.writeFile(new URL('./screen-inventory.json',import.meta.url),JSON.stringify(records,null,2));await browser.close();console.log(`Captured ${records.length} screens`);
