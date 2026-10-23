import { expect, test } from "@playwright/test";
import { parcelNames } from "../../src/scenes/names";
import { scenarioParagraph } from "../helpers/scenario-copy";

test("loading conditions and exact question remain available with choices", async ({
  page,
}) => {
  for (const parcel of ["boat", "camera", "socks"] as const) {
    await page.goto(`/scenes.html?scene=compact&parcel=${parcel}`);
    const gift = parcelNames[parcel];
    const questionText = scenarioParagraph("4027C712")
      .replace("(название подарка)", gift.accusative)
      .replace("он(а)", gift.pronoun)
      .replace("доехал(а)", gift.arrived);
    const question = page.getByTestId("scene-question");
    await expect(
      question.locator("p").filter({ hasText: questionText }),
    ).toBeVisible();
    await expect(question).toContainText("Перевозчик найден");
    for (const [index, condition] of [
      /тяжёлыми ящиками.*без креплений/,
      /хрупкой посудой.*красные стропы/,
      /ниша.*за тремя коробками/,
      /передней стенки.*подушки/,
    ].entries()) {
      const control = page.locator(`[data-hotspot="place-${index + 1}"]`);
      await expect(control).toHaveAccessibleName(condition);
      const bounds = await control.boundingBox();
      if (!bounds) throw new Error("Missing loading control bounds");
      expect(bounds.width).toBeGreaterThanOrEqual(44);
      expect(bounds.height).toBeGreaterThanOrEqual(44);
    }
    await expect(
      page.getByRole("group", { name: "Варианты выбора" }),
    ).toBeVisible();
  }
});
