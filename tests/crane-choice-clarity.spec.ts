import { expect, test, type Page } from '@playwright/test';

// Owner 19.11: on the quay it must be obvious where to tap and who Ivan and Petr are, on a phone too.
const box = async (page: Page, selector: string) => (await page.locator(selector).boundingBox())!;
const overlap = (a: { x: number; y: number; width: number; height: number }, b: typeof a) =>
  a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }, { width: 320, height: 640 }]) {
  test(`${viewport.width}x${viewport.height}: one-word pins are the only choice UI`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto('/scenes.html?scene=crane&parcel=socks&recipient=alva');
    await expect(page.locator('[data-artwork-ready="true"]')).toBeVisible();
    await page.waitForTimeout(600);

    // Owner 20.11: one word per pin, no role after a dot; the pins are the only choice UI.
    for (const [id, word] of [['remote', 'С пульта'], ['rush', 'Пешком'], ['petr', 'Пётр']])
      await expect(page.locator(`[data-quay-pin="${id}"]`)).toHaveText(word);
    await expect(page.locator('[data-scene-choice]')).toHaveCount(0);
    await expect(page.locator('[data-layer="ladder"]')).toHaveCount(0);
    const stage = await box(page, '[data-world-scene="crane"]');
    const chips = await Promise.all(['remote', 'rush', 'petr'].map((id) => box(page, `[data-quay-pin="${id}"] > span`)));
    for (const chip of chips) {
      // Every chip stays on the picture, never under the sheet below it.
      expect(chip.x).toBeGreaterThanOrEqual(stage.x - 1);
      expect(chip.x + chip.width).toBeLessThanOrEqual(stage.x + stage.width + 1);
      expect(chip.y).toBeGreaterThanOrEqual(stage.y - 1);
      expect(chip.y + chip.height).toBeLessThanOrEqual(stage.y + stage.height + 1);
    }
    // The word never spills out of its chip.
    for (const id of ['remote', 'rush', 'petr'])
      expect(await page.locator(`[data-quay-pin="${id}"] b`).evaluate((b) => {
        const word = b.getBoundingClientRect(), chip = b.parentElement!.getBoundingClientRect();
        return word.left >= chip.left && word.right <= chip.right && b.scrollWidth <= b.clientWidth + 1;
      }), id).toBe(true);
    for (let i = 0; i < chips.length; i++)
      for (let j = i + 1; j < chips.length; j++) expect(overlap(chips[i], chips[j]), `chips ${i} ${j}`).toBe(false);

    for (const id of ['remote', 'rush', 'petr']) {
      const hotspot = await box(page, `[data-hotspot="${id}"]`);
      expect(Math.min(hotspot.width, hotspot.height)).toBeGreaterThanOrEqual(44);
    }
    if (viewport.width < 900) expect(stage.height).toBeGreaterThan(viewport.height * 0.35);

    // Pin → card: picking a pin opens its card and presses the pin.
    await page.locator('[data-hotspot="petr"]').click();
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
  await page.locator('[data-hotspot="remote"]').click();
  const packets = page.locator('[data-barge-packets]');
  await expect(packets).toHaveCount(1);
  expect(await packets.evaluate((node) => getComputedStyle(node).animationName)).toBe('none');
  await context.close();
});
