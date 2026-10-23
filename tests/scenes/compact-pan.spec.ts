import { expect, test } from "@playwright/test";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
  { width: 768, height: 1024 },
  { width: 1440, height: 900 },
]) {
  test(`entire truck and all four loading places fit ${viewport.width}×${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/scenes.html?scene=compact&parcel=camera");
    await page.getByRole("button", { name: "К сцене", exact: true }).click();
    const stage = page.locator('[data-world-scene="compact"]');
    const plane = stage.locator('[data-world-plane]');
    await expect(plane).toBeVisible();
    const stageBox = await stage.boundingBox();
    const planeBox = await plane.boundingBox();
    if (!stageBox || !planeBox) throw new Error("Missing truck bounds");
    expect(planeBox.x).toBeGreaterThanOrEqual(stageBox.x - 1);
    expect(planeBox.x + planeBox.width).toBeLessThanOrEqual(stageBox.x + stageBox.width + 1);
    expect(planeBox.y).toBeGreaterThanOrEqual(stageBox.y - 1);
    expect(planeBox.y + planeBox.height).toBeLessThanOrEqual(stageBox.y + stageBox.height + 1);
    expect(await stage.evaluate((n) => n.scrollWidth <= n.clientWidth + 1)).toBe(true);
    await expect(stage.locator("figcaption")).toHaveCount(0);
    for (const n of [1, 2, 3, 4]) {
      const button = stage.locator(`[data-hotspot="place-${n}"]`);
      const box = await button.boundingBox();
      if (!box) throw new Error(`Missing loading place ${n}`);
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
      expect(box.x).toBeGreaterThanOrEqual(stageBox.x - 1);
      expect(box.x + box.width).toBeLessThanOrEqual(stageBox.x + stageBox.width + 1);
      await button.focus();
      expect(await button.evaluate((node) => {
        const b = node.getBoundingClientRect();
        return node.contains(document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2));
      })).toBe(true);
    }
    await stage.locator('[data-hotspot="place-4"]').press("Enter");
    await expect(page.locator('[data-choice-inspection="compact:place-4"]')).toBeVisible();
  });
}
