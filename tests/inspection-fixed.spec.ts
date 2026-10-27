import { test, expect } from '@playwright/test';

for (const scene of ['compact', 'inventory', 'crane', 'lastmile']) {
  test(`${scene}: every option description and confirmation fits`, async ({ page }) => {
    await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
    const intro = page.getByRole('button', { name: /^(Далее|К выбору|К сцене)$/ });
    for (let n = 0; n < 20 && await intro.isVisible(); n++) await intro.click();
    const choices = page.locator(scene === 'crane' ? '[data-hotspot]' : '[data-scene-choice]');
    const count = await choices.count();
    expect(count).toBeGreaterThan(0);
    for (let index = 0; index < count; index++) {
      await choices.nth(index).click();
      const dialog = page.locator('[data-choice-inspection]');
      await expect(dialog).toBeVisible();
      const copy = dialog.locator('[aria-label="Описание варианта"]');
      for (let fragment = 0; fragment < 30; fragment++) {
        if (await copy.isVisible()) await expect.poll(() => copy.evaluate(e => ({
          choice: e.closest('[data-choice-inspection]')?.getAttribute('data-choice-inspection'),
          height: e.clientHeight,
          contentHeight: e.scrollHeight,
          width: e.clientWidth,
          contentWidth: e.scrollWidth,
          fits: e.scrollHeight <= e.clientHeight + 1 && e.scrollWidth <= e.clientWidth + 1,
        }))).toMatchObject({ fits: true });
        await expect(dialog.locator('[data-choice-confirm]')).toBeInViewport({ ratio: 0.99 });
        const next = dialog.getByRole('button', { name: 'Следующий фрагмент', exact: true });
        if (!await next.count() || !await next.isEnabled()) break;
        expect(fragment).toBeLessThan(29);
        await next.click();
      }
      await dialog.locator('[data-choice-cancel]').click();
      await expect(dialog).toHaveCount(0);
    }
  });
}
