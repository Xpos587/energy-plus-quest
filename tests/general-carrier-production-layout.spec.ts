import { expect, test } from '@playwright/test';

for (const [width, height] of [[320,568],[390,844],[844,390],[1440,900],[1920,1080]]) {
  test(`production carrier map and task panel fit ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/');
    await page.evaluate(() => {
      const scope = 'quest-carrier-production';
      localStorage.setItem('energy-quest-save-v1', JSON.stringify({version:1,scope,state:{step:'carrier',profile:'student',recipient:'khor',parcel:'boat'}}));
    });
    await page.reload();
    const map = page.locator('[data-map-viewport]');
    await expect(map).toBeVisible();
    await expect(map.locator('[data-carrier-choice]')).toHaveCount(4);
    const express = map.locator('[data-map-autopick]');
    await expect(express).toBeEnabled();
    await expect(express).toHaveAttribute('aria-label', 'Подобрать фуру автоматически');
    await express.click();
    await expect(page.locator('[data-choice-inspection="express"]')).toBeVisible();
    await page.locator('[data-choice-cancel]').click();
    const question = page.getByTestId('scene-question');
    if (width > 700) {
      await expect(question).toHaveCSS('position', 'absolute');
      const box = await question.boundingBox();
      expect(Math.abs(box!.width - (height <= 500 ? 340 : 420))).toBeLessThanOrEqual(1);
    }
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&document.documentElement.scrollHeight<=innerHeight)).toBe(true);
  });
}
