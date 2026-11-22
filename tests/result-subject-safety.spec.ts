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
    // The result is the live quay in its end state (client Fedya 22.11); the drawing covers the stage at the choice's camera.
    const stage = page.locator('[data-barge-art][data-crane-result="petr"][data-artwork-ready="true"]');
    await expect(stage).toBeVisible();
    const box = await stage.evaluate((s) => { const a = s.getBoundingClientRect(), p = s.firstElementChild!.getBoundingClientRect(); return [p.left - a.left, p.top - a.top, p.right - a.right, p.bottom - a.bottom]; });
    expect(box[0]).toBeLessThanOrEqual(0.5); expect(box[1]).toBeLessThanOrEqual(0.5);
    expect(box[2]).toBeGreaterThanOrEqual(-0.5); expect(box[3]).toBeGreaterThanOrEqual(-0.5);
    // Petr in the cab (his sheet) and the gift on the deck are drawn.
    await expect(stage.locator('[data-layer="cabPetr"]')).toHaveCount(1);
    await expect(stage.locator('[data-layer="gift"]')).toHaveCount(1);
  });
}
