import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [749, 794],
  [734, 709],
  [1440, 900],
  [1873, 1985],
]) {
  test(`truck preview keeps the carrier map on screen at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "alva", "socks");
    const map = page.locator('[data-mode="live"]');
    const before = await map.boundingBox();
    await expect(page.getByRole("button", { name: "Подробнее о задаче" })).toHaveCount(0);
    await pickCarrier(page, "express");
    await expect(page.locator('[data-choice-inspection="express"]')).toBeVisible();
    const during = await map.boundingBox();
    expect(during?.x).toBe(before?.x);
    expect(during?.y).toBe(before?.y);
    expect(during?.width).toBe(before?.width);
    expect(during?.height).toBeGreaterThan(100);
    expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBeLessThanOrEqual(height + 1);
    await page.locator('[data-choice-cancel]').click();
    await expect(page.locator('[data-choice-inspection]')).toHaveCount(0);
    await expect(map).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollHeight)).toBeLessThanOrEqual(height + 1);
  });
}
