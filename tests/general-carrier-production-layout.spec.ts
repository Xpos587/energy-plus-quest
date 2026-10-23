import { expect, test } from '@playwright/test';
for (const [width, height] of [[320,568],[390,844],[844,390],[1440,900],[1920,1080]]) {
  test(`production retains the frozen carrier layout ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/');
    await page.evaluate(() => {
      const scope = 'quest-carrier-production';
      localStorage.setItem('energy-quest-save-v1', JSON.stringify({version:1,scope,state:{step:'carrier',profile:'student',recipient:'khor',parcel:'boat'}}));
    });
    await page.reload();
    const controls = page.locator('[data-carrier-controls]');
    await expect(controls).toBeVisible();
    await expect(controls.locator('[data-scene-choice]')).toHaveCount(5);
    const question = page.getByTestId('scene-question');
    if (width > 700) {
      await expect(question).toHaveCSS('position', 'absolute');
      const box = await question.boundingBox();
      expect(Math.abs(box!.width - (height <= 500 ? 320 : 400))).toBeLessThanOrEqual(1);
      const hint = page.locator('[data-map-zoom-hint]');
      if (await hint.isVisible()) {
        const h = await hint.boundingBox();
        expect(h!.x+h!.width).toBeLessThanOrEqual(box!.x-8);
      }
    }
    for (const button of await controls.locator('button').all()) await expect(button).toBeInViewport();
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight)).toBe(true);
  });
}
