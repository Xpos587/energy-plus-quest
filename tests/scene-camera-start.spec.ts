import { expect, test } from "@playwright/test";

// Lastmile opens on the helicopter; its framing is covered in scene-usability.spec.ts.
for (const scene of ["carrier", "inventory", "crane"]) {
  test(`${scene} starts at the left and highlights only the pan hint`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width: 390, height: 844 });
    if (scene === "carrier") {
      await page.goto("/");
      for (const id of ["professional", "alva", "camera"])
        await page.locator(`[data-choice="${id}"]`).click();
    } else await page.goto(`/scenes.html?scene=${scene}&parcel=camera`);
    const viewport = page.locator("[data-pan-viewport]");
    await expect(viewport).toBeVisible();
    await expect.poll(() => viewport.evaluate((el) => el.scrollLeft)).toBe(0);
    const question = page.getByTestId("scene-question");
    await expect(question).toHaveCSS("opacity", "1");
    await page
      .getByRole("button", { name: "Закрыть условие", exact: true })
      .click();
    const hint = page.getByRole("status").filter({ hasText: "Листайте сцену" });
    await expect(hint).toBeVisible();
    await expect(hint).toHaveCSS("opacity", "1");
    await expect(question).toHaveCSS("opacity", "0.28");
    await expect
      .poll(() => viewport.evaluate((el) => el.scrollLeft))
      .toBeGreaterThan(0);
    await page.screenshot({ path: info.outputPath(`${scene}-tutorial.png`) });
    await page.getByRole("button", { name: "Условие", exact: true }).click();
    await expect(hint).toHaveCount(0);
    await expect(question).toHaveCSS("opacity", "1");
  });
}
