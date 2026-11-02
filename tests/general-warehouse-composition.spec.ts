import { expect, test } from '@playwright/test';

// The same illustrated hall and native coordinate plane must work at every viewport.
for (const [width, height] of [[320, 568], [390, 844], [844, 390], [1440, 900]]) {
  for (const parcel of ['boat', 'camera', 'socks']) {
    test(`warehouse coordinate plane and accessible choices ${width}x${height} ${parcel}`, async ({ page }) => {
      await page.setViewportSize({ width, height });
      await page.emulateMedia({ reducedMotion: 'reduce' });
      await page.goto('/');
      await page.evaluate(({ parcel }) => {
        localStorage.clear();
        const scope = 'quest-warehouse-composition';
        localStorage.setItem('energy-quest-save-v1', JSON.stringify({ version: 1, scope, state: { step: 'outcome', profile: 'student', recipient: 'khor', parcel, carrier: 'old' } }));
        localStorage.setItem(scope + ':remaining', 'true');
        localStorage.setItem(scope + ':scenes', JSON.stringify({ progress: { sceneIndex: 1, phase: 'choice', answers: { compact: 'place-1' }, finished: false }, briefed: ['compact', 'inventory', 'crane', 'lastmile'] }));
      }, { parcel });
      await page.reload();
      await page.evaluate(() => document.fonts.ready);
      const stage = page.locator('[data-world-scene=inventory]');
      const image = stage.locator('picture img');
      await image.evaluate(i => i.decode());
      expect(await image.evaluate(i => i.currentSrc)).toContain('inventory-master-v7');
      await expect(stage.locator('[data-warehouse-annotations] svg')).toHaveAttribute('viewBox', '0 0 1672 941');
      await expect(stage.locator('[data-hotspot]')).toHaveCount(4);
      for (const id of ['entrance', 'alphabet', 'keeper', 'wms']) {
        const choice = page.locator(`[data-hotspot=${id}]`);
        await expect(choice).toBeVisible();
        await expect(choice).toBeInViewport();
        await expect(choice).toBeEnabled();
      }
      const initial = await image.boundingBox();
      await page.locator('[data-hotspot=alphabet]').click();
      await page.locator('[data-choice-confirm]').click();
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      const returned = await image.boundingBox();
      expect(Math.abs(returned!.y - initial!.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(returned!.height - initial!.height)).toBeLessThanOrEqual(1);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight)).toBe(true);
    });
  }
}
