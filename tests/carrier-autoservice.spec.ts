import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  for (const id of ["old", "old4"]) {
    test(`${id} uses the autoservice result and retains the story at ${width}x${height}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height });
      await openCarrier(page, "professional", "arseniy", "boat");
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      const image = page.locator(`[data-outcome-art="${id}"]`);
      await expect
        .poll(() =>
          image.evaluate(
            (i: HTMLImageElement) => i.complete && i.naturalWidth > 0,
          ),
        )
        .toBe(true);
      const expected =
        width === 1440
          ? `${id}-wide-v8`
          : width === 390
            ? id === "old"
              ? "old-portrait-v2"
              : "old4-portrait-v1"
            : `${id}-v5`;
      expect(
        await image.evaluate((i: HTMLImageElement) => i.currentSrc),
      ).toContain(expected);
      await expect(page.locator("[data-result-reading]")).toContainText(
        "В связи с поломкой ее задержали на сервисе",
      );
      for (const [key, score] of [
        ["energy", "0"],
        ["empathy", "-3"],
        ["efficiency", "-3"],
      ])
        await expect(
          page.locator(`[data-score-key="${key}"] strong`),
        ).toHaveText(score);
      await expect(
        page.getByRole("button", { name: "Назад к машинам", exact: true }),
      ).toBeInViewport({ ratio: 1 });
      await expect(
        page.getByRole("button", { name: "К следующей сцене", exact: true }),
      ).toBeInViewport({ ratio: 1 });
    });
  }
}
