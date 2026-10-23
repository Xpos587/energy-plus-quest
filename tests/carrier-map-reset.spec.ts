import { expect, test } from '@playwright/test';
import { openCarrier } from './helpers/open-preparation';

test('a changed carrier map has a visible reset back to its initial view', async ({ page }, info) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await openCarrier(page, 'professional', 'alva', 'boat');
  const map = page.locator('[data-map-viewport]');
  const surface = page.locator('[data-map-surface]');
  const reset = page.getByRole('button', { name: 'Вернуть карту', exact: true });
  await expect(reset).toHaveCount(0);
  const initial = await surface.getAttribute('style');
  await map.focus();
  await page.keyboard.press('+');
  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('ArrowDown');
  await expect(reset).toBeVisible();
  await expect(reset).toBeInViewport({ ratio: 1 });
  await page.screenshot({ path: `.tmp-work/carrier-reset-${info.project.name}.png` });
  if (info.project.use.hasTouch) await reset.tap();
  else await reset.click();
  await expect(map).toHaveAttribute('data-map-scale', '1');
  await expect(surface).toHaveAttribute('style', initial!);
  await expect(reset).toHaveCount(0);
  await expect(page.locator('[data-choice-inspection], [data-layout="result"]')).toHaveCount(0);
});
