import { expect, test } from '@playwright/test';
for (const choice of ['entrance','alphabet','keeper','wms']) {
  test(`${choice} responsive panorama`, async ({page},info) => {
    await page.goto('/scenes.html?scene=inventory&parcel=boat&recipient=khor');
    const condition=page.getByRole('region',{name:'Условие задания',exact:true});
    for(let i=0;i<30&&await condition.isVisible();i++) await condition.getByRole('button',{name:/^(Далее|К выбору)$/}).click();
    await page.locator(`[data-scene-choice="${choice}"]`).click();
    await page.locator('[data-choice-confirm]').click();
    const img=page.locator('[data-outcome-scene] img');
    await img.evaluate(async el=>(el as HTMLImageElement).decode());
    await page.evaluate(()=>document.fonts.ready);
    const desktop=page.viewportSize()!.width>=901&&page.viewportSize()!.height>=501;
    const details=await img.evaluate(el=>({src:(el as HTMLImageElement).currentSrc,fit:getComputedStyle(el).objectFit}));
    expect(details.src).toContain(desktop?`inventory-${choice}-boat-panorama-v1`:`inventory-${choice}-boat-family-v1`);
    expect(details.fit).toBe(desktop?'cover':'contain');
    const art=(await img.boundingBox())!, panel=(await page.locator('[data-sheet-panel]').boundingBox())!;
    expect(art.y+art.height).toBeLessThanOrEqual(panel.y+1);
    for(const b of await page.locator('[data-result-reader] footer button').all()) await expect(b).toBeInViewport({ratio:1});
    await page.screenshot({path:`design/style-pilot-2026-09-28/desktop-panorama/${choice}-live-${info.project.name}.png`});
  });
}
test('other gifts retain original artwork on desktop',async({page})=>{
 await page.goto('/scenes.html?scene=inventory&parcel=socks&recipient=arseniy');
 const condition=page.getByRole('region',{name:'Условие задания',exact:true});
 for(let i=0;i<30&&await condition.isVisible();i++) await condition.getByRole('button',{name:/^(Далее|К выбору)$/}).click();
 await page.locator('[data-scene-choice="wms"]').click();await page.locator('[data-choice-confirm]').click();
 await expect(page.locator('[data-desktop-panorama]')).toHaveCount(0);
 expect(await page.locator('[data-outcome-scene] img').getAttribute('src')).toContain('inventory-wms-v8');
});
