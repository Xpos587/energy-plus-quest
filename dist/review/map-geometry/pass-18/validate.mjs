import { chromium } from '@playwright/test';
import { writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root = fileURLToPath(new URL('.', import.meta.url));
const browser = await chromium.launch({ headless: true });
const results = [];
await mkdir(`${root}screenshots`, { recursive: true });
try {
  for (const [width, height] of [[375,667],[390,844],[768,1024],[1024,768],[1440,900]]) {
    const page = await browser.newPage({ viewport: { width, height }, acceptDownloads: true });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto('http://localhost:4173/review/map-geometry/pass-18/index.html', { waitUntil: 'networkidle' });
    await page.locator('#map').evaluate(image => image.decode());
    assert.equal(await page.locator('[data-choice]').count(), 5);
    assert.equal(await page.locator('[data-choice="express"]').count(), 1);
    for (const [id, number] of [['old',1],['near',2],['crew',3],['old4',4],['express',null]]) {
      await page.locator(`[data-choice="${id}"]`).click();
      await page.locator('#outcome').evaluate(image => image.decode());
      assert.equal(await page.locator('#result').getAttribute('data-carrier'), id);
      const format = width <= 650 ? 'mobile' : 'desktop';
      assert.ok((await page.locator('#outcome').evaluate(image => image.currentSrc)).endsWith(`${id}-${format}.png`));
      assert.equal(await page.locator('#outcome-download').getAttribute('href'), `${id}-${format}.png`);
      if (number) {
        assert.equal(await page.locator('#truck').getAttribute('src'), `truck-${number}.png`);
        assert.equal(await page.locator('#map-detail').isVisible(), true);
      } else assert.equal(await page.locator('#map-detail').isVisible(), false);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      const [download] = await Promise.all([page.waitForEvent('download'), page.locator('#outcome-download').click()]);
      assert.equal(download.suggestedFilename(), `${id}-${format}.png`);
      await download.delete();
    }
    await page.locator('[data-choice="express"]').click();
    await page.locator('#outcome').evaluate(image => image.decode());
    await page.screenshot({ path: `${root}screenshots/express-${width}x${height}.png`, fullPage: true });
    await page.locator('[data-choice="old4"]').click();
    await page.locator('#outcome').evaluate(image => image.decode());
    await page.screenshot({ path: `${root}screenshots/${width}x${height}.png`, fullPage: true });
    const [mapDownload] = await Promise.all([page.waitForEvent('download'), page.locator('a[href="map-with-girl.png"]').click()]);
    assert.equal(mapDownload.suggestedFilename(), 'map-with-girl.png');
    await mapDownload.delete();
    await page.locator('#back').click();
    assert.equal(await page.locator('[data-choice="old4"]').evaluate(e => e === document.activeElement), true);
    assert.deepEqual(errors, []);
    results.push({ width, height, choices: 5, responsiveSources: 'passed', downloads: 6, overflow: false, consoleErrors: errors, girl: 'same pass17 sprite baked into full uncropped map; pixel-checked separately' });
    await page.close();
  }
} finally { await browser.close(); }
await writeFile(`${root}validation.json`, JSON.stringify({ candidateOnly: true, browser: 'Chromium', results, limits: 'Static review, not animation/speed or live integration; no Safari/Firefox claim.' }, null, 2));
console.log('PASS: 5 viewports, 25 choice-to-outcome mappings, 30 downloads, no overflow or page errors.');
