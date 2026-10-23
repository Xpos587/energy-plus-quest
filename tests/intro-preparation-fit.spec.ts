import { expect, type Page, test } from "@playwright/test";

async function fits(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  const geometry = await page.evaluate(() => ({
    width: innerWidth,
    height: innerHeight,
    sw: document.documentElement.scrollWidth,
    sh: document.documentElement.scrollHeight,
    buttons: [...document.querySelectorAll("button")]
      .filter((e) => e.getClientRects().length)
      .map((e) => {
        const r = e.getBoundingClientRect();
        return {
          text: e.textContent,
          top: r.top,
          bottom: r.bottom,
          height: r.height,
        };
      }),
  }));
  expect(geometry.sw).toBeLessThanOrEqual(geometry.width);
  expect(geometry.sh).toBeLessThanOrEqual(geometry.height);
  for (const b of geometry.buttons) {
    expect(b.top, b.text || "").toBeGreaterThanOrEqual(0);
    expect(b.bottom, b.text || "").toBeLessThanOrEqual(geometry.height);
    expect(b.height, b.text || "").toBeGreaterThanOrEqual(44);
  }
}
for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`full preparation and returns at ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await fits(page);
    await page.locator("[data-intro-enter]").click();
    await fits(page);
    await page.locator("[data-intro-next]").click();
    await fits(page);
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(page.locator("[data-intro-next]")).toBeVisible();
    await page.locator("[data-intro-next]").click();
    await page.locator("[data-intro-start]").click();
    await fits(page);
    for (const profile of ["student", "professional"]) {
      await page.locator(`[data-choice="${profile}"]`).click();
      await fits(page);
      for (const recipient of ["alva", "khor", "arseniy"]) {
        await page.locator(`[data-choice="${recipient}"]`).click();
        await fits(page);
        for (const parcel of ["camera", "socks", "boat"]) {
          await page.locator(`[data-choice="${parcel}"]`).click();
          await expect(page.locator("[data-preparation-step]")).toHaveCount(0);
          await page
            .getByRole("button", { name: "К выбору подарка", exact: true })
            .click();
          await expect(
            page.locator('[data-preparation-step="parcel"]'),
          ).toBeVisible();
          await fits(page);
        }
        await page.getByRole("button", { name: "Назад", exact: true }).click();
        await expect(
          page.locator('[data-preparation-step="recipient"]'),
        ).toBeVisible();
      }
      await page.getByRole("button", { name: "Назад", exact: true }).click();
      await expect(
        page.locator('[data-preparation-step="profile"]'),
      ).toBeVisible();
    }
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(page.locator("[data-intro-enter]")).toBeVisible();
  });
}
