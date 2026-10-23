import { test, expect } from '@playwright/test';

const captures = process.env.BARGE_CAPTURE_DIR ?? '.tmp-work/barge-style-after';

for (const parcel of ['camera', 'socks', 'boat']) {
  for (const id of ['rush', 'wait', 'petr', 'remote']) {
    test(`${parcel} ${id}: choice, consequence, revise, continue`, async ({ page }, info) => {
      await page.goto(`/scenes.html?scene=crane&parcel=${parcel}&recipient=alva`);
      const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
      for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
      await page.locator('img').evaluateAll(async images => {
        await Promise.all(images.map(image => (image as HTMLImageElement).decode().catch(() => {})));
      });
      if (id === 'rush') await page.screenshot({ path: `${captures}/${info.project.name}-${parcel}-choice.png` });
      const choice = page.locator(`[data-scene-choice="${id}"]`);
      await choice.click();
      await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ ratio: 1 });
      await page.locator('[data-choice-confirm]').click();
      await expect(page.locator('[data-result-reader]')).toBeVisible();
      await page.locator('[data-outcome-scene="crane"] img').evaluate(async (image: HTMLImageElement) => image.decode());
      const art = page.locator('[data-outcome-scene="crane"] img');
      const version = id === 'petr' ? (parcel === 'boat' ? 'v12' : 'v8') : (id === 'remote' && parcel !== 'boat') ? 'v3' : id === 'remote' || (id === 'rush' && parcel !== 'boat') ? 'v2' : 'v1';
      await expect(art).toHaveAttribute('src', new RegExp(`${id}-${parcel}-${version}`));
      await page.screenshot({ path: `${captures}/${info.project.name}-${parcel}-${id}.png` });
      const scrollingPetr = id === 'petr' && page.viewportSize()!.width > 900 && page.viewportSize()!.height > 500;
      if (scrollingPetr) {
        const dimensions = await art.evaluate((img: HTMLImageElement) => ({ rendered: img.clientWidth / img.clientHeight, source: img.naturalWidth / img.naturalHeight }));
        expect(Math.abs(dimensions.rendered - dimensions.source)).toBeLessThan(0.01);
        await page.getByRole('button', { name: 'Изменить выбор', exact: true }).scrollIntoViewIfNeeded();
        await page.screenshot({ path: `${captures}/${info.project.name}-${parcel}-${id}-reading.png` });
      }
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).scrollIntoViewIfNeeded();
      await expect(page.getByRole('button', { name: 'Изменить выбор', exact: true })).toBeInViewport({ ratio: 1 });
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      await expect(page.locator('[data-result-reader]')).toHaveCount(0);
      await choice.click();
      await page.locator('[data-choice-confirm]').click();
      for (let n = 0; n < 30; n++) {
        const more = page.getByRole('button', { name: 'Читать дальше', exact: true });
        if (!await more.isVisible()) break;
        if (scrollingPetr) await more.scrollIntoViewIfNeeded();
        await expect(more).toBeInViewport({ ratio: 1 });
        await more.click();
      }
      const proceed = page.getByRole('button', { name: 'Продолжить', exact: true });
      await proceed.scrollIntoViewIfNeeded();
      await expect(proceed).toBeInViewport({ ratio: 1 });
      await proceed.click();
      await expect(page.locator('[data-scene="lastmile"]')).toBeVisible();
      await expect(page.locator('[data-scene-briefing][data-reading="true"]')).toBeVisible();
      await page.screenshot({ path: `${captures}/${info.project.name}-${parcel}-${id}-lastmile.png` });
    });
  }
}
