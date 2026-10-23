import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [820, 1180],
  [844, 390],
  [1440, 900],
]) {
  test(`carrier labels stay concise at ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "alva", "boat");
    const choices = page.locator("[data-scene-choice]");
    await expect(choices).toHaveText([
      "Красная фура",
      "Синяя фура",
      "Зелёная фура",
      "Жёлтая фура",
      "Подобрать автоматически",
    ]);
    await page.locator('[data-scene-choice="crew"]').click();
    await expect(page.locator("[data-choice-inspection] h3")).toHaveText(
      "Зелёная фура",
    );
    await expect(page.locator('[data-carrier-inspection="crew"]')).toContainText(
      "Два водителя",
    );
    await expect(page.locator('[data-carrier-inspection="crew"]')).toContainText(
      "48 км/ч",
    );
  });
}
