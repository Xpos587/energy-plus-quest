import { test, expect } from '@playwright/test';

for (const width of [320, 620, 835, 1440]) {
  for (const scene of ['compact', 'inventory', 'crane', 'lastmile']) {
    test(`${scene} uses its choice panel at ${width}px`, async ({ page }, info) => {
      await page.setViewportSize({ width, height: width === 320 ? 568 : 794 });
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      const condition = page.getByRole('region', { name: 'Условие задания', exact: true });
      for (let i = 0; i < 30 && await condition.isVisible(); i++) {
        await condition.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ }).click();
      }
      const answers = page.locator('[data-scene-choice]');
      for (const answer of await answers.all()) {
        await expect(answer).toBeInViewport({ ratio: 1 });
        expect((await answer.boundingBox())!.height).toBeGreaterThanOrEqual(44);
        if (width === 1440) expect((await answer.boundingBox())!.height).toBeLessThanOrEqual(64);
      }
      const last = await answers.last().boundingBox();
      const navigation = await page.getByRole('button', { name: 'О задаче', exact: true }).boundingBox();
      expect(navigation!.y - last!.y - last!.height).toBeGreaterThanOrEqual(8);
      expect(navigation!.y - last!.y - last!.height).toBeLessThanOrEqual(16);
      if (scene === 'compact' && width > 600 && width <= 900) {
        const third = await answers.nth(2).boundingBox();
        expect(Math.abs(last!.x + last!.width - third!.x - third!.width)).toBeLessThan(2);
      }
      await page.screenshot({ path: info.outputPath(`${scene}-${width}.png`) });
    });
  }
}
