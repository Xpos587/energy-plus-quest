import { expect, test } from "@playwright/test";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
])
  for (const parcel of ["boat", "camera", "socks"])
    test(`Petr keeps both consequences together ${width}x${height} ${parcel}`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height });
      await page.goto(
        `/scenes.html?scene=crane&parcel=${parcel}&recipient=khor`,
      );
      for (let n = 0; n < 40; n++) {
        const f = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
        if (!(await f.isVisible())) break;
        await f.click();
      }
      await page.locator('[data-scene-choice="petr"]').click();
      await expect(page.locator("[data-result]")).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Читать дальше", exact: true }),
      ).toHaveCount(0);
      const copy = page.getByTestId("result-copy");
      await expect(copy.locator("span:not([hidden])")).toHaveCount(2);
      expect(
        await copy.evaluate((e) => e.scrollHeight <= e.clientHeight + 1),
      ).toBe(true);
      const r = page.locator("[data-result-reading]");
      expect(
        await r.evaluate((e) => e.scrollHeight <= e.clientHeight + 1),
      ).toBe(true);
      for (const label of ["Изменить выбор", "Продолжить"])
        await expect(
          page.getByRole("button", { name: label, exact: true }),
        ).toBeInViewport({ ratio: 1 });
      expect(
        await page.evaluate(
          () => document.documentElement.scrollHeight <= innerHeight,
        ),
      ).toBe(true);
    });
