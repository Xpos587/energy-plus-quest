import { expect, test } from "@playwright/test";
import { openCarrier, openPreparation } from "./helpers/open-preparation";

test("preparation keeps selections and progress visible as the story advances", async ({
  page,
}) => {
  await openPreparation(page);
  for (const [id, heading] of [
    ["professional", "Кому отправим подарок?"],
    ["alva", "Что отправим Майме?"],
    ["camera", "Выбор перевозчика"],
  ]) {
    await page.locator(`[data-choice="${id}"]`).click();
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  }
  await expect(page.locator("header [data-selection-context]")).toHaveCount(3);
  await expect(page.locator("[data-scene-progress]")).toHaveAttribute(
    "aria-label",
    "Этап 1 из 5: Перевозчик",
  );
  await page.getByRole("button", { name: "К выбору подарка" }).click();
  await expect(
    page.getByRole("heading", { name: "Что отправим Майме?" }),
  ).toBeVisible();
  await expect(page.locator('[data-preparation-step="parcel"]')).toBeVisible();
  await expect(page.getByRole("button", { name: "Лодка" })).toBeVisible();
});

test("city map plays behind five distinct carrier choices", async ({
  page,
}) => {
  await openCarrier(page);
  await expect(page.locator("[data-carrier-choice]")).toHaveCount(4);
  await expect(page.locator("[data-scene-choice]")).toHaveCount(5);
  const video = page.locator("[data-city-video]");
  await expect(video).toBeVisible();
  await expect
    .poll(() =>
      video.evaluate((element: HTMLVideoElement) => element.currentTime),
    )
    .toBeGreaterThan(0);
  await expect(video).toHaveJSProperty("controls", false);
});

for (const [id, scores] of [
  ["old", ["0", "-3", "-3"]],
  ["near", ["+1", "0", "-2"]],
  ["crew", ["-3", "+3", "+4"]],
  ["old4", ["0", "-3", "-3"]],
  ["express", ["-1", "+5", "+5"]],
] as const) {
  test(`${id} confirms the approved score and permits a revised carrier choice`, async ({
    page,
  }) => {
    await openCarrier(page);
    await page.locator(`[data-scene-choice="${id}"]`).click();
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator(`[data-layout="result"][data-carrier="${id}"]`),
    ).toBeVisible();
    await expect(page.locator("[data-score-key] strong")).toHaveText([
      ...scores,
    ]);
    await expect(page.locator(`[data-outcome-art="${id}"]`)).toBeVisible();
    await page.getByRole("button", { name: "Назад к машинам" }).click();
    await expect(page.locator("[data-scene-choice]")).toHaveCount(5);
  });
}

test("near result keeps the approved delay and cause for the selected gift", async ({
  page,
}) => {
  await openCarrier(page, "professional", "alva", "camera");
  await page.locator('[data-scene-choice="near"]').click();
  await page.locator("[data-choice-confirm]").click();
  const result = page.locator("[data-result-reader]");
  await expect(result).toContainText("фотоаппарат с опозданием на три дня");
  await expect(result).toContainText("рядом с офисом");
  await expect(result).toContainText("водитель ехал очень медленно");
});
