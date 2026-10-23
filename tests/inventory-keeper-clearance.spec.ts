import { expect, test } from '@playwright/test';
import contours from '../src/scenes/inventory/segmentedContours.json' with { type: 'json' };
import { openInventory } from './inventory-fixture';

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  test(`keeper remains unobscured at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openInventory(page);
    const plane = (await page.locator('[data-world-plane]').boundingBox())!;
    const button = page.locator('[data-hotspot="keeper"]');
    const marker = await button.evaluate(el => {
      const rect = el.getBoundingClientRect(), ink = getComputedStyle(el, '::before');
      const left = parseFloat(ink.left), top = parseFloat(ink.top);
      return { x: rect.x + left, y: rect.y + top, width: rect.width - left - parseFloat(ink.right), height: rect.height - top - parseFloat(ink.bottom) };
    });
    const points = [...contours.regions.keeper.path.matchAll(/(?:M|L)\s+([\d.]+)\s+([\d.]+)/g)];
    const xs = points.map(p => Number(p[1])), ys = points.map(p => Number(p[2]));
    const keeper = { x: plane.x + plane.width * Math.min(...xs) / contours.width, y: plane.y + plane.height * Math.min(...ys) / contours.height, width: plane.width * (Math.max(...xs) - Math.min(...xs)) / contours.width, height: plane.height * (Math.max(...ys) - Math.min(...ys)) / contours.height };
    // Clip the painted badge against the keeper silhouette, rather than the
    // empty corners of a bounding box beside his head.
    let polygon = points.map(p => ({ x: plane.x + plane.width * Number(p[1]) / contours.width, y: plane.y + plane.height * Number(p[2]) / contours.height }));
    for (const [axis, edge, sign] of [['x', marker.x, 1], ['x', marker.x + marker.width, -1], ['y', marker.y, 1], ['y', marker.y + marker.height, -1]] as const) {
      const clipped: typeof polygon = [];
      for (let i = 0; i < polygon.length; i++) {
        const a = polygon[i], b = polygon[(i + 1) % polygon.length];
        const aInside = (a[axis] - edge) * sign >= 0, bInside = (b[axis] - edge) * sign >= 0;
        if (aInside) clipped.push(a);
        if (aInside !== bInside) {
          const t = (edge - a[axis]) / (b[axis] - a[axis]);
          clipped.push({ x: a.x + t * (b.x - a.x), y: a.y + t * (b.y - a.y) });
        }
      }
      polygon = clipped;
    }
    const overlap = Math.abs(polygon.reduce((sum, a, i) => { const b = polygon[(i + 1) % polygon.length]; return sum + a.x * b.y - b.x * a.y; }, 0)) / 2;
    expect(overlap).toBeLessThan(0.1);
    const gapX = Math.max(0, keeper.x - (marker.x + marker.width), marker.x - (keeper.x + keeper.width));
    const gapY = Math.max(0, keeper.y - (marker.y + marker.height), marker.y - (keeper.y + keeper.height));
    expect(Math.hypot(gapX, gapY)).toBeLessThan(44);
    await expect(page.locator('[data-hotspot="keeper"]')).toBeInViewport({ ratio: 1 });
    await page.locator('[data-hotspot="keeper"]').click();
    await expect(page.locator('[data-scene-consequence="inventory-keeper"]')).toBeVisible();
    await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    await expect(page.locator('[data-hotspot="keeper"]')).toBeVisible();
  });
}
