import { expect, test } from "@playwright/test";

const sizes = [
  [320, 568],
  [390, 844],
  [820, 1180],
  [1440, 1000],
  [844, 390],
];
for (const [width, height] of sizes)
  test(`scene1 all five choices through results and next scene at ${width}x${height}`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width, height });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    for (const id of ["professional", "alva", "boat"])
      await page.locator(`[data-choice="${id}"]`).click();
    await expect(page.locator("[data-city-video]")).toBeVisible();
    await page.screenshot({
      path: info.outputPath(`live-${width}x${height}.png`),
    });
    for (const id of ["old", "near", "crew", "old4", "express"]) {
      const choice = page.locator(`[data-carrier-choice="${id}"]`);
      await choice.scrollIntoViewIfNeeded();
      const box = (await choice.boundingBox())!;
      expect(box.width).toBeGreaterThanOrEqual(44);
      expect(box.height).toBeGreaterThanOrEqual(44);
      await choice.click();
      await expect(
        page.locator(`[data-layout="result"][data-carrier="${id}"]`),
      ).toBeVisible();
      const image = page.locator(`[data-outcome-art="${id}"]:visible`);
      await expect
        .poll(() =>
          image.evaluate(
            (el: HTMLImageElement) => el.complete && el.naturalWidth > 0,
          ),
        )
        .toBe(true);
      await expect(image).toHaveAttribute(
        "src",
        new RegExp(`scene1-live/${id}-`),
      );
      expect(
        await page.locator("[data-score-key] strong").allTextContents(),
      ).toEqual(
        {
          old: ["0", "-3", "-3"],
          old4: ["0", "-3", "-3"],
          near: ["+1", "0", "-2"],
          crew: ["-3", "+3", "+4"],
          express: ["-1", "+5", "+5"],
        }[id],
      );
      await page
        .getByRole("button", { name: "К следующей сцене", exact: true })
        .click();
      await expect(page.locator('[data-scene="compact"]')).toBeVisible();
      await page.getByRole("button", { name: "Назад", exact: true }).click();
      await expect(page.locator("[data-carrier-choice]")).toHaveCount(5);
    }
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    expect(errors).toEqual([]);
  });
