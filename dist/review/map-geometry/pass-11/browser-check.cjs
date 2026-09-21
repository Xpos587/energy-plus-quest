const { chromium } = require('/home/michael/Github/energy-plus-quest/node_modules/playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = __dirname;
const artifacts = '/home/michael/.local/state/energy-plus-quest/production/2026-09-16-geometry-reference/pass-11';
const url = 'http://localhost:4173/review/map-geometry/pass-11/index.html';
const sha = buffer => crypto.createHash('sha256').update(buffer).digest('hex');
(async () => {
  const browser = await chromium.launch();
  fs.mkdirSync(path.join(artifacts, 'screenshots'), { recursive: true });
  const timeline = await browser.newPage({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  for (const t of [0,.48,.96,1.44]) {
    await timeline.goto(`${url}?t=${t}`);
    await timeline.waitForFunction(() => document.querySelector('[data-smoke]')?.children.length > 0);
    for (let truck = 0; truck < 2; truck++) {
      await timeline.locator('.details figure svg').nth(truck).screenshot({path:path.join(artifacts,`timeline-${truck === 0 ? 1 : 4}-${t}.png`)});
    }
  }
  await timeline.close();
  const results = [];
  for (const [width,height] of [[375,667],[1440,900],[320,568],[390,844],[820,1180],[568,320]]) {
    const page = await browser.newPage({ viewport: { width,height }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(`${url}?t=.4`);
    assert.equal(response.status(), 200);
    await page.waitForFunction(() => document.querySelector('[data-smoke]')?.children.length > 0);
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.equal(await page.locator('video').count(), 0);
    const initial = await page.locator('[data-smoke="overview"]').innerHTML();
    const initialPixels = sha(await page.locator('.overview').screenshot());
    await page.locator('#toggle').click();
    await page.waitForTimeout(450);
    assert.notEqual(await page.locator('[data-smoke="overview"]').innerHTML(), initial);
    assert.notEqual(sha(await page.locator('.overview').screenshot()), initialPixels);
    await page.locator('#toggle').click();
    const paused = await page.locator('[data-smoke="overview"]').innerHTML();
    await page.waitForTimeout(150);
    assert.equal(await page.locator('[data-smoke="overview"]').innerHTML(), paused);
    await page.locator('#time').evaluate(input => { input.value = '0.4'; input.dispatchEvent(new Event('input', { bubbles: true })); });
    assert.equal(await page.locator('#clock').innerText(),'0.40 s');
    const overview = await page.locator('.overview').boundingBox();
    assert(Math.abs(overview.width / overview.height - 1.44) < .01);
    assert((await page.locator('[data-smoke="overview"] [data-truck="1"]').count()) >= 2);
    assert((await page.locator('[data-smoke="overview"] [data-truck="4"]').count()) >= 2);
    for (const link of await page.locator('nav a,button').all()) assert((await link.boundingBox()).height >= 44);
    await page.evaluate(() => scrollTo(0,0));
    await page.screenshot({ path: path.join(artifacts,'screenshots',`${width}x${height}.png`) });
    await page.locator('.details').screenshot({path:path.join(artifacts,'screenshots',`${width}x${height}-exhaust.png`)});
    assert.deepEqual(errors, []);
    results.push({width,height,status:'passed',overviewWidth:overview.width,playingChangesPixels:true,pausedIsStable:true});
    await page.close();
  }
  const previous = JSON.parse(fs.readFileSync(path.join(root,'../pass-09/manifest.json')));
  assert.equal(sha(fs.readFileSync(path.join(root,'../index.html'))),previous.unchangedMainIndexSHA256);
  for (const [file,hash] of Object.entries(previous.files)) assert.equal(sha(fs.readFileSync(path.join(root,'../pass-09',file))),hash,`Pass09 changed: ${file}`);
  const pass10 = JSON.parse(fs.readFileSync(path.join(root,'../pass-10/manifest.json')));
  for (const [file,hash] of Object.entries(pass10.files)) assert.equal(sha(fs.readFileSync(path.join(root,'../pass-10',file))),hash,`Pass10 changed: ${file}`);
  for (const name of ['professional','student','arseniy','alva','khor']) assert.equal(sha(fs.readFileSync(path.join(root,`${name}.webp`))),sha(fs.readFileSync(`/home/michael/Github/energy-plus-quest/design/scene-01/assets/current/choices/${name}.webp`)));
  await browser.close();
  const output = {passed:true,results,unchangedMainIndex:true,unchangedPass09Files:true,unchangedPass10Files:true,unchangedCharacterReferences:true,scope:'Static map and stationary cab-side smoke only; no speed or route claim.'};
  fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(output,null,2));
  fs.writeFileSync(path.join(artifacts,'validation.json'),JSON.stringify(output,null,2));
  console.log(JSON.stringify(output,null,2));
})().catch(error => { console.error(error);process.exit(1); });
