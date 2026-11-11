// Review real last-mile interactions. Before images are isolated to the browser;
// after images come from local public media, with no candidate interception or UI hiding.
// Usage: bun scripts/capture-lastmile-rollout.mjs <rollout-root>
import { chromium } from 'playwright';
import { mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

const root = path.resolve(process.argv[2] ?? '');
assert(process.argv[2], 'rollout root required');
const output = path.join(root, 'screens');
await mkdir(output, { recursive: true });
const inventory = JSON.parse(await readFile(path.join(root, 'inventory.json'), 'utf8'));
const before = new Map(inventory.map(row => [row.path.replace(/^public/, ''), path.join(root, 'before', row.path.replace(/^public\//, ''))]));
const observations = [];
const browser = await chromium.launch({ headless: true });
try {
  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    for (const phase of ['before', 'after']) {
      const cases = phase === 'before' ? [['alva', 'boat']] : [
        ['alva', 'boat'], ['alva', 'socks'], ['khor', 'boat'], ['khor', 'socks'], ['arseniy', 'boat'], ['arseniy', 'socks'],
      ];
      for (const [recipient, parcel] of cases) {
        const context = await browser.newContext({ viewport, reducedMotion: 'reduce' });
        if (phase === 'before') {
          await context.route('**/*.webp*', route => {
            const file = before.get(new URL(route.request().url()).pathname);
            return file ? route.fulfill({ path: file, contentType: 'image/webp' }) : route.continue();
          });
        }
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(`http://127.0.0.1:4173/scenes.html?scene=lastmile&parcel=${parcel}&recipient=${recipient}&profile=professional`);
        await page.locator('[data-scene-briefing]').waitFor();
        for (let i = 0; i < 30; i++) {
          const button = page.locator('[data-scene-briefing]').getByRole('button', { name: /^(Далее|К выбору)$/ });
          if (!(await button.isVisible())) break;
          await button.click();
          if (await page.locator('[data-scene-briefing]').getAttribute('data-reading') === 'false') break;
        }
        await page.locator('[data-hotspot="helicopter"]').waitFor();
        await page.evaluate(() => document.fonts.ready);
        async function capture(stage, expected, selector) {
          await page.waitForFunction(({ expected, selector }) => {
            const image = document.querySelector(selector);
            return image?.complete && image.naturalWidth > 0 && image.currentSrc.includes(expected);
          }, { expected, selector });
          await page.locator(selector).evaluate(image => image.decode());
          await page.waitForFunction(() => !document.querySelector('[data-artwork-status]'));
          await page.evaluate(async () => {
            await Promise.all([...document.images]
              .filter(image => image.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }))
              .map(image => image.decode()));
            // Decoded pixels still need a compositor frame; include progress icons too.
            await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
          });
          const state = await page.evaluate(selector => {
            const image = document.querySelector(selector);
            return {
              src: image.currentSrc, width: image.naturalWidth, height: image.naturalHeight,
              visible: image.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true }),
              bounds: image.getBoundingClientRect().toJSON(),
              overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
              camera: document.querySelector('[data-world-plane]')?.getAttribute('style') ?? null,
              leg: document.querySelector('[data-delivery-leg]')?.getAttribute('data-delivery-leg') ?? null,
              beat: document.querySelector('[data-outcome-beat]')?.getAttribute('data-outcome-beat') ?? null,
              resultText: document.querySelector('[data-result-reading]')?.textContent ?? null,
            };
          }, selector);
          assert.equal(state.overflow, 0);
          assert.equal(state.visible, true);
          if (stage !== 'map') {
            assert.equal(state.leg, stage === 'flight' ? 'flight' : 'ground');
            if (recipient !== 'arseniy') assert.equal(state.beat, stage === 'flight' ? '0' : '1');
          }
          assert.deepEqual(errors, []);
          const file = `${viewport.width}x${viewport.height}-${recipient}-${parcel}-${phase}-${stage}.png`;
          await page.screenshot({ path: path.join(output, file) });
          observations.push({ viewport, phase, recipient, parcel, stage, file, ...state, errors: [...errors] });
        }
        if (parcel === 'boat') {
          const format = viewport.width === 1440 ? 'wide' : 'tall';
          await capture('map', `choice-${format}-${recipient}.webp`, '[data-world-scene] img');
        }
        // Cases without a map screenshot must still finish the initial map load.
        await page.locator('[data-world-scene] img').evaluate(image => image.decode());
        await page.locator('[data-hotspot="helicopter"]').click();
        const gift = parcel === 'boat' ? 'boat' : 'parcel';
        await capture('flight', `flight-${gift}${recipient === 'arseniy' ? '-arseniy' : ''}-tall.webp`, '[data-delivery-leg="flight"] img');
        if (recipient !== 'arseniy') {
          for (let i = 0; i < 30 && await page.locator('[data-delivery-leg="ground"]').count() === 0; i++) {
            await page.getByRole('button', { name: 'Читать дальше', exact: true }).click();
          }
          const ground = recipient === 'khor' ? `helicopter-ground-khor-${gift}-v6.webp` : gift === 'boat' ? 'helicopter-ground-boat-final-v5.webp' : 'helicopter-ground-alva-parcel-v6.webp';
          await capture('legacy-ground', ground, '[data-delivery-leg="ground"] img');
        }
        await context.close();
      }
    }
    const pair = observations.filter(row => row.viewport.width === viewport.width && row.recipient === 'alva' && row.parcel === 'boat' && row.stage === 'map');
    assert.equal(pair.length, 2);
    assert.equal(pair[0].camera, pair[1].camera, 'rollout must preserve map camera');
  }
  const after = observations.filter(row => row.phase === 'after');
  assert.equal(new Set(after.filter(row => row.stage === 'map').map(row => new URL(row.src).pathname)).size, 6);
  assert.equal(new Set(after.filter(row => row.stage === 'flight').map(row => new URL(row.src).pathname)).size, 4);
  assert.equal(new Set(after.filter(row => row.stage === 'legacy-ground').map(row => new URL(row.src).pathname)).size, 4);
  console.log(JSON.stringify(observations, null, 2));
} finally {
  await browser.close();
}
