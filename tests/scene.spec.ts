import { expect, type Page, test } from "@playwright/test";

const reviewScreenshot = (projectName: string, state: string) =>
  `design/scene-01/review/${state}-${projectName === "mobile-chromium" ? "mobile" : "desktop"}.png`;

async function settle(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() =>
    [...document.images].every(
      (image) => image.complete && image.naturalWidth > 0,
    ),
  );
  await page.waitForTimeout(700);
}

test("plays the first scene from intro to an illustrated outcome", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Доставляем радость/ }),
  ).toBeVisible();
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "intro"),
  });

  await page.getByRole("button", { name: /Начать игру/ }).click();
  await expect(
    page.getByRole("heading", { name: "Кто отправится в путь?" }),
  ).toBeVisible();
  await expect(
    page.locator('[data-art-version="feedback-v4"]').first(),
  ).toBeVisible();
  await expect(page.locator('[data-score-art="feedback-v5"]')).toHaveCount(3);
  for (const label of ["Энергия", "Эмпатия", "Эффективность"]) {
    await expect(
      page.locator("[data-score-key]").filter({ hasText: label }),
    ).toBeVisible();
  }
  for (const role of ["student", "professional"]) {
    const card = page.locator(`[data-choice="${role}"]`);
    await expect(card.locator('[data-role-part="label"]')).toHaveCount(0);
    await expect(card.locator('[data-role-part="title"]')).toBeVisible();
    await expect(card.locator('[data-role-part="action"]')).toBeVisible();
  }
  await expect(
    page.getByText("Начало игры · роль", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Выберите, кто отправится в путь.", { exact: true }),
  ).toHaveCount(0);
  await expect(page.getByText("Сцена 01", { exact: true })).toHaveCount(0);
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "profile"),
  });

  await page.getByRole("button", { name: /Студент/ }).click();
  await expect(
    page.getByRole("heading", { name: "Выберите получателя" }),
  ).toBeVisible();
  await expect(
    page.locator('[class*="screenHeading"] [class*="eyebrow"]'),
  ).toHaveCount(0);
  await expect(
    page.locator('[data-choice="alva"] [data-role-part="label"]'),
  ).toHaveCount(0);
  await expect(
    page.locator('[data-choice="khor"] [data-role-part="label"]'),
  ).toHaveCount(0);
  await expect(
    page.locator('[data-choice="arseniy"] [data-role-part="label"]'),
  ).toHaveCount(0);
  await expect(
    page.getByText("Выберите того, кому мы повезём подарок.", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Вахтовый работник", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText("Вахтовик Арсений", { exact: true }),
  ).toBeVisible();
  const khorImage = page.locator(
    '[data-choice="khor"] [class*="choiceSymbol"] img',
  );
  await expect(khorImage).toHaveCSS("object-fit", "contain");
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "recipient"),
  });
  await page.getByRole("button", { name: /Альва/ }).click();
  await expect(
    page.getByRole("heading", { name: "Что будет в посылке?" }),
  ).toBeVisible();
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "parcel"),
  });
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();

  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /(?:Машин(?:а|ы)|Express)/ }),
  ).toHaveCount(4);
  await expect(
    page
      .locator('section[aria-label="Карта доступных перевозчиков"]')
      .getByRole("button"),
  ).toHaveCount(4);
  await expect(
    page.getByRole("button", { name: /дальний маршрут от склада/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /короткий маршрут рядом со складом/i }),
  ).toBeVisible();
  await expect(page.locator('[data-art-version="feedback-v4"]')).toBeVisible();
  for (const carrier of ["old", "near", "crew", "express"]) {
    await expect(page.locator(`[data-map-label="${carrier}"]`)).toBeVisible();
  }
  await expect(page.getByText("Машина 1", { exact: true })).toBeVisible();
  await expect(page.getByText("Два водителя", { exact: true })).toBeVisible();
  await expect(page.getByText("Машины 1 и 4", { exact: true })).toHaveCount(0);
  await expect(page.getByText("Широкий маршрут", { exact: true })).toHaveCount(
    0,
  );
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "carrier"),
  });

  await page.getByRole("button", { name: /^Машина 2:/ }).click();
  await expect(
    page.getByRole("heading", { name: "Близко — не значит быстро" }),
  ).toBeVisible();
  await expect(page.locator('[data-outcome-art="near"]')).toBeVisible();
  await expect(page.locator('[class*="outcomeTokenThumb"]')).toHaveCount(2);
  await expect(
    page.locator('[data-outcome-art="near"][data-art-version="feedback-v5"]'),
  ).toBeVisible();
  for (const rejectedLabel of ["График", "Техника", "Экипаж", "Цена"]) {
    await expect(page.getByText(rejectedLabel, { exact: true })).toHaveCount(0);
  }
  await expect(
    page.getByRole("button", { name: /Назад к машинам/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Назад к машинам/ }),
  ).toHaveAttribute("data-control-style", "secondary");
  await expect(
    page.getByRole("button", { name: /Начать заново/ }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Начать заново/ }),
  ).toHaveAttribute("data-control-style", "secondary");
  await expect(
    page.getByText(/Теперь нам нужно погрузить подарок/),
  ).toBeVisible();
});

test("frames the slower outcomes constructively instead of as breakdown imagery", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать игру/ }).click();
  await page.getByRole("button", { name: /Студент/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await page
    .getByRole("button", { name: /дальний маршрут от склада/i })
    .click();

  await expect(
    page.getByRole("heading", { name: "Маршрут потребовал больше времени" }),
  ).toBeVisible();
  await expect(
    page.locator('[data-outcome-art="old"][data-art-version="feedback-v5"]'),
  ).toBeVisible();
  await expect(page.getByText("Возраст берёт своё")).toHaveCount(0);
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "outcome-old"),
  });
});

test("returns from an outcome to the map and then shows the Express result", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать игру/ }).click();
  await page.getByRole("button", { name: /Студент/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();

  await page.getByRole("button", { name: /^Машина 3:/ }).click();
  await expect(
    page.getByRole("heading", { name: "Два водителя лучше одного" }),
  ).toBeVisible();

  await page.getByRole("button", { name: /Назад к машинам/ }).click();
  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();

  await page
    .getByRole("button", { name: "Express: Автоподбор Express" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Перевозчик найден за два часа" }),
  ).toBeVisible();
  await expect(
    page.getByText(/За два часа Express нашёл новую фуру с двумя водителями/),
  ).toBeVisible();
  await expect(page.locator('[data-outcome-art="express"]')).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Начать заново/ }),
  ).toBeVisible();
  await expect(page.getByText(/Рекомендация Express/)).toHaveCount(0);
  await settle(page);
  await page.screenshot({
    fullPage: false,
    path: reviewScreenshot(testInfo.project.name, "outcome"),
  });
});
