import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`keeper remains unobscured at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openInventory(page);
    // The visible disc can clear the keeper on either axis: above the head or beside the body.
    // WorldArt.module.css draws a 30px disc inside the 44px transparent hit target.
    const pin = (await page.locator('[data-hotspot="keeper"]').boundingBox())!, keeper = (await page.locator('[data-warehouse-zone="keeper"]').boundingBox())!;
    const discLeft = pin.x + pin.width / 2 - 15;
    const discBottom = pin.y + pin.height / 2 + 15;
    expect(discLeft >= keeper.x + keeper.width || discBottom <= keeper.y + keeper.height * 0.25).toBe(true);
    await expect(page.locator('[data-warehouse-zone="keeper"]')).toBeInViewport({ ratio: 1 });
    await page.locator('[data-hotspot="keeper"]').click();
    await page.locator('[data-choice-confirm]').click();
    await expect(page.locator('[data-scene-consequence="inventory-keeper"]')).toBeVisible();
    await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    await expect(page.locator('[data-hotspot="keeper"]')).toBeVisible();
  });
}
