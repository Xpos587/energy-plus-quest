import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

function visiblePart(rect: { x: number; y: number; width: number; height: number }, width: number, height: number) {
  return {
    width: Math.max(0, Math.min(rect.x + rect.width, width) - Math.max(rect.x, 0)),
    height: Math.max(0, Math.min(rect.y + rect.height, height) - Math.max(rect.y, 0)),
  };
}

async function expectBoundedScene(page: Page) {
  const viewport = page.viewportSize()!;
  const scene = page.locator("[data-world-scene]");
  await expect(scene).toHaveCount(1);
  const bounds = await scene.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThan(0);
  expect(bounds!.height).toBeGreaterThan(0);
  const visible = visiblePart(bounds!, viewport.width, viewport.height);
  expect(visible.width).toBeGreaterThanOrEqual(Math.min(64, bounds!.width * 0.5));
  expect(visible.height).toBeGreaterThanOrEqual(Math.min(64, bounds!.height * 0.5));
  return bounds!;
}

async function expectCarrierResultGeometry(page: Page) {
  const viewport = page.viewportSize()!;
  const art = page.locator("[data-result-art]");
  const panel = page.locator("[data-sheet-panel]");
  await expect(art).toHaveCount(1);
  await expect(panel).toBeVisible();
  const a = await art.boundingBox();
  const p = await panel.boundingBox();
  expect(a).not.toBeNull();
  expect(p).not.toBeNull();
  expect(a!.width).toBeGreaterThan(0);
  expect(a!.height).toBeGreaterThan(0);
  expect(p!.width).toBeGreaterThan(0);
  expect(p!.height).toBeGreaterThan(0);
  const imageVisible = visiblePart(a!, viewport.width, viewport.height);
  const panelVisible = visiblePart(p!, viewport.width, viewport.height);
  expect(imageVisible.width).toBeGreaterThanOrEqual(Math.min(80, a!.width * 0.5));
  expect(imageVisible.height).toBeGreaterThanOrEqual(Math.min(80, a!.height * 0.5));
  expect(panelVisible.width).toBeGreaterThanOrEqual(Math.min(80, p!.width * 0.5));
  expect(panelVisible.height).toBeGreaterThanOrEqual(Math.min(32, p!.height * 0.5));
  await art.locator("img").evaluateAll(async nodes => Promise.all(nodes.map(async node => {
    const image = node as HTMLImageElement;
    await image.decode();
    if (!image.naturalWidth || !image.naturalHeight) throw new Error("Carrier result art failed to decode");
  })));
  return a!;
}

async function finishResult(page: Page, label: string) {
  const more = page.getByRole("button", { name: "Читать дальше", exact: true });
  for (let step = 0; step < 40 && await more.isVisible(); step++) await more.click();
  await expect(more).toHaveCount(0);
  const next = page.getByRole("button", { name: label, exact: true });
  await expect(next).toBeInViewport({ ratio: 0.98 });
  await next.click();
}

test("tablet choice preserves prompt and artwork through inspection", async ({ page }) => {
  await page.setViewportSize({ width: 749, height: 794 });
  await page.goto("/scenes.html?scene=compact&parcel=camera&recipient=alva");
  const prompt = page.locator('[data-testid="scene-question"]');
  await expect(prompt).toBeVisible();
  const original = await prompt.textContent();
  const before = await expectBoundedScene(page);
  const marker = page.locator('[data-hotspot="auto"]');
  await marker.focus();
  await expect(marker).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("[data-choice-inspection]")).toBeVisible();
  await expectBoundedScene(page);
  await page.locator("[data-choice-cancel]").click();
  await expect(marker).toBeFocused();
  await expect(prompt).toHaveText(original!);
  expect(await expectBoundedScene(page)).toEqual(before);
  await marker.click();
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-result-reader]")).toBeVisible();
});

for (const width of [734, 749, 900, 1024, 1100, 390, 320]) {
  test(`carrier result artwork and reader remain bounded at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 734 ? 709 : 794 });
    await openCarrier(page, "professional", "alva", "socks");
    await pickCarrier(page, "near");
    await page.locator("[data-choice-confirm]").click();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    const before = await expectCarrierResultGeometry(page);
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    const reading = page.locator("[data-result-reading]");
    const initial = await reading.innerText();
    const more = page.getByRole("button", { name: "Читать дальше", exact: true });
    if (await more.isVisible()) {
      await more.click();
      await expect(reading).not.toHaveText(initial);
      expect(await expectCarrierResultGeometry(page)).toEqual(before);
    }
    await finishResult(page, "Дальше: погрузка");
  });
}

for (const [width, height] of [[320, 568], [375, 667], [734, 709]]) {
  test(`loading artwork and confirmation remain reachable at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=compact&parcel=socks&recipient=alva");
    await expectBoundedScene(page);
    const marker = page.locator('[data-hotspot="auto"]');
    await expect(marker).toBeInViewport({ ratio: 0.98 });
    const markerBounds = await marker.boundingBox();
    expect(markerBounds!.width).toBeGreaterThanOrEqual(43);
    expect(markerBounds!.height).toBeGreaterThanOrEqual(43);
    await marker.click();
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expectBoundedScene(page);
    const confirm = page.locator("[data-choice-confirm]");
    await expect(confirm).toBeInViewport({ ratio: 0.98 });
    const confirmBounds = await confirm.boundingBox();
    expect(confirmBounds!.width).toBeGreaterThanOrEqual(43);
    expect(confirmBounds!.height).toBeGreaterThanOrEqual(43);
    await confirm.click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
  });
}
