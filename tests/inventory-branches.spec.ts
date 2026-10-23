import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const parcel of ['boat', 'camera', 'socks']) {
  test(`${parcel}: four results, score, return and barge`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    const branches = { entrance: [-2, -1, 0], alphabet: [-3, 0, -1], keeper: [1, 4, -3], wms: [4, 4, 5] };
    for (const [choice, scores] of Object.entries(branches)) {
      await openInventory(page, parcel);
      await page.locator(`[data-scene-choice="${choice}"]`).click();
      await expect(page.locator('[data-scene-consequence]')).toHaveAttribute('data-scene-consequence', `inventory-${choice}${choice === 'alphabet' ? `-${parcel}` : ''}`);
      const image = page.locator('[data-outcome-scene] img');
      await image.evaluate((img: HTMLImageElement) => img.decode());
      for (const [i, score] of scores.entries()) {
        await expect(page.locator(`[data-score-key="${['energy', 'empathy', 'efficiency'][i]}"] strong`)).toHaveText(score > 0 ? `+${score}` : String(score));
      }
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      await expect(page.locator('[data-scene-choice]')).toHaveCount(4);
      await page.locator(`[data-scene-choice="${choice}"]`).click();
      const more = page.getByRole('button', { name: 'Читать дальше', exact: true });
      for (let i = 0; i < 32 && await more.isVisible(); i++) {
        await expect(more).toBeInViewport({ ratio: 1 });
        const text = await page.getByTestId('result-copy').innerText();
        await more.click();
        await expect(page.getByTestId('result-copy')).not.toHaveText(text);
      }
      if (choice === 'wms') {
        // The frozen scenario currently contains no WMS link label or URL.
        await expect(page.locator('[data-result-link] a[href^="http"]')).toHaveCount(0);
      }
      const next = page.getByRole('button', { name: 'Продолжить', exact: true });
      await expect(next).toBeInViewport({ ratio: 1 });
      await next.click();
      await expect(page.locator('[data-scene="crane"]')).toBeVisible();
    }
  });
}
