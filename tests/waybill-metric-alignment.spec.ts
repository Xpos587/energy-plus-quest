import { expect, test } from "@playwright/test";
import sharp from "sharp";

for (const [width, height] of [[390, 844], [1440, 900]]) {
  test(`waybill icons centre on label ink at ${width}×${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await page.locator("[data-intro-enter]").click();
    await page.locator("[data-intro-next]").click();
    await page.evaluate(() => document.fonts.ready);
    const headings = page.getByRole("list", { name: "Показатели" }).locator("strong");
    await expect(headings).toHaveCount(3);
    const { data, info } = await sharp(await page.screenshot({ scale: "css" })).removeAlpha().raw().toBuffer({ resolveWithObject: true });
    for (const heading of await headings.all()) {
      const { name, text, iconY } = await heading.evaluate(el => {
        const icon = el.querySelector("svg")!.getBoundingClientRect();
        const range = document.createRange();
        range.selectNodeContents(el.lastChild!);
        return { name: range.toString(), text: range.getBoundingClientRect().toJSON(), iconY: icon.y + icon.height / 2 };
      });
      expect(Math.abs(text.y + text.height / 2 - iconY), name).toBeLessThanOrEqual(1);
      // A Range includes the font's blank leading. Measure the painted letters on the white sheet.
      const inkRows = [];
      for (let y = Math.floor(text.top); y < Math.ceil(text.bottom); y++) {
        const start = (y * info.width + Math.floor(text.left)) * info.channels;
        const end = (y * info.width + Math.ceil(text.right)) * info.channels;
        if (data.subarray(start, end).some(channel => channel < 215)) inkRows.push(y);
      }
      expect(inkRows.length, name).toBeGreaterThan(0);
      expect(Math.abs((inkRows[0] + inkRows[inkRows.length - 1] + 1) / 2 - iconY), name).toBeLessThanOrEqual(1);
    }
  });
}
