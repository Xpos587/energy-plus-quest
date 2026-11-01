import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`WMS complete action and paging at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    for (const parcel of ['boat', 'camera', 'socks']) {
      await openInventory(page, parcel);
      await page.locator('[data-hotspot="wms"]').click();
      await page.locator('[data-choice-confirm]').click();
      const img = page.locator('[data-scene-consequence="inventory-wms"] img');
      await img.evaluate((image: HTMLImageElement) => image.decode());
      await expect(img).toHaveAttribute('src', /warehouse-v10\/outcome-wms\.webp$/);
      const action = await img.evaluate((image: HTMLImageElement) => {
        const scale = Math.max(image.clientWidth / image.naturalWidth, image.clientHeight / image.naturalHeight);
        const focus = getComputedStyle(image).objectPosition.split(' ').map(parseFloat);
        const left = (image.clientWidth - image.naturalWidth * scale) * focus[0] / 100;
        const top = (image.clientHeight - image.naturalHeight * scale) * focus[1] / 100;
        // Kiosk screen, the forklift and the gift entering the truck in the 1960×840 source.
        return { left: left + 600 * scale, right: left + 1500 * scale, top: top + 380 * scale, bottom: top + 760 * scale, width: image.clientWidth, height: image.clientHeight };
      });
      expect(action.left).toBeGreaterThanOrEqual(0);
      expect(action.right).toBeLessThanOrEqual(action.width);
      expect(action.top).toBeGreaterThanOrEqual(0);
      expect(action.bottom).toBeLessThanOrEqual(action.height);
      if (height > width) {
        const overflow = await img.evaluate((image: HTMLImageElement) => image.naturalHeight * Math.max(image.clientWidth / image.naturalWidth, image.clientHeight / image.naturalHeight) - image.clientHeight);
        // No top/bottom crop of heads or wheels; the wide source may lose its sides.
        expect(overflow).toBeLessThan(2);
      }
      const more = page.getByRole('button', { name: 'Читать дальше', exact: true });
      for (let i = 0; i < 32 && await more.isVisible(); i++) {
        await expect(more).toBeInViewport({ ratio: 1 });
        await expect(page.getByRole('button', { name: 'Изменить выбор', exact: true })).toBeInViewport({ ratio: 1 });
        const text = await page.getByTestId('result-copy').innerText();
        await more.click();
        await expect(page.getByTestId('result-copy')).not.toHaveText(text);
      }
      await expect(page.getByRole('button', { name: 'Продолжить', exact: true })).toBeInViewport({ ratio: 1 });
      expect(await page.evaluate(() => document.documentElement.scrollHeight <= innerHeight && document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    }
  });
}
