import { expect, test } from "@playwright/test";

for (const viewport of [{ width: 320, height: 568 }, { width: 390, height: 844 }, { width: 1440, height: 900 }]) {
  test(`selection questions stay with their answers at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    if (await page.locator("[data-intro-next]").count()) {
      await page.locator("[data-intro-next]").click();
    }
    await page.locator("[data-intro-start]").click();
    const panel = page.locator("[data-selection-panel]");
    for (const [title, choice, count] of [
      ["Вы:", "student", 2],
      ["Выберите своего получателя:", "alva", 3],
      ["Выберите посылку:", "camera", 3],
    ] as const) {
      await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
      await expect(panel.getByRole("heading", { name: title, exact: true })).toBeInViewport({ ratio: 1 });
      await expect(panel.locator("[data-choice]")).toHaveCount(count);
      for (const button of await panel.locator("[data-choice]").all()) {
        await expect(button).toBeInViewport({ ratio: 1 });
      }
      if (choice !== "camera") await panel.locator(`[data-choice="${choice}"]`).click();
    }
    await panel.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(panel.getByRole("heading", { name: "Выберите своего получателя:", exact: true })).toBeVisible();
    await panel.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(panel.getByRole("heading", { name: "Вы:", exact: true })).toBeVisible();
  });
}
