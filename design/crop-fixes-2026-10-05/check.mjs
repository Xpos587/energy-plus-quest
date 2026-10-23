import {chromium} from '@playwright/test';
const b=await chromium.launch({args:['--disable-gpu']});
for(const [w,h] of [[393,852],[820,1180],[1440,900]])for(const [scene,choice] of [['carrier','crew'],['carrier','old'],['inventory','entrance'],['inventory','keeper'],['inventory','wms'],['lastmile','helicopter'],['compact','place-3']]){
 const p=await b.newPage({viewport:{width:w,height:h}});
 if(scene==='carrier'){
 await p.addInitScript(id=>localStorage.setItem('energy-quest-save-v1',JSON.stringify({version:1,scope:'quest-crop-check',state:{step:'outcome',profile:'professional',recipient:'alva',parcel:'boat',carrier:id}})),choice);
 await p.goto('http://127.0.0.1:4173/');
 }else{
 await p.goto(`http://127.0.0.1:4173/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
 const next=p.getByRole('button',{name:/^(Далее|К выбору)$/});
 for(let i=0;i<20&&await next.isVisible();i++)await next.click();
 await p.locator(`[data-scene-choice="${choice}"]`).click();await p.locator('[data-choice-confirm]').click();
 }
 await p.locator('[data-result-reader]').waitFor();
 await p.locator('img').evaluateAll(es=>Promise.all(es.map(e=>e.decode().catch(()=>{}))));
 await p.screenshot({path:`design/crop-fixes-2026-10-05/${scene}-${choice}-${w}.png`});
 console.log(scene,choice,w);
 await p.close();
}
await b.close();
