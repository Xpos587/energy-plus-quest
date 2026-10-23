import { expect, test } from '@playwright/test';
test('WMS panorama pilot composition', async ({page},info) => {
  await page.route('**/*inventory-wms-boat-family-v1*', route=>route.fulfill({path:'design/style-pilot-2026-09-28/desktop-panorama/wms-wide-v1.png',contentType:'image/png'}));
  await page.goto('/scenes.html?scene=inventory&parcel=boat&recipient=khor');
  const condition=page.getByRole('region',{name:'Условие задания',exact:true});
  for(let i=0;i<30&&await condition.isVisible();i++) await condition.getByRole('button',{name:/^(Далее|К выбору)$/}).click();
  await page.locator('[data-scene-choice="wms"]').click();
  await page.locator('[data-choice-confirm]').click();
  await page.addStyleTag({content:'[data-outcome-scene="inventory"] img { object-fit: cover !important; object-position: center !important; }'});
  const img=page.locator('[data-outcome-scene] img');
  await img.evaluate(async el=>(el as HTMLImageElement).decode());
  await page.evaluate(()=>document.fonts.ready);
  const metrics=await img.evaluate(el=>{
    const img=el as HTMLImageElement, r=img.getBoundingClientRect();
    const scale=Math.max(r.width/img.naturalWidth,r.height/img.naturalHeight);
    return {src:img.currentSrc,natural:[img.naturalWidth,img.naturalHeight],area:{x:r.x,y:r.y,width:r.width,height:r.height},scale,cropX:(img.naturalWidth-r.width/scale)/2,cropY:(img.naturalHeight-r.height/scale)/2};
  });
  expect(metrics.natural).toEqual([2001,786]);
  expect(metrics.cropY).toBeLessThan(1);
  expect(metrics.cropX).toBeLessThan(150);
  const panel=(await page.locator('[data-sheet-panel]').boundingBox())!;
  expect(metrics.area.y+metrics.area.height).toBeLessThanOrEqual(panel.y+1);
  for(const b of await page.locator('[data-result-reader] footer button').all()) await expect(b).toBeInViewport({ratio:1});
  await page.screenshot({path:`design/style-pilot-2026-09-28/desktop-panorama/wms-pilot-${info.project.name}.png`});
  console.log(JSON.stringify({viewport:page.viewportSize(),...metrics}));
});
