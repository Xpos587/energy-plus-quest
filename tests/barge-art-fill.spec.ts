import { expect, test } from "@playwright/test";
// Scene 4 art fills its block on choice, card and result: no sky-coloured bands at any screen.
test.use({ contextOptions: { reducedMotion: "reduce" } });

const covered = (root: Element, selector: string) => {
  const a = root.getBoundingClientRect();
  const b = root.querySelector(selector)!.getBoundingClientRect();
  return { left: b.left - a.left, top: b.top - a.top, right: b.right - a.right, bottom: b.bottom - a.bottom };
};
const fills = (box: { left: number; top: number; right: number; bottom: number }) => {
  expect(box.left).toBeLessThanOrEqual(0.5);
  expect(box.top).toBeLessThanOrEqual(0.5);
  expect(box.right).toBeGreaterThanOrEqual(-0.5);
  expect(box.bottom).toBeGreaterThanOrEqual(-0.5);
};

for (const [width, height] of [[1440, 900], [1280, 800], [1024, 768], [844, 390], [440, 956], [390, 844], [360, 640], [320, 568]]) {
  test(`barge art fills its block at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=crane&parcel=camera&recipient=alva");
    const stage = page.locator("[data-barge-art]");
    fills(await stage.evaluate(covered, ":scope > div"));
    await page.locator('[data-hotspot="remote"]').click();
    await page.waitForTimeout(600); // camera move to the open card
    fills(await stage.evaluate(covered, ":scope > div"));
    await page.locator("[data-choice-confirm]").click();
    const figure = page.locator("[data-scene-consequence]");
    await expect(figure.locator("img")).toHaveCSS("object-fit", "cover");
    fills(await figure.evaluate(covered, "img"));
    // Phone result rows are also landscape: the tall still cuts off the crane above the reader.
    const rail = width > 1000 && height > 700;
    const portrait = width <= 1000 && height >= 701 && height > width;
    if (portrait) await expect(figure.locator("img")).toHaveCSS("object-position", "50% 80%");
    await expect.poll(() => figure.locator("img").evaluate((i: HTMLImageElement) => i.currentSrc)).toMatch(rail || portrait ? /outcome-remote-rail\.webp/ : /outcome-remote\.webp/);
  });
}
