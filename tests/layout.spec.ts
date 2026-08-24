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

test("keeps the playable route inside one viewport", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Доставляем радость/ }),
  ).toBeVisible();
  await expectNoPageScroll(page);

  await page.getByRole("button", { name: /Начать игру/ }).click();
  await expectScoreIcons(page);
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);

  const initialViewport = page.viewportSize();
  if (initialViewport && initialViewport.width <= 760) {
    await expect(page.getByAltText("Энергия+", { exact: true })).toBeVisible();

    const headerHeight = await page
      .locator("header")
      .evaluate((element) => element.getBoundingClientRect().height);
    const scoreMetrics = await page
      .locator("[data-score-key]")
      .evaluateAll((elements) =>
        elements.map((element) => {
          const box = element.getBoundingClientRect();
          const icon = element.querySelector("img")?.getBoundingClientRect();
          const value = element
            .querySelector("strong")
            ?.getBoundingClientRect();

          return {
            height: box.height,
            iconValueGap:
              icon && value
                ? value.left - icon.right
                : Number.POSITIVE_INFINITY,
          };
        }),
      );

    expect(headerHeight).toBeLessThanOrEqual(62);
    for (const metric of scoreMetrics) {
      expect(metric.height).toBeLessThanOrEqual(44);
      expect(metric.iconValueGap).toBeLessThanOrEqual(6);
    }
  }

  if (initialViewport && initialViewport.width > 1380) {
    const brandBox = await page
      .locator('[class*="brandCluster"]')
      .boundingBox();
    const progressBox = await page
      .getByRole("navigation", { name: "Прогресс сцены" })
      .boundingBox();
    const progressOverflow = await page
      .getByRole("navigation", { name: "Прогресс сцены" })
      .evaluate((element) => element.scrollWidth - element.clientWidth);

    expect(brandBox).not.toBeNull();
    expect(progressBox).not.toBeNull();
    expect((brandBox?.x ?? 0) + (brandBox?.width ?? 0)).toBeLessThanOrEqual(
      progressBox?.x ?? 0,
    );
    expect(progressOverflow).toBeLessThanOrEqual(1);
  }

  await page.getByRole("button", { name: /Студент/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Альва/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);

  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Express: Автоподбор Express" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /(?:Машин(?:а|ы)|Express)/ }),
  ).toHaveCount(4);

  const viewport = page.viewportSize();
  if (viewport && viewport.width > 760 && viewport.width <= 1380) {
    const scoreBottom = await page
      .locator("[data-score-key]")
      .evaluateAll((elements) =>
        Math.max(
          ...elements.map((element) => element.getBoundingClientRect().bottom),
        ),
      );
    const progressTop = await page
      .getByRole("navigation", { name: "Прогресс сцены" })
      .evaluate((element) => element.getBoundingClientRect().top);

    expect(scoreBottom).toBeLessThanOrEqual(progressTop);
  }

  if (
    viewport &&
    viewport.width > 760 &&
    viewport.width <= 1120 &&
    viewport.height <= 700
  ) {
    const missionBottom = await page
      .locator('[class*="missionBar"]')
      .evaluate((element) => element.getBoundingClientRect().bottom);
    const carrierTops = await page
      .locator('section[aria-label="Карта доступных перевозчиков"] button')
      .evaluateAll((elements) =>
        elements.map((element) => element.getBoundingClientRect().top),
      );

    expect(Math.min(...carrierTops)).toBeGreaterThanOrEqual(missionBottom);
  }
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);

  await page
    .getByRole("button", { name: "Express: Автоподбор Express" })
    .click();
  await expect(
    page.getByRole("heading", { name: "Перевозчик найден за два часа" }),
  ).toBeVisible();
  await expectResultScoresDoNotOverlap(page);
  if (viewport && viewport.width > 760) {
    const resultPanel = await page
      .locator('[data-layout="result"] [data-carrier="express"]')
      .boundingBox();
    expect(resultPanel).not.toBeNull();
    expect(resultPanel?.x ?? 0).toBeGreaterThanOrEqual(viewport.width * 0.6);
  }

  if (viewport && viewport.width <= 760 && viewport.height <= 720) {
    const panelTop = await page
      .locator('[data-layout="result"] [class*="resultPanel"]')
      .evaluate((element) => element.getBoundingClientRect().top);
    const artworkBottom = await page
      .locator('[data-layout="result"] [class*="outcomeBackdrop"]')
      .evaluate((element) => element.getBoundingClientRect().bottom);
    expect(panelTop).toBeGreaterThanOrEqual(artworkBottom - 2);
  }
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
  await expect(
    page.getByRole("button", { name: /Назад к машинам/ }),
  ).toBeVisible();

  await page.getByRole("button", { name: /Назад к машинам/ }).click();
  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);

  await page.getByRole("button", { name: /Назад/ }).first().click();
  await expect(
    page.getByRole("heading", { name: "Что будет в посылке?" }),
  ).toBeVisible();
  await expectControlsInsideViewport(page);
  await expectNoPageScroll(page);
});
