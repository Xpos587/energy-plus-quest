import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
const dir=new URL('.',import.meta.url).pathname;
const browser=await chromium.launch();const records=[];
try{
for(const [name,width,height] of [['tablet',820,1180],['mobile',390,844],['small',320,568]])for(const input of ['mouse','touch']){
 const context=await browser.newContext({viewport:{width,height},hasTouch:input==='touch'});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.route(/inventory-barge-style-v6/,r=>r.fulfill({path:dir+'../clean-colors/warehouse-v4.png',contentType:'image/png'}));
 await page.goto('http://127.0.0.1:4173/scenes.html?scene=inventory&parcel=boat&recipient=alva');
 for(let n=0;n<30;n++){const next=page.getByRole('button',{name:/^(Далее|К выбору|К сцене)$/});if(!await next.isVisible())break;await next.click();}
 const marker=page.locator('[data-choice-id="entrance"][data-hotspot]');const before=await marker.boundingBox();const steps=[];const cdp=input==='touch'?await context.newCDPSession(page):null;
 for(let n=0;n<8;n++){
  const box=await marker.boundingBox();if(box.x>=0&&box.x+box.width<=width)break;
  const start=width*.2,end=width*.8,y=height*.30;
  if(input==='mouse'){await page.mouse.move(start,y);await page.mouse.down();await page.mouse.move(end,y,{steps:20});await page.mouse.up();}
  else{await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:start,y}]});for(let i=1;i<=20;i++){await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:start+(end-start)*i/20,y}]});await page.waitForTimeout(15);}await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});}
  await page.waitForTimeout(300);steps.push(await marker.boundingBox());
 }
 const exposed=await marker.boundingBox();await page.screenshot({path:dir+`${name}-${input}-pan.png`});let success=false,failure=null;
 try{if(input==='touch')await marker.tap({timeout:2000});else await marker.click({timeout:2000});await page.locator('[data-choice-confirm]').waitFor({state:'visible',timeout:2000});success=await marker.getAttribute('aria-pressed')==='true';}catch(e){failure=String(e);}
 await page.screenshot({path:dir+`${name}-${input}-selected.png`});records.push({name,input,before,steps,exposed,success,failure,errors});await context.close();
}
await fs.writeFile(dir+'pointer-receipt.json',JSON.stringify(records,null,2));console.log(JSON.stringify(records,null,2));
}finally{await browser.close();}
