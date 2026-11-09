import { test, expect } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";
for (const [scene, id] of [
  ["carrier", "express"],
  ["compact", "place-1"],
  ["inventory", "wms"],
  ["crane", "rush"],
  ["lastmile", "rover"],
]) {
  test(`${scene} result controls share a symmetric grid`, async ({
    page,
  }, info) => {
    if (scene === "carrier") {
      await openCarrier(page, "professional", "arseniy", "socks");
      await pickCarrier(page, id as "express");
    } else {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      const intro = page.getByRole("region", {
        name: "Условие задания",
        exact: true,
      });
      for (let n = 0; n < 30 && (await intro.isVisible()); n++)
        await intro
          .getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ })
          .click();
      await page.locator(`[data-hotspot="${id}"]`).click();
    }
    // Last mile opens the result straight from the vehicle; the others confirm on a card.
    if (scene !== "lastmile") await page.locator("[data-choice-confirm]").click();
    const footer = page.locator("[data-result-reader] footer");
    await expect(footer).toBeVisible({ timeout: 15_000 }); // the quay plays the crane consequence first
    await page.evaluate(() => document.fonts.ready);
    for (let p = 0; p < 20; p++) {
      const buttons = footer.locator("button");
      await expect(buttons).toHaveCount(2);
      const a = (await buttons.nth(0).boundingBox())!,
        b = (await buttons.nth(1).boundingBox())!;
      const score = (await footer.locator("[data-score-delta]").boundingBox())!;
      expect(Math.abs(a.width - b.width)).toBeLessThan(1);
      expect(Math.abs(a.height - b.height)).toBeLessThan(1);
      // One row, or one column in a narrow rail.
      expect(Math.min(Math.abs(a.y - b.y), Math.abs(a.x - b.x))).toBeLessThan(1);
      expect(Math.abs(a.height - score.height)).toBeLessThan(1);
      for (const button of await buttons.all()) {
        await expect(button).toBeInViewport({ ratio: 1 });
        expect(
          await button.evaluate((el) => el.scrollHeight <= el.clientHeight + 1),
        ).toBe(true);
      }
      const cells = await footer.locator("[data-score-key]").evaluateAll((es) =>
        es.map((e) => {
          const r = e.getBoundingClientRect();
          return { w: r.width, y: r.y, h: r.height };
        }),
      );
      expect(
        Math.max(...cells.map((c) => c.w)) - Math.min(...cells.map((c) => c.w)),
      ).toBeLessThan(1);
      if (p === 0)
        await page.screenshot({
          path: `.tmp-work/footer-grid/${scene}-${info.project.name}.png`,
        });
      const next = page.getByRole("button", {
        name: "Читать дальше",
        exact: true,
      });
      if (!(await next.isVisible())) break;
      await next.click();
    }
  });
}
