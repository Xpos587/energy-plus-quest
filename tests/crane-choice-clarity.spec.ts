import { expect, test, type Page } from '@playwright/test';

// Owner 19.11: on the quay it must be obvious where to tap and who Ivan and Petr are, on a phone too.
const box = async (page: Page, selector: string) => (await page.locator(selector).boundingBox())!;
const overlap = (a: { x: number; y: number; width: number; height: number }, b: typeof a) =>
  a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }, { width: 320, height: 640 }]) {
  test(`${viewport.width}x${viewport.height}: named pins and a synced option list`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/scenes.html?scene=crane&parcel=socks&recipient=alva');
    await expect(page.locator('[data-artwork-ready="true"]')).toBeVisible();
    await page.waitForTimeout(600);

    await expect(page.locator('[data-quay-pin="remote"]')).toContainText('Иван');
    await expect(page.locator('[data-quay-pin="petr"]')).toContainText('Пётр');
    const stage = await box(page, '[data-world-scene="crane"]');
    const chips = await Promise.all(['remote', 'rush', 'petr'].map((id) => box(page, `[data-quay-pin="${id}"] > span`)));
    for (const chip of chips) {
      // Every chip stays on the picture, never under the sheet below it.
      expect(chip.x).toBeGreaterThanOrEqual(stage.x - 1);
      expect(chip.x + chip.width).toBeLessThanOrEqual(stage.x + stage.width + 1);
      expect(chip.y).toBeGreaterThanOrEqual(stage.y - 1);
      expect(chip.y + chip.height).toBeLessThanOrEqual(stage.y + stage.height + 1);
    }
    for (let i = 0; i < chips.length; i++)
      for (let j = i + 1; j < chips.length; j++) expect(overlap(chips[i], chips[j]), `chips ${i} ${j}`).toBe(false);

    for (const id of ['remote', 'rush', 'petr']) {
      const hotspot = await box(page, `[data-hotspot="${id}"]`);
      expect(Math.min(hotspot.width, hotspot.height)).toBeGreaterThanOrEqual(44);
      const option = page.locator(`[data-scene-choice="${id}"]`);
      await expect(option).toBeInViewport({ ratio: 1 });
      expect((await option.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    }
    // Phones: three compact chips in one row, the quay keeps most of the screen.
    if (viewport.width < 900) {
      const ys = await Promise.all(['remote', 'rush', 'petr'].map(async (id) => Math.round((await box(page, `[data-scene-choice="${id}"]`)).y)));
      expect(new Set(ys).size).toBe(1);
      expect(stage.height).toBeGreaterThan(viewport.height * 0.35);
    }

    // List → pin: pointing at a row lights its pin; picking a row opens the same card and presses the pin.
    if (viewport.width >= 900) {
      await page.locator('[data-scene-choice="petr"]').hover();
      await expect(page.locator('[data-hotspot="petr"]')).toHaveAttribute('data-hotspot-lit', 'true');
      await page.locator('[data-hotspot="remote"]').hover();
      await expect(page.locator('[data-scene-choice="remote"]')).toHaveAttribute('data-focused', 'true');
    }
    await page.locator('[data-scene-choice="petr"]').click();
    await expect(page.locator('[data-choice-inspection="petr"]')).toBeVisible();
    await expect(page.locator('[data-hotspot="petr"]')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ ratio: 1 });
    await page.getByRole('button', { name: 'К причалу' }).click();

    // Pin → card: the remote signal is drawn with moving packets.
    await page.locator('[data-hotspot="remote"]').click();
    await expect(page.locator('[data-choice-inspection="remote"]')).toBeVisible();
    await expect(page.locator('[data-choice-confirm]')).toBeInViewport({ ratio: 1 });
    const packets = page.locator('[data-barge-packets]');
    await expect(packets).toHaveCount(1);
    expect(await packets.evaluate((node) => getComputedStyle(node).animationName)).not.toBe('none');
  });
}

test('reduced motion: the remote signal packets stand still', async ({ browser }) => {
  const context = await browser.newContext({ reducedMotion: 'reduce', viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto('/scenes.html?scene=crane&parcel=socks&recipient=alva');
  await page.locator('[data-scene-choice="remote"]').click();
  const packets = page.locator('[data-barge-packets]');
  await expect(packets).toHaveCount(1);
  expect(await packets.evaluate((node) => getComputedStyle(node).animationName)).toBe('none');
  await context.close();
});
