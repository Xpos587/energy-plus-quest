import { expect, test } from '@playwright/test';

// Source-pixel extents checked against revision 10 (1x canvas pixels): vehicles, АБК, chum camp and the whole barge.
const bounds = {
  wide: { width: 1672, height: 1393, objects: [[50, 386, 435, 574], [85, 576, 376, 750], [350, 606, 560, 766], [562, 676, 695, 763], [1115, 254, 1514, 445], [1384, 384, 1616, 588], [9, 765, 650, 1127]] },
  tall: { width: 1280, height: 1536, objects: [[190, 635, 620, 858], [324, 830, 645, 1046], [618, 880, 858, 1062], [874, 942, 1028, 1054], [623, 77, 905, 239], [819, 205, 1126, 367], [205, 1109, 964, 1425]] },
};

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1180, 820], [1366, 768], [1440, 900], [1920, 1080], [2560, 1080]]) {
  test(`lastmile vehicles and destinations fit ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('/scenes.html?scene=lastmile&parcel=boat&recipient=khor');
    const next = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
    for (let i = 0; i < 10 && await next.isVisible(); i++) await next.click();
    const stage = page.locator('[data-world-scene="lastmile"]');
    await stage.locator('img').evaluate((image: HTMLImageElement) => image.decode());
    const view = await stage.evaluate(el => {
      const s = el.getBoundingClientRect();
      const p = el.querySelector('[data-world-plane]')!.getBoundingClientRect();
      const hint = document.querySelector('[data-carrier-tap-hint]')!.getBoundingClientRect();
      return { width: s.width, height: s.height, left: p.left-s.left, top: p.top-s.top, planeWidth: p.width, hintBottom: hint.bottom-s.top, format: el.querySelector('img')!.src.includes('choice-wide') ? 'wide' as const : 'tall' as const };
    });
    const drawing = bounds[view.format];
    const scale = view.planeWidth / drawing.width;
    for (const [x0, y0, x1, y1] of drawing.objects) {
      expect(view.left + x0*scale).toBeGreaterThanOrEqual(-1);
      expect(view.top + y0*scale).toBeGreaterThanOrEqual(view.hintBottom); // Clear the instruction overlay.
      expect(view.left + x1*scale).toBeLessThanOrEqual(view.width+1);
      expect(view.top + y1*scale).toBeLessThanOrEqual(view.height+1);
    }
    for (const id of ['helicopter', 'pipe-carrier', 'rover', 'robot']) {
      await expect(stage.locator(`[data-hotspot="${id}"]`)).toBeInViewport({ ratio: 1 });
      expect(await stage.evaluate((el, { id, width, height }) => {
        const marker = el.querySelector<HTMLElement>(`[data-hotspot="${id}"]`)!;
        const path = el.querySelector<SVGGeometryElement>(`[data-lastmile-zone="${id}"]`)!;
        return path.isPointInFill(new DOMPoint(parseFloat(marker.style.left)*width/100, parseFloat(marker.style.top)*height/100));
      }, { id, width: drawing.width, height: drawing.height })).toBe(true);
    }
  });
}
