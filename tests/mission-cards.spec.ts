import { expect, test } from '@playwright/test';

for (const [width, height] of [[1440, 900], [390, 844], [320, 568], [568, 320]]) {
  test(`mission cards keep goals readable and grouped at ${width}x${height}`, async ({ page }, info) => {
    test.setTimeout(90000);
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    for (const scene of ['compact', 'inventory', 'crane']) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      await page.evaluate(() => document.fonts.ready);
      const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
      if (await condition.isVisible()) {
        // Teach the situation first; criteria belong beside the actual decision.
        await expect(condition.locator('[data-compact-goals]')).toHaveCount(0);
        const reading = condition.getByTestId('scene-intro');
        await expect(reading).toHaveCSS('font-weight', '400');
        expect(await reading.evaluate(node => parseFloat(getComputedStyle(node).fontSize))).toBeGreaterThanOrEqual(17);
        await page.screenshot({ path: info.outputPath(`${scene}-${width}-condition.png`) });
        for (let i = 0; i < 40 && await condition.isVisible(); i++) {
          await expect.poll(() => reading.evaluate(node => node.scrollHeight <= node.clientHeight + 1)).toBe(true);
          const next = condition.getByRole('button', { name: /^(Далее|К выбору)$/ });
          await expect(next).toBeInViewport({ ratio: 0.99 });
          expect((await next.boundingBox())!.height).toBeGreaterThanOrEqual(44);
          await next.click();
        }
        await expect(condition).toHaveCount(0);
      }
      const card = page.getByTestId('scene-question');
      const goals = card.getByRole('list', { name: 'Что важно' });
      await expect(goals.locator('li')).toHaveCount(3);
      // Icons and words must read as a single row, not three detached towers.
      expect(await goals.locator('li').evaluateAll(items => items.every(item => {
        const icon = item.querySelector('svg')!.getBoundingClientRect();
        const label = item.querySelector('span')!;
        const text = label.getBoundingClientRect();
        return icon.right <= text.left - 4 &&
          Math.abs(icon.top + icon.height / 2 - text.top - text.height / 2) < 2 &&
          parseFloat(getComputedStyle(label).fontSize) >= 14 &&
          label.scrollWidth <= label.clientWidth + 1 && label.scrollHeight <= label.clientHeight + 1;
      }))).toBe(true);
      expect(await card.evaluate(node => node.scrollWidth <= node.clientWidth + 1)).toBe(true);
      await expect(goals.locator('button, a, [tabindex]')).toHaveCount(0);
      await page.locator('[data-scene-world] img').evaluateAll(images => Promise.all(images.map(img => (img as HTMLImageElement).decode())));
      await page.screenshot({ path: info.outputPath(`${scene}-${width}-choice.png`) });
    }
  });
}

for (const width of [390, 320]) {
  test(`condition remains readable and complete with 200% text at ${width}px`, async ({ page }) => {
    test.setTimeout(90000);
    await page.setViewportSize({ width, height: width === 320 ? 568 : 844 });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    for (const scene of ['inventory', 'crane']) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      await page.evaluate(() => document.fonts.ready);
      const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
      await condition.evaluate(root => {
        const nodes = [root, ...root.querySelectorAll('*')].filter(node => node instanceof HTMLElement);
        const sizes = nodes.map(node => parseFloat(getComputedStyle(node).fontSize));
        nodes.forEach((node, index) => node.style.fontSize = `${sizes[index] * 2}px`);
        window.dispatchEvent(new Event('resize'));
      });
      const seen = new Set<string>();
      for (let i = 0; i < 40 && await condition.isVisible(); i++) {
        const reading = condition.getByTestId('scene-intro');
        await reading.scrollIntoViewIfNeeded();
        await expect(reading).toBeInViewport();
        await expect.poll(() => reading.evaluate(node => node.scrollHeight <= node.clientHeight + 1)).toBe(true);
        const text = (await reading.textContent())!;
        expect(text.trim().length).toBeGreaterThan(0);
        expect(seen.has(text)).toBe(false);
        seen.add(text);
        const next = condition.getByRole('button', { name: /^(Далее|К выбору)$/ });
        await next.scrollIntoViewIfNeeded();
        await expect(next).toBeInViewport({ ratio: 0.99 });
        expect(await condition.evaluate(node => node.scrollWidth <= node.clientWidth + 1)).toBe(true);
        await next.click();
      }
      await expect(condition).toHaveCount(0);
    }
  });
}
