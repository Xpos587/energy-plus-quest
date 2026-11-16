import { expect, test } from '@playwright/test';

// R18 uses a static flight plate, not the retired animated SVG rotor.
for (const reducedMotion of ['no-preference', 'reduce'] as const) {
  test(`helicopter flight plate loads with ${reducedMotion} and returns to the choices`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion });
    await page.goto('/scenes.html?scene=lastmile&parcel=boat&recipient=alva');
    const reading = page.getByRole('button', { name: /^(Далее|К выбору)$/ });
    for (let step = 0; step < 30 && await reading.isVisible(); step++) await reading.click();
    await page.locator('[data-hotspot="helicopter"]').click();
    await page.locator("[data-choice-confirm]").click();
    const flight = page.locator('[data-delivery-leg="flight"] img');
    await expect(flight).toBeVisible();
    await expect(flight).toHaveAttribute('src', /revision-18\/flight-boat-tall\.webp$/);
    await flight.evaluate((image: HTMLImageElement) => image.decode());
    await expect(flight).not.toHaveJSProperty('naturalWidth', 0);
    expect(await flight.evaluate(image => getComputedStyle(image).animationName)).toBe('none');
    await expect(page.locator('[data-result-heading]')).toHaveAttribute('data-result-heading', 'helicopter');
    await page.getByRole('button', { name: 'Изменить выбор', exact: true }).click();
    await expect(page.locator('[data-delivery-leg]')).toHaveCount(0);
    await expect(page.locator('[data-hotspot]')).toHaveCount(4);
    await page.locator('[data-hotspot="rover"]').click();
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator('[data-result-heading]')).toHaveAttribute('data-result-heading', 'rover');
    await expect(page.locator('[data-delivery-leg]')).toHaveCount(0);
  });
}
