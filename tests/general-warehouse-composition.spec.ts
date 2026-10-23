import { expect, test } from '@playwright/test';

// Technical routing evidence for the shown21Oct artwork, which is artistically rejected.
// A physically correct scene may use camera zoom/pan; simultaneous visibility of
// every badge and forced edge-to-edge filling are deliberately not requirements.
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
      const format = await stage.getAttribute('data-format');
      const image = stage.locator('picture img');
      await image.evaluate(i => i.decode());
      expect(await image.evaluate(i => i.currentSrc)).toContain(format === 'mobile' ? 'overview-mobile-native-v3' : 'overview-receiving-parallel-labels-v1');
      await expect(stage.locator('[data-warehouse-annotations] svg')).toHaveAttribute('viewBox', format === 'mobile' ? '0 0 1024 1536' : '0 0 1546 1017');
      await expect(stage.locator('[data-hotspot]')).toHaveCount(4);
      for (const id of ['entrance', 'alphabet', 'keeper', 'wms']) {
        const choice = page.locator(`[data-scene-choice=${id}]`);
        await expect(choice).toBeVisible();
        await expect(choice).toBeInViewport();
        await expect(choice).toBeEnabled();
      }
      const initial = await image.boundingBox();
      await page.locator('[data-scene-choice=alphabet]').click();
      await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
      const returned = await image.boundingBox();
      expect(Math.abs(returned!.y - initial!.y)).toBeLessThanOrEqual(1);
      expect(Math.abs(returned!.height - initial!.height)).toBeLessThanOrEqual(1);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth && document.documentElement.scrollHeight <= innerHeight)).toBe(true);
    });
  }
}
