import { expect, type Page, test } from "@playwright/test";

async function openMap(page: Page) {
  await page.goto("/");
  for (const id of ["professional", "alva", "boat"])
    await page.locator(`[data-choice="${id}"]`).click();
}

for (const [width, height, variant] of [
  [320, 480, "mobile"],
  [320, 568, "tablet"],
  [390, 844, "tablet"],
  [440, 956, "desktop"],
  [820, 1180, "desktop"],
  [1440, 900, "desktop"],
  [844, 390, "tablet"],
] as const) {
  test(`painted video fits the whole city at ${width}x${height}`, async ({
    page,
  }, info) => {
    await page.setViewportSize({ width, height });
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await openMap(page);
    const video = page.locator("[data-city-video]");
    await expect(video).toBeVisible();
    await expect
      .poll(() => video.evaluate((el: HTMLVideoElement) => el.readyState))
      .toBeGreaterThanOrEqual(2);
    await expect
      .poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime))
      .toBeGreaterThan(0);
    const state = await video.evaluate((el: HTMLVideoElement) => ({
      src: el.currentSrc,
      muted: el.muted,
      inline: el.playsInline,
      loop: el.loop,
      duration: el.duration,
      ratio:
        el.getBoundingClientRect().width / el.getBoundingClientRect().height,
      fit: getComputedStyle(el).objectFit,
    }));
    expect(state.src).toContain(`city-motion-${variant}.mp4`);
    expect(state).toMatchObject({
      muted: true,
      inline: true,
      loop: true,
      fit: "contain",
    });
    expect(state.duration).toBeCloseTo(64, 1);
    expect(state.ratio).toBeCloseTo(1440 / 1000, 2);
    expect(state.src).toContain("/scene1-live/separated-routes/");
    await expect(
      page.getByRole("button", {
        name: /Масштаб|Увеличить карту|Показать всю карту|Показать грузовик/,
      }),
    ).toHaveCount(0);
    await expect(
      page.locator("[data-map-surface] canvas, [data-truck-number]"),
    ).toHaveCount(0);
    await expect(page.locator("[data-carrier-choice]")).toHaveCount(5);
    for (const choice of await page.locator("[data-carrier-choice]").all()) {
      await choice.scrollIntoViewIfNeeded();
      const rect = (await choice.boundingBox())!;
      expect(rect.width).toBeGreaterThanOrEqual(44);
      expect(rect.height).toBeGreaterThanOrEqual(44);
    }
    await video.scrollIntoViewIfNeeded();
    await expect(
      page.getByRole("button", {
        name: /Приостановить движение|Продолжить движение/,
      }),
    ).toHaveCount(0);
    await expect(video).toHaveJSProperty("controls", false);
    await page.screenshot({
      path: info.outputPath(`video-${width}x${height}.png`),
      fullPage: true,
    });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.locator('[data-carrier-choice="crew"]').click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="crew"]'),
    ).toBeVisible();
    await expect(video).toHaveCount(0);
    expect(errors).toEqual([]);
  });
}

test("trucks start on entry without a playback toggle", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openMap(page);
  const video = page.locator("[data-city-video]");
  await expect
    .poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime))
    .toBeGreaterThan(0);
  const time = await video.evaluate((el: HTMLVideoElement) => el.currentTime);
  await expect
    .poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime))
    .toBeGreaterThan(time + 0.3);
  await expect(
    page.getByRole("button", {
      name: /Приостановить движение|Продолжить движение/,
    }),
  ).toHaveCount(0);
  await video.evaluate((el: HTMLVideoElement) => {
    el.currentTime = el.duration - 0.25;
  });
  await expect
    .poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime))
    .toBeLessThan(2);
  await expect(video).toHaveJSProperty("paused", false);
});

test("a rejected play request can be retried and leaving the map stops playback", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.addInitScript(() => {
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () {
      // Block every automatic attempt, including StrictMode's second setup.
      if (this.dataset.playbackAllowed !== "true") {
        this.autoplay = false;
        this.pause();
        return Promise.reject(
          new DOMException("Playback blocked", "NotAllowedError"),
        );
      }
      return play.call(this);
    };
  });
  await openMap(page);
  const play = page.getByRole("button", {
    name: "Запустить движение",
    exact: true,
  });
  await expect(play).toBeVisible();
  const video = page.locator("[data-city-video]");
  await video.evaluate((el: HTMLVideoElement) => {
    el.dataset.playbackAllowed = "true";
  });
  await play.click();
  await expect
    .poll(() => video.evaluate((el: HTMLVideoElement) => el.currentTime))
    .toBeGreaterThan(0);
  const detached = (await video.elementHandle())!;
  await page.locator('[data-carrier-choice="old"]').click();
  await expect
    .poll(() => detached.evaluate((el) => (el as HTMLVideoElement).paused))
    .toBe(true);
  await detached.dispose();
});

test("failed video keeps poster and all carrier choices usable", async ({
  page,
}) => {
  await page.route("**/city-motion-*.mp4", (route) => route.abort());
  await openMap(page);
  await expect(page.getByRole("status")).toContainText(
    "Не удалось загрузить видео",
  );
  const poster = page.locator("[data-city-poster]");
  await expect(poster).toBeVisible();
  await expect
    .poll(() =>
      poster.evaluate(
        (el: HTMLImageElement) => el.complete && el.naturalWidth > 0,
      ),
    )
    .toBe(true);
  await page.locator('[data-carrier-choice="near"]').click();
  await expect(
    page.locator('[data-layout="result"][data-carrier="near"]'),
  ).toBeVisible();
});
