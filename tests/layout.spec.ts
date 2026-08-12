import { expect, type Page, test } from "@playwright/test";

async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }));

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(
    dimensions.clientWidth + 1,
  );
}

test("keeps the complete route usable without horizontal overflow", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "ДОСТАВЛЯЕМ РАДОСТЬ" }),
  ).toBeVisible();
  await expectNoHorizontalOverflow(page);

  await page.getByRole("button", { name: /Начать маршрут/ }).click();
  await page.getByRole("button", { name: /Студент/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await page.getByRole("button", { name: /Открыть карту/ }).click();

  await expect(
    page.getByRole("heading", { name: "Кому доверите первый участок?" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Запустить Express/ }),
  ).toBeVisible();
  await expectNoHorizontalOverflow(page);

  await page.getByRole("button", { name: /Запустить Express/ }).click();
  await expect(
    page.getByRole("heading", { name: "Перевозчик найден за два часа" }),
  ).toBeVisible();
  await page.getByRole("button", { name: /Разобрать подбор Express/ }).click();
  await expect(
    page.getByRole("heading", {
      name: "Не искать фуру. Найти лучшее решение.",
    }),
  ).toBeVisible();
  await expectNoHorizontalOverflow(page);
  await page.getByRole("button", { name: /Зафиксировать результат/ }).click();
  await expect(
    page.getByRole("heading", { name: "Первый участок пройден" }),
  ).toBeVisible();
  await expectNoHorizontalOverflow(page);
});
