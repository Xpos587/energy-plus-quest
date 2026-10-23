import { expect, test } from "@playwright/test";
test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    const scope = "quest-ending-actions";
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
    for (const k of ["remaining", "intro-seen", "ending-profile"])
      localStorage.setItem(`${scope}:${k}`, "true");
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
});
test("file-share cancellation, failure and retry preserve the PNG and original copy", async ({
  page,
}) => {
  await page.addInitScript(() => {
    let calls = 0;
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: () => true,
    });
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: async (data: ShareData) => {
        calls++;
        (window as unknown as { shared: unknown }).shared = {
          calls,
          type: data.files?.[0].type,
          text: data.text,
        };
        if (calls === 1) throw new DOMException("Cancelled", "AbortError");
        if (calls === 2) throw new DOMException("Failed", "NotAllowedError");
      },
    });
  });
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  const share = page.getByRole("button", { name: "Отправить сертификат" });
  await share.click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await share.click();
  await expect(page.getByRole("alert")).toContainText(
    "Не удалось отправить файл",
  );
  await share.click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(
    await page.evaluate(
      () => (window as unknown as { shared: unknown }).shared,
    ),
  ).toMatchObject({ calls: 3, type: "image/png" });
});
test("unsupported sharing keeps download, text links and the practice placeholder usable", async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: () => false,
    });
  });
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Отправить сертификат" }),
  ).toHaveCount(0);
  for (let i = 0; i < 2; i++) {
    const pending = page.waitForEvent("download");
    await page.getByRole("button", { name: "Скачать сертификат" }).click();
    expect((await pending).suggestedFilename()).toMatch(/\.png$/);
  }
  await page.getByRole("button", { name: "Закрыть", exact: true }).click();
  await page.getByRole("button", { name: "Записаться на практику" }).click();
  await expect(page.getByRole("status")).toHaveText(
    "Ссылка на запись пока недоступна.",
  );
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  for (const [name, host] of [
    ["MAX", "max.ru"],
    ["Telegram", "t.me"],
    ["ВКонтакте", "vk.com"],
  ]) {
    const link = page.getByRole("link", { name, exact: true });
    const url = new URL((await link.getAttribute("href"))!);
    expect(url.hostname).toBe(host);
  }
});
test("download failure reports an error and retries after the image becomes available", async ({
  page,
}) => {
  await page.route("**/brand/quest-brand-lockup.svg", (route) => route.abort());
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  await page.getByRole("button", { name: "Скачать сертификат" }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "Не удалось скачать сертификат. Попробуйте ещё раз.",
  );
  await page.unroute("**/brand/quest-brand-lockup.svg");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Скачать сертификат" }).click();
  expect((await pending).suggestedFilename()).toMatch(/\.png$/);
  await expect(page.getByRole("alert")).toHaveCount(0);
});
