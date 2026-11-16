import { expect, test } from '@playwright/test';

import exported from '../design/scene-05/r4/runtime.json' with { type: 'json' };
// Independent Blender projections, not the production UI's framing constants.
const bounds = exported.views;

for (const [width, height] of [[320, 568], [360, 640], [375, 667], [390, 844], [412, 915], [600, 960], [1024, 1366], [667, 375], [844, 390], [1180, 820], [1024, 768], [1366, 768], [1440, 900], [1920, 1080], [2560, 1080]]) {
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
    // The existing breathing ring reaches 1.15x. Check its entire animation envelope,
    // not a lucky screenshot frame, and keep each label off neighbouring vehicles.
    const annotations = await stage.evaluate(el => [...el.querySelectorAll('[data-lastmile-ripple]')].map(circle => {
      const id = circle.getAttribute('data-lastmile-ripple')!;
      const path = el.querySelector<SVGGraphicsElement>(`[data-lastmile-zone="${id}"]`)!;
      const box = path.getBoundingClientRect();
      const label = el.querySelector(`[data-lastmile-label="${id}"]`)!.getBoundingClientRect();
      return { id, cx: Number(circle.getAttribute('cx')), cy: Number(circle.getAttribute('cy')), radius: Number(circle.getAttribute('r')) * 1.15, box: box.toJSON(), label: label.toJSON() };
    }));
    expect(annotations).toHaveLength(4);
    for (let i = 0; i < annotations.length; i++) for (let j = i + 1; j < annotations.length; j++) {
      const a = annotations[i], b = annotations[j];
      expect(Math.hypot(a.cx - b.cx, a.cy - b.cy), `${a.id}/${b.id} breathing rings overlap`).toBeGreaterThan(a.radius + b.radius);
      for (const [label, box] of [[a.label, b.box], [b.label, a.box], [a.label, b.label]]) {
        expect(label.right <= box.left || label.left >= box.right || label.bottom <= box.top || label.top >= box.bottom, `${a.id}/${b.id} labels overlap`).toBe(true);
      }
    }
    const drawing = bounds[view.format];
    const scale = view.planeWidth / drawing.width;
    for (const [x0, y0, x1, y1] of Object.values(drawing.objects)) {
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
