import { expect, test } from "@playwright/test";
import { carrierFacts, mapCarrierIds } from "../src/game/carrierFacts";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [620, 768],
  [624, 794],
  [835, 974],
  [844, 390],
  [1440, 900],
]) {
  test(`inspect and compare trucks before committing at ${width}x${height}`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width, height });
    await openCarrier(page, "professional", "alva", "boat");
    await expect(page.locator("[data-map-controls]")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "К выбору подарка", exact: true })).toBeInViewport({ ratio: 1 });
    await expect(page.getByRole("button", { name: "Подробнее о задаче", exact: true })).toHaveCount(0);
    const surface = page.locator("[data-map-surface]");
    const poster = surface.locator("[data-city-plate]");
    await expect(surface).toHaveAttribute("data-motion-reason", "ready");
    const overviewPlate = (await poster.getAttribute("data-city-plate"))!;
    for (const id of [...mapCarrierIds, "express"] as const) {
      await pickCarrier(page, id);
      await expect(
        page.locator(`[data-carrier-inspection="${id}"]`),
      ).toBeVisible();
      for (const fact of await page
        .locator(`[data-carrier-inspection="${id}"] dl > div`)
        .all()) {
        await expect(fact.locator("dt")).toBeInViewport({ ratio: 1 });
        await expect(fact.locator("dd")).toBeInViewport({ ratio: 1 });
      }
      await expect(page.locator('[data-layout="result"]')).toHaveCount(0);
      await page.screenshot({ path: info.outputPath(`${id}-inspection.png`) });
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator(`[data-carrier-inspection="${id}"]`)).toHaveCount(0);
      // Wait for the overview artwork, not the departing inspection's still-ready atlas.
      await expect(poster).toHaveAttribute("data-city-plate", overviewPlate);
      await expect(surface).toHaveAttribute("data-motion-reason", "ready");
      if (id !== "express") await expect(page.locator(`[data-carrier-choice="${id}"]`)).toBeFocused();
    }
    await pickCarrier(page, "crew");
    await expect(page.locator('[data-carrier-inspection="crew"] img')).toHaveCount(0);
    await expect(page.locator('[data-camera-inspection="true"] [data-map-viewport]')).toBeVisible();
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="crew"]'),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth + 1,
      ),
    ).toBe(true);
  });
}

test("short carrier outcome fills the available reading area at 620x768", async ({ page }) => {
  await page.setViewportSize({ width: 620, height: 768 });
  await openCarrier(page, "professional", "alva", "boat");
  await pickCarrier(page, "near");
  await page.locator('[data-choice-confirm]').click();
  const reading = page.locator('[data-result-reading]');
  await expect(reading).toContainText('водитель оказался очень неторопливым');
  await expect(page.getByRole('button', { name: 'Дальше: погрузка', exact: true })).toBeInViewport({ ratio: 1 });
  expect(await reading.evaluate(el => el.firstElementChild!.getBoundingClientRect().height - el.clientHeight)).toBeLessThanOrEqual(1);
});

test("city truck inspection shows qualitative pace and the model year", async ({ page }) => {
  await openCarrier(page, "professional", "alva", "boat");
  await expect(page.locator("[data-map-surface]")).toHaveAttribute("data-motion-reason", "ready");
  await pickCarrier(page, "near");
  const inspection = page.locator('[data-carrier-inspection="near"]');
  await expect(inspection).toContainText("Очень медленно");
  await expect(inspection).toContainText(String(carrierFacts.near.buildYear));
});

test("paused poster targets remain reachable below the mobile header by keyboard", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "boat");
  await expect(page.locator("[data-map-surface]")).toHaveAttribute("data-motion-reason", "reduced-motion");
  for (const id of mapCarrierIds) {
    const target = page.locator(`[data-carrier-choice="${id}"]`);
    await target.focus();
    await expect(target).toBeFocused();
    // The Express badge can sit above the truck body. Its painted dial must
    // still be reachable, without clicking through the Express badge.
    await expect
      .poll(() =>
        target.locator("span").evaluate((dial) => {
          const box = dial.getBoundingClientRect();
          const hit = document.elementFromPoint(box.left + Math.min(22, box.width / 2), box.y + box.height / 2);
          return hit?.closest("[data-carrier-choice]") === dial.parentElement;
        }),
      )
      .toBe(true);
    await target.press("Enter");
    await expect(
      page.locator(`[data-carrier-inspection="${id}"]`),
    ).toBeVisible();
    await page.locator("[data-choice-cancel]").click();
    await expect(target).toBeFocused();
  }
});
