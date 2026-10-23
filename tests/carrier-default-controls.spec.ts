import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`default carrier choices use Lucide Truck without color labels ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openCarrier(page, "professional", "arseniy", "boat");
    expect(new URL(page.url()).searchParams.has("carrier-ui")).toBe(false);
    const controls = page.locator("[data-carrier-controls]");
    await expect(controls).toBeVisible();
    await expect(controls.locator("svg.lucide-truck")).toHaveCount(4);
    if (width >= 900) {
      const box = await controls.boundingBox();
      expect(box?.width).toBeLessThan(650);
    }
    for (const [id, label] of [
      ["old", "Красная фура"],
      ["near", "Синяя фура"],
      ["crew", "Зелёная фура"],
      ["old4", "Жёлтая фура"],
    ]) {
      const button = controls.getByRole("button", { name: label, exact: true });
      await expect(button).toHaveText("");
      const rect = await button.boundingBox();
      expect(rect?.width).toBeGreaterThanOrEqual(44);
      expect(rect?.height).toBeGreaterThanOrEqual(44);
      await button.click();
      await expect(page.locator("[data-speedometer]")).toBeVisible();
      await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
        ratio: 1,
      });
      await page.locator("[data-choice-cancel]").click();
      await expect(button).toBeFocused();
      await button.click();
      await page.locator("[data-choice-confirm]").click();
      await expect(
        page.locator(`[data-layout="result"][data-carrier="${id}"]`),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Назад к машинам", exact: true })
        .click();
    }
    await controls
      .getByRole("button", { name: "Подобрать автоматически", exact: true })
      .click();
    await expect(page.locator("[data-speedometer]")).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="express"]'),
    ).toBeVisible();
  });
}
