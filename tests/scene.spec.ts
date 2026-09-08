import { expect, type Page, test } from "@playwright/test";

async function playReviewPath(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
}

const cases = [
  ["№1", "old", "Маршрут потребовал больше времени"],
  ["№2", "near", "Близко — не значит быстро"],
  ["№3", "crew", "Два водителя лучше одного"],
  ["№4", "old4", "Маршрут потребовал больше времени"],
  ["Подобрать автоматически", "express", "Перевозчик найден за два часа"],
] as const;

test("preserves brand UI and incremental context with four scene steps", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("header [data-selection-context]")).toHaveCount(0);
  const logos = page.locator("header img");
  const logoWidths = await logos.evaluateAll((images) =>
    images.map((image) => image.getBoundingClientRect().width),
  );
  expect(Math.abs(logoWidths[0] - logoWidths[1])).toBeLessThan(1);
  expect(
    await page
      .locator('[data-step="profile"]')
      .evaluate(
        (element) => getComputedStyle(element, "::after").backgroundImage,
      ),
  ).toBe("none");
  await expect(
    page.getByRole("heading", { name: "Кто отправится в путь?" }),
  ).toHaveCSS("font-family", /EPQ Normalidad Proxy/);
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await expect(page.locator("header [data-selection-context]")).toHaveCount(1);
  await expect(
    page.getByRole("button", { name: "Хор", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/с языка хантов|самец оленя/)).toHaveCount(0);
  await page.getByRole("button", { name: /Альва/ }).click();
  await expect(page.locator("header [data-selection-context]")).toHaveCount(2);
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  const progress = page.getByRole("navigation", { name: "Этапы доставки" });
  await expect(progress.locator("[data-progress-step]")).toHaveCount(5);
  await expect(progress.locator('[aria-current="step"] > span')).toHaveText(
    "Перевозчик",
  );
  for (const label of [
    "Перевозчик",
    "Загрузка",
    "Склад",
    "Баржа",
    "Последняя миля",
  ]) {
    await expect(progress.getByText(label, { exact: true })).toBeVisible();
  }
  expect(
    await page
      .locator("header [data-selection-context]")
      .evaluateAll((es) =>
        es.map((e) => e.getAttribute("data-selection-context")),
      ),
  ).toEqual(["profile", "recipient", "parcel"]);
});

test("carrier has four choice actions, authored motion and an accessible static description", async ({
  page,
}) => {
  await playReviewPath(page);
  const motion = page.locator('video[data-map-media="authored-video"]');
  await expect(motion).toHaveAttribute("autoplay", "");
  await expect(motion).toHaveAttribute("preload", "auto");
  await expect.poll(() => motion.evaluate((video: HTMLVideoElement) => video.currentTime)).toBeGreaterThan(0);
  await expect(page.locator("[data-carrier-hotspot]")).toHaveCount(0);
  await expect(page.locator("[data-pickup-label]")).toBeVisible();
  await expect(
    page.locator('[data-map-media="authored-video"]:visible'),
  ).toHaveCount(1);
  await expect(page.getByRole("button", { name: /Приостановить|Продолжить/ })).toHaveCount(0);
  await expect(page.locator("[data-motion-description]")).toHaveAttribute("data-visually-hidden", "true");
  for (const [label] of cases) await expect(page.getByRole("button", { name: label, exact: true })).toBeVisible();
});

test("carrier loads only the active map video", async ({ page }) => {
  const videoRequests: string[] = [];
  page.on("request", (request) => {
    if (
      request.resourceType() === "media" &&
      new URL(request.url()).pathname.endsWith(".mp4")
    )
      videoRequests.push(request.url());
  });
  await playReviewPath(page);
  await expect(page.locator('[data-map-media="authored-video"]')).toHaveCount(
    1,
  );
  await expect.poll(() => new Set(videoRequests).size).toBe(1);
});

test("motion starts again after changing format without a pause control", async ({ page }) => {
  await playReviewPath(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect.poll(() => page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime)).toBeGreaterThan(0);
  await expect(page.getByRole("button", { name: /Приостановить|Продолжить/ })).toHaveCount(0);
});

