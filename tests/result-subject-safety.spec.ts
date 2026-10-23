import { expect, test } from '@playwright/test';

// These landmarks cover both workers' helmets and the loaded gift in the
// approved Petr composition. They must remain inside the displayed image.
for (const [width, height] of [[1440, 900], [1920, 1080], [390, 844], [320, 568]]) {
  test(`Petr keeps workers and gift visible at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.addInitScript(() => {
      const scope = 'quest-subject-safety';
      localStorage.setItem('energy-quest-save-v1', JSON.stringify({ version: 1, scope, state: {
        step: 'outcome', profile: 'student', recipient: 'alva', parcel: 'boat', carrier: 'crew',
        scores: { energy: 0, empathy: 0, efficiency: 0 },
      } }));
      localStorage.setItem(`${scope}:remaining`, 'true');
      localStorage.setItem(`${scope}:intro-seen`, 'true');
      localStorage.setItem(`${scope}:scenes`, JSON.stringify({ progress: {
        sceneIndex: 2, phase: 'result', answers: { compact: 'place-4', inventory: 'wms', crane: 'petr' }, finished: false,
      } }));
    });
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    const image = page.locator('[data-scene-consequence="crane-petr"] img');
    await expect(image).toBeVisible();
    const visible = await image.evaluate((img: HTMLImageElement) => {
      const box = img.getBoundingClientRect();
      const style = getComputedStyle(img);
      const scale = style.objectFit === 'contain'
        ? Math.min(box.width / img.naturalWidth, box.height / img.naturalHeight)
        : Math.max(box.width / img.naturalWidth, box.height / img.naturalHeight);
      const positions = style.objectPosition.split(' ').map(p => parseFloat(p) / 100);
      const x = (box.width - img.naturalWidth * scale) * positions[0];
      const y = (box.height - img.naturalHeight * scale) * positions[1];
      const landmarks = img.naturalWidth / img.naturalHeight > 2.5
        ? [[0.27, 0.09], [0.4, 0.13], [0.79, 0.98]]
        : [[420 / 1672, 75 / 941], [750 / 1672, 100 / 941], [1600 / 1672, 900 / 941]];
      return landmarks.map(([sx, sy]) => ({
        x: x + sx * img.naturalWidth * scale, y: y + sy * img.naturalHeight * scale, width: box.width, height: box.height,
      }));
    });
    for (const point of visible) {
      expect(point.x).toBeGreaterThanOrEqual(0);
      expect(point.y).toBeGreaterThanOrEqual(0);
      expect(point.x).toBeLessThanOrEqual(point.width);
      expect(point.y).toBeLessThanOrEqual(point.height);
    }
  });
}
