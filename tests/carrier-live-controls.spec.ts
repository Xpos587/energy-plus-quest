import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`compact live carrier controls ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "arseniy", "boat");
    await page.goto("/?carrier-ui=speedometer");
    const choices = page.locator("[data-carrier-controls]");
    await expect(choices).toBeVisible();
    await expect(choices).not.toContainText("Синяя");
    for (const button of await choices.locator("button").all()) {
      const rect = await button.boundingBox();
      expect(rect?.width).toBeGreaterThanOrEqual(44);
      expect(rect?.height).toBeGreaterThanOrEqual(44);
    }
    for (const id of ["old", "near", "crew", "old4"]) {
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await expect(page.locator("[data-speedometer]")).toBeVisible();
      await expect(page.locator("[data-choice-inspection]")).not.toContainText(
        "км/ч",
      );
      await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
        ratio: 1,
      });
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator(`[data-scene-choice="${id}"]`)).toBeFocused();
    }
    await page.locator('[data-scene-choice="near"]').click();
    await page.waitForFunction(
      () =>
        document
          .querySelector("[data-speedometer]")
          ?.getAttribute("data-speedometer-value") !== "0",
    );
    const first = await page
      .locator("[data-speedometer]")
      .getAttribute("data-speedometer-value");
    await expect
      .poll(() =>
        page
          .locator("[data-speedometer]")
          .getAttribute("data-speedometer-value"),
      )
      .not.toBe(first);
    const outline = await page
      .locator('[data-carrier-choice="near"]')
      .evaluate((el) => getComputedStyle(el, "::after").content);
    expect(outline).toBe("none");
  });
}
