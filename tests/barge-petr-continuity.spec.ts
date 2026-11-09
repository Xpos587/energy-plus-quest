import { expect, test } from "@playwright/test";
// The quay outcome animation is covered by barge-flow; here the result comes at once.
test.use({ contextOptions: { reducedMotion: "reduce" } });

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
      await page.locator('[data-hotspot="petr"]').click();
      await page.locator("[data-choice-confirm]").click();
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
      if (width <= 360 || height <= 600) {
        // Small screens: the whole outcome stays in one block that scrolls to its last line.
        await expect(r).toHaveCSS("overflow-y", "auto");
        await r.evaluate((e) => (e.scrollTop = e.scrollHeight));
        expect(
          await r.evaluate((e) => e.scrollTop + e.clientHeight >= e.scrollHeight - 1),
        ).toBe(true);
        await expect(copy.locator("span:not([hidden])").last()).toBeInViewport();
      } else
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
