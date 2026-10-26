import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [1440, 900],
  [1920, 1080],
  [844, 390],
  [390, 844],
  [320, 568],
]) {
  test(`carrier choice panel groups question choices and navigation ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openCarrier(page, "professional", "arseniy", "boat");
    const panel = page.locator('[data-testid="scene-question"]'),
      map = page.locator("[data-map-viewport]");
    const p = await panel.boundingBox(),
      m = await map.boundingBox();
    if (!p || !m) throw Error("layout missing");
    if (width >= 701) {
      expect(p.width).toBeLessThanOrEqual(420);
      expect(p.height).toBeLessThanOrEqual(360);
      expect(m.width).toBe(width);
      expect(m.height).toBeGreaterThanOrEqual(height - 100);
    } else {
      expect(p.width).toBe(width);
      expect(p.y + p.height).toBeCloseTo(height, 0);
      expect(m.y + m.height).toBeCloseTo(p.y, 0);
    }
    for (const button of await panel.getByRole("button").all()) {
      await expect(button).toBeInViewport({ ratio: 1 });
      const box = await button.boundingBox();
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(box?.height).toBeGreaterThanOrEqual(44);
    }
    for (const [id, year] of [
      ["old", "2011"],
      ["near", "2021"],
      ["crew", "2024"],
      ["old4", "2013"],
    ]) {
      const button = page.locator(`[data-scene-choice="${id}"]`);
      await button.click();
      await expect(page.locator("[data-speedometer]")).toBeVisible();
      await expect(page.locator("[data-choice-inspection]")).toContainText(
        year,
      );
      if (id === "crew")
        await expect(page.locator("[data-choice-inspection]")).toContainText(
          "Два водителя",
        );
      await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
        ratio: 1,
      });
      await page.locator("[data-choice-cancel]").click();
      await expect(button).toBeFocused();
    }
    await pickCarrier(page, "express");
    await expect(page.locator("[data-choice-inspection]")).toContainText(
      "Express",
    );
    await page.locator("[data-choice-cancel]").click();
    await page.getByRole("button", { name: "О задаче", exact: true }).click();
    await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
      "data-reading",
      "true",
    );
  });
}
