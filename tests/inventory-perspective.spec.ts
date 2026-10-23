import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';
import contours from '../src/scenes/inventory/segmentedContours.json' with { type: 'json' };

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`R4 local master and all gift targets at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    for (const [parcel, letter] of [['boat', 'Л'], ['camera', 'Ф'], ['socks', 'Н']]) {
      await openInventory(page, parcel);
      const image = page.locator('[data-world-plane] picture img');
      await expect(image).toHaveAttribute('src', /warehouse-revision-4-2026-10-18\/overview-r4-v11-local\.png$/);
      const plane = (await image.boundingBox())!, stage = (await page.locator('[data-world-scene="inventory"]').boundingBox())!, header = (await page.getByRole('banner').boundingBox())!;
      const sign = contours.overviewRequiredBounds;
      expect(plane.x + plane.width * sign.left / contours.width).toBeGreaterThanOrEqual(Math.max(0, stage.x) - 1);
      expect(plane.x + plane.width * sign.right / contours.width).toBeLessThanOrEqual(Math.min(width, stage.x + stage.width) + 1);
      expect(plane.y + plane.height * sign.top / contours.height).toBeGreaterThanOrEqual(Math.max(stage.y, header.y + header.height) - 1);
      expect(plane.y + plane.height * sign.bottom / contours.height).toBeLessThanOrEqual(Math.min(height, stage.y + stage.height) + 1);
      await expect(page.locator('[data-warehouse-surround]')).toHaveCount(0);
      await expect(page.locator('[data-hotspot="alphabet"]')).toHaveAttribute('aria-label', new RegExp(`буква ${letter}`));
      for (const id of ['entrance', 'alphabet', 'keeper', 'wms']) {
        const marker = page.locator(`[data-hotspot="${id}"]`);
        await expect(marker).toBeInViewport({ ratio: 1 });
        await expect(page.locator(`[data-scene-choice="${id}"]`)).toBeInViewport({ ratio: 1 });
        await marker.click();
        await expect(page.locator('[data-scene-consequence]')).toHaveAttribute('data-scene-consequence', `inventory-${id}${id === 'alphabet' ? `-${parcel}` : ''}`);
        await page.locator('[data-outcome-scene] img').evaluate((img: HTMLImageElement) => img.decode());
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
        await expect(marker).toBeVisible();
      }
    }
  });
}
