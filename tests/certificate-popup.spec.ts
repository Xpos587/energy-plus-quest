import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    const scope = "quest-certificate-popup-test";
    localStorage.setItem(
      "energy-quest-save-v1",
      JSON.stringify({
        version: 1,
        scope,
        state: {
          step: "outcome",
          profile: "student",
          recipient: "alva",
          parcel: "socks",
          carrier: "old",
          scores: { energy: 0, empathy: 0, efficiency: 0 },
        },
      }),
    );
    for (const key of ["remaining", "intro-seen", "ending-profile"])
      localStorage.setItem(`${scope}:${key}`, "true");
    localStorage.setItem(
      `${scope}:scenes`,
      JSON.stringify({
        progress: {
          sceneIndex: 3,
          phase: "result",
          finished: true,
          answers: {
            compact: "place-1",
            inventory: "entrance",
            crane: "rush",
            lastmile: "helicopter",
          },
        },
      }),
    );
  });
  await page.reload();
});

test("downloads the story JPEG and shares the public result page", async ({
  page,
}) => {
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Скачать картинку" }).click();
  const download = await pending;
  expect(download.suggestedFilename()).toMatch(/\.jpg$/);
  const size = await page.evaluate(async (path) => {
    const image = new Image();
    image.src = path;
    await image.decode();
    return [image.naturalWidth, image.naturalHeight];
  }, `data:image/jpeg;base64,${(await import("node:fs")).readFileSync((await download.path())!).toString("base64")}`);
  expect(size).toEqual([1080, 1920]);
  const vk = new URL(
    (await page.getByRole("link", { name: "ВКонтакте", exact: true }).getAttribute("href"))!,
  );
  expect(vk.searchParams.get("title")).toBe("Я — логистический гик!");
  expect(vk.searchParams.get("url")).toMatch(/\/r\/(?:student|professional)-efficiency\/$/u);
  const telegram = new URL(
    (await page.getByRole("link", { name: "Telegram", exact: true }).getAttribute("href"))!,
  );
  expect(telegram.searchParams.get("url")).toBe(vk.searchParams.get("url"));
  const max = new URL(
    (await page.getByRole("link", { name: "MAX", exact: true }).getAttribute("href"))!,
  );
  expect(max.searchParams.get("text")).toBe(`Я — логистический гик! ${vk.searchParams.get("url")}`);
});

test("native sharing sends the JPEG with short first-person copy", async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: () => true,
    });
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: async (data: ShareData) => {
        (window as unknown as { shared: unknown }).shared = {
          type: data.files?.[0].type,
          text: data.text,
        };
        throw new DOMException("Cancelled", "AbortError");
      },
    });
  });
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  await page.getByRole("button", { name: "Отправить картинку" }).click();
  const shared = await page.evaluate(
    () =>
      (window as unknown as { shared: { type: string; text: string } }).shared,
  );
  expect(shared.type).toBe("image/jpeg");
  expect(shared.text).toContain("Я — логистический гик!");
  expect(shared.text).not.toContain("Узнайте больше");
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("final card and actions fit narrow and landscape screens", async ({
  page,
}) => {
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 844, height: 390 },
  ]) {
    await page.setViewportSize(viewport);
    const overflow = await page.evaluate(
      () =>
        document.documentElement.scrollWidth -
        document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(1);
    await expect(
      page.getByRole("button", { name: "Поделиться", exact: true }),
    ).toBeInViewport();
  }
});
