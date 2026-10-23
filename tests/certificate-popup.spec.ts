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

test("downloads the PNG directly and offers MAX text sharing", async ({
  page,
}) => {
  await expect(
    page.getByRole("button", { name: "Скачать сертификат" }),
  ).toBeVisible();
  await expect(page.locator("[data-practice-cta]")).toBeVisible();
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Скачать сертификат" }).click();
  expect((await pending).suggestedFilename()).toMatch(/\.png$/);
  const max = page.getByRole("link", { name: "MAX", exact: true });
  const url = new URL((await max.getAttribute("href")) ?? "");
  expect(url.hostname).toBe("max.ru");
  expect(url.pathname).toBe("/:share");
  expect(url.searchParams.get("text")).toContain("Я — логистический гик!");
  await expect(page.getByRole("dialog")).toHaveCount(0);
});

test("native sharing sends the PNG with short first-person copy", async ({
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
  await expect(
    page.getByRole("button", { name: "Отправить сертификат" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Отправить сертификат" }).click();
  const shared = await page.evaluate(
    () =>
      (window as unknown as { shared: { type: string; text: string } }).shared,
  );
  expect(shared.type).toBe("image/png");
  expect(shared.text).toContain("Я — логистический гик!");
  expect(shared.text).not.toContain("Запишитесь на практику");
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
      page.getByRole("button", { name: "Скачать сертификат" }),
    ).toBeVisible();
    if (viewport.width === 320) {
      await page.getByRole("button", { name: "Подробнее о практике" }).click();
    }
    await expect(
      page.getByRole("link", { name: "MAX", exact: true }),
    ).toBeVisible();
  }
});

test("certificate actions have clear names and work with a keyboard", async ({
  page,
}) => {
  await expect(page.locator("[data-logist-certificate] h1")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("button", { name: "Скачать сертификат" }),
  ).toBeFocused();
  await expect(
    page.getByRole("navigation", { name: "Поделиться текстом результата" }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "MAX", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Пройти заново" }),
  ).toBeVisible();
});