test("page visibility pauses and resumes map media", async ({ page }) => {
  await playReviewPath(page);
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => true,
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect
    .poll(() =>
      page
        .locator('[data-map-media="authored-video"]')
        .evaluate((video) => (video as HTMLVideoElement).paused),
    )
    .toBe(true);
  await page.evaluate(() => {
    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => false,
    });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect
    .poll(() =>
      page
        .locator('[data-map-media="authored-video"]')
        .evaluate((video) => !(video as HTMLVideoElement).paused),
    )
    .toBe(true);
});

test("scenario motion starts even when the OS requests reduced decorative motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await playReviewPath(page);
  await expect.poll(() => page.locator("video").evaluate((v: HTMLVideoElement) => v.currentTime)).toBeGreaterThan(0);
});

test("a rejected autoplay keeps a poster and a user retry control", async ({
  page,
}) => {
  await page.addInitScript(() => {
    (window as Window & { allowMapPlay?: boolean }).allowMapPlay = false;
    HTMLMediaElement.prototype.play = () =>
      (window as Window & { allowMapPlay?: boolean }).allowMapPlay
        ? Promise.resolve()
        : Promise.reject(new Error("blocked"));
  });
  await playReviewPath(page);
  await expect(page.locator('[data-map-media="poster"]')).toHaveCount(1);
  await expect(page.getByRole("button", { name: "Запустить движение" })).toBeVisible();
  await page.evaluate(() => {
    (window as Window & { allowMapPlay?: boolean }).allowMapPlay = true;
  });
  await page.getByRole("button", { name: "Запустить движение" }).click();
  await expect(page.getByRole("button", { name: "Запустить движение" })).toHaveCount(0);
});

test("a media error falls back to the poster", async ({ page }) => {
  await page.route(/\.mp4(?:\?|$)/, (route) =>
    route.request().resourceType() === "media"
      ? route.abort()
      : route.continue(),
  );
  await playReviewPath(page);
  await expect(page.locator('[data-map-media="poster"]')).toHaveCount(1);
  await expect(page.getByText(/Анимация карты недоступна/)).toBeVisible();
});

test("a failed poster leaves a neutral map fallback and its choices", async ({
  page,
}) => {
  await page.route(/\.mp4(?:\?|$)/, (route) =>
    route.request().resourceType() === "media"
      ? route.abort()
      : route.continue(),
  );
  await playReviewPath(page);
  await page.locator('[data-map-media="poster"]').dispatchEvent("error");
  await expect(page.locator('[data-map-media="fallback"]')).toBeVisible();
  await expect(
    page.getByRole("button", { name: "№1", exact: true }),
  ).toBeVisible();
});

test("leaving the carrier screen pauses its active media", async ({ page }) => {
  await page.addInitScript(() => {
    const pause = HTMLMediaElement.prototype.pause;
    HTMLMediaElement.prototype.pause = function () {
      (window as Window & { mapPauseCalls?: number }).mapPauseCalls =
        ((window as Window & { mapPauseCalls?: number }).mapPauseCalls ?? 0) +
        1;
      return pause.call(this);
    };
  });
  await playReviewPath(page);
  const before = await page.evaluate(
    () => (window as Window & { mapPauseCalls?: number }).mapPauseCalls ?? 0,
  );
  await page.getByRole("button", { name: "№1", exact: true }).click();
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          (window as Window & { mapPauseCalls?: number }).mapPauseCalls ?? 0,
      ),
    )
    .toBeGreaterThan(before);
});

test("an obsolete play rejection after resize does not replace the new source", async ({
  page,
}) => {
  await page.addInitScript(() => {
    let calls = 0;
    HTMLMediaElement.prototype.play = () => {
      calls += 1;
      if (calls === 1)
        return new Promise<void>((_resolve, reject) => {
          (window as Window & { rejectMapPlay?: () => void }).rejectMapPlay =
            () => reject(new DOMException("interrupted", "AbortError"));
        });
      return Promise.resolve();
    };
  });
  await playReviewPath(page);
  await expect
    .poll(() =>
      page.evaluate(() =>
        Boolean(
          (window as Window & { rejectMapPlay?: () => void }).rejectMapPlay,
        ),
      ),
    )
    .toBe(true);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() =>
    (window as Window & { rejectMapPlay?: () => void }).rejectMapPlay?.(),
  );
  await expect(
    page.locator('[data-map-media="authored-video"][data-format="mobile"]'),
  ).toHaveCount(1);
  await expect(page.locator('[data-map-media="fallback"]')).toHaveCount(0);
});

