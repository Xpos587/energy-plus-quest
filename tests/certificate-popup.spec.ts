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
  expect(vk.searchParams.get("title")).toBe("Моё звание в игре «Доставляем радость» — «Логистический гик»");
  expect(vk.searchParams.get("url")).toBe("https://e-plus.media/specprojects/joydelivery/r/student-efficiency/");
  expect(vk.searchParams.get("image")).toBe("https://e-plus.media/specprojects/joydelivery/r/student-efficiency/card.jpg");
  const telegram = new URL(
    (await page.getByRole("link", { name: "Telegram", exact: true }).getAttribute("href"))!,
  );
  expect(telegram.searchParams.get("url")).toBe(vk.searchParams.get("url"));
  expect(telegram.searchParams.get("text")).toBe("Моё звание в игре «Доставляем радость» — «Логистический гик». Пройдите игру и узнайте, какой вы логист.");
  const max = new URL(
    (await page.getByRole("link", { name: "MAX", exact: true }).getAttribute("href"))!,
  );
  expect(max.searchParams.get("text")).toBe(`${telegram.searchParams.get("text")} ${vk.searchParams.get("url")}`);
});

test("on touch devices each messenger button sends the JPEG with copy and link", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const media = window.matchMedia.bind(window);
    window.matchMedia = (query: string) =>
      query === "(pointer: coarse)" ? ({ ...media(query), matches: true }) : media(query);
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
        (window as unknown as { calls: number }).calls =
          ((window as unknown as { calls?: number }).calls ?? 0) + 1;
        throw new DOMException("Cancelled", "AbortError");
      },
    });
  });
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  for (const name of ["Telegram", "ВКонтакте", "MAX"])
    await page.getByRole("link", { name, exact: true }).click();
  expect(await page.evaluate(() => (window as unknown as { calls: number }).calls)).toBe(3);
  expect(page.context().pages()).toHaveLength(1);
  const shared = await page.evaluate(
    () =>
      (window as unknown as { shared: { type: string; text: string } }).shared,
  );
  expect(shared.type).toBe("image/jpeg");
  expect(shared.text).toContain("Моё звание в игре «Доставляем радость» — «Логистический гик».");
  expect(shared.text).toMatch(/ https:\/\/e-plus\.media\/specprojects\/joydelivery\/r\/student-[a-z]+\/$/u);
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
