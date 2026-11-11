// bun scripts/capture-compact-gifts.mjs .tmp-work/<review>/before camera,boat [base-url]
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const [out, gifts = 'camera,boat', base = 'http://127.0.0.1:4181'] = process.argv.slice(2);
assert(out?.startsWith('.tmp-work/'), 'Keep review captures in project scratch storage');
const parcels = gifts.split(',');
assert(parcels.every(p => ['camera', 'boat', 'socks'].includes(p)), 'Unknown gift');
await mkdir(out, { recursive: true });
const browser = await chromium.launch();
const checks = [], errors = [];
async function settle(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    await Promise.allSettled(document.getAnimations()
      .filter(a => Number.isFinite(a.effect?.getComputedTiming().endTime)).map(a => a.finished));
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
}
try {
  for (const [width, height] of [[1440, 900], [390, 844]]) {
    const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
    page.on('pageerror', error => errors.push(error.message));
    for (const parcel of parcels) {
      await page.goto(`${base}/scenes.html?scene=compact&parcel=${parcel}&recipient=alva`);
      const next = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
      for (let n = 0; n < 20 && await next.isVisible(); n++) await next.click();
      await page.locator('[data-hotspot="place-3"]').waitFor();
      await settle(page);
      const choiceTarget = await page.locator('[data-hotspot="place-3"]').getAttribute('style');
      await page.screenshot({ path: `${out}/${width}x${height}-${parcel}-choice.png` });
      for (const id of ['place-1', 'place-2', 'place-3', 'place-4', 'auto']) {
        await page.locator(`[data-hotspot="${id}"]`).click();
        await page.locator('[data-choice-confirm]').click();
        await page.waitForFunction(parcel => {
          const figure = document.querySelector('[data-fixed-result]');
          const picture = figure?.querySelector('img');
          return picture ? picture.complete && picture.naturalWidth > 0 :
            [...(figure?.querySelectorAll('image') ?? [])].some(el => el.getAttribute('href')?.includes(`${parcel}-zone`));
        }, parcel);
        await settle(page);
        const data = await page.locator('[data-fixed-result]').evaluate(async (figure, parcel) => {
          const htmlImage = figure.querySelector('img');
          const href = htmlImage?.currentSrc ?? [...figure.querySelectorAll('image')]
            .find(image => image.getAttribute('href')?.includes(`${parcel}-zone`))?.getAttribute('href');
          const image = new Image(); image.src = href; await image.decode();
          const badge = figure.querySelector('[aria-pressed="true"] [data-layout-badge]')?.getBoundingClientRect();
          return { source: image.src, decodedWidth: image.naturalWidth,
            zones: figure.querySelectorAll('[data-loading-zone]').length,
            disabled: figure.querySelectorAll('button:disabled').length,
            badge: badge ? { left: badge.left, top: badge.top, right: badge.right, bottom: badge.bottom } : null };
        }, parcel);
        assert.equal(data.zones, 0);
        assert.equal(data.disabled, parcel === 'boat' && id === 'place-3' ? 0 : 4);
        assert(data.source.includes(`${parcel}-zone`), `${parcel}/${id}: ${data.source}`);
        await page.screenshot({ path: `${out}/${width}x${height}-${parcel}-${id}.png` });
        checks.push({ width, height, parcel, id, ...data });
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
        await settle(page);
        assert.equal(await page.locator('[data-hotspot="place-3"]').getAttribute('style'), choiceTarget);
      }
    }
    await page.close();
  }
  assert.deepEqual(errors, []);
  await writeFile(`${out}/checks.json`, JSON.stringify({ checks, errors }, null, 2));
  console.log(`PASS ${checks.length} settled results: decoded gift images, no orange overlays, locked choices, unchanged choice targets, no page errors.`);
} finally {
  await browser.close();
}
