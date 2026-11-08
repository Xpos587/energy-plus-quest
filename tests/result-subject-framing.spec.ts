import {test,expect} from '@playwright/test';
const subjects: Record<string,number[]> = {
 // Current inventory outcomes (10-28 art): entrance 2004x785 worker + the box he pushes (phones keep
 // «Приёмка», b0353e2), keeper 1672x941 the whole storekeeper, wms 1671x941 as inventory-wms-framing.spec.ts.
 entrance:[600,245,1090,710], keeper:[215,100,700,886],
 wms:[409,158,1290,870], helicopter:[330,570,1340,1090],
};
for(const [width,height] of [[393,852],[820,1180],[1440,900]])
for (const [scene,choice] of [['inventory','entrance'],['inventory','keeper'],['inventory','wms'],['lastmile','helicopter']]) {
 test(`${scene} ${choice}: action remains visible at ${width}`,async({page})=>{
  await page.setViewportSize({width,height});
  await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
  const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
  for(let i=0;i<20&&await next.isVisible();i++)await next.click();
  await page.locator(`[data-hotspot="${choice}"]`).click();if(scene!=='lastmile')await page.locator('[data-choice-confirm]').click();
  await expect(page.locator('[data-scene-consequence]')).toBeVisible();
  const image=page.locator('[data-outcome-scene] img');
  await image.evaluate(async (el:HTMLImageElement)=>el.decode());
  const visible=await image.evaluate((el:HTMLImageElement)=>{
   const s=getComputedStyle(el),w=el.clientWidth,h=el.clientHeight;
   const scale=Math.max(w/el.naturalWidth,h/el.naturalHeight);
   const [px,py]=s.objectPosition.split(' ').map(v=>parseFloat(v)/100);
   const left=(el.naturalWidth-w/scale)*px,top=(el.naturalHeight-h/scale)*py;
   return [left,top,left+w/scale,top+h/scale];
  });
  const [x1,y1,x2,y2]=subjects[choice];
  expect(visible[0]).toBeLessThanOrEqual(x1+2);
  expect(visible[1]).toBeLessThanOrEqual(y1+2);
  expect(visible[2]).toBeGreaterThanOrEqual(x2-2);
  expect(visible[3]).toBeGreaterThanOrEqual(y2-2);
  if (scene === 'inventory' && choice === 'wms' && width === 393)
   expect(visible[2]).toBeGreaterThanOrEqual(1293);
  await expect(page.getByRole('button',{name:'Изменить выбор',exact:true})).toBeInViewport();
 });
}
