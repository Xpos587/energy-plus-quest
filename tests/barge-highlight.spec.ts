import { test, expect, type Page } from '@playwright/test';
// R19: after «Изменить выбор» the previous way stayed lit next to the new one.
test.use({ contextOptions: { reducedMotion: 'reduce' } });

// Lit layers per way (artwork.ts actors; "near" renders as top, "ivan" as pru).
const lit: Record<string, string> = { remote: 'pru+top', rush: 'ladder+top', wait: 'top', petr: 'far+top' };
// Every ordered pair of the four ways exactly once.
const order = ['rush', 'petr', 'remote', 'wait', 'rush', 'remote', 'petr', 'wait', 'remote', 'rush', 'wait', 'petr', 'rush'];

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
