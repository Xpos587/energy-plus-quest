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

test("result keeps a labelled share action and hides social/download until opened", async ({
  page,
}) => {
  await page.reload();
  await expect(
    page.getByRole("button", { name: "Поделиться", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Скачать сертификат", exact: true }),
  ).not.toBeVisible();
  for (const name of ["Пройти заново", "Вернуться на главную"]) {
    const action = page.getByRole("button", { name, exact: true });
    await expect(action).toHaveText("");
    await expect(action).toHaveAttribute("title", name);
  }
  await expect(
    page.locator("[data-logist-certificate] [data-practice-cta]"),
  ).toHaveCount(0);
  await expect(page.locator("[data-practice-cta]")).toContainText(
    "Узнайте больше",
  );
  await page.getByRole("button", { name: "Поделиться", exact: true }).click();
  for (const name of ["MAX", "Telegram", "ВКонтакте"]) {
    const action = page.getByRole("link", { name, exact: true });
    await expect(action).toHaveText(name);
    await expect(action).toHaveAttribute("title", name);
  }
  await expect(
    page.getByRole("link", { name: "MAX", exact: true }).locator("img"),
  ).toHaveAttribute("src", "/brand/max-official.svg");
});

test("gift handover keeps every recipient and present readable without offscreen actions", async ({
  page,
}) => {
  await page.goto("/");
  for (const viewport of [
    { width: 320, height: 568 },
    { width: 390, height: 844 },
    { width: 844, height: 390 },
    { width: 1440, height: 900 },
  ]) {
    await page.setViewportSize(viewport);
    for (const recipient of ["alva", "khor", "arseniy"])
      for (const parcel of ["socks", "camera", "boat"]) {
        await page.evaluate(
          async ({ recipient, parcel }) => {
            const load = (url: string) => import(/* @vite-ignore */ url);
            const React = (await load("/node_modules/.vite/deps/react.js"))
              .default;
            const { createRoot } = (
              await load("/node_modules/.vite/deps/react-dom_client.js")
            ).default;
            const { JourneyEnding } = await load(
              "/src/scenes/JourneyEnding.tsx",
            );
            const state = window as unknown as {
              giftRoot?: { unmount(): void; render(node: unknown): void };
            };
            state.giftRoot?.unmount();
            const host = document.createElement("div");
            document.body.replaceChildren(host);
            state.giftRoot = createRoot(host);
            state.giftRoot!.render(
              React.createElement(JourneyEnding, {
                context: { profile: "student", recipient, parcel },
                scores: { energy: 0, empathy: 0, efficiency: 0 },
                onRestart: () => {},
              }),
            );
          },
          { recipient, parcel },
        );
        const action = page.getByRole("button", {
          name: "Узнать, какой вы логист",
        });
        await expect(action).toBeVisible();
        await expect(page.locator("[data-resolution-art]")).toHaveAttribute(
          "src",
          new RegExp(`${recipient}-${parcel}`),
        );
        await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
        const box = await action.boundingBox();
        expect(
          box!.y + box!.height,
          `${recipient}/${parcel}/${viewport.width}`,
        ).toBeLessThanOrEqual(viewport.height);
        expect(
          await page.evaluate(() => document.documentElement.scrollWidth),
        ).toBeLessThanOrEqual(viewport.width);
      }
  }
});

test("home icon returns to the opening screen", async ({ page }) => {
  await page.reload();
  await page
    .getByRole("button", { name: "Вернуться на главную", exact: true })
    .click();
  await expect(page.locator("[data-journey-ending]")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Скачать сертификат", exact: true }),
  ).toHaveCount(0);
  await expect(page.locator("main")).toBeVisible();
});

test("restart icon starts a fresh journey", async ({ page }) => {
  await page.reload();
  await page
    .getByRole("button", { name: "Пройти заново", exact: true })
    .click();
  await expect(page.locator("[data-journey-ending]")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Скачать сертификат", exact: true }),
  ).toHaveCount(0);
  const state = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("energy-quest-save-v1")!),
  );
  expect(state.state.step).toBe("profile");
  expect(state.state.profile).toBeUndefined();
});

test("compact practice uses an icon-only return action and restores heading focus", async ({
  page,
}) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.reload();
  await page.getByRole("button", { name: "Подробнее о практике" }).click();
  const back = page.getByRole("button", { name: "Назад к результату" });
  await expect(back).toHaveText("");
  await expect(back).toHaveAttribute("title", "Назад к результату");
  await back.click();
  await expect(page.locator("[data-logist-certificate] h1")).toBeFocused();
});

test("main service actions retain visible keyboard focus and accessible names", async ({
  page,
}) => {
  await page.reload();
  await page.locator("[data-logist-certificate] h1").focus();
  for (const name of [
    "Записаться на практику",
    "Поделиться",
    "Пройти заново",
    "Вернуться на главную",
  ]) {
    await page.keyboard.press("Tab");
    const action = page.getByRole("button", { name, exact: true });
    await expect(action).toBeFocused();
    expect(
      await action.evaluate((el) => getComputedStyle(el).outlineWidth),
    ).toBe("3px");
  }
});
