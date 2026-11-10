import { test, expect, type Page } from '@playwright/test';
// R19: after «Изменить выбор» the previous way stayed lit next to the new one.
test.use({ contextOptions: { reducedMotion: 'reduce' } });

// Lit layers per way (artwork.ts actors; "near" renders as top, "ivan" as pru).
const lit: Record<string, string> = { remote: 'pru+top', rush: 'ladder+top', petr: 'far+top' };
// Every ordered pair of the three ways exactly once.
const order = ['rush', 'petr', 'remote', 'rush', 'remote', 'petr', 'rush'];

const litLayers = (page: Page) => page.locator('[data-world-scene=crane] [data-lit]').evaluateAll(
  layers => layers.map(layer => (layer as HTMLElement).dataset.layer).sort().join('+'));

test('only the current way is lit across every change of choice', async ({ page }, info) => {
  test.setTimeout(120_000);
  const touch = !!info.project.use.hasTouch;
  const press = (selector: string) => touch ? page.locator(selector).tap() : page.locator(selector).click();
  await page.goto('/scenes.html?scene=crane&parcel=camera&recipient=alva');
  const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
  const revise = page.getByRole('button', { name: 'Изменить выбор', exact: true });
  for (const [step, id] of order.entries()) {
    if (step > 0) {
      await revise.scrollIntoViewIfNeeded();
      touch ? await revise.tap() : await revise.click();
      await expect(page.locator('[data-result-reader]')).toHaveCount(0);
      await expect.poll(() => litLayers(page), `nothing lit after revising ${order[step - 1]}`).toBe('');
    }
    await press(`[data-hotspot="${id}"]`);
    await expect.poll(() => litLayers(page), `${order[step - 1] ?? 'start'} -> ${id}`).toBe(lit[id].split('+').sort().join('+'));
    await press('[data-choice-confirm]');
    await expect(page.locator('[data-result-reader]')).toBeVisible();
  }
});

// R19 round 2: on a phone the four ways must stay four separate fingertips.
for (const [width, height] of [[320, 568], [390, 844], [1440, 900]]) {
  test(`quay tap targets stay 44px with an 8px gap at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto('/scenes.html?scene=crane&parcel=camera&recipient=alva&carrier=near');
    const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
    for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
    const rects = await page.locator('[data-world-scene=crane] [data-hotspot]').evaluateAll(
      nodes => nodes.map(node => {
        const rect = node.getBoundingClientRect();
        return { id: (node as HTMLElement).dataset.hotspot!, x: rect.x, y: rect.y, w: rect.width, h: rect.height };
      }));
    expect(rects).toHaveLength(3);
    for (const rect of rects) {
      expect(rect.w, `${rect.id} width`).toBeGreaterThanOrEqual(44);
      expect(rect.h, `${rect.id} height`).toBeGreaterThanOrEqual(44);
    }
    for (let i = 0; i < rects.length; i++) {
      for (let j = i + 1; j < rects.length; j++) {
        const a = rects[i];
        const b = rects[j];
        const gap = Math.max(a.x - (b.x + b.w), b.x - (a.x + a.w), a.y - (b.y + b.h), b.y - (a.y + a.h));
        expect(gap, `${a.id} vs ${b.id}`).toBeGreaterThanOrEqual(8);
      }
    }
  });
}
