import { expect, test } from "@playwright/test";

const reviewScreenshot = (projectName: string, state: string) =>
  `design/scene-01/review/${state}-${projectName === "mobile-chromium" ? "mobile" : "desktop"}.png`;

test("completes the first scene and always reveals Express", async ({
  page,
}, testInfo) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "ДОСТАВЛЯЕМ РАДОСТЬ" }),
  ).toBeVisible();
  await page.waitForTimeout(1000);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "intro"),
  });

  await page.getByRole("button", { name: /Начать маршрут/ }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "profile"),
  });
  await page.getByRole("button", { name: /Студент/ }).click();
  await page.waitForTimeout(1000);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "recipient"),
  });
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.waitForTimeout(500);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "parcel"),
  });
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await page.waitForTimeout(500);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "briefing"),
  });
  await page.getByRole("button", { name: /Открыть карту/ }).click();

  await expect(
    page.getByRole("heading", { name: "Кому доверите первый участок?" }),
  ).toBeVisible();
  await page.waitForTimeout(700);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "carrier"),
  });
  await page.getByRole("button", { name: /^Машина 2:/ }).click();

  await expect(
    page.getByRole("heading", { name: "Близко — не значит быстро" }),
  ).toBeVisible();
  await page.waitForTimeout(700);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "outcome"),
  });
  await page.getByRole("button", { name: /Сравнить с Express/ }).click();
  await expect(
    page.getByRole("heading", {
      name: "Не искать фуру. Найти лучшее решение.",
    }),
  ).toBeVisible();
  await expect(page.getByText("Рекомендация Express")).toBeVisible();
  await page.waitForTimeout(700);
  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "express"),
  });

  await page.getByRole("button", { name: /Зафиксировать результат/ }).click();
  await expect(
    page.getByRole("heading", { name: "Первый участок пройден" }),
  ).toBeVisible();
  await page.waitForTimeout(700);

  await page.screenshot({
    fullPage: true,
    path: reviewScreenshot(testInfo.project.name, "complete"),
  });
});

test("offers Express as a visible carrier choice", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Начать маршрут/ }).click();
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Арсений/ }).click();
  await page.getByRole("button", { name: /Лодка/ }).click();
  await page.getByRole("button", { name: /Открыть карту/ }).click();

  const expressChoice = page.getByRole("button", {
    name: /Запустить Express/,
  });
  await expect(expressChoice).toBeVisible();
  await expressChoice.click();
  await expect(
    page.getByRole("heading", { name: "Перевозчик найден за два часа" }),
  ).toBeVisible();
});
