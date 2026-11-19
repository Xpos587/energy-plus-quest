import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function readBriefing(page: Page) {
  const briefing = page.locator("[data-scene-briefing]");
  if (await briefing.getAttribute("data-reading") === "true") {
    for (let step = 0; step < 30 && await briefing.getAttribute("data-reading") === "true"; step++) {
      const advance = briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
      await expect(advance).toBeVisible();
      await advance.click();
    }
  } else {
    await expect(page.locator('[data-testid="scene-question"]')).toBeVisible();
    if (await page.locator('[data-scene="compact"] [data-scene-briefing]').count())
      await expect(page.locator('[data-scene="compact"] [data-testid="scene-intro"]')).toHaveCount(0);
  }
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function finishResult(page: Page, label: string) {
  const reading = page.locator("[data-result-reading]");
  await expect(page.locator("[data-result-reader]")).toBeVisible();
  const initial = await reading.innerText();
  const more = page.getByRole("button", { name: "Читать дальше", exact: true });
  if (await more.isVisible()) {
    await more.click();
    await expect(reading).not.toHaveText(initial);
  }
  for (let step = 0; step < 40 && await more.isVisible(); step++) await more.click();
  await expect(more).toHaveCount(0);
  const next = page.getByRole("button", { name: label, exact: true });
  await expect(next).toBeInViewport();
  await next.click();
}

async function expectNoHorizontalOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
}

async function expectSceneHeader(page: Page) {
  const header = page.locator("[data-scene-header]").first();
  await expect(header).toBeVisible();
  const bounds = await header.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThan(0);
  expect(bounds!.height).toBeGreaterThan(0);
  expect(bounds!.x).toBeGreaterThanOrEqual(-1);
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual((page.viewportSize()!.width) + 1);
  await expect(page.locator("[data-scene-progress]")).toBeVisible();
  const logos = await header.locator("img").evaluateAll(nodes => nodes.map(node => {
    const r = node.getBoundingClientRect(); return [r.x, r.y, r.width, r.height];
  }));
  expect(logos.length).toBeGreaterThan(0);
  for (const [x, y, width, height] of logos) {
    expect(width).toBeGreaterThan(0);
    expect(height).toBeGreaterThan(0);
    expect(x).toBeGreaterThanOrEqual(-1);
    expect(x + width).toBeLessThanOrEqual((page.viewportSize()!.width) + 1);
    expect(y).toBeGreaterThanOrEqual(-1);
  }
}

async function expectResultHeader(page: Page) {
  const header = page.locator("header[data-header-result]");
  await expect(header).toBeVisible();
  const bounds = await header.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThan(0);
  expect(bounds!.height).toBeGreaterThan(0);
  await expect(header.locator("img")).not.toHaveCount(0);
}

const stages = [
  ["compact", "auto", "Дальше: склад"],
  ["inventory", "wms", "Дальше: баржа"],
  ["crane", "remote", "Дальше: последняя миля"],
  ["lastmile", "pipe-carrier", "К вручению подарка"],
] as const;

test("remaining stages preserve current copy, geometry, scores and accessible choices", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await openCarrier(page, "professional", "alva", "boat");
  await pickCarrier(page, "express");
  await page.locator("[data-choice-confirm]").click();
  await finishResult(page, "Дальше: погрузка");
  for (const [index, [scene, option, label]] of stages.entries()) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await readBriefing(page);
    await expectSceneHeader(page);
    const heading = page.getByRole("heading", { level: 1 });
    await expect(heading).toHaveCount(1);
    await expect(heading).not.toContainText(/Сцена \d/);
    const question = page.locator('[data-testid="scene-question"]');
    await expect(question).toBeVisible();
    expect((await question.innerText()).trim().length).toBeGreaterThan(20);
    await expectNoHorizontalOverflow(page);

    const hotspot = page.locator(`[data-hotspot="${option}"]`);
    await expect(hotspot).toBeVisible();
    expect((await hotspot.getAttribute("aria-label"))?.length ?? 0).toBeGreaterThan(0);
    await hotspot.focus();
    await expect(hotspot).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport();
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    await expect(page.locator("[data-header-result]")).toBeVisible();
    await expectResultHeader(page);
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await expect(page.getByRole("button", { name: "Изменить выбор" })).toBeInViewport();
    await expectNoHorizontalOverflow(page);
    await finishResult(page, label);
  }
  await expect(page.locator("[data-journey-ending]")).toBeVisible();
  expect(errors).toEqual([]);
});

test("back restores compact result, choice copy and usable layout at four viewports", async ({ page }) => {
  await openCarrier(page, "student", "khor", "camera");
  await pickCarrier(page, "near");
  await page.locator("[data-choice-confirm]").click();
  await finishResult(page, "Дальше: погрузка");
  const prompt = page.locator('[data-scene="compact"] [data-testid="scene-question"]');
  await expect(prompt).toBeVisible();
  const choiceCopy = (await prompt.locator("[data-choice-prompt]").innerText()).trim();
  await expect(page.locator('[data-scene="compact"] [data-testid="scene-intro"]')).toHaveCount(0);
  const marker = page.locator('[data-hotspot="place-1"]');
  await marker.click();
  await page.locator("[data-choice-confirm]").click();
  await finishResult(page, "Дальше: склад");
  await expect(page.locator('[data-scene="inventory"]')).toBeVisible();
  await page.getByRole("button", { name: /^К этапу «/ }).click();
  await expect(page.locator('[data-scene="compact"] [data-result-reader]')).toBeVisible();
  await page.getByRole("button", { name: "Изменить выбор" }).click();
  await expect(prompt).toBeVisible();
  await expect(prompt.locator("[data-choice-prompt]")).toHaveText(choiceCopy);
  for (const [width, height] of [[844, 390], [320, 568], [1440, 900], [375, 667]]) {
    await page.setViewportSize({ width, height });
    await expectNoHorizontalOverflow(page);
    await expect(prompt).toBeVisible();
    const bounds = await prompt.boundingBox();
    expect(bounds).not.toBeNull();
    expect(bounds!.x).toBeGreaterThanOrEqual(-1);
    expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(width + 1);
  }
});
