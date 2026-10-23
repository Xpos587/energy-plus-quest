import { expect, type Page, test } from "@playwright/test";

async function carrier(page: Page) {
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await page
    .getByRole("button", { name: "Закрыть условие", exact: true })
    .click();
}
async function fits(page: Page) {
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  ).toBe(true);
  for (const selector of ["[data-choice-confirm]", "[data-choice-cancel]"]) {
    const button = page.locator(selector);
    await expect(button).toBeInViewport({ ratio: 1 });
    const b = await button.boundingBox();
    expect(b?.height).toBeGreaterThanOrEqual(44);
  }
}
test("inspect, cancel and confirm across all five scenes without premature outcomes", async ({
  page,
}, info) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await carrier(page);
  const choice = page.locator('[data-carrier-choice="crew"]');
  await choice.click();
  await expect(page.locator('[data-step="carrier"]')).toBeVisible();
  await expect(page.locator("[data-score-key]")).toHaveCount(0);
  await fits(page);
  await page.screenshot({ path: info.outputPath("carrier-inspection.png") });
  await page.locator("[data-choice-cancel]").click();
  await expect(choice).toBeFocused();
  await choice.click();
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-score-key]")).toHaveCount(3);
  await page
    .getByRole("button", { name: "К следующей сцене", exact: true })
    .click();
  for (const [index, [scene, id]] of [
    ["compact", "place-2"],
    ["inventory", "wms"],
    ["crane", "remote"],
    ["lastmile", "rover"],
  ].entries()) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await expect(page.getByTestId("scene-question")).toBeAttached();
    await page
      .getByRole("button", { name: "Закрыть условие", exact: true })
      .click();
    await expect(
      page.locator(
        `[data-scene="${scene}"] [data-choice-id]:not([data-hotspot])`,
      ),
    ).toHaveCount(scene === "compact" ? 1 : 0);
    const canvas = await page
      .locator(`[data-world-scene="${scene}"]`)
      .boundingBox();
    expect(canvas?.height).toBeGreaterThanOrEqual(
      (page.viewportSize()?.height ?? 0) - 1,
    );
    await page.screenshot({ path: info.outputPath(`${scene}-overview.png`) });
    await page.locator(`[data-choice-id="${id}"]`).click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await fits(page);
    await page.locator("[data-choice-inspection] h3").press("Escape");
    await expect(page.locator(`[data-choice-id="${id}"]`)).toBeFocused();
    await page.locator(`[data-choice-id="${id}"]`).click();
    await page.screenshot({ path: info.outputPath(`${scene}-inspection.png`) });
    await page.locator("[data-choice-confirm]").click();
    await expect(page.getByTestId("result-copy")).toBeVisible();
    if (scene !== "compact") {
      await expect
        .poll(() =>
          page
            .locator("[data-scene-consequence] > img")
            .evaluate(
              (image: HTMLImageElement) =>
                image.complete && image.naturalWidth > 0,
            ),
        )
        .toBe(true);
    }
    await page.screenshot({ path: info.outputPath(`${scene}-result.png`) });
    const paragraphs = page.getByTestId("result-copy").locator("p");
    const paragraphCount = await paragraphs.count();
    for (let paragraph = 0; paragraph < paragraphCount; paragraph++) {
      await expect(paragraphs.nth(paragraph)).toBeVisible();
      if (paragraph < paragraphCount - 1)
        await page
          .getByRole("button", { name: "Следующий абзац", exact: true })
          .click();
    }
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await page
      .getByRole("button", {
        name: index === 3 ? "Завершить" : "Продолжить",
        exact: true,
      })
      .click();
  }
  await expect(
    page.getByRole("button", { name: "Завершено", exact: true }),
  ).toBeDisabled();
  expect(errors).toEqual([]);
});

test("briefing can be reread and a pending answer survives resizing without committing", async ({
  page,
}) => {
  await carrier(page);
  await page.getByRole("button", { name: "Условие", exact: true }).click();
  await expect(page.getByTestId("scene-intro")).toContainText("Доставить");
  await page.getByRole("button", { name: "Далее", exact: true }).click();
  await page.getByRole("button", { name: "К сцене", exact: true }).click();
  await page.locator('[data-carrier-choice="express"]').click();
  await page.setViewportSize({ width: 844, height: 390 });
  await fits(page);
  await expect(page.locator('[data-step="carrier"]')).toBeVisible();
  await page.setViewportSize({ width: 320, height: 568 });
  await fits(page);
  await page.locator("[data-choice-inspection] h3").press("Escape");
  await expect(page.locator('[data-carrier-choice="express"]')).toBeFocused();
  await expect(page.getByTestId("scene-question")).toBeVisible();
});
