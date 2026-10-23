// Run against the local preview: node scripts/check-compact-art.mjs http://127.0.0.1:4193
import assert from 'node:assert/strict';
import { mkdir, readFile } from 'node:fs/promises';
import { chromium } from '@playwright/test';

const truckOnly = process.argv.includes('--truck');
const base = process.argv[2] ?? 'http://127.0.0.1:4193';
const manifest = JSON.parse(await readFile(new URL('../src/scenes/worldManifest.json', import.meta.url)));
const view = manifest.scenes.compact.desktop;
assert.deepEqual(view, manifest.scenes.compact.mobile, 'One art coordinate system at every size');
await mkdir('.tmp-work/compact-art-check', { recursive: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  await page.goto(`${base}/${view.image}`);
  const geometry = await page.evaluate(() => {
    const bounds = (id) => {
      const { x, y, width, height } = document.getElementById(id).getBBox();
      return { x, y, width, height };
    };
    return Object.fromEntries(['heavy-crates', 'protected-dishes', 'recess-left', 'recess-right', 'recess-base', 'front-wall-restraints', 'pillow-padding', 'heavy-straps', 'heavy-floor-anchors'].map(id => [id, bounds(id)]));
  });
  const points = view.hotspots.map(p => ({ x: (p.x * view.width - 45) / .8, y: (p.y * view.height + 30) / .8 }));
  for (const [index, id] of [[0, 'heavy-crates'], [1, 'protected-dishes']]) {
    const cargo = geometry[id];
    assert(points[index].x > cargo.x && points[index].x < cargo.x + cargo.width);
    assert(points[index].y < cargo.y, `${id}: marker is in free space above the actual cargo`);
    assert(cargo.y + cargo.height >= 479, `${id}: cargo reaches the shared floor`);
  }
  const straps = geometry['heavy-straps'];
  const anchors = geometry['heavy-floor-anchors'];
  assert(straps.y + straps.height >= anchors.y, 'Heavy over-top straps reach real floor rings');
  assert(anchors.y + anchors.height <= 489, 'Anchor rings are mounted on the actual floor');
  const recess = points[2];
  assert(recess.x > geometry['recess-left'].x + geometry['recess-left'].width);
  assert(recess.x < geometry['recess-right'].x);
  assert(recess.y > geometry['recess-left'].y && recess.y < geometry['recess-base'].y);
  const front = geometry['front-wall-restraints'];
  assert(points[3].x > front.x && points[3].x < front.x + front.width);
  assert(points[3].y > front.y && points[3].y < front.y + front.height);
  assert(geometry['pillow-padding'].x + geometry['pillow-padding'].width < points[3].x);

  const structure = await page.evaluate(() => ({
    doors: ['rear-door-far', 'rear-door-near'].every(id => document.getElementById(id)),
    wheels: document.querySelectorAll('#trailer-rear-axles use').length,
    solid: ['opaque-far-wall', 'front-bulkhead', 'load-floor', 'sectioned-near-sill', 'continuous-chassis', 'tractor'].every(id => document.getElementById(id)),
    ramp: !!document.getElementById('threshold-bridge'),
  }));
  assert.deepEqual(structure, { doors: true, wheels: 3, solid: true, ramp: false });
  for (const [width, height] of [[1440, 900], [375, 667], [568, 320]]) {
    await page.setViewportSize({ width, height });
    await page.goto(`${base}/scenes.html?scene=compact`);
    await page.locator('[data-world-plane] img').evaluate(img => img.decode());
    await page.screenshot({ path: `.tmp-work/compact-art-check/natural-${width}x${height}.png` });
    // Exercise the requested smallest image width in the real renderer, not synthetic marker math.
    if (width === 568) await page.locator('[data-world-scene]').evaluate(stage => {
      stage.style.width = '229.5px';
      stage.style.height = '137.7px';
    });
    await page.waitForTimeout(100);
    const plane = await page.locator('[data-world-plane]').boundingBox();
    if (width === 568) assert(Math.abs(plane.width - 229.5) < 0.1);
    const boxes = [];
    for (const point of view.hotspots) {
      const button = page.locator(`[data-hotspot="${point.id}"]`);
      const box = await button.boundingBox();
      assert(box.width >= 44 && box.height >= 44);
      assert(Math.abs(box.x + box.width / 2 - plane.x - point.x * plane.width) < 1);
      assert(Math.abs(box.y + box.height / 2 - plane.y - point.y * plane.height) < 1);
      assert(box.x >= plane.x && box.x + box.width <= plane.x + plane.width);
      assert(box.y >= plane.y && box.y + box.height <= plane.y + plane.height);
      for (const other of boxes) assert(
        box.x + box.width <= other.x || other.x + other.width <= box.x ||
        box.y + box.height <= other.y || other.y + other.height <= box.y,
        '44px rectangular hit areas must not overlap',
      );
      assert(await button.evaluate(node => {
        const b = node.getBoundingClientRect();
        return document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2)?.closest('button') === node;
      }), 'Marker is not occluded by the panel');
      boxes.push(box);
    }
    await page.screenshot({ path: `.tmp-work/compact-art-check/checked-${width}x${height}.png` });
    await page.locator('[data-hotspot="place-3"]').press('Enter');
    assert(await page.getByTestId('result-copy').isVisible());
    assert.equal(await page.locator('[data-world-scene]').getAttribute('data-placement'), '3');
  }
  for (const [width, height] of (truckOnly ? [[390, 844], [320, 568]] : [[820, 600], [900, 600], [1440, 900], [375, 667], [568, 320]])) {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    for (const parcel of (truckOnly ? ['boat'] : ['camera', 'socks', 'boat'])) {
      for (const choice of (truckOnly ? ['place-3', 'place-4'] : ['place-1', 'place-2', 'place-3', 'place-4', 'auto'])) {
        await page.goto(`${base}/scenes.html?scene=compact&parcel=${parcel}`);
        await page.locator('[data-world-plane] img').evaluate(img => img.decode());
        const gift = page.locator('[data-placed-parcel]');
        assert.equal(await gift.getAttribute('data-parcel-location'), 'loading-apron');
        assert.equal(await gift.evaluate(node => getComputedStyle(node).transitionDuration), '0s');
        await page.locator(`[data-choice-id="${choice}"]`).press('Enter');
        const place = choice === 'auto' ? parcel === 'boat' ? 4 : 3 : Number(choice.at(-1));
        const blocked = parcel === 'boat' && place === 3;
        assert.equal(await gift.getAttribute('data-parcel-location'), blocked ? 'loading-apron' : `place-${place}`);
        assert.equal(await page.locator('[data-placement-blocked]').count(), blocked ? 1 : 0);
        // Measure rendered SVG geometry, not just the semantic data attributes.
        const measured = await gift.evaluate(node => {
          const matrix = new DOMMatrix(getComputedStyle(node).transform);
          const { x, y, width, height } = node.getBoundingClientRect();
          const turn = node.querySelector('g');
          return { x, y, width, height, tx: matrix.e, ty: matrix.f,
            scale: Math.hypot(matrix.a, matrix.b),
            turnDuration: turn ? getComputedStyle(turn).transitionDuration : '0s' };
        });
        const expected = blocked ? [490, 569] : place === 1 ? [190, 345] : place === 2 ? [399, 367] : place === 3 ? [640, 379]
          : parcel === 'boat' ? [852, 320] : parcel === 'camera' ? [850, 356] : [850, 471];
        assert.deepEqual([measured.tx, measured.ty], expected, 'Parcel contacts the authored load surface');
        assert.equal(measured.scale, 1, 'No shrinking a gift to fit');
        const actualWidth = measured.width / (await page.locator('[data-world-plane]').boundingBox()).width * 1000;
        assert(Math.abs(actualWidth - (parcel === 'boat' ? place === 4 ? 98 : 294 : 77) * .8) < .1,
          `The drawn gift silhouette keeps its authored size: ${parcel}/${place}/${actualWidth}`);
        assert.equal(measured.turnDuration, '0s', 'Reduced motion also disables boat rotation');
        const plane = await page.locator('[data-world-plane]').boundingBox();
        const panel = await page.locator('[data-result="true"]').boundingBox();
        assert(measured.x >= plane.x - 1 && measured.y >= plane.y - 1);
        assert(measured.x + measured.width <= plane.x + plane.width + 1);
        assert(measured.y + measured.height <= plane.y + plane.height + 1);
        assert(measured.x + measured.width <= panel.x || measured.x >= panel.x + panel.width ||
          measured.y + measured.height <= panel.y || measured.y >= panel.y + panel.height,
          `Result panel cannot cover the actual selected gift: ${width}x${height}/${parcel}/${choice}`);
        assert.equal(await page.locator(`[data-hotspot="place-${place}"]`).evaluate(node => getComputedStyle(node).opacity), '0',
          'Chosen number cannot hide the small gift');
        if (choice === 'auto' || blocked || (parcel === 'boat' && choice === 'place-4')) await page.screenshot({ path: `.tmp-work/compact-art-check/result-${width}x${height}-${parcel}-${choice}.png` });
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
        assert.equal(await gift.getAttribute('data-parcel-location'), 'loading-apron');
        assert.equal(await page.locator('[data-placement-blocked]').count(), 0);
      }
    }
  }
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  assert.notEqual(await page.locator('[data-placed-parcel]').evaluate(node => getComputedStyle(node).transitionDuration), '0s');
  console.log(`PASS: ${truckOnly ? '4 targeted boat placements' : '75 real gift placements and automatic mapping'}, revision, fixed scale, contact geometry, unobscured results and reduced motion.`);
  console.log('PASS: actual SVG cargo/space geometry, floor contact, shared coordinates, real 229.5px plane, non-overlapping unoccluded 44px targets, keyboard selection.');
} finally {
  await browser.close();
}
