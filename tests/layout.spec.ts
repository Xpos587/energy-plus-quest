import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
  { width: 1440, height: 900 },
]) {
  test(`decision, result and next scene fit ${viewport.width}x${viewport.height}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await openCarrier(page, "professional", "khor", "boat");
    await page.evaluate(() => document.fonts.ready);
    const noHorizontalOverflow = async () =>
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth + 1,
        ),
      ).toBe(true);
    await noHorizontalOverflow();
    for (const choice of await page.locator("[data-scene-choice]").all()) {
      await choice.scrollIntoViewIfNeeded();
      await expect(choice).toBeInViewport({ ratio: 0.98 });
      expect((await choice.boundingBox())?.height).toBeGreaterThanOrEqual(44);
    }

    await page.locator('[data-scene-choice="crew"]').click();
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
      ratio: 0.95,
    });
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator('[data-layout="result"]')).toBeVisible();
    await noHorizontalOverflow();
    await expect(page.locator('[data-outcome-art="crew"]')).toBeVisible();
    await expect(page.locator("[data-score-key]")).toHaveCount(3);

    await page
      .getByRole("button", { name: "Загрузить подарок в фуру" })
      .click();
    await expect(page.locator('[data-scene="compact"]')).toBeVisible();
    await expect(page.getByTestId("scene-question")).toContainText("лодку");
    await noHorizontalOverflow();
  });
}

test("parcel and recipient names stay grammatical in the next decision", async ({
  page,
}) => {
  for (const [recipient, parcel, expected] of [
    ["alva", "camera", "фотоаппарат"],
    ["khor", "socks", "вязаные носки"],
    ["arseniy", "boat", "лодку"],
  ] as const) {
    await openCarrier(page, "professional", recipient, parcel);
    await page.locator('[data-scene-choice="crew"]').click();
    await page.locator("[data-choice-confirm]").click();
    await page
      .getByRole("button", { name: "Загрузить подарок в фуру" })
      .click();
    const question = page.getByTestId("scene-question");
    await expect(question).toContainText(expected);
    await expect(question).not.toContainText(
      /\{recipient\}|\{parcel\}|\(название подарка\)/,
    );
  }
});
