import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [624, 794],
  [390, 844],
  [320, 568],
]) {
  for (const [scene, choice] of [
    ["carrier", "express"],
    ["compact", "place-1"],
    ["inventory", "alphabet"],
    ["crane", "rush"],
    ["lastmile", "helicopter"],
  ]) {
    test(`${scene} portrait result uses available narrative space at ${width}x${height}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height });
      if (scene === "carrier") {
        await openCarrier(page, "professional", "alva", "boat");
        await pickCarrier(page, "express");
      } else {
        await page.goto(
          `/scenes.html?scene=${scene}&parcel=boat&recipient=alva`,
        );
        const briefing = page.getByRole("button", {
          name: /^(Далее|К выбору|К сцене)$/,
        });
        await expect(briefing.or(page.locator('[data-briefing-inline="true"]'))).toBeVisible();
        for (let index = 0; index < 30 && (await briefing.isVisible()); index++)
          await briefing.click();
        await page.locator(`[${["crane", "compact", "lastmile"].includes(scene) ? "data-hotspot" : "data-scene-choice"}="${choice}"]`).click();
      }
      // Inventory and Last mile open the result straight from the choice.
      if (["carrier", "crane", "compact"].includes(scene))
        await page.locator("[data-choice-confirm]").click();
      const reading = page.locator("[data-result-reading]");
      await expect(reading).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      let count = 0;
      for (;;) {
        await expect
          .poll(async () =>
            reading.evaluate((el) => {
              // The sheet hugs its copy and sits flush with the frame bottom.
              const frame = el
                .closest('[data-layout="result"]')!
                .getBoundingClientRect();
              const panel = el
                .closest("[data-sheet-panel]")!
                .getBoundingClientRect();
              return Math.abs(frame.bottom - panel.bottom);
            }),
          )
          .toBeLessThan(2);
        const geometry = await reading.evaluate((el) => ({
          textHeight: el.firstElementChild!.getBoundingClientRect().height,
          height: el.getBoundingClientRect().height,
          footerBottom: el
            .closest("[data-sheet-panel]")!
            .querySelector("footer")!
            .getBoundingClientRect().bottom,
        }));
        expect(geometry.textHeight).toBeLessThanOrEqual(geometry.height + 1);
        expect(geometry.footerBottom).toBeLessThanOrEqual(height - 10);
        if (width === 624 && scene === "carrier")
          expect(height - geometry.footerBottom).toBeLessThanOrEqual(24);
        for (const button of await page
          .locator("[data-result-reader] footer button")
          .all())
          await expect(button).toBeInViewport({ ratio: 1 });
        const next = page.getByRole("button", {
          name: "Читать дальше",
          exact: true,
        });
        count++;
        if (!(await next.isVisible())) break;
        expect(count).toBeLessThan(20);
        await next.click();
      }
    });
  }
}
