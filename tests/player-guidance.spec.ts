import { test, expect } from '@playwright/test';

test('start explains the mission before the first selection', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Доставьте подарок через пять этапов пути.')).toBeVisible();
  await expect(page.locator('[data-choice="student"]')).toBeInViewport();
  await page.locator('[data-choice="student"]').click();
  await expect(page.locator('[data-choice="alva"]')).toBeVisible();
});

test('barge result shows indicators directly and allows revising the choice', async ({ page }) => {
  await page.goto('/scenes.html?scene=crane&parcel=boat&recipient=alva');
  const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
  await page.locator('[data-scene-choice="petr"]').click();
  await page.locator('[data-choice-confirm]').click();
  await expect(page.getByText('Что означают показатели?')).toHaveCount(0);
  await expect(page.locator('[data-score-key="efficiency"]')).toContainText('-3');
  const back = page.getByRole('button', { name: 'Изменить выбор', exact: true });
  await expect(back).toBeInViewport({ ratio: 1 });
  await back.click();
  await expect(page.locator('[data-scene-choice]')).toHaveCount(4);
});

test('barge story pages fit and continue to lastmile only after the final page', async ({ page }) => {
  await page.goto('/scenes.html?scene=crane&parcel=boat&recipient=alva');
  const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
  await page.locator('[data-scene-choice="remote"]').click();
  await page.locator('[data-choice-confirm]').click();
  let pages = 0;
  for (; pages < 30; pages++) {
    const reading = page.locator('[data-result-reading]');
    await expect.poll(() => reading.evaluate(e => e.scrollHeight <= e.clientHeight + 1 && e.scrollWidth <= e.clientWidth + 1)).toBe(true);
    const forward = page.getByRole('button', { name: 'Читать дальше', exact: true });
    if (!await forward.count()) break;
    await expect(page.getByRole('button', { name: 'Продолжить', exact: true })).toHaveCount(0);
    await expect(forward).toBeInViewport({ ratio: 1 });
    await forward.click();
  }
  expect(pages).toBeLessThan(30);
  const next = page.getByRole('button', { name: 'Продолжить', exact: true });
  await expect(next).toBeInViewport({ ratio: 1 });
  await next.click();
  await expect(page.locator('[data-scene="lastmile"]')).toBeVisible();
});

test('desktop result stays fixed when the wheel is over the illustration', async ({ page }) => {
  test.skip(page.viewportSize()!.width < 901);
  await page.goto('/scenes.html?scene=crane&parcel=boat&recipient=alva');
  const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
  await page.locator('[data-scene-choice="petr"]').click();
  await page.locator('[data-choice-confirm]').click();
  await page.locator('[data-outcome-scene="crane"] img').evaluate((image: HTMLImageElement) => image.decode());
  await page.mouse.move(600, 350);
  await page.mouse.wheel(0, 650);
  await expect.poll(() => page.locator('[data-layout="result"]').evaluate(element => element.scrollTop)).toBe(0);
  await expect.poll(() => page.locator('[data-layout="result"]').evaluate(element => element.scrollHeight <= element.clientHeight + 1)).toBe(true);
});
