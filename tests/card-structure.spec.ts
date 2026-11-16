import { expect, test } from '@playwright/test';
import { openCarrier, pickCarrier } from './helpers/open-preparation';

for (const [width, height] of [[1440, 900], [1280, 720]]) {
  test(`desktop task rail leaves the whole scene unobstructed at ${width}`, async ({ page }) => {
    test.setTimeout(90000);
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    for (const scene of ['compact', 'inventory', 'crane', 'lastmile']) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=arseniy`);
      await page.evaluate(() => document.fonts.ready);
      const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
      let pages = 0;
      while (await condition.isVisible() && pages < 20) {
        const world = (await page.locator('[data-scene-world]').boundingBox())!;
        const card = (await condition.boundingBox())!;
        expect(world.x + world.width).toBeLessThanOrEqual(card.x + 1);
        await expect(condition.getByRole('button', { name: /^(Далее|К выбору)$/ })).toBeInViewport({ ratio: .99 });
        await condition.getByRole('button', { name: /^(Далее|К выбору)$/ }).click();
        pages++;
      }
      expect(pages).toBeLessThanOrEqual(2);
      const card = page.getByTestId('scene-question');
      const world = (await page.locator('[data-scene-world]').boundingBox())!;
      expect(world.x + world.width).toBeLessThanOrEqual((await card.boundingBox())!.x + 1);
      const image = card.locator('[data-delivery-reminder] img');
      await expect(image).toHaveCSS('object-fit', 'cover');
      expect(await image.evaluate(n => parseFloat(getComputedStyle(n).borderRadius))).toBeGreaterThanOrEqual(6);
      for (const button of await card.locator('[data-choice-navigation] button').all()) {
        expect(await button.evaluate(n => parseFloat(getComputedStyle(n).borderTopWidth))).toBeGreaterThanOrEqual(1);
        expect(await button.evaluate(n => getComputedStyle(n).backgroundColor)).not.toBe('rgba(0, 0, 0, 0)');
      }
      if (scene !== 'lastmile') {
        const goals = card.locator('[data-compact-goals]');
        expect(await goals.evaluate(n => parseFloat(getComputedStyle(n).borderTopWidth))).toBeGreaterThanOrEqual(1);
        const rows = await goals.locator('li').evaluateAll(nodes => nodes.map(n => n.getBoundingClientRect().toJSON()));
        expect(rows.every(r => Math.abs(r.x - rows[0].x) < 1)).toBe(true);
        expect(rows[1].y).toBeGreaterThanOrEqual(rows[0].y + rows[0].height);
      }
      if (scene === 'inventory') {
        await expect(page.locator('[data-warehouse-label]')).toHaveCount(0);
        await expect(page.locator('[data-hotspot]')).toHaveCount(4);
      }
      const pin = page.locator(scene === 'crane' ? '[data-hotspot=rush]' : '[data-hotspot]').first();
      await pin.click();
      const inspection = page.locator('[data-choice-inspection]');
      expect(world.x + world.width).toBeLessThanOrEqual((await inspection.boundingBox())!.x + 1);
      await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ ratio: .99 });
      if (scene === 'crane') {
        const rows = await page.locator('[data-crane-facts] dl > div').evaluateAll(nodes => nodes.map(n => n.getBoundingClientRect().toJSON()));
        expect(rows[1].y).toBeGreaterThanOrEqual(rows[0].y + rows[0].height);
        expect(await page.locator('[data-crane-facts] dd').first().evaluate(n => parseFloat(getComputedStyle(n).fontSize))).toBeLessThanOrEqual(18);
        await expect(page.locator('[data-crane-facts] > p')).toHaveCSS('border-left-width', '0px');
      }
    }
  });
  test(`carrier result fits controls and reads in at most two pages at ${width}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await openCarrier(page, 'professional', 'khor', 'socks');
    await pickCarrier(page, 'express');
    await page.locator('[data-choice-confirm]').click();
    const footer = page.locator('[data-result-reader] footer');
    await expect(footer).toBeInViewport({ ratio: .99 });
    const pages = [];
    for (let i = 0; i < 20; i++) {
      const reading = page.locator('[data-result-reading]');
      await expect.poll(() => reading.evaluate(n => n.scrollHeight <= n.clientHeight + 1)).toBe(true);
      pages.push((await page.getByTestId('result-copy').innerText()).trim());
      const next = page.getByRole('button', { name: 'Читать дальше', exact: true });
      if (!await next.count()) break;
      for (let tab = 0; tab < 20 && !await next.evaluate(n => n === document.activeElement && n.matches(':focus-visible')); tab++) await page.keyboard.press('Tab');
      await expect(next).toBeFocused();
      await expect(next).toHaveCSS('text-decoration-line', 'none');
      await expect(next).toHaveCSS('filter', 'brightness(0.85)');
      await next.click();
    }
    expect(pages.length).toBeLessThanOrEqual(2);
    expect(pages.every(p => p.split(/\s+/u).length >= 5)).toBe(true);
  });
}
