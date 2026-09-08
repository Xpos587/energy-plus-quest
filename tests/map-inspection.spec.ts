import { expect, test } from "@playwright/test";

test("map inspection follows the media clock and never selects a carrier", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  const video = page.locator("video");
  await expect(video).toBeVisible();
  await video.evaluate((v: HTMLVideoElement) => {
    v.pause();
    v.currentTime = 16;
  });
  await expect
    .poll(() => video.evaluate((v: HTMLVideoElement) => v.seeking))
    .toBe(false);
  const markers = page.locator("[data-truck-inspect]");
  await expect(markers).toHaveCount(4);
  await expect(markers.first()).toHaveCSS("font-size", "18px");
  const before = await markers.first().getAttribute("style");
  await video.evaluate((v: HTMLVideoElement) => {
    v.currentTime = 32;
  });
  await expect
    .poll(() => markers.first().getAttribute("style"))
    .not.toBe(before);
  await markers.nth(2).focus();
  await page.keyboard.press("Enter");
  const modal = page.getByRole("dialog");
  await expect(modal).toBeVisible();
  for (let i = 1; i <= 4; i++) {
    await modal.getByRole("button", { name: `№${i}`, exact: true }).click();
    await expect(modal).toHaveAttribute("aria-label", `Машина №${i}`);
    await expect
      .poll(() =>
        modal
          .locator("img")
          .evaluate(
            (img: HTMLImageElement) => img.complete && img.naturalWidth >= 900,
          ),
      )
      .toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(modal).not.toBeVisible();
  await expect(markers.nth(2)).toBeFocused();
  await expect(
    page.getByRole("button", { name: "Подобрать автоматически", exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollHeight <= innerHeight,
    ),
  ).toBe(true);
});

for (const viewport of [
  { width: 320, height: 568 },
  { width: 844, height: 390 },
]) {
  test(`inspection fits ${viewport.width}x${viewport.height}`, async ({
    page,
  }) => {
    await page.setViewportSize(viewport);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/");
    await page.getByRole("button", { name: /Профессионал/ }).click();
    await page.getByRole("button", { name: /Альва/ }).click();
    await page.getByRole("button", { name: /Фотоаппарат/ }).click();
    await expect(page.locator("video")).toHaveCount(0);
    const markers = page.locator("[data-truck-inspect]");
    await markers.nth(2).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(
      dialog.getByRole("button", { name: "Закрыть" }),
    ).toBeInViewport();
    await expect(
      dialog.getByRole("button", { name: "№4", exact: true }),
    ).toBeInViewport();
    expect(
      await dialog.evaluate((el) => el.scrollHeight <= el.clientHeight),
    ).toBe(true);
    await page.screenshot({
      path: `/tmp/r23-inspection-${viewport.width}.png`,
    });
    await dialog.getByRole("button", { name: "Закрыть" }).click();
    await expect(markers.nth(2)).toBeFocused();
    await page.screenshot({ path: `/tmp/r23-overview-${viewport.width}.png` });
  });
}
