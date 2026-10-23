import { expect, test } from "@playwright/test";

test("shared scene prototype keeps the task visible and commits only after confirmation", async ({ page }) => {
  await page.goto("/review/shared-interface-2026-09-28/index.html");
  await expect(page.getByRole("heading", { name: "Погрузка на баржу" })).toBeVisible();
  await expect(page.getByTestId("task-question")).toBeVisible();
  await page.getByRole("button", { name: "Позвать Ивана" }).click();
  await expect(page.getByTestId("choice-preview")).toBeVisible();
  await expect(page.getByTestId("task-question")).toBeVisible();
  await expect(page.getByTestId("committed-result")).toBeHidden();
  await page.getByRole("button", { name: "Вернуться к вариантам" }).click();
  await expect(page.getByTestId("choice-preview")).toBeHidden();
  await page.getByRole("button", { name: "Позвать Ивана" }).click();
  await page.getByRole("button", { name: "Подтвердить выбор" }).click();
  await expect(page.getByTestId("committed-result")).toContainText("Позвать Ивана");
});

test("the same controls work for all five scenes and on a small phone", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.goto("/review/shared-interface-2026-09-28/index.html");
  for (const scene of ["Перевозчик", "Укладка", "Склад", "Баржа", "Последняя миля"]) {
    await page.getByRole("button", { name: scene, exact: true }).click();
    await expect(page.getByTestId("task-question")).toBeVisible();
    await expect(page.locator(".hotspot").first()).toBeVisible();
    await expect.poll(() => page.locator("#scene-art").evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
    await expect(page.locator("body")).toHaveJSProperty("scrollWidth", 320);
  }
});
