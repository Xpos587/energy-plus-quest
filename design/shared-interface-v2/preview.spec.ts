import { expect, test } from '@playwright/test';
const url = '/design/shared-interface-v2/index.html';
test('real choice descriptions, cancellation and confirmation stay separate', async ({ page }) => {
  await page.goto(url);
  await expect(page.getByRole('heading', { name: 'Погрузка на баржу' })).toBeVisible();
  await page.locator('[data-hotspot="rush"]').click();
  await expect(page.getByTestId('inspection')).toBeVisible();
  await expect(page.getByTestId('question')).toBeVisible();
  await expect(page.getByTestId('result')).toHaveCount(0);
  await page.getByRole('button', { name: 'К вариантам' }).click();
  await expect(page.getByTestId('inspection')).toHaveCount(0);
  await page.locator('[data-hotspot="rush"]').click();
  await page.getByRole('button', { name: 'Выбрать', exact: true }).click();
  await expect(page.getByTestId('result')).toBeVisible();
});
for (const width of [320, 390]) test(`all real scenes pan on a ${width}px phone`, async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width, height: width === 320 ? 568 : 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:4184' + url);
  for (const name of ['Перевозчик', 'Укладка', 'Склад', 'Баржа', 'Последняя миля']) {
    await page.getByRole('button', { name: 'Маршрут' }).click();
    await page.getByRole('button', { name, exact: true }).click();
    const pan = page.locator('[data-pan-viewport]');
    await expect.poll(() => pan.evaluate(el => el.scrollWidth - el.clientWidth)).toBeGreaterThan(50);
    const before = await pan.evaluate(el => { el.scrollLeft = 0; return el.scrollLeft; });
    const session = await context.newCDPSession(page);
    const y = width === 320 ? 310 : 410;
    await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: width - 30, y }] });
    for (let x = width - 50; x > 25; x -= 25) await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x, y }] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await expect.poll(() => pan.evaluate(el => el.scrollLeft)).toBeGreaterThan(before + 20);
    await expect(page.getByTestId('question')).toBeVisible();
    expect(await page.evaluate(() => document.body.scrollWidth)).toBe(width);
    await session.detach();
  }
  await page.screenshot({ path: `/tmp/energy-shared-ui-v2-${width}.png` });
  await context.close();
});
