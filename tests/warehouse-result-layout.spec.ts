import { expect, test } from '@playwright/test';
for (const choice of ['entrance', 'alphabet', 'keeper', 'wms']) {
  test(`warehouse ${choice}: full illustration stays clear of result`, async ({ page }, info) => {
    await page.goto('/scenes.html?scene=inventory&parcel=boat&recipient=khor');
    const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
    for (let i = 0; i < 30 && await condition.isVisible(); i++) await condition.getByRole('button', { name: /^(Далее|К выбору)$/ }).click();
    await page.locator(`[data-scene-choice="${choice}"]`).click();
    await page.locator('[data-choice-confirm]').click();
    const art = page.locator('[data-outcome-scene]');
    const panel = page.locator('[data-sheet-panel]');
    await expect(panel).toBeVisible();
    const a = (await art.boundingBox())!;
    const b = (await panel.boundingBox())!;
    console.log(JSON.stringify({choice,viewport:page.viewportSize(),art:a,panel:b,aspect:a.width/a.height}));
    if (page.viewportSize()!.width >= 901 && page.viewportSize()!.height > 500) {
      expect(a.x).toBe(0);
      expect(a.width).toBe(page.viewportSize()!.width);
      expect(b.x).toBe(0);
      expect(b.width).toBe(page.viewportSize()!.width);
      expect(Math.abs(a.y+a.height-b.y)).toBeLessThan(1);
    }
    const overlap = Math.max(0, Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x))*Math.max(0,Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y));
    expect(overlap).toBe(0);
    const desktopPanorama = page.viewportSize()!.width >= 901 && page.viewportSize()!.height >= 501;
    expect(await art.locator('img').evaluate(el=>getComputedStyle(el).objectFit)).toBe(desktopPanorama ? 'cover' : 'contain');
    for (const button of await panel.locator('footer button').all()) await expect(button).toBeInViewport({ratio:1});
    await art.locator('img').evaluate(async el=>(el as HTMLImageElement).decode());
    await page.screenshot({path:`.tmp-work/choice-buttons/warehouse-${choice}-${info.project.name}.png`});
  });
}
