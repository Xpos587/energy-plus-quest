import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';
for (const choice of ['entrance', 'alphabet', 'keeper', 'wms']) {
  test(`warehouse ${choice}: full illustration stays clear of result`, async ({ page }, info) => {
    await openInventory(page, 'boat');
    await page.locator(`[data-hotspot="${choice}"]`).click();
    await page.locator('[data-choice-confirm]').click();
    const art = page.locator('[data-outcome-scene]');
    const panel = page.locator('[data-sheet-panel]');
    await expect(panel).toBeVisible();
    const a = (await art.boundingBox())!;
    const b = (await panel.boundingBox())!;
    console.log(JSON.stringify({choice,viewport:page.viewportSize(),art:a,panel:b,aspect:a.width/a.height}));
    const overlap = Math.max(0, Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x))*Math.max(0,Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y));
    expect(overlap).toBe(0);
    for (const button of await panel.locator('footer button').all()) await expect(button).toBeInViewport({ratio:1});
    await art.locator('img').evaluate(async el=>(el as HTMLImageElement).decode());
    await page.screenshot({path:`.tmp-work/v17/result-layout/warehouse-${choice}-${info.project.name}.png`});
  });
}
