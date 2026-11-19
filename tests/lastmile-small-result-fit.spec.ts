import { expect, test } from '@playwright/test';

for (const [recipient, parcel] of [['arseniy', 'boat'], ['arseniy', 'camera'], ['arseniy', 'socks'], ['alva', 'boat'], ['khor', 'camera']]) {
  test(`helicopter text fits and both actions are reachable at 320px: ${recipient}/${parcel}`, async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto(`/scenes.html?scene=lastmile&recipient=${recipient}&parcel=${parcel}`);
    const briefing = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
    for (let n = 0; n < 35 && await briefing.isVisible(); n++) await briefing.click();
    await page.locator('[data-choice-id="helicopter"]').click();
    await page.locator('[data-choice-confirm]').click();
    await page.evaluate(() => document.fonts.ready);
    await page.locator('[data-scene-consequence] img').evaluate((image: HTMLImageElement) => image.decode());
    const seen = [];
    const next = page.locator('[data-result-reader] footer button').last();
    for (let n = 0; n < 30; n++) {
      const reader = page.locator('[data-result-reading]');
      expect(await reader.evaluate(e => e.scrollHeight <= e.clientHeight + 1)).toBe(true);
      seen.push(await page.getByTestId('result-copy').innerText());
      // Short phones scroll the result sheet, not the document, to reach the footer.
      await page.locator('[data-sheet-panel]').hover({ position: { x: 4, y: 4 } });
      await page.mouse.wheel(0, 2000);
      await expect(next).toBeInViewport({ ratio: 1 });
      await expect(page.getByRole('button', { name: 'Изменить выбор', exact: true })).toBeInViewport({ ratio: 1 });
      if (await next.getAttribute('aria-label') !== 'Читать дальше') break;
      await next.click();
    }
    expect(seen.join(' ')).toContain('Вертолет быстро преодолел леса и болота');
    await expect(page.getByRole('button', { name: 'К вручению подарка', exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight)).toBe(true);
  });
}
