import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`keeper remains unobscured at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openInventory(page);
    // No painted badge may cover the keeper: the object itself is the target.
    expect(await page.locator('[data-hotspot="keeper"]').evaluate(el => getComputedStyle(el, '::before').content)).toBe('none');
    await expect(page.locator('[data-warehouse-zone="keeper"]')).toBeInViewport({ ratio: 1 });
    await page.locator('[data-hotspot="keeper"]').click();
    await page.locator('[data-choice-confirm]').click();
    await expect(page.locator('[data-scene-consequence="inventory-keeper"]')).toBeVisible();
    await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    await expect(page.locator('[data-hotspot="keeper"]')).toBeVisible();
  });
}
