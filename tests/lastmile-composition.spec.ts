import { expect, test } from '@playwright/test';

import { lastmileChoiceArtwork as bounds } from '../src/scenes/lastmile/expandedArtwork';
// Published R5 geometry and rendered hit areas. Paint composition is reviewed visually,
// not inferred from the obsolete R4 Blender object projections.

for (const [width, height] of [[320, 568], [360, 640], [375, 667], [390, 844], [412, 915], [600, 960], [1024, 1366], [667, 375], [844, 390], [1180, 820], [1024, 768], [1366, 768], [1440, 900], [1920, 1080], [2560, 1080]]) {
  test(`lastmile artwork and hit areas fit ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('/scenes.html?scene=lastmile&parcel=boat&recipient=khor');
    const next = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
    for (let i = 0; i < 10 && await next.isVisible(); i++) await next.click();
    const stage = page.locator('[data-world-scene="lastmile"]');
    await expect(stage).toHaveAttribute('data-artwork-ready', 'true');
    await stage.locator('img').evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
    const view = await stage.evaluate(el => {
      const s = el.getBoundingClientRect();
      const p = el.querySelector('[data-world-plane]')!.getBoundingClientRect();
      const hint = document.querySelector('[data-carrier-tap-hint]')!.getBoundingClientRect();
      return { width: s.width, height: s.height, left: p.left-s.left, top: p.top-s.top, planeWidth: p.width, planeHeight: p.height, hintBottom: hint.bottom-s.top };
    });
    // One wide drawing on every screen (owner 22.11).
    await expect(stage.locator('img').first()).toHaveAttribute('src', /revision-30\/choice-wide\.webp$/);
    // The art always covers the whole stage: no bands at any layout.
    expect(view.left).toBeLessThanOrEqual(0.5);
    expect(view.top).toBeLessThanOrEqual(0.5);
    expect(view.left + view.planeWidth).toBeGreaterThanOrEqual(view.width - 0.5);
    expect(view.top + view.planeHeight).toBeGreaterThanOrEqual(view.height - 0.5);
    // The existing breathing ring reaches 1.15x. Check its entire animation envelope,
    // not a lucky screenshot frame. Vehicle names must not cover the drawing.
    await expect(stage.locator('[data-lastmile-label]')).toHaveCount(0);
    const annotations = await stage.evaluate(el => [...el.querySelectorAll('[data-lastmile-ripple]')].map(circle => {
      const id = circle.getAttribute('data-lastmile-ripple')!;
      return { id, cx: Number(circle.getAttribute('cx')), cy: Number(circle.getAttribute('cy')), radius: Number(circle.getAttribute('r')) * 1.15 };
    }));
    expect(annotations).toHaveLength(4);
    for (let i = 0; i < annotations.length; i++) for (let j = i + 1; j < annotations.length; j++) {
      const a = annotations[i], b = annotations[j];
      expect(Math.hypot(a.cx - b.cx, a.cy - b.cy), `${a.id}/${b.id} breathing rings overlap`).toBeGreaterThan(a.radius + b.radius);
    }
    const drawing = bounds;
    const zones = await stage.evaluate(el => {
      const stage = el.getBoundingClientRect();
      return [...el.querySelectorAll('[data-lastmile-zone]')].map(path => {
        const box = path.getBoundingClientRect();
        return { left: box.left - stage.left, top: box.top - stage.top, right: box.right - stage.left, bottom: box.bottom - stage.top };
      });
    });
    expect(zones).toHaveLength(4);
    // One wide drawing that always covers: a stage narrower than the quay row itself (1024x1366 beside the side panel)
    // trims both row ends evenly; every vehicle then still keeps its centre, and its hotspot, on screen.
    const row = Math.max(...zones.map(b => b.right)) - Math.min(...zones.map(b => b.left));
    for (const box of zones) {
      if (row <= view.width) {
        expect(box.left).toBeGreaterThanOrEqual(-1);
        expect(box.right).toBeLessThanOrEqual(view.width + 1);
      } else {
        expect((box.left + box.right) / 2).toBeGreaterThan(0);
        expect((box.left + box.right) / 2).toBeLessThan(view.width);
      }
      expect(box.top).toBeGreaterThanOrEqual(view.hintBottom);
      expect(box.bottom).toBeLessThanOrEqual(view.height + 1);
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
