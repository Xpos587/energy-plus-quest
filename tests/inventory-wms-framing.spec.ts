import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`WMS complete action and paging at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    for (const parcel of ['boat', 'camera', 'socks']) {
      await openInventory(page, parcel);
      await page.locator('[data-scene-choice="wms"]').click();
      const img = page.locator('[data-scene-consequence="inventory-wms"] img');
      await img.evaluate((image: HTMLImageElement) => image.decode());
      await expect(img).toHaveAttribute('src', /warehouse-revision-3-2026-10-18\/wms-stylized-v3\.png$/);
      const action = await img.evaluate((image: HTMLImageElement) => {
        const scale = Math.max(image.clientWidth / image.naturalWidth, image.clientHeight / image.naturalHeight);
        const focus = getComputedStyle(image).objectPosition.split(' ').map(parseFloat);
        const left = (image.clientWidth - image.naturalWidth * scale) * focus[0] / 100;
        const top = (image.clientHeight - image.naturalHeight * scale) * focus[1] / 100;
        // Worker, scanner and all trolley wheels in the reviewed 1672×941 source.
        return { left: left + 405 * scale, right: left + 1295 * scale, top: top + 150 * scale, bottom: top + 870 * scale, width: image.clientWidth, height: image.clientHeight };
      });
      expect(action.left).toBeGreaterThanOrEqual(0);
      expect(action.right).toBeLessThanOrEqual(action.width);
      expect(action.top).toBeGreaterThanOrEqual(0);
      expect(action.bottom).toBeLessThanOrEqual(action.height);
      if (height > width) {
        const geometry = await img.evaluate((image: HTMLImageElement) => ({ width: image.clientWidth, height: image.clientHeight, ratio: image.naturalHeight / image.naturalWidth }));
        // The whole composition is visible: no top/bottom crop of head or wheels.
        expect(Math.abs(geometry.height - geometry.width * geometry.ratio)).toBeLessThan(2);
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
