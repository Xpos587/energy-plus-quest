import { expect, test, type Page, type Locator } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function readBriefing(page: Page) {
  const briefing = page.locator("[data-scene-briefing]");
  for (let step = 0; step < 30 && await briefing.getAttribute("data-reading") === "true"; step++)
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function expectTouchTarget(target: Locator, page: Page) {
  const bounds = await target.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThanOrEqual(43);
  expect(bounds!.height).toBeGreaterThanOrEqual(43);
  const viewport = page.viewportSize()!;
  expect(Math.max(0, Math.min(bounds!.x + bounds!.width, viewport.width) - Math.max(bounds!.x, 0))).toBeGreaterThan(0);
  expect(Math.max(0, Math.min(bounds!.y + bounds!.height, viewport.height) - Math.max(bounds!.y, 0))).toBeGreaterThan(0);
  await expect(target).toBeInViewport({ ratio: 0.98 });
}

async function finishResult(page: Page, nextLabel: string) {
  const reader = page.locator("[data-result-reader]");
  await expect(reader).toBeVisible();
  const more = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let step = 0; step < 40 && await more.isVisible(); step++) {
    await expectTouchTarget(more, page);
    await more.click();
  }
  await expect(more).toHaveCount(0);
  const next = reader.getByRole("button", { name: nextLabel, exact: true });
  await expectTouchTarget(next, page);
  await next.click();
}

test("inspect, cancel and confirm across all five scenes without premature outcomes", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await openCarrier(page);

  await pickCarrier(page, "crew");
  await expect(page.locator("[data-score-key]")).toHaveCount(0);
  await expectTouchTarget(page.locator("[data-choice-cancel]"), page);
  await page.locator("[data-choice-cancel]").click();
  await expect(page.locator('[data-carrier-choice="crew"]')).toBeFocused();
  await pickCarrier(page, "crew");
  await expectTouchTarget(page.locator("[data-choice-confirm]"), page);
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-score-key]")).toHaveCount(3);
  await finishResult(page, "Дальше: погрузка");

  for (const [scene, id, next] of [
    ["compact", "place-2", "Дальше: склад"],
    ["inventory", "wms", "Дальше: баржа"],
    ["crane", "remote", "Дальше: последняя миля"],
    ["lastmile", "rover", "К вручению подарка"],
  ]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await readBriefing(page);
    await expect(page.getByTestId("scene-question")).toBeAttached();
    const hotspot = page.locator(`[data-hotspot="${id}"]`);
    await expectTouchTarget(hotspot, page);
    await hotspot.click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    await expectTouchTarget(page.locator("[data-choice-confirm]"), page);
    await page.locator("[data-choice-inspection] h3").press("Escape");
    await expect(hotspot).toBeFocused();
    await hotspot.click();
    await expectTouchTarget(page.locator("[data-choice-confirm]"), page);
    await page.locator("[data-choice-confirm]").click();
    await expect(page.getByTestId("result-copy")).toBeVisible();
    if (scene !== "compact") {
      const image = page.locator("[data-scene-consequence] img");
      await expect.poll(() => image.evaluate((node: HTMLImageElement) => node.complete && node.naturalWidth > 0)).toBe(true);
      expect((await image.getAttribute("alt"))?.trim().length ?? 0).toBeGreaterThan(0);
    }
    await expect(page.locator("[data-score-key]")).toHaveCount(3);
    await finishResult(page, next);
  }
  await expect(page.locator("[data-journey-ending]")).toBeVisible();
  expect(errors).toEqual([]);
});

test("briefing can be reread and a pending carrier answer survives resizing without committing", async ({ page }) => {
  await openCarrier(page);
  await page.getByRole("button", { name: "Задание", exact: true }).click();
  await expect(page.getByTestId("scene-intro")).toBeVisible();
  for (let step = 0; step < 30; step++) {
    const advance = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
    if (!(await advance.isVisible())) break;
    await advance.click();
  }
  await expect(page.getByTestId("scene-intro")).toHaveCount(0);
  await pickCarrier(page, "express");
  await page.setViewportSize({ width: 844, height: 390 });
  await expectTouchTarget(page.locator("[data-choice-confirm]"), page);
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await page.setViewportSize({ width: 320, height: 568 });
  await expectTouchTarget(page.locator("[data-choice-confirm]"), page);
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await page.locator("[data-choice-inspection] h3").press("Escape");
  await expect(page.locator('[data-carrier-choice="express"]')).toBeFocused();
  await expect(page.getByTestId("scene-question")).toBeVisible();
});
