import { expect, test } from "@playwright/test";

for (const [width, height, variant] of [
  [1440, 900, "desktop"],
  [390, 844, "mobile"],
] as const) {
  test(`installed city loop crosses its boundary at ${width}px`, async ({ page }, info) => {
    await page.setViewportSize({ width, height });
    await page.goto("/");
    await page.locator("[data-intro-next]").click();
    await page.locator("[data-intro-start]").click();
    for (const id of ["professional", "alva", "boat"]) {
      await page.locator(`[data-choice="${id}"]`).click();
    }
    await page.getByRole("button", { name: "К выбору", exact: true }).click();
    const video = page.locator("[data-city-video]");
    await expect(video).toBeVisible();
    await expect.poll(() => video.evaluate((el: HTMLVideoElement) => el.readyState)).toBeGreaterThanOrEqual(2);
    const contract = await video.evaluate((el: HTMLVideoElement) => ({
      duration: el.duration, loop: el.loop, src: el.currentSrc,
      width: el.videoWidth, height: el.videoHeight,
    }));
    expect(contract.duration).toBeCloseTo(64, 2);
    expect(contract.loop).toBe(true);
    expect(contract.src).toContain(`city-motion-${variant}.mp4`);
    expect(contract.width / contract.height).toBeCloseTo(1.44, 2);
    expect(contract.width).toBe(variant === "desktop" ? 3600 : 1920);
    await video.evaluate((el: HTMLVideoElement) => { el.pause(); el.currentTime = 63.75; });
    await expect.poll(() => video.evaluate((el: HTMLVideoElement) => el.seeking)).toBe(false);
    await page.screenshot({ path: info.outputPath("before-loop.png") });
    await video.evaluate((el: HTMLVideoElement) => el.play());
    await expect.poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime), { timeout: 5000 }).toBeLessThan(2);
    await expect(video).toHaveJSProperty("ended", false);
    await expect(video).toHaveJSProperty("paused", false);
    await page.screenshot({ path: info.outputPath("after-loop.png") });
    await expect(page.locator("[data-carrier-choice]")).toHaveCount(4);
  });
}
