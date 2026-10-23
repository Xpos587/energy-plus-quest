import { chromium } from 'playwright';
import { mkdir,writeFile } from 'node:fs/promises';
const out=process.argv[2]; if(!out)throw new Error('Usage: node closeups.mjs OUTPUT');await mkdir(out,{recursive:true});
const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1440,height:1000}});
await page.goto('http://localhost:4173/');for(const id of ['professional','alva','boat'])await page.locator(`[data-choice="${id}"]`).click();await page.locator('[data-map-surface][data-motion-state]').waitFor();
const notes=[];
for(let sample=0;sample<2;sample++){
 if(sample)await page.waitForTimeout(8000);
 for(let index=0;index<4;index++){
  await page.getByRole('button',{name:`Показать грузовик №${index+1} на карте`,exact:true}).click();await page.waitForTimeout(100);
  const data=await page.evaluate(async(index)=>{
   const {mapFrame,mapFit,project}=await import('/src/game/illustratedMapMotion.ts');
   const surface=document.querySelector('[data-map-surface]'),r=surface.getBoundingClientRect();
   const time=Number(surface.dataset.motionTime),pose=mapFrame(time)[index],scale=Math.max(mapFit(r.width,r.height).scale*2.6,r.width/460);
   const marker=surface.querySelectorAll('[data-truck-number]')[index];const mp=project(pose.markerX,pose.markerY,3.3);
   const x=parseFloat(marker.style.left)-mp[0]*scale,y=parseFloat(marker.style.top)+34-mp[1]*scale;
   const c=project(pose.x,pose.y),t=project(pose.markerX,pose.markerY);
   const left=Math.max(0,x+Math.min(c[0]-53,t[0]-85)*scale-8),right=Math.min(r.width,x+Math.max(c[0]+53,t[0]+85)*scale+8);
   const top=Math.max(0,Math.min(y+Math.min(c[1]-53,t[1]-85)*scale-8,parseFloat(marker.style.top)-24)),bottom=Math.min(r.height,y+Math.max(c[1]+53,t[1]+85)*scale+8);
   return {time,index,clip:{x:r.x+left,y:r.y+top,width:right-left,height:bottom-top}};
  },index);
  await page.screenshot({path:`${out}/truck-${index+1}-${sample}.png`,clip:data.clip});notes.push(data);
 }
}
await writeFile(`${out}/closeups.json`,JSON.stringify(notes,null,2));await browser.close();
