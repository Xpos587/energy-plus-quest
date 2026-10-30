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
test("file-share cancellation, failure and retry preserve the JPEG and original copy", async ({
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
  const share = page.getByRole("button", { name: "Отправить картинку" });
  await share.click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await share.click();
  await expect(page.getByRole("alert")).toContainText(
    "Не удалось отправить картинку",
  );
  await share.click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(
    await page.evaluate(
      () => (window as unknown as { shared: unknown }).shared,
    ),
  ).toMatchObject({ calls: 3, type: "image/jpeg" });
});
test("unsupported sharing keeps download, the VK link and the company link usable", async ({
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
    page.getByRole("button", { name: "Отправить картинку" }),
  ).toHaveCount(0);
  for (let i = 0; i < 2; i++) {
    const pending = page.waitForEvent("download");
    await page.getByRole("button", { name: "Скачать картинку" }).click();
    expect((await pending).suggestedFilename()).toMatch(/\.jpg$/);
  }
  const vk = new URL(
    (await page.getByRole("link", { name: "ВКонтакте", exact: true }).getAttribute("href"))!,
  );
  expect(vk.hostname).toBe("vk.com");
  expect(vk.searchParams.get("url")).toMatch(/\/r\/[a-z]+-[a-z]+\/$/u);
  expect(vk.searchParams.get("image")).toBe(`${vk.searchParams.get("url")}card.jpg`);
  await page.getByRole("button", { name: "Закрыть", exact: true }).click();
  await expect(
    page.locator("[data-company-cta] a"),
  ).toHaveAttribute("href", "https://supply.gazprom-neft.ru/");
});
test("download failure reports an error and retries after the image becomes available", async ({
  page,
}) => {
  await page.route("**/brand/quest-brand-lockup.svg", (route) => route.abort());
  await page.reload();
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  await page.getByRole("button", { name: "Скачать картинку" }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "Не удалось скачать картинку. Попробуйте ещё раз.",
  );
  await page.unroute("**/brand/quest-brand-lockup.svg");
  const pending = page.waitForEvent("download");
  await page.getByRole("button", { name: "Скачать картинку" }).click();
  expect((await pending).suggestedFilename()).toMatch(/\.jpg$/);
  await expect(page.getByRole("alert")).toHaveCount(0);
});
