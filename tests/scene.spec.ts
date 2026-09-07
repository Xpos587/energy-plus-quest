import { expect, type Page, test } from "@playwright/test";

async function playReviewPath(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await page.getByRole("button", { name: /Альва/ }).click();
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
}

const cases = [
  ["№1", "old", "Маршрут потребовал больше времени"],
  ["№2", "near", "Близко — не значит быстро"],
  ["№3", "crew", "Два водителя лучше одного"],
  ["№4", "old", "Маршрут потребовал больше времени"],
  ["Подобрать автоматически", "express", "Перевозчик найден за два часа"],
] as const;

test("preserves brand UI and incremental context with four scene steps", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator("header [data-selection-context]")).toHaveCount(0);
  const logos = page.locator("header img");
  const logoWidths = await logos.evaluateAll((images) =>
    images.map((image) => image.getBoundingClientRect().width),
  );
  expect(Math.abs(logoWidths[0] - logoWidths[1])).toBeLessThan(1);
  expect(
    await page
      .locator('[data-step="profile"]')
      .evaluate(
        (element) => getComputedStyle(element, "::after").backgroundImage,
      ),
  ).toBe("none");
  await expect(
    page.getByRole("heading", { name: "Кто отправится в путь?" }),
  ).toHaveCSS("font-family", /EPQ Normalidad Proxy/);
  await page.getByRole("button", { name: /Профессионал/ }).click();
  await expect(page.locator("header [data-selection-context]")).toHaveCount(1);
  await expect(
    page.getByRole("button", { name: "Хор", exact: true }),
  ).toBeVisible();
  await expect(page.getByText(/с языка хантов|самец оленя/)).toHaveCount(0);
  await page.getByRole("button", { name: /Альва/ }).click();
  await expect(page.locator("header [data-selection-context]")).toHaveCount(2);
  await page.getByRole("button", { name: /Фотоаппарат/ }).click();
  const progress = page.getByRole("navigation", { name: "Этапы доставки" });
  await expect(progress.locator("[data-progress-step]")).toHaveCount(5);
  await expect(progress.locator('[aria-current="step"] > span')).toHaveText(
    "Перевозчик",
  );
  for (const label of [
    "Перевозчик",
    "Загрузка",
    "Склад",
    "Баржа",
    "Последняя миля",
  ]) {
    await expect(progress.getByText(label, { exact: true })).toBeVisible();
  }
  expect(
    await page
      .locator("header [data-selection-context]")
      .evaluateAll((es) =>
        es.map((e) => e.getAttribute("data-selection-context")),
      ),
  ).toEqual(["profile", "recipient", "parcel"]);
});

test("carrier has five neutral panel actions, static labels and no back or hotspots", async ({
  page,
}) => {
  await playReviewPath(page);
  await expect(page.locator("[data-carrier-hotspot]")).toHaveCount(0);
  await expect(page.locator("[data-truck-number]")).toHaveCount(4);
  await expect(page.getByText("Забрать груз", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Назад", exact: true }),
  ).toHaveCount(1);
  await expect(page.getByRole("button")).toHaveCount(6);
  for (const [label] of cases)
    await expect(
      page.getByRole("button", { name: label, exact: true }),
    ).toBeVisible();
  const colors = await page
    .getByRole("button")
    .evaluateAll((es) => es.map((e) => getComputedStyle(e).backgroundColor));
  expect(new Set(colors).size).toBe(1);
  const before = await page.locator('[data-truck="truck-2"]').boundingBox();
  await page.locator('[data-truck="truck-2"]').click({ force: true });
  await expect(
    page.getByRole("heading", { name: "Выберите транспорт для подарка" }),
  ).toBeVisible();
  expect(before).not.toBeNull();
});

for (const [control, outcome, title] of cases) {
  test(`${control} retains ${outcome} score mapping and return context`, async ({
    page,
  }) => {
    await playReviewPath(page);
    await page.getByRole("button", { name: control, exact: true }).click();
    await expect(page.getByRole("heading", { name: title })).toBeVisible();
    await expect(
      page.locator(`[data-outcome-art="${outcome}"]:visible`),
    ).toBeVisible();
    await expect(
      page.locator('[data-layout="result"] [data-selection-context]'),
    ).toHaveCount(0);
    await expect(page.locator("header [data-selection-context]")).toHaveCount(
      3,
    );
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await expect(page.locator("[data-score-key] svg")).toHaveCount(3);
    await expect(page.locator("[data-score-key] i")).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "К следующей сцене" }),
    ).toBeDisabled();
    await page.getByRole("button", { name: "Назад к машинам" }).click();
    await expect(page.locator("header [data-selection-context]")).toHaveCount(
      3,
    );
    await expect(page.getByRole("button")).toHaveCount(6);
  });
}

test("near uses the forecast and signed deltas without fictional continuation", async ({
  page,
}) => {
  await playReviewPath(page);
  await page.getByRole("button", { name: "№2", exact: true }).click();
  await expect(
    page.getByText("К чему приведёт выбор", { exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByText(
      "Перевозчик выбран; груз ещё ждёт загрузки. Машина рядом, но водитель едет неторопливо. Если темп сохранится, Девочка Альва получит фотоаппарат на три дня позже.",
      { exact: true },
    ),
  ).toBeVisible();
  for (const [key, score] of [
    ["energy", "+1"],
    ["empathy", "0"],
    ["efficiency", "-2"],
  ]) {
    await expect(page.locator(`[data-score-key="${key}"] strong`)).toHaveText(
      score,
    );
  }
  await expect(
    page.getByRole("button", { name: "К следующей сцене" }),
  ).toBeDisabled();
  await expect(
    page.getByText("Продолжение пока недоступно", { exact: true }),
  ).toHaveCount(0);
});
