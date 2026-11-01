import { expect, test } from '@playwright/test';

// Source-pixel extents checked against revision 11 (1x canvas pixels): vehicles, АБК, chum camp and the whole barge.
const bounds = {
  wide: { width: 2056, height: 1841, objects: [[242, 738, 627, 926], [277, 928, 568, 1102], [542, 958, 752, 1118], [754, 1028, 887, 1115], [1307, 606, 1706, 797], [1576, 736, 1808, 940], [201, 1117, 842, 1479]] },
  tall: { width: 1664, height: 1952, objects: [[382, 923, 812, 1146], [516, 1118, 837, 1334], [810, 1168, 1050, 1350], [1066, 1230, 1220, 1342], [815, 365, 1097, 527], [1011, 493, 1318, 655], [397, 1397, 1156, 1713]] },
};

for (const [width, height] of [[320, 568], [360, 640], [375, 667], [390, 844], [412, 915], [600, 960], [1024, 1366], [667, 375], [844, 390], [1180, 820], [1366, 768], [1440, 900], [1920, 1080], [2560, 1080]]) {
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
      return { width: s.width, height: s.height, left: p.left-s.left, top: p.top-s.top, planeWidth: p.width, planeHeight: p.height, hintBottom: hint.bottom-s.top, format: el.querySelector('img')!.src.includes('choice-wide') ? 'wide' as const : 'tall' as const };
    });
    // The art always covers the whole stage: no bands at any layout.
    expect(view.left).toBeLessThanOrEqual(0.5);
    expect(view.top).toBeLessThanOrEqual(0.5);
    expect(view.left + view.planeWidth).toBeGreaterThanOrEqual(view.width - 0.5);
    expect(view.top + view.planeHeight).toBeGreaterThanOrEqual(view.height - 0.5);
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
