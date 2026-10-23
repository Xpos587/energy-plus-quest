import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 375, height: 667 },
  { width: 360, height: 640 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
  { width: 1440, height: 900 },
]) {
  test(`carrier labels and map fit at ${viewport.width}x${viewport.height}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await openCarrier(page, "professional", "alva", "boat");
    await page.evaluate(() => document.fonts.ready);

    const choices = page.locator("[data-scene-choice]");
    await expect(choices).toHaveCount(5);
    const labels = await choices.evaluateAll((elements) =>
      elements.map((element) => element.textContent?.trim() ?? ""),
    );
    expect(labels).toEqual([
      "Красная фура",
      "Синяя фура",
      "Зелёная фура",
      "Жёлтая фура",
      "Подобрать автоматически",
    ]);
    for (const choice of await choices.all()) {
      await expect(choice).toBeInViewport({ ratio: 0.98 });
      const box = await choice.boundingBox();
      expect(box?.height).toBeGreaterThanOrEqual(44);
      expect(box?.width).toBeGreaterThanOrEqual(44);
      expect(
        await choice.evaluate(
          (element) => element.scrollWidth <= element.clientWidth + 1,
        ),
      ).toBe(true);
    }
    await expect(
      page.getByRole("region", { name: "Карта доступных перевозчиков" }),
    ).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(viewport.width + 1);
    expect(
      await page.evaluate(() => document.documentElement.scrollHeight),
    ).toBeLessThanOrEqual(viewport.height + 1);
    if (viewport.width === 320 || viewport.width === 390 || viewport.width === 1440) {
      await page.screenshot({ path: `/tmp/quest-carrier-current-${viewport.width}x${viewport.height}.png` });
    }
  });
}

test("map marker opens carrier inspection and cancel restores the overview", async ({
  page,
}) => {
  await openCarrier(page);
  const map = page.locator("[data-map-viewport]");
  await expect(map).toHaveAttribute("data-map-scale", "1");
  const marker = page.locator('[data-carrier-choice="crew"]');
  await expect(marker).toHaveAccessibleName(/зелёная фура/i);
  await marker.click();
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expect
    .poll(async () => Number(await map.getAttribute("data-map-scale")))
    .toBeCloseTo(2.4, 2);
  await page.locator("[data-choice-cancel]").click();
  await expect(page.locator("[data-choice-inspection]")).toHaveCount(0);
  await expect
    .poll(async () => Number(await map.getAttribute("data-map-scale")))
    .toBeCloseTo(1, 2);
  await expect(page.locator('[data-scene-choice="crew"]')).toBeVisible();
});
