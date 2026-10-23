import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";

for (const carrier of ["old", "old4", "crew"] as const) {
  for (const [width, height] of [[390, 844], [1440, 900]] as const) {
    test(`boat too large for place 3 keeps ${carrier} cab at ${width}x${height}`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.goto(`/scenes.html?scene=compact&parcel=boat&recipient=alva&carrier=${carrier}`);
      const next = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
      for (let i = 0; i < 20 && await next.isVisible(); i++) await next.click();
      await page.locator('[data-scene-choice="place-3"]').click();
      const result = page.locator('[data-failure-art="boat-place-3"]');
      await expect(result).toBeVisible();
      const image = result.locator("img");
      await expect(image).toHaveJSProperty("complete", true);
      const currentSrc = await image.evaluate((node: HTMLImageElement) => node.currentSrc);
      expect(currentSrc).toContain(`boat-zone3-no-fit-${width > 900 ? "wide-" : ""}${carrier}-v50.webp`);
      expect(await image.evaluate((node: HTMLImageElement) => node.naturalWidth)).toBeGreaterThan(0);
      await mkdir(".tmp-work/compact-place3", { recursive: true });
      await page.screenshot({ path: `.tmp-work/compact-place3/boat-place-3-${carrier}-${width}.png` });
    });
  }
}
