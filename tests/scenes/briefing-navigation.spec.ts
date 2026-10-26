import { expect, test } from "@playwright/test";

test("Back retraces condition then previous result; Continue restarts the condition", async ({
  page,
}) => {
  test.setTimeout(60_000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  const read = async () => {
    for (let step = 0; step < 30; step++) {
      if (!(await page.getByTestId("scene-intro").isVisible())) break;
      await page.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
    }
    await expect(page.getByTestId("scene-intro")).toHaveCount(0);
    await page.locator("[data-pan-viewport]").dispatchEvent("scene-pan-start");
  };
  const confirm = async (id: string) => {
    await page.locator(`[data-hotspot="${id}"]`).scrollIntoViewIfNeeded();
    await page.locator(`[data-hotspot="${id}"]`).click();
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result]")).toBeVisible();
    await page.getByRole("button", { name: "Продолжить", exact: true }).click();
  };
  await read();
  await page.locator('[data-carrier-choice="near"]').click();
  await page.locator("[data-choice-confirm]").click();
  const carrierScores = await page
    .locator("[data-score-key]")
    .allTextContents();
  await page
    .getByRole("button", { name: "Дальше: погрузка", exact: true })
    .click();
  const compactFirst = await page.getByTestId("scene-intro").textContent();
  await read();
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expect(page.getByTestId("scene-intro")).toHaveText(compactFirst!);
  await page.getByRole("button", { name: "Назад", exact: true }).click();
  await expect(
    page.locator('[data-layout="result"][data-carrier="near"]'),
  ).toBeVisible();
  expect(await page.locator("[data-score-key]").allTextContents()).toEqual(
    carrierScores,
  );
  await page
    .getByRole("button", { name: "Дальше: погрузка", exact: true })
    .click();
  await expect(page.getByTestId("scene-intro")).toHaveText(compactFirst!);
  await read();
  await confirm("place-3");
  for (const [scene, previous, option] of [
    ["inventory", "compact", "wms"],
    ["crane", "inventory", "remote"],
    ["lastmile", "crane", "robot"],
  ]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    const firstPart = await page.getByTestId("scene-intro").textContent();
    if (scene === "crane") {
      await page.getByRole("button", { name: "Далее", exact: true }).click();
      const secondPart = await page.getByTestId("scene-intro").textContent();
      await page.reload();
      await expect(page.getByTestId("scene-intro")).toHaveText(secondPart!);
      await page.getByRole("button", { name: "Назад", exact: true }).click();
      await expect(page.getByTestId("scene-intro")).toHaveText(firstPart!);
    }
    await read();
    await page.reload();
    await expect(page.getByTestId("scene-intro")).toHaveCount(0);
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(page.getByTestId("scene-intro")).toBeVisible();
    await expect(page.getByTestId("scene-intro")).toHaveText(firstPart!);
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await page.getByRole("button", { name: "Назад", exact: true }).click();
    await expect(
      page.locator(`[data-scene="${previous}"] [data-result]`),
    ).toBeVisible();
    await page.getByRole("button", { name: "Продолжить", exact: true }).click();
    await expect(page.getByTestId("scene-intro")).toBeVisible();
    await expect(page.getByTestId("scene-intro")).toHaveText(firstPart!);
    await expect(page.locator("[data-hotspot]").first()).toBeHidden();
    await read();
    if (scene !== "lastmile") await confirm(option);
  }
  expect(errors).toEqual([]);
});
