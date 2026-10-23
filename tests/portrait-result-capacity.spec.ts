import { expect, test } from "@playwright/test";

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
        await page.goto("/");
        for (const id of ["professional", "alva", "boat"])
          await page.locator(`[data-choice="${id}"]`).click();
      } else
        await page.goto(
          `/scenes.html?scene=${scene}&parcel=boat&recipient=alva`,
        );
      const briefing = page.getByRole("button", {
        name: /^(Далее|К выбору|К сцене)$/,
      });
      await expect(briefing.or(page.locator('[data-briefing-inline="true"]'))).toBeVisible();
      for (let index = 0; index < 30 && (await briefing.isVisible()); index++)
        await briefing.click();
      if (scene === "carrier")
        await page
          .getByRole("button", { name: "Поручить выбор Express", exact: true })
          .click();
      else await page.locator(`[data-scene-choice="${choice}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      const reading = page.locator("[data-result-reading]");
      await expect(reading).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      let count = 0;
      for (;;) {
        await expect
          .poll(async () =>
            reading.evaluate((el) => {
              const frame = el
                .closest('[data-layout="result"]')!
                .getBoundingClientRect();
              const panel = el
                .closest("[data-sheet-panel]")!
                .getBoundingClientRect();
              const box = el.getBoundingClientRect();
              return Math.abs(
                parseFloat(getComputedStyle(el).maxHeight) -
                  (frame.bottom - box.top - (panel.bottom - box.bottom)),
              );
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
        if (width === 624 && scene === "carrier") {
          expect(height - geometry.footerBottom).toBeLessThanOrEqual(24);
          await expect(reading).toContainText("раньше запланированного!");
        }
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
