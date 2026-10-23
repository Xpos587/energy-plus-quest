import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`root live gauge follows playback and pause ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "arseniy", "boat");
    expect(new URL(page.url()).search).toBe("");
    for (const [id, year] of [
      ["old", "2011"],
      ["near", "2021"],
      ["crew", "2024"],
      ["old4", "2013"],
    ]) {
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await expect(page.locator("[data-speedometer]")).toBeVisible();
      await expect(page.locator("[data-choice-inspection]")).toContainText(
        "Год выпуска",
      );
      await expect(page.locator("[data-choice-inspection]")).toContainText(
        year,
      );
      if (id === "crew")
        await expect(page.locator("[data-choice-inspection]")).toContainText(
          "Два водителя",
        );
      else
        await expect(
          page.locator("[data-choice-inspection]"),
        ).not.toContainText("водителя");
      await expect(page.locator("[data-choice-inspection]")).toContainText(
        "Темп движения",
      );
      await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
        ratio: 1,
      });
      await page.locator("[data-choice-cancel]").click();
    }
    await page.locator('[data-scene-choice="near"]').click();
    const gauge = page.locator("[data-speedometer]");
    await expect
      .poll(async () =>
        Number(await gauge.getAttribute("data-speedometer-value")),
      )
      .toBeGreaterThan(0);
    const initial = await gauge.getAttribute("data-speedometer-value");
    await expect
      .poll(() => gauge.getAttribute("data-speedometer-value"))
      .not.toBe(initial);
    await page
      .locator("[data-city-video]")
      .evaluate((v: HTMLVideoElement) => v.pause());
    await expect(gauge).toHaveAttribute("data-speedometer-value", "0.000");
    await page
      .locator("[data-city-video]")
      .evaluate((v: HTMLVideoElement) => v.play());
    await expect
      .poll(async () =>
        Number(await gauge.getAttribute("data-speedometer-value")),
      )
      .toBeGreaterThan(0);
    await page.locator("[data-choice-cancel]").click();
    await page.locator('[data-scene-choice="express"]').click();
    await expect(gauge).toHaveCount(0);
  });
}
