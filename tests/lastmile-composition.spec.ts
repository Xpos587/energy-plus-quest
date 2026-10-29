import { expect, test } from '@playwright/test';

// Source-pixel extents, checked against the revision-7 illustration, not just hotspot centres.
const bounds = {
  wide: { width: 1942, height: 809, objects: [[474, 215, 771, 399], [622, 406, 853, 554], [759, 540, 908, 651], [878, 631, 1004, 732], [1114, 85, 1410, 314], [1280, 350, 1480, 510]] },
  tall: { width: 948, height: 1659, objects: [[40, 800, 317, 963], [324, 952, 482, 1074], [511, 1006, 633, 1111], [664, 1037, 773, 1137], [417, 445, 663, 700], [733, 625, 899, 818]] },
};

for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1180, 820], [1440, 900], [1920, 1080], [2560, 1080]]) {
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
      return { width: s.width, height: s.height, left: p.left-s.left, top: p.top-s.top, planeWidth: p.width, format: el.querySelector('img')!.src.includes('choice-wide') ? 'wide' as const : 'tall' as const };
    });
    const drawing = bounds[view.format];
    const scale = view.planeWidth / drawing.width;
    for (const [x0, y0, x1, y1] of drawing.objects) {
      expect(view.left + x0*scale).toBeGreaterThanOrEqual(-1);
      expect(view.top + y0*scale).toBeGreaterThanOrEqual(-1);
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
