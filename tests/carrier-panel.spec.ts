import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 844, height: 390 },
  { width: 1440, height: 900 },
]) {
  test(`carrier decision and result remain usable at ${viewport.width}x${viewport.height}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await openCarrier(page, "professional", "alva", "boat");

    const task = page.getByRole("region", { name: "Задание сцены" });
    await expect(task).toContainText("Выберите грузовик, который лучше всего справится с такой задачей.");
    await expect(task.locator("[data-scene-choice]")).toHaveCount(5);
    await expect(page.locator("[data-map-viewport]")).toBeVisible();
    await expect(task).not.toContainText("Красная фура — старая");

    await pickCarrier(page, "near");
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await expect(page.locator("[data-choice-confirm]")).toBeVisible();
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="near"]'),
    ).toBeVisible();
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await expect(page.locator('[data-score-key="energy"] strong')).toHaveText(
      "+1",
    );
    await expect(
      page.locator('[data-score-key="efficiency"] strong'),
    ).toHaveText("-2");
    await expect(page.locator('[data-outcome-art="near"]')).toBeVisible();
    await page.getByRole("button", { name: "Назад к машинам" }).click();
    await expect(task.locator("[data-scene-choice]")).toHaveCount(5);
  });
}

test("automatic carrier route explains Express before confirmation", async ({
  page,
}) => {
  await openCarrier(page);
  await pickCarrier(page, "express");
  const inspection = page.locator("[data-choice-inspection]");
  await expect(inspection).toContainText("Express");
  await expect(inspection).toContainText(/подбира|перевоз/i);
  await page.locator("[data-choice-cancel]").click();
  await expect(inspection).toHaveCount(0);
  await expect(page.locator('[data-scene-choice="express"]')).toBeFocused();
});
