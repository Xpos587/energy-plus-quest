import { expect, type Page, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

function intersection(rect: { x: number; y: number; width: number; height: number }, width: number, height: number) {
  return {
    width: Math.max(0, Math.min(rect.x + rect.width, width) - Math.max(rect.x, 0)),
    height: Math.max(0, Math.min(rect.y + rect.height, height) - Math.max(rect.y, 0)),
  };
}

async function checkLayout(page: Page, state: string) {
  const viewport = page.viewportSize()!;
  const app = page.locator("[data-scene]").last();
  const sceneId = await app.getAttribute("data-scene");
  const panel = state === "result"
    ? app.locator("[data-sheet-panel]")
    : state === "condition"
      ? page.getByRole("region", { name: "Условие задания", exact: true })
      : state === "inspection"
        ? app.locator("[data-choice-inspection]")
        : app.locator("[data-testid='scene-question'], [data-map-viewport]").first();
  await expect(panel).toHaveCount(1);
  const p = await panel.boundingBox();
  expect(p, `${state} panel bounds`).not.toBeNull();
  expect(p!.width, `${state} panel width`).toBeGreaterThan(0);
  expect(p!.height, `${state} panel height`).toBeGreaterThan(0);
  const visiblePanel = intersection(p!, viewport.width, viewport.height);
  expect(visiblePanel.width, `${state} visible panel width`).toBeGreaterThanOrEqual(Math.min(32, p!.width * 0.5));
  expect(visiblePanel.height, `${state} visible panel height`).toBeGreaterThanOrEqual(Math.min(24, p!.height * 0.5));

  const carrierResult = sceneId === "carrier" && state === "result";
  const carrierChoice = sceneId === "carrier" && state !== "result";
  const art = carrierResult
    ? app.locator("[data-result-art]")
    : carrierChoice
      ? app.locator("[data-map-viewport]")
      : state === "result" && sceneId !== "compact"
        ? app.locator("[data-scene-consequence]")
        : app.locator("[data-scene-world]");
  await expect(art).toHaveCount(1);
  const a = await art.boundingBox();
  expect(a, `${state} artwork bounds`).not.toBeNull();
  expect(a!.width, `${state} artwork width`).toBeGreaterThan(0);
  expect(a!.height, `${state} artwork height`).toBeGreaterThan(0);
  const visibleArt = intersection(a!, viewport.width, viewport.height);
  expect(visibleArt.width, `${state} visible artwork width`).toBeGreaterThanOrEqual(Math.min(32, a!.width * 0.5));
  expect(visibleArt.height, `${state} visible artwork height`).toBeGreaterThanOrEqual(Math.min(24, a!.height * 0.5));

  const header = carrierResult
    ? page.locator("header[data-header-result]")
    : app.locator("[data-scene-header]");
  if (await header.count()) {
    const h = await header.first().boundingBox();
    expect(h, `${state} header bounds`).not.toBeNull();
    expect(h!.width).toBeGreaterThan(0);
    expect(h!.height).toBeGreaterThan(0);
    const visibleHeader = intersection(h!, viewport.width, viewport.height);
    expect(visibleHeader.width).toBeGreaterThan(0);
    expect(visibleHeader.height).toBeGreaterThan(0);
    if (!carrierResult && !carrierChoice && (viewport.height > 500 && (viewport.width > 900 || viewport.width < viewport.height))) {
      const overlap = Math.max(0, Math.min(a!.x + a!.width, h!.x + h!.width) - Math.max(a!.x, h!.x)) *
        Math.max(0, Math.min(a!.y + a!.height, h!.y + h!.height) - Math.max(a!.y, h!.y));
      expect(overlap, `${state} header is separate from artwork`).toBeLessThan(2);
    }
  }

  // Separate-rail/portrait result layouts reserve distinct art and reading regions.
  if (state === "result" && !carrierResult && sceneId !== "compact" && (viewport.width > 900 && viewport.height > 500 || viewport.height > viewport.width)) {
    const overlap = Math.max(0, Math.min(a!.x + a!.width, p!.x + p!.width) - Math.max(a!.x, p!.x)) *
      Math.max(0, Math.min(a!.y + a!.height, p!.y + p!.height) - Math.max(a!.y, p!.y));
    expect(overlap, `${state} result panel does not cover artwork`).toBeLessThan(2);
  }
  const imageSizes = await art.locator("img").evaluateAll(async nodes => {
    await Promise.all(nodes.map(async node => {
      const image = node as HTMLImageElement;
      if (image.getAttribute("src")) await image.decode();
    }));
    return nodes.map(node => {
      const image = node as HTMLImageElement;
      return [image.naturalWidth, image.naturalHeight];
    });
  });
  if (imageSizes.length) {
    for (const [width, height] of imageSizes) {
      expect(width, "artwork has intrinsic width").toBeGreaterThan(0);
      expect(height, "artwork has intrinsic height").toBeGreaterThan(0);
    }
  } else {
    await expect(art).toHaveAttribute("aria-label", /.+/);
  }
}

async function readBriefing(page: Page) {
  const briefing = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && (await briefing.getAttribute("data-reading")) === "true"; n++)
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function readResult(page: Page) {
  const more = page.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 30 && (await more.isVisible()); n++) {
    await expect(more).toBeInViewport({ ratio: 0.98 });
    await more.click();
  }
  await expect(more).toHaveCount(0);
}

async function expectConfirmReachable(page: Page) {
  const confirm = page.locator("[data-choice-confirm]");
  await confirm.scrollIntoViewIfNeeded();
  const bounds = await confirm.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThanOrEqual(43);
  expect(bounds!.height).toBeGreaterThanOrEqual(43);
  const viewport = page.viewportSize()!;
  expect(bounds!.x).toBeGreaterThanOrEqual(-1);
  expect(bounds!.y).toBeGreaterThanOrEqual(-1);
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(viewport.width + 1);
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height + 1);
  await expect(confirm).toBeInViewport({ ratio: 0.98 });
}

test("all five stages retain bounded artwork and panels through delivery", async ({ page }) => {
  test.setTimeout(90_000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "khor", "boat");
  await checkLayout(page, "choice");
  await pickCarrier(page, "express");
  await expectConfirmReachable(page);
  await checkLayout(page, "inspection");
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator('[data-layout="result"]')).toBeVisible();
  await readResult(page);
  await checkLayout(page, "result");
  await page.getByRole("button", { name: "Дальше: погрузка", exact: true }).click();
  for (const [scene, choice, label] of [
    ["compact", "auto", "Дальше: склад"],
    ["inventory", "wms", "Дальше: баржа"],
    ["crane", "remote", "Дальше: последняя миля"],
    ["lastmile", "rover", "К вручению подарка"],
  ]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    const briefing = page.locator("[data-scene-briefing]");
    await expect(briefing).toBeVisible();
    if (await briefing.getAttribute("data-reading") === "true") await checkLayout(page, "condition");
    await readBriefing(page);
    await checkLayout(page, "choice");
    await page.locator(`[data-hotspot="${choice}"]`).click();
    await expectConfirmReachable(page);
    await checkLayout(page, "inspection");
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible({ timeout: 15_000 });
    await readResult(page);
    await checkLayout(page, "result");
    await page.getByRole("button", { name: label, exact: true }).click();
  }
});
