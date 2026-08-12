import { expect, type Page, test } from "@playwright/test";

async function expectNoPageScroll(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientHeight: document.documentElement.clientHeight,
    clientWidth: document.documentElement.clientWidth,
    scrollHeight: document.documentElement.scrollHeight,
    scrollWidth: document.documentElement.scrollWidth,
  }));

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(
    dimensions.clientWidth + 1,
  );
  expect(dimensions.scrollHeight).toBeLessThanOrEqual(
    dimensions.clientHeight + 1,
  );
}

async function expectControlsInsideViewport(page: Page) {
  const controls = page.getByRole("button").filter({ visible: true });
  const count = await controls.count();

  for (let index = 0; index < count; index += 1) {
    await expect(controls.nth(index)).toBeInViewport();
  }
}

async function expectScoreIcons(page: Page) {
  for (const key of ["energy", "empathy", "efficiency"]) {
    const score = page.locator(`[data-score-key="${key}"]`).first();
    await expect(score).toBeVisible();
    await expect(score.locator("img")).toBeVisible();
  }
}

async function expectResultScoresDoNotOverlap(page: Page) {
  const resultScores = page.locator('[data-layout="result"] [data-score-key]');

  for (let index = 0; index < (await resultScores.count()); index += 1) {
    const score = resultScores.nth(index);
    const labelBox = await score.locator("span").boundingBox();
    const valueBox = await score.locator("strong").boundingBox();

    expect(labelBox).not.toBeNull();
    expect(valueBox).not.toBeNull();
    const overlapWidth =
      Math.min(
        (labelBox?.x ?? 0) + (labelBox?.width ?? 0),
        (valueBox?.x ?? 0) + (valueBox?.width ?? 0),
      ) - Math.max(labelBox?.x ?? 0, valueBox?.x ?? 0);
    const overlapHeight =
      Math.min(
        (labelBox?.y ?? 0) + (labelBox?.height ?? 0),
        (valueBox?.y ?? 0) + (valueBox?.height ?? 0),
      ) - Math.max(labelBox?.y ?? 0, valueBox?.y ?? 0);

    expect(overlapWidth > 0.5 && overlapHeight > 0.5).toBe(false);
  }
}

test("keeps the complete route inside one viewport", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "ДОСТАВЛЯЕМ РАДОСТЬ" }),
  ).toBeVisible();
  await expectNoPageScroll(page);

  await page.getByRole("button", { name: /Начать маршрут/ }).click();
  await expectScoreIcons(page);
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Студент/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Альва/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Открыть карту/ }).click();

  await expect(
    page.getByRole("heading", { name: "Кому доверите первый участок?" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Запустить Express/ }),
  ).toBeVisible();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);

  await page.getByRole("button", { name: /Запустить Express/ }).click();
  await expect(
    page.getByRole("heading", { name: "Перевозчик найден за два часа" }),
  ).toBeVisible();
  await expectResultScoresDoNotOverlap(page);
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Разобрать подбор Express/ }).click();
  await expect(
    page.getByRole("heading", {
      name: "Не искать фуру. Найти лучшее решение.",
    }),
  ).toBeVisible();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Зафиксировать результат/ }).click();
  await expect(
    page.getByRole("heading", { name: "Первый участок пройден" }),
  ).toBeVisible();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
});
