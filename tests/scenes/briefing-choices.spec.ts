import { expect, test } from "@playwright/test";

for (const scene of ["carrier", "compact", "inventory", "crane", "lastmile"]) {
  test(`${scene}: choices appear only after reading the condition`, async ({
    page,
  }) => {
    await page.goto(
      scene === "carrier"
        ? "/"
        : `/scenes.html?scene=${scene}&parcel=camera&recipient=alva`,
    );
    if (scene === "carrier") {
      for (const id of ["professional", "alva", "camera"])
        await page.locator(`[data-choice="${id}"]`).click();
    }
    const overlays = page.locator(
      '[data-interaction="inspect-confirm"] :is([data-hotspot], [data-carrier-choice], [data-callout], [data-callout-target], [data-loading-zone])',
    );
    expect(await overlays.count()).toBeGreaterThan(0);
    const read = async () => {
      for (let step = 0; step < 30; step++) {
        if (!(await page.getByTestId("scene-intro").isVisible())) break;
        for (const overlay of await overlays.all())
          await expect(overlay).toBeHidden();
        await page.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
      }
      await expect(page.getByTestId("scene-intro")).toHaveCount(0);
    };
    await expect(page.getByTestId("scene-intro")).toBeVisible();
    await page.locator("[data-world-plane] picture img").evaluateAll((images) =>
      Promise.all(images.map((image) => (image as HTMLImageElement).decode())),
    );
    await page.screenshot({
      path: `.tmp-work/briefing-${scene}-${test.info().project.name}.png`,
    });
    await read();
    const marker = page
      .locator(
        scene === "carrier" ? '[data-carrier-choice="near"]' : "[data-hotspot]",
      )
      .first();
    await expect(marker).toBeVisible();
    await page.getByRole("button", { name: "Условие", exact: true }).click();
    await expect(page.getByTestId("scene-intro")).toBeVisible();
    await read();
    await marker.scrollIntoViewIfNeeded();
    await marker.click();
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await page.locator("[data-choice-cancel]").click();
    await page.locator("[data-pan-viewport]").dispatchEvent("scene-pan-start");
    await page.screenshot({
      path: `.tmp-work/compact-labels-${scene}-${test.info().project.name}.png`,
    });
  });
}

test("compact labels keep a generous touch target outside their visible surface", async ({
  page,
}) => {
  await page.goto("/scenes.html?scene=crane&parcel=camera&recipient=alva");
  for (let step = 0; step < 30; step++) {
    if (!(await page.getByTestId("scene-intro").isVisible())) break;
    await page.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  }
  await page.locator("[data-pan-viewport]").dispatchEvent("scene-pan-start");
  const marker = page.locator('[data-hotspot="rush"]');
  await marker.scrollIntoViewIfNeeded();
  const rect = (await marker.boundingBox())!;
  expect(rect.height).toBeLessThanOrEqual(34);
  await page.mouse.click(rect.x + rect.width / 2, rect.y - 4);
  await expect(
    page.locator('[data-choice-inspection="crane:rush"]'),
  ).toBeVisible();
});
