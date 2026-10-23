import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

test("automatic inspection uses the manual desktop card shell without zooming the map", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await openCarrier(page, "professional", "arseniy", "boat");
  await page.locator('[data-scene-choice="near"]').click();
  const manual = await page.locator("[data-choice-inspection]").boundingBox();
  await page.locator("[data-choice-cancel]").click();
  await expect(page.locator("[data-map-viewport]")).toHaveAttribute(
    "data-map-scale",
    "1",
  );
  const scale = "1";
  await page.locator('[data-scene-choice="express"]').click();
  const automatic = await page
    .locator("[data-choice-inspection]")
    .boundingBox();
  expect(automatic?.width).toBeCloseTo(manual?.width, 0);
  expect(automatic?.x).toBeCloseTo(manual?.x, 0);
  await expect(page.locator("[data-map-viewport]")).toHaveAttribute(
    "data-map-scale",
    scale,
  );
  await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
    ratio: 1,
  });
  await page.locator("[data-choice-confirm]").click();
  const icon = page.locator("[data-score-delta] svg").first();
  expect((await icon.boundingBox())?.width).toBeGreaterThanOrEqual(22);
});

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  for (const id of ["old", "near", "crew", "old4", "express"]) {
    test(`${id} cancel, result, return and Compact preserve choices at ${width}x${height}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height });
      await openCarrier(page, "professional", "arseniy", "boat");
      await page.locator(`[data-scene-choice="${id}"]`).click();
      for (const attr of ["data-choice-cancel", "data-choice-confirm"])
        await expect(page.locator(`[${attr}]`)).toBeInViewport({ ratio: 1 });
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator(`[data-scene-choice="${id}"]`)).toBeFocused();
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      await expect(
        page.locator(`[data-layout="result"][data-carrier="${id}"]`),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Назад к машинам", exact: true })
        .click();
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      const next = page.getByRole("button", {
        name: "Читать дальше",
        exact: true,
      });
      for (let n = 0; (await next.count()) && n < 6; n++) {
        await expect(next).toBeInViewport({ ratio: 1 });
        await next.click();
      }
      await expect(
        page.getByRole("button", { name: "К следующей сцене", exact: true }),
      ).toBeInViewport({ ratio: 1 });
      await page
        .getByRole("button", { name: "К следующей сцене", exact: true })
        .click();
      await expect(page.locator('[data-scene="compact"]')).toBeVisible();
      const state = await page.evaluate(
        () =>
          JSON.parse(localStorage.getItem("energy-quest-save-v1") ?? "{}")
            .state,
      );
      expect(state).toMatchObject({
        profile: "professional",
        recipient: "arseniy",
        parcel: "boat",
        carrier: id,
      });
    });
  }
}

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`yellow result loads the revised resource at ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "arseniy", "boat");
    await page.locator('[data-scene-choice="old4"]').click();
    await page.locator("[data-choice-confirm]").click();
    const art = page.locator('[data-outcome-art="old4"]');
    await expect
      .poll(() =>
        art.evaluate(
          (el: HTMLImageElement) => el.complete && el.naturalWidth > 0,
        ),
      )
      .toBe(true);
    expect(
      await art.evaluate((el: HTMLImageElement) => el.currentSrc),
    ).toContain(
      width === 1440
        ? "old4-wide-v8"
        : width === 390
          ? "old4-portrait-v1"
          : "old4-v5",
    );
    if (width < 600) await expect(art).toHaveCSS("object-position", "15% 50%");
  });
}