for (const [control, outcome, title] of cases) {
  test(`${control} retains ${outcome} score mapping and return context`, async ({
    page,
  }) => {
    await playReviewPath(page);
    await page.getByRole("button", { name: control, exact: true }).click();
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
    await expect(
      page.locator(`[data-outcome-art="${outcome}"]:visible`),
    ).toBeVisible();
    await expect(
      page.locator('[data-layout="result"] [data-selection-context]'),
    ).toHaveCount(0);
    await expect(page.locator("header [data-selection-context]")).toHaveCount(
      3,
    );
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await expect(page.locator("[data-score-key] svg")).toHaveCount(3);
    await expect(page.locator("[data-score-key] i")).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "К следующей сцене" }),
    ).toBeDisabled();
    await page.getByRole("button", { name: "Назад к машинам" }).click();
    await expect(page.locator("header [data-selection-context]")).toHaveCount(
      3,
    );
    await expect(page.getByRole("button")).toHaveCount(10);
  });
}

test("near uses the forecast and signed deltas without fictional continuation", async ({
  page,
}) => {
  await playReviewPath(page);
  await page.getByRole("button", { name: "№2", exact: true }).click();
  await expect(
    page.getByText("К чему приведёт выбор", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText(
      "Перевозчик выбран; груз ещё ждёт загрузки. Машина рядом, но водитель едет неторопливо. Если темп сохранится, Девочка Альва получит фотоаппарат на три дня позже.",
      { exact: true },
    ),
  ).toBeVisible();
  for (const [key, score] of [
    ["energy", "+1"],
    ["empathy", "0"],
    ["efficiency", "-2"],
  ]) {
    await expect(page.locator(`[data-score-key="${key}"] strong`)).toHaveText(
      score,
    );
  }
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeDisabled();
  await expect(
    page.getByText("Продолжение пока недоступно", { exact: true }),
  ).toHaveCount(0);
});

test("old trucks 1 and 4 have different media but the same consequence", async ({
  page,
}) => {
  await playReviewPath(page);
  await page.getByRole("button", { name: "№1", exact: true }).click();
  const firstImage = await page
    .locator('[data-outcome-art="old"]:visible')
    .getAttribute("src");
  const firstScores = await page
    .locator("[data-score-key] strong")
    .allTextContents();
  const firstCopy = await page
    .locator('[data-layout="result"] p')
    .textContent();
  await page
    .getByRole("button", { name: "Назад к машинам", exact: true })
    .click();
  await page.getByRole("button", { name: "№4", exact: true }).click();
  const fourthImage = page.locator('[data-outcome-art="old4"]:visible');
  await expect(fourthImage).toBeVisible();
  expect(await fourthImage.getAttribute("src")).not.toBe(firstImage);
  expect(
    await page.locator("[data-score-key] strong").allTextContents(),
  ).toEqual(firstScores);
  expect(await page.locator('[data-layout="result"] p').textContent()).toBe(
    firstCopy,
  );
});

test("authored video continues through two complete loop boundaries", async ({
  page,
}) => {
  test.setTimeout(40000);
  await playReviewPath(page);
  const result = await page
    .locator("video[data-map-media]")
    .evaluate(async (video: HTMLVideoElement) => {
      video.pause();
      video.currentTime = 0;
      video.playbackRate = 8;
      await video.play();
      return new Promise<{
        loops: number;
        frames: number;
        maximumRestartTime: number;
      }>((resolve, reject) => {
        let previous = 0;
        let loops = 0;
        let frames = 0;
        let maximumRestartTime = 0;
        const timeout = setTimeout(
          () => reject(new Error("video did not finish two loops")),
          25000,
        );
        const observe = (_now: number, frame: VideoFrameCallbackMetadata) => {
          frames += 1;
          if (previous > 60 && frame.mediaTime < previous) {
            loops += 1;
            maximumRestartTime = Math.max(maximumRestartTime, frame.mediaTime);
          }
          previous = frame.mediaTime;
          if (loops === 2) {
            clearTimeout(timeout);
            video.pause();
            resolve({ loops, frames, maximumRestartTime });
          } else video.requestVideoFrameCallback(observe);
        };
        video.requestVideoFrameCallback(observe);
      });
    });
  expect(result.loops).toBe(2);
  expect(result.frames).toBeGreaterThan(100);
  expect(result.maximumRestartTime).toBeLessThan(2);
});
