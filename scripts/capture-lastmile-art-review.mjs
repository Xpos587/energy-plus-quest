// Read-only runtime preview: candidate images are served only in this browser context.
// Usage: bun scripts/capture-lastmile-art-review.mjs <candidate-directory> <output-directory>
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const [candidateDir, outputDir] = process.argv.slice(2);
assert(candidateDir && outputDir, 'candidate and output directories required');
await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const observations = [];
try {
  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    for (const phase of ['before', 'after']) {
      const context = await browser.newContext({ viewport, reducedMotion: 'reduce' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      if (phase === 'after') {
        await page.route(/\/revision-18\/choice-(wide|tall)-\w+\.webp(?:\?.*)?$/, route => {
          const format = route.request().url().match(/choice-(wide|tall)-/)[1];
          return route.fulfill({ path: path.resolve(candidateDir, `choice-${format}.webp`), contentType: 'image/webp' });
        });
      }
      await page.goto('http://127.0.0.1:4173/scenes.html?scene=lastmile&parcel=boat&recipient=alva&profile=professional');
      await page.locator('[data-scene-briefing]').waitFor();
      for (let i = 0; i < 30; i++) {
        const button = page.locator('[data-scene-briefing]').getByRole('button', { name: /^(Далее|К выбору)$/ });
        if (!(await button.isVisible())) break;
        await button.click();
        if (await page.locator('[data-scene-briefing]').getAttribute('data-reading') === 'false') break;
      }
      await page.locator('[data-hotspot="helicopter"]').waitFor();
      await page.locator('[data-world-scene] img').evaluateAll(images => Promise.all(images.map(image => image.decode())));
      // Art review only: moving a helicopter requires a later accepted hotspot update.
      await page.addStyleTag({ content: '[data-hotspot], [data-lastmile-annotations], [data-carrier-tap-hint] { visibility:hidden !important; }' });
      const state = await page.evaluate(() => ({
        overflow: Math.max(0, document.documentElement.scrollWidth-innerWidth),
        images: [...document.querySelectorAll('[data-world-scene] img')].map(i => ({ src:i.currentSrc, width:i.naturalWidth, height:i.naturalHeight })),
        camera: document.querySelector('[data-world-plane]')?.getAttribute('style'),
      }));
      assert.equal(state.overflow, 0);
      assert.equal(errors.length, 0, errors.join('\n'));
      const file = `${viewport.width}x${viewport.height}-${phase}.png`;
      await page.screenshot({ path: path.join(outputDir, file) });
      observations.push({ phase, viewport, ...state, errors });
      await context.close();
    }
  }
  for (let i = 0; i < observations.length; i += 2) assert.equal(observations[i].camera, observations[i+1].camera, 'review must not change runtime camera');
  console.log(JSON.stringify(observations, null, 2));
} finally {
  await browser.close();
}
