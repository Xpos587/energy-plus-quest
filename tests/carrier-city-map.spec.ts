import { expect, test } from "@playwright/test";
import { carrierFacts, mapCarrierIds } from "../src/game/carrierFacts";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

// The painted city is the only way to choose: four driving rigs and the
// Express call pill under the warehouse doors. No video, numbers or buttons.
for (const [width, height] of [
  [390, 844],
  [844, 390],
  [1440, 900],
] as const) {
  test(`city map offers every carrier at ${width}x${height}`, async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "arseniy", "boat");

    const plate = page.locator("[data-city-plate]");
    await expect(plate).toBeVisible();
    await expect(plate).toHaveAttribute(
      "data-city-plate",
      width >= height * 1.3 ? "wide" : "tall",
    );
    await expect
      .poll(() =>
        plate.evaluate((image: HTMLImageElement) => image.naturalWidth),
      )
      .toBeGreaterThan(0);
    await expect(page.locator("video")).toHaveCount(0);
    await expect(page.locator("[data-carrier-tap-hint]")).toContainText(
      "Нажмите на фуру",
    );

    const rigs = page.locator("[data-carrier-choice]:not([data-map-autopick])");
    await expect(rigs).toHaveCount(4);
    for (const id of mapCarrierIds) {
      const rig = page.locator(`[data-carrier-choice="${id}"]`);
      await expect(rig).toHaveAccessibleName(
        `Рассмотреть: ${carrierFacts[id].label}`,
      );
      await expect(rig).toHaveText("");
      const box = await rig.boundingBox();
      expect(
        Math.min(box?.width ?? 0, box?.height ?? 0),
      ).toBeGreaterThanOrEqual(36);
    }
    const express = page.locator("[data-map-autopick]");
    await expect(express).toBeInViewport();
    const call = await express.boundingBox();
    expect(call?.height).toBeGreaterThanOrEqual(24);

    // A rig: qualitative pace on the dial, no km/h, focus returns on cancel.
    await pickCarrier(page, "near");
    const card = page.locator("[data-choice-inspection]");
    await expect(card.locator("h3")).toHaveText(carrierFacts.near.label);
    await expect(page.locator("[data-speedometer]")).toBeVisible();
    await expect(card).toContainText(carrierFacts.near.pace);
    await expect(card).not.toContainText("км/ч");
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport();
    await page.locator("[data-choice-cancel]").click();
    await expect(card).toHaveCount(0);
    await expect(page.locator('[data-carrier-choice="near"]')).toBeFocused();

    // Express explains itself before confirmation, then leads to loading.
    await pickCarrier(page, "express");
    await expect(card.locator("h3")).toHaveText("Express подберёт фуру");
    await expect(card).toContainText("Как такси, только для грузов");
    await expect(page.locator("[data-speedometer]")).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="express"]'),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /Дальше: погрузка|Читать дальше/ }),
    ).toBeVisible();
    expect(errors).toEqual([]);
  });
}

test("reduced motion keeps the rigs still and choosable", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "boat");
  const rig = page.locator('[data-carrier-choice="crew"]');
  const first = await rig.boundingBox();
  await page.waitForTimeout(800);
  expect(await rig.boundingBox()).toEqual(first);
  await rig.click();
  await expect(page.locator('[data-choice-inspection="crew"]')).toBeVisible();
});
