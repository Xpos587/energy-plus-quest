import type { Page } from '@playwright/test';

/** Read the existing scene condition before testing a warehouse decision. */
export async function openInventory(page: Page, parcel = 'boat') {
  await page.goto(`${process.env.INVENTORY_TEST_URL ?? ''}/scenes.html?scene=inventory&parcel=${parcel}&recipient=alva`);
  const choice = page.locator('[data-hotspot="wms"]');
  const next = page.getByRole('button', { name: /^(К выбору|Далее)$/ });
  for (let i = 0; i < 12; i++) {
    // Wait for actual navigation, not a 1.2-second rendering budget under CI load.
    await page.locator('[data-hotspot="wms"]:visible').or(next).first().waitFor({ state: 'visible' });
    if (await choice.isVisible()) break;
    await next.click();
  }
  await choice.waitFor({ state: 'visible' });
  await page.locator('[data-world-plane] picture img').evaluate((img: HTMLImageElement) => img.decode());
}
