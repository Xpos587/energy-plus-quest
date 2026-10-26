import { expect, test } from "@playwright/test";
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
    for (const id of ["old", "near", "crew", "old4"]) {
      const button = page.locator(`[data-scene-choice="${id}"]`);
      await expect(button).toBeInViewport({ ratio: 1 });
      const rect = await button.boundingBox();
      expect(rect?.width).toBeGreaterThanOrEqual(44);
      expect(rect?.height).toBeGreaterThanOrEqual(44);
      await button.click();
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
      await expect(
        page.locator(`[data-carrier-inspection="${id}"]`),
      ).toHaveCount(0);
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

test("all truck inspections survive unavailable motion video", async ({
  page,
}) => {
  await page.route("**/scene1-live/**/*.mp4", (route) => route.abort());
  await openCarrier(page, "professional", "alva", "boat");
  await expect(page.locator("[data-map-viewport]")).toBeVisible();
  await pickCarrier(page, "near");
  await expect(page.locator('[data-carrier-inspection="near"]')).toContainText("17 км/ч");
  await expect(page.locator('[data-carrier-inspection="near"]')).toContainText(
    "2021",
  );
});

test("paused poster targets remain reachable below the mobile header by keyboard", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "boat");
  for (const id of ["near", "old", "crew", "old4"]) {
    const target = page.locator(`[data-carrier-choice="${id}"]`);
    await target.focus();
    await expect
      .poll(() =>
        target.evaluate((element) => {
          const box = element.getBoundingClientRect();
          const hit = document.elementFromPoint(
            box.x + box.width / 2,
            box.y + box.height / 2,
          );
          return hit === element || element.contains(hit);
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
