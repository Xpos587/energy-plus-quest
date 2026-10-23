import {expect,test} from '@playwright/test';
async function readCondition(page: import('@playwright/test').Page) {
 for(let n=0;n<30;n++) {
  const forward=page.getByRole('button',{name:/^(Далее|К выбору)$/});
  if(!await forward.isVisible()) break;
  await forward.click();
 }
}
test('Compact result camera respects reduced motion',async({page})=>{
 await page.emulateMedia({reducedMotion:'reduce'});
 await page.goto('/scenes.html?scene=compact&parcel=boat&recipient=alva&carrier=old');
 await readCondition(page);
 await page.locator('[data-scene-choice="place-2"]').click();
 await expect(page.locator('[data-world-plane]')).toHaveCSS('transition-duration','0s');
});
for(const [width,height] of [[320,568],[390,844],[844,390],[1440,900]]) {
 test(`Compact visible zones and direct selection ${width}x${height}`,async({page})=>{
  await page.setViewportSize({width,height});
  await page.goto('/scenes.html?scene=compact&parcel=boat&recipient=alva&carrier=old');
 await readCondition(page);
  const zones=page.locator('[data-loading-zone]');
  await expect(zones).toHaveCount(4);
  for(const zone of await zones.all()) {
   await expect(zone).toBeInViewport({ratio:1});
   expect(await zone.evaluate(e=>Number(getComputedStyle(e).strokeOpacity))).toBe(1);
   expect(await zone.evaluate(e=>parseFloat(getComputedStyle(e).strokeWidth))).toBeGreaterThanOrEqual(2.5);
  }
  for(const id of ['place-1','place-2','place-3','place-4']) {
   await page.locator(`[data-hotspot="${id}"]`).click();
   await expect(page.locator('[data-result-reader]')).toBeVisible();
   const art=page.locator('[data-world-scene=compact]');
   if(id==='place-3')await expect(art).toHaveAttribute('data-failure-art','boat-place-3');
   else await expect(art).toHaveAttribute('data-detail-zone',id);
   await page.getByRole('button',{name:'Изменить выбор',exact:true}).click();
  }
  for(const choice of await page.locator('[data-scene-choice]').all())await expect(choice).toBeInViewport({ratio:1});
  expect(await page.evaluate(()=>document.documentElement.scrollHeight<=innerHeight)).toBe(true);
 });
}
