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
    await expect(page.locator("video")).toHaveCount(1);
    const markers = page.locator("[data-truck-inspect]");
    const target = await markers.nth(2).boundingBox();
    await page.mouse.click(target!.x + target!.width / 2, target!.y + target!.height / 2);
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

test("callouts move continuously instead of jumping between placements", async ({ page }) => {
  await page.goto("/");
  for (const name of [/Профессионал/, /Альва/, /Фотоаппарат/])
    await page.getByRole("button", { name }).click();
  const maximumSpeed = await page.evaluate(async () => {
    let previous: { time: number; points: number[][] } | null = null;
    let maximum = 0;
    const start = performance.now();
    await new Promise<void>((resolve) => {
      const sample = (time: number) => {
        const points = [...document.querySelectorAll<HTMLElement>("[data-truck-inspect]")]
          .map(el => [parseFloat(el.style.left), parseFloat(el.style.top)]);
        if (previous && time > previous.time)
          points.forEach((p, i) => {
            maximum = Math.max(maximum, Math.hypot(p[0] - previous!.points[i][0], p[1] - previous!.points[i][1]) * 1000 / (time - previous!.time));
          });
        previous = { time, points };
        if (time - start < 3000) requestAnimationFrame(sample); else resolve();
      };
      requestAnimationFrame(sample);
    });
    return maximum;
  });
  expect(maximumSpeed).toBeLessThan(180);
});
