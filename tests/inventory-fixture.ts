import type { Page } from '@playwright/test';

/** Read the existing scene condition before testing a warehouse decision. */
export async function openInventory(page: Page, parcel = 'boat') {
  await page.goto(`${process.env.INVENTORY_TEST_URL ?? ''}/scenes.html?scene=inventory&parcel=${parcel}&recipient=alva`);
  const choice = page.locator('[data-scene-choice="wms"]');
  for (let i = 0; i < 12 && !await choice.isVisible(); i++) {
    const next = page.getByRole('button', { name: /^(К выбору|Далее)$/ });
    if (await next.isVisible()) await next.click();
    else await page.waitForTimeout(100);
  }
  await choice.waitFor({ state: 'visible' });
  await page.locator('[data-world-plane] picture img').evaluate((img: HTMLImageElement) => img.decode());
}
