import { chromium } from 'playwright';
import { writeFile } from 'node:fs/promises';
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
await p.addInitScript(()=>{const native=requestAnimationFrame.bind(window);window.requestAnimationFrame=cb=>native(t=>{if(!window.freezeSceneFrame)cb(t)});});
await p.goto('http://localhost:4173/');for(const id of ['professional','alva','boat'])await p.locator(`[data-choice="${id}"]`).click();await p.locator('[data-map-surface][data-motion-state]').waitFor();await p.waitForTimeout(12000);
for(const state of ['before','after']){
 if(state==='before')await p.evaluate(()=>window.freezeSceneFrame=true);
 else {await p.getByRole('button',{name:'Приостановить движение',exact:true}).click();await p.waitForTimeout(200);}
 const result=await p.evaluate(()=>{const s=document.querySelector('[data-map-surface]');const c=s.querySelector('canvas');return{time:s.dataset.motionTime,width:c.width,height:c.height,image:c.toDataURL()}});
 await writeFile(`/tmp/scene1-dirty-${state}.png`,Buffer.from(result.image.split(',')[1],'base64'));delete result.image;console.log(state,result);
}
await b.close();
