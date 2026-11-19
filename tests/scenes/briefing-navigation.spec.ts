import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "../helpers/open-preparation";

async function finishBriefing(page: Page) {
  const briefing = page.locator("[data-scene-briefing]");
  for (let step = 0; step < 30 && await briefing.getAttribute("data-reading") === "true"; step++) {
    const advance = briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
    await expect(advance).toBeVisible();
    await advance.click();
  }
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function finishResult(page: Page, label: string) {
  const more = page.getByRole("button", { name: "Читать дальше", exact: true });
  for (let step = 0; step < 40 && await more.isVisible(); step++) await more.click();
  await expect(more).toHaveCount(0);
  const next = page.getByRole("button", { name: label, exact: true });
  await expect(next).toBeVisible();
  await next.click();
}

async function confirmChoice(page: Page, id: string, label: string) {
  const hotspot = page.locator(`[data-hotspot="${id}"]`);
  await expect(hotspot).toBeVisible();
  await hotspot.click();
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expect(page.locator("[data-result-reader]")).toHaveCount(0);
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-result-reader]")).toBeVisible();
  const resultText = await page.locator("[data-result-reading]").innerText();
  const scores = await page.locator("[data-score-key]").allTextContents();
  expect(scores).toHaveLength(3);
  await finishResult(page, label);
  return { resultText, scores };
}

test("current briefing, persistence and back navigation preserve previous results", async ({ page }) => {
  test.setTimeout(60_000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await openCarrier(page, "professional", "alva", "camera");
  await finishBriefing(page);
  await pickCarrier(page, "near");
  await page.locator("[data-choice-confirm]").click();
  const carrierScores = await page.locator("[data-score-key]").allTextContents();
  await finishResult(page, "Дальше: погрузка");

  const compactQuestion = page.locator('[data-scene="compact"] [data-testid="scene-question"]');
  await expect(compactQuestion).toBeVisible();
  await expect(page.locator('[data-scene="compact"] [data-testid="scene-intro"]')).toHaveCount(0);
  const compactPrompt = await compactQuestion.innerText();
  expect(compactPrompt.length).toBeGreaterThan(30);
  const { resultText: compactResultText, scores: compactScores } = await confirmChoice(page, "place-3", "Дальше: склад");

  const inventoryBriefing = page.locator('[data-scene="inventory"] [data-scene-briefing]');
  await expect(inventoryBriefing).toHaveAttribute("data-reading", "true");
  const inventoryCopy = await page.getByTestId("scene-intro").textContent();
  await finishBriefing(page);
  await page.reload();
  await expect(page.locator('[data-scene="inventory"] [data-scene-briefing]')).toHaveAttribute("data-reading", "false");
  await expect(page.locator('[data-scene="inventory"] [data-testid="scene-intro"]')).toHaveCount(0);
  await page.getByRole("button", { name: "Задание", exact: true }).click();
  await expect(page.locator('[data-scene="inventory"] [data-scene-briefing]')).toHaveAttribute("data-reading", "true");
  await expect(page.getByTestId("scene-intro")).toHaveText(inventoryCopy!);
  await finishBriefing(page);

  await page.getByRole("button", { name: /^К этапу «/ }).click();
  await expect(page.locator('[data-scene="compact"] [data-result-reader]')).toBeVisible();
  expect(compactScores).toHaveLength(3);
  expect(await page.locator("[data-score-key]").allTextContents()).toEqual(compactScores);
  await expect(page.locator("[data-result-reading]")).toContainText(compactResultText.slice(0, 30));
  await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
  await page.getByRole("button", { name: /^К этапу «/ }).click();
  await expect(page.locator('[data-layout="result"][data-carrier="near"]')).toBeVisible();
  expect(await page.locator("[data-score-key]").allTextContents()).toEqual(carrierScores);
  expect(errors).toEqual([]);
});
