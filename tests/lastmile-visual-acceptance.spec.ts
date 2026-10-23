import { expect, test } from '@playwright/test';

for (const recipient of ['alva', 'khor', 'arseniy']) {
  for (const parcel of ['boat', 'camera', 'socks']) {
    test(`${recipient}/${parcel}: four outcomes, return and handover`, async ({ page }) => {
      await page.setViewportSize({ width: 390, height: 844 });
      await page.goto(`/scenes.html?scene=lastmile&recipient=${recipient}&parcel=${parcel}`);
      const briefing = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
      for (let n = 0; n < 10 && await briefing.isVisible(); n++) await briefing.click();
      for (const id of ['helicopter', 'rover', 'robot', 'pipe-carrier']) {
        await expect(page.locator('[data-hotspot]')).toHaveCount(4);
        await page.locator(`[data-choice-id="${id}"]:not([data-callout-target])`).click();
        const art = page.locator('[data-scene-consequence]');
        await expect(art).toBeVisible();
        await expect(art.locator('img')).toHaveJSProperty('complete', true);
        await expect(art.locator('img')).not.toHaveJSProperty('naturalWidth', 0);
        await expect(page.locator('[data-result]')).toBeVisible();
        for (let n = 0; n < 12; n++) {
          const read = page.getByRole('button', { name: 'Читать дальше', exact: true });
          if (!await read.isVisible()) break;
          await read.click();
        }
        await expect(page.getByRole('button', { name: 'К вручению подарка', exact: true })).toBeVisible();
        const overflow = await page.evaluate(() => document.documentElement.scrollHeight > innerHeight || document.documentElement.scrollWidth > innerWidth);
        expect(overflow).toBe(false);
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      }
      await page.locator('[data-choice-id="rover"]:not([data-callout-target])').click();
      const read = page.getByRole('button', { name: 'Читать дальше', exact: true });
      for (let n = 0; n < 12 && await read.isVisible(); n++) await read.click();
      await page.getByRole('button', { name: 'К вручению подарка', exact: true }).click();
      await expect(page.locator('[data-scene="lastmile"]')).toHaveCount(0);
    });
  }
}
