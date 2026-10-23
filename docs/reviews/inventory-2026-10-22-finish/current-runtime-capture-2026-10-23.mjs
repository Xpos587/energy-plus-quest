import { chromium } from '@playwright/test';
import { writeFile } from 'node:fs/promises';
import sharp from 'sharp';
const dir = 'docs/reviews/inventory-2026-10-22-finish/';
const base = 'http://127.0.0.1:4344';
const browser = await chromium.launch();
const rows = [];
try {
  for (const [name, width, height] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, reducedMotion: 'reduce', serviceWorkers: 'block' });
    const page = await context.newPage();
    await page.goto(base);
    await page.evaluate(() => {
      const scope = 'quest-warehouse-human-review-2026-10-23';
      localStorage.setItem('energy-quest-save-v1', JSON.stringify({ version: 1, scope, state: { step: 'outcome', profile: 'student', recipient: 'alva', parcel: 'boat', carrier: 'old' } }));
      localStorage.setItem(scope + ':intro-seen', 'true');
      localStorage.setItem(scope + ':remaining', 'true');
      localStorage.setItem(scope + ':scenes', JSON.stringify({ progress: { sceneIndex: 1, phase: 'choice', answers: { compact: 'place-1' }, finished: false }, briefed: ['compact', 'inventory'] }));
    });
    await page.reload();
    const image = page.locator('[data-world-scene="inventory"] picture img');
    await image.waitFor({ state: 'visible', timeout: 15000 }).catch(async error => {
      console.error((await page.locator('body').innerText()).slice(0, 4000));
      console.error(await page.locator('[data-world-scene]').evaluateAll(nodes => nodes.map(node => node.getAttribute('data-world-scene'))));
      await page.screenshot({ path: dir + 'current-runtime-capture-diagnostic.png' });
      throw error;
    });
    await image.evaluate(async (img) => { await img.decode(); await document.fonts.ready; });
    await page.waitForTimeout(300);
    const evidence = await image.evaluate((img) => {
      const r = img.getBoundingClientRect();
      return { currentSrc: img.currentSrc, native: [img.naturalWidth, img.naturalHeight], displayed: [r.width, r.height], rect: r.toJSON(), dpr: devicePixelRatio, page: [innerWidth, innerHeight], scroll: [document.documentElement.scrollWidth, document.documentElement.scrollHeight], choiceNames: [...document.querySelectorAll('[data-scene-choice]')].map(el => el.textContent?.trim()), url: location.href };
    });
    const response = await page.request.get(evidence.currentSrc);
    const decoded = await sharp(await response.body()).metadata();
    const { native: intrinsicBrowserSize, ...rest } = evidence;
    rows.push({ name, width, height, httpStatus: response.status(), intrinsicBrowserSize, decodedResourcePixels: [decoded.width, decoded.height], ...rest });
    await page.screenshot({ path: dir + `current-runtime-${name}-2026-10-23.png` });
    await context.close();
  }
} finally { await browser.close(); }
await writeFile(dir + 'current-runtime-2026-10-23.json', JSON.stringify({ base, isolatedContexts: true, userBrowserProgressTouched: false, candidateIntegrated: false, rows }, null, 2));
console.log(JSON.stringify(rows.map(({ name, currentSrc, httpStatus, decodedResourcePixels }) => ({ name, currentSrc, httpStatus, decodedResourcePixels }))));
