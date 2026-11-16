import { expect, test } from "@playwright/test";
import { parcelNames } from "../../src/scenes/names";
import { scenarioParagraph } from "../helpers/scenario-copy";

test("loading goals, current question and named targets remain available with choices", async ({
  page,
}) => {
  test.setTimeout(90_000);
  for (const parcel of ["boat", "camera", "socks"] as const) {
    await page.goto(`/scenes.html?scene=compact&parcel=${parcel}`);
    const gift = parcelNames[parcel];
    const questionText = scenarioParagraph("4027C712")
      .replace("(название подарка)", gift.accusative)
      .replace("он(а)", gift.pronoun)
      .replace("доехал(а)", gift.arrived)
      .replace(" в целости и сохранности, а погрузка прошла быстро и легко", " в целости");
    const intro = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
    for (let n = 0; n < 20 && (await intro.isVisible()); n++) await intro.click();
    const question = page.getByTestId("scene-question");
    await expect(
      question.locator("p").filter({ hasText: questionText }),
    ).toBeVisible();
    for (const goal of ["Погрузить быстро", "Довезти целым", "Не занять лишнее"])
      await expect(page.getByRole("list", { name: "Что важно" }).getByText(goal, { exact: true })).toBeVisible();
    for (const [index, condition] of [
      /ящиками с гирями.*Креплений нет/,
      /посудой.*стропы/,
      /ниша над коробками/,
      /передней стенки.*подушками/,
    ].entries()) {
      const control = page.locator(`[data-hotspot="place-${index + 1}"]`);
      await expect(control).toHaveAccessibleName(condition);
      const bounds = await control.boundingBox();
      if (!bounds) throw new Error("Missing loading control bounds");
      expect(bounds.width).toBeGreaterThanOrEqual(44);
      expect(bounds.height).toBeGreaterThanOrEqual(44);
    }
  }
});
