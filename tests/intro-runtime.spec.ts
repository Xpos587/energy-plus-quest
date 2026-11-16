import { expect, test } from "@playwright/test";

for (const reducedMotion of ["reduce", "no-preference"] as const) {
  test(`landscape introduction keeps navigation clear (${reducedMotion})`, async ({ page }, info) => {
    await page.setViewportSize({ width: 844, height: 390 });
    await page.emulateMedia({ reducedMotion });
    await page.goto("/");
    await page.locator("[data-intro-enter]").click();
    await page.evaluate(() => document.fonts.ready);
    const cards = page.locator('[aria-label="Этапы доставки в игре"]');
    const next = page.locator("[data-intro-next]");
    await expect(next).toBeInViewport({ ratio: 1 });
    const cardBox = (await cards.boundingBox())!;
    const nextBox = (await next.boundingBox())!;
    expect(cardBox.y + cardBox.height).toBeLessThanOrEqual(nextBox.y);
    await page.screenshot({ path: info.outputPath("intro-landscape.png") });
    await next.click();
    await page.locator("[data-intro-start]").click();
    await expect(page.locator('[data-choice="professional"]')).toBeVisible();
  });
}

test("portrait introduction does not download hidden scene illustrations", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator("[data-intro-enter]").click();
  const scenes = page.locator("img[data-stage]");
  await expect(scenes).toHaveCount(5);
  await page.waitForTimeout(500);
  // Hidden illustrations should not compete with the visible timeline and cover.
  expect(await scenes.evaluateAll(images => images.filter(image => (image as HTMLImageElement).currentSrc))).toHaveLength(0);
  await page.setViewportSize({ width: 844, height: 390 });
  await expect.poll(() => scenes.evaluateAll(images => images.filter(image => {
    const img = image as HTMLImageElement;
    return img.complete && img.naturalWidth > 0;
  }).length)).toBe(5);
});
