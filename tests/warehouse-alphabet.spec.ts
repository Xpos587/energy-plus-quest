import { expect, test } from "@playwright/test";

for (const [parcel, letter] of [
  ["camera", "Ф"],
  ["socks", "Н"],
  ["boat", "Л"],
] as const) {
  test(`${parcel}: alphabet marker, sign and result refer to the same gift`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto(
      `/scenes.html?scene=inventory&parcel=${parcel}&recipient=alva`,
    );
    const image = page.locator("[data-world-plane] > picture img");
    await image.evaluate((element: HTMLImageElement) => element.decode());
    await expect(image).toHaveAttribute(
      "src",
      /inventory-barge-style-v6.webp$/,
    );
    await page.getByRole("button", { name: "Закрыть условие" }).click();
    await expect(
      page.locator(
        "[data-warehouse-annotations] text, [data-warehouse-annotations] rect",
      ),
    ).toHaveCount(0);
    const marker = page.locator('[data-hotspot="alphabet"]');
    await expect(marker).toHaveAttribute(
      "aria-label",
      new RegExp(`буква ${letter}`),
    );
    await marker.click();
    await expect(
      page.locator('[data-hotspot="alphabet"]'),
    ).toHaveAttribute("aria-pressed", "true");
    await expect(page.locator("[data-inspection-question]")).toHaveText(
      "Давайте решим, куда его разместить.",
    );
    await page.locator("[data-choice-confirm]").click();
    const result = page.locator("[data-scene-consequence] img");
    await result.evaluate((element: HTMLImageElement) => element.decode());
    await expect(result).toHaveAttribute(
      "src",
      new RegExp(`inventory-alphabet-${parcel}.webp$`),
    );
    await expect(result).toHaveAttribute("alt", new RegExp(`буквой ${letter}`));
  });
}
