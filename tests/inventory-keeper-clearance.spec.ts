import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`keeper remains unobscured at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openInventory(page);
    // The numbered pin stands above the keeper's head, its tail at the anchor; the pin disc ends above it.
    const pin = (await page.locator('[data-hotspot="keeper"]').boundingBox())!, keeper = (await page.locator('[data-warehouse-zone="keeper"]').boundingBox())!;
    expect(pin.y + pin.height / 2 + 15).toBeLessThanOrEqual(keeper.y + keeper.height * 0.25);
    await expect(page.locator('[data-warehouse-zone="keeper"]')).toBeInViewport({ ratio: 1 });
    await page.locator('[data-hotspot="keeper"]').click();
    await page.locator('[data-choice-confirm]').click();
    await expect(page.locator('[data-scene-consequence="inventory-keeper"]')).toBeVisible();
    await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    await expect(page.locator('[data-hotspot="keeper"]')).toBeVisible();
  });
}
