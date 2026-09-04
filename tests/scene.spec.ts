import { expect, type Locator, type Page, test } from "@playwright/test";

const progressLabels = ["Профиль", "Получатель", "Подарок", "Перевозчик"];

async function settle(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() =>
    [...document.images].every(
      (image) => image.complete && image.naturalWidth > 0,
    ),
  );
  await page.waitForTimeout(700);
}

async function expectContext(locator: Locator, keys: string[]) {
  await expect(locator.locator("[data-selection-context]")).toHaveCount(
    keys.length,
  );
  expect(
    await locator
      .locator("[data-selection-context]")
      .evaluateAll((elements) =>
        elements.map((element) =>
          element.getAttribute("data-selection-context"),
        ),
      ),
  ).toEqual(keys);
}

async function expectCompactHeader(page: Page) {
  const progress = page.getByRole("navigation", { name: "Прогресс сцены" });
  await expect(progress.locator("[data-progress-step]")).toHaveCount(4);
  await expect(progress.locator('[aria-current="step"]')).toHaveCount(1);
  for (const label of progressLabels) {
    await expect(progress.getByText(label, { exact: true })).toHaveCSS(
      "clip-path",
      "inset(50%)",
    );
  }
  await expect(page.locator("header [data-score-key]")).toHaveCount(0);
}

async function playReviewPath(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать игру/ }).click();
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
}

test("first scene uses compact progress and incremental selection context", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать игру/ }).click();

  await expectCompactHeader(page);
  await expectContext(page.locator("header"), []);
  await expect(
    page.locator(
      '[data-choice="professional"] [data-art-version="feedback-v12"]',
    ),
  ).toBeVisible();

  await page.getByRole("button", { name: /Профессионал/ }).click();
  await expectCompactHeader(page);
  await expectContext(page.locator("header"), ["profile"]);

  await page.getByRole("button", { name: /Альва/ }).click();
  await expectCompactHeader(page);
  await expectContext(page.locator("header"), ["profile", "recipient"]);

  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expectCompactHeader(page);
  await expectContext(page.locator("header"), [
    "profile",
    "parcel",
    "recipient",
  ]);
});

test("carrier map exposes four numbered trucks and a separate Express control", async ({
  page,
}) => {
  await playReviewPath(page);

  const hotspots = page.locator("[data-carrier-hotspot]");
  await expect(hotspots).toHaveCount(4);
  expect(
    await hotspots.evaluateAll((elements) =>
      elements.map((element) => element.getAttribute("data-truck")),
    ),
  ).toEqual(["truck-1", "truck-2", "truck-3", "truck-4"]);
  for (const number of [1, 2, 3, 4]) {
    await expect(
      page.locator(`[data-truck="truck-${number}"]`).getByText(String(number), {
        exact: true,
      }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: `Машина №${number}`, exact: true }),
    ).toBeVisible();
  }

  await expect(page.locator("[data-express-control]")).toHaveCount(1);
  await expect(
    page.getByRole("button", { name: "Автоподбор Express", exact: true }),
  ).toBeVisible();
  await expect(
    page.locator(
      '[data-map-media="generated"][data-art-version="feedback-v12"]',
    ),
  ).toBeVisible();

  for (const choice of ["№1 или №4", "№2", "№3"]) {
    await expect(
      page.getByRole("button", { name: choice, exact: true }),
    ).toBeVisible();
  }
});

test("truck 1 and duplicated truck 4 choice share the old result", async ({
  page,
}) => {
  await playReviewPath(page);
  await page.getByRole("button", { name: "Машина №1", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Маршрут потребовал больше времени" }),
  ).toBeVisible();

  await page.getByRole("button", { name: "Назад к машинам" }).click();
  await page.getByRole("button", { name: "№1 или №4", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Маршрут потребовал больше времени" }),
  ).toBeVisible();
});

test("truck 2, truck 3, and Express keep their existing outcomes", async ({
  page,
}) => {
  const cases = [
    ["Машина №2", "Близко — не значит быстро"],
    ["Машина №3", "Два водителя лучше одного"],
    ["Автоподбор Express", "Перевозчик найден за два часа"],
  ] as const;

  for (const [control, title] of cases) {
    await playReviewPath(page);
    await page.getByRole("button", { name: control, exact: true }).click();
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
  }
});

test("all carrier outcomes use the feedback-v12 artwork set", async ({
  page,
}) => {
  const cases = [
    ["Машина №1", "old"],
    ["Машина №2", "near"],
    ["Машина №3", "crew"],
    ["Автоподбор Express", "express"],
  ] as const;

  for (const [control, outcome] of cases) {
    await playReviewPath(page);
    await page.getByRole("button", { name: control, exact: true }).click();

    const artwork = page.locator(
      `[data-outcome-art="${outcome}"][data-art-version="feedback-v12"]`,
    );
    await expect(artwork).toBeVisible();
    await expect(artwork).toHaveAttribute(
      "src",
      new RegExp(
        `/feedback-v12/production/outcomes/${outcome}-desktop\\.webp$`,
      ),
    );
    await expect(
      artwork.locator("xpath=preceding-sibling::source"),
    ).toHaveAttribute(
      "srcset",
      new RegExp(`/feedback-v12/production/outcomes/${outcome}-mobile\\.webp$`),
    );
  }
});

test("outcome keeps one score delta and active review continuation", async ({
  page,
}) => {
  await playReviewPath(page);
  await page.getByRole("button", { name: "Машина №2", exact: true }).click();

  await expectContext(page.locator('[data-layout="result"]'), [
    "profile",
    "parcel",
    "recipient",
  ]);
  await expect(page.locator("header [data-score-key]")).toHaveCount(0);
  await expect(
    page.locator('[data-layout="result"] [data-score-key]'),
  ).toHaveCount(3);
  await expect(
    page.locator('[data-outcome-art="near"][data-art-version="feedback-v12"]'),
  ).toBeVisible();

  for (const removed of [
    "Изменение срока",
    "Дальше · скоро",
    "Начать заново",
    "Теперь нам нужно погрузить подарок...",
  ]) {
    await expect(page.getByText(removed, { exact: true })).toHaveCount(0);
  }

  await expect(
    page.getByRole("button", { name: "Назад к машинам" }),
  ).toBeVisible();
  const continueButton = page.getByRole("button", { name: "Едем дальше" });
  await expect(continueButton).toBeEnabled();
  await continueButton.click();
  await expect(page.getByRole("status")).toHaveText(
    "Продолжение маршрута появится в следующей версии",
  );
  await settle(page);
});

test("carrier choices remain static with reduced motion", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await playReviewPath(page);

  const animations = await page
    .locator("[data-carrier-hotspot]")
    .evaluateAll((elements) =>
      elements.map((element) => getComputedStyle(element).animationName),
    );
  expect(animations).toEqual(["none", "none", "none", "none"]);
});
