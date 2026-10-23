import { expect, test } from "@playwright/test";

const outcomes = [
  ["compact", "place-2"],
  ["inventory", "alphabet"],
  ["crane", "rush"],
] as const;

for (const [width, height] of [[624, 794], [390, 844], [320, 568]]) {
  for (const [scene, choice] of outcomes) {
    test(`${scene} boat ${choice} result stays still at ${width}x${height}`, async ({ page }, info) => {
      await page.setViewportSize({ width, height });
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
      const briefing = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
      await expect(briefing.or(page.locator('[data-briefing-inline="true"]'))).toBeVisible();
      for (let index = 0; index < 30 && await briefing.isVisible(); index++) await briefing.click();
      await page.locator(`[data-scene-choice="${choice}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-result-reading]")).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      const samples = await page.evaluate(async () => {
        const reader = document.querySelector<HTMLElement>("[data-result-reader]")!;
        const panel = reader.closest<HTMLElement>("[data-sheet-panel]")!;
        const reading = reader.querySelector<HTMLElement>("[data-result-reading]")!;
        const samples = [];
        for (let frame = 0; frame < 90; frame++) {
          await new Promise(requestAnimationFrame);
          if (frame >= 30) samples.push({
            top: panel.getBoundingClientRect().top,
            height: reading.getBoundingClientRect().height,
            density: reader.dataset.resultDensity,
            text: reading.textContent,
            overflow: reading.firstElementChild!.getBoundingClientRect().height - reading.clientHeight,
          });
        }
        return samples;
      });
      const positions = samples.map(sample => sample.top);
      console.log(JSON.stringify({ scene, choice, width, height, minTop: Math.min(...positions), maxTop: Math.max(...positions), densities: [...new Set(samples.map(sample => sample.density))] }));
      expect(Math.max(...positions) - Math.min(...positions)).toBeLessThanOrEqual(1);
      expect(new Set(samples.map(sample => sample.text)).size).toBe(1);
      expect(Math.max(...samples.map(sample => sample.overflow))).toBeLessThanOrEqual(1);
      if (scene === "compact" && width === 624) {
        const images = page.locator('[data-layout="result"] img');
        for (const image of await images.all()) await image.evaluate(async (element: HTMLImageElement) => element.decode());
        await page.screenshot({ path: info.outputPath("compact-boat-place-2-stable.png") });
      }
    });
  }
}
