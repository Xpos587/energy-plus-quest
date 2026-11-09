import { test, expect, type Page } from '@playwright/test';
// R19: after «Изменить выбор» the old pick stayed lit next to the new one in every scene.
test.use({ contextOptions: { reducedMotion: 'reduce' } });

const litLayers = (page: Page) => page.locator('[data-world-scene=crane] [data-lit]').evaluateAll(
  layers => layers.map(layer => (layer as HTMLElement).dataset.layer).sort().join('+'));
// Lit layers per crane way (artwork.ts actors; "near" renders as top, "ivan" as pru).
const crane: Record<string, string> = { remote: 'pru+top', rush: 'ladder+top', wait: 'top', petr: 'far+top' };
// What a card highlights, per scene: any visible focus/selected mark.
const marks = '[data-focused="true"], [aria-pressed="true"], [data-active="true"]:not(svg), [data-lit]';

const scenes = [
  { name: 'carrier', pairs: [['near', 'crew']] },
  { name: 'compact', pairs: [['place-1', 'place-3'], ['auto', 'place-2']] },
  { name: 'inventory', pairs: [['entrance', 'keeper'], ['wms', 'alphabet']] },
  { name: 'crane', pairs: [['rush', 'petr'], ['remote', 'wait']] },
  { name: 'lastmile', pairs: [['helicopter', 'robot'], ['rover', 'pipe-carrier']] },
] as const;

async function open(page: Page, name: string, touch: boolean) {
  if (name === 'carrier') {
    await page.goto('/');
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.reload();
    for (const step of ['[data-intro-enter]', '[data-intro-next]', '[data-intro-start]',
      '[data-choice="professional"]', '[data-choice="alva"]', '[data-choice="camera"]']) {
      await page.locator(step).click();
    }
    return;
  }
  await page.goto(`/scenes.html?scene=${name}&parcel=camera&recipient=alva&carrier=near`);
  const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 30 && await intro.isVisible(); n++) await intro.click();
  void touch;
}

for (const { name, pairs } of scenes) {
  test(`${name}: only the current pick is highlighted`, async ({ page }, info) => {
    test.setTimeout(90_000);
    const touch = !!info.project.use.hasTouch;
    // Map rigs keep driving, so activate them like the map's own tests: focus, then Enter.
    const press = (locator: ReturnType<Page['locator']>) => name === 'carrier'
      ? locator.focus().then(() => page.keyboard.press('Enter'))
      : touch ? locator.tap() : locator.click();
    await open(page, name, touch);
    const target = (id: string) => page.locator(
      `:is([data-hotspot="${id}"], [data-carrier-choice="${id}"], [data-scene-choice="${id}"]):visible`).first();
    const back = page.locator('button:visible', { hasText: /^\s*(Изменить выбор|К машинам)\s*$/ }).first();
    for (const [step, [first, second]] of pairs.entries()) {
      if (step > 0) {
        // A fresh scene per pair keeps the flow short.
        await page.goto('/');
        await open(page, name, touch);
      }
      await press(target(first));
      // Some scenes commit the choice straight from the zone, others show a card to confirm.
      const confirm = page.locator('[data-choice-confirm]:visible').first();
      if (await confirm.count()) await press(confirm);
      await back.waitFor();
      await back.scrollIntoViewIfNeeded();
      await press(back);
      await expect.poll(() => page.locator(marks).evaluateAll(
        nodes => nodes.filter(node => node.getClientRects().length).length),
      `nothing stays lit after revising ${first}`).toBe(0);
      await press(target(second));
      // Every mark on the card screen must belong to the new pick and nothing else.
      await expect.poll(() => name === 'crane' ? litLayers(page) : page.locator(marks).evaluateAll(
        nodes => [...new Set(nodes.filter(node => node.getClientRects().length)
          .map(node => node.dataset.hotspot ?? node.dataset.sceneChoice ?? node.dataset.carrierChoice ?? ''))]
          .filter(Boolean).sort().join('+')),
      // lastmile commits straight from the zone and hides the drawing on the result screen.
      `${first} -> ${second}`).toBe(name === 'crane' ? crane[second] : name === 'lastmile' ? '' : second);
    }
  });
}
