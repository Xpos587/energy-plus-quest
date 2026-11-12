import { expect, test } from '@playwright/test';
import { openInventory } from './inventory-fixture';

// Native v4 bounds: entire worker and loaded trolley (keeper: worker + gift).
// Alphabet bounds also include the parcel-specific plaque; entrance includes «Приёмка».
const subjects: Record<string, number[]> = {
  alphabet: [605, 210, 1370, 735],
  entrance: [400, 5, 1285, 725],
  keeper: [210, 160, 1290, 895],
  wms: [400, 150, 1300, 880],
};
for (const [width, height] of [[320, 568], [390, 844], [430, 932], [820, 1180], [844, 390], [1440, 900]]) {
  test(`warehouse result subjects remain whole at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    for (const [id, parcel] of [['alphabet', 'camera'], ['alphabet', 'boat'], ['alphabet', 'socks'], ['entrance', 'boat'], ['keeper', 'boat'], ['wms', 'boat']]) {
      await openInventory(page, parcel);
      await page.locator(`[data-hotspot="${id}"]`).click();
      await page.locator('[data-choice-confirm]').click();
      const image = page.locator('[data-outcome-scene] img');
      await image.evaluate((el: HTMLImageElement) => el.decode());
      const visible = await image.evaluate((el: HTMLImageElement) => {
        const s = getComputedStyle(el), w = el.clientWidth, h = el.clientHeight;
        const scale = (s.objectFit === 'contain' ? Math.min : Math.max)(w / el.naturalWidth, h / el.naturalHeight);
        const [px, py] = s.objectPosition.split(' ').map(v => parseFloat(v) / 100);
        const left = (el.naturalWidth - w / scale) * px, top = (el.naturalHeight - h / scale) * py;
        return [left, top, left + w / scale, top + h / scale];
      });
      const [left, top, right, bottom] = subjects[id];
      expect(visible[0], `${id}/${parcel}: left edge`).toBeLessThanOrEqual(left);
      expect(visible[1], `${id}/${parcel}: top edge`).toBeLessThanOrEqual(top);
      expect(visible[2], `${id}/${parcel}: right edge`).toBeGreaterThanOrEqual(right);
      expect(visible[3], `${id}/${parcel}: bottom edge`).toBeGreaterThanOrEqual(bottom);
      await expect(page.getByRole('button', { name: 'Изменить выбор', exact: true })).toBeInViewport({ ratio: 1 });
      const more = page.getByRole('button', { name: 'Читать дальше', exact: true });
      for (let i = 0; i < 32 && await more.isVisible(); i++) {
        await expect(more).toBeInViewport({ ratio: 1 });
        await more.click();
      }
      await expect(page.getByRole('button', { name: 'Продолжить', exact: true })).toBeInViewport({ ratio: 1 });
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight)).toBe(true);
    }
  });
}
