import { expect, test, type Page } from "@playwright/test";

function visibleIntersection(rect: { x: number; y: number; width: number; height: number }, viewport: { width: number; height: number }) {
  return {
    width: Math.max(0, Math.min(rect.x + rect.width, viewport.width) - Math.max(rect.x, 0)),
    height: Math.max(0, Math.min(rect.y + rect.height, viewport.height) - Math.max(rect.y, 0)),
  };
}

async function expectSceneGeometry(page: Page, result = false) {
  const viewport = page.viewportSize()!;
  const frame = page.locator("[data-scene-world]");
  await expect(frame).toHaveCount(1);
  const f = await frame.boundingBox();
  expect(f).not.toBeNull();
  expect(f!.width).toBeGreaterThan(0);
  expect(f!.height).toBeGreaterThan(0);
  const visibleFrame = visibleIntersection(f!, viewport);
  expect(visibleFrame.width).toBeGreaterThanOrEqual(Math.min(80, f!.width * 0.5));
  expect(visibleFrame.height).toBeGreaterThanOrEqual(Math.min(80, f!.height * 0.5));

  const header = result ? page.locator("header[data-header-result]") : page.locator("[data-scene-header]");
  await expect(header.first()).toBeVisible();
  const h = await header.first().boundingBox();
  expect(h).not.toBeNull();
  expect(h!.width).toBeGreaterThan(0);
  expect(h!.height).toBeGreaterThan(0);
  const visibleHeader = visibleIntersection(h!, viewport);
  expect(visibleHeader.width).toBeGreaterThan(0);
  expect(visibleHeader.height).toBeGreaterThan(0);

  const artwork = result
    ? frame.locator("[data-scene-consequence] img")
    : frame.locator("[data-world-scene] img");
  await expect(artwork).not.toHaveCount(0);
  const imageBounds = await artwork.first().boundingBox();
  expect(imageBounds).not.toBeNull();
  expect(imageBounds!.width).toBeGreaterThan(0);
  expect(imageBounds!.height).toBeGreaterThan(0);
  const visibleArt = visibleIntersection(imageBounds!, viewport);
  expect(visibleArt.width).toBeGreaterThan(0);
  expect(visibleArt.height).toBeGreaterThan(0);
  await artwork.evaluateAll(async nodes => {
    await Promise.all(nodes.map(async node => {
      const image = node as HTMLImageElement;
      if (image.getAttribute("src")) await image.decode();
      if (!image.naturalWidth || !image.naturalHeight)
        throw new Error(`Artwork failed to load: ${image.currentSrc || image.src}`);
    }));
  });

  if (result) {
    const panel = page.locator("[data-sheet-panel]");
    const p = await panel.boundingBox();
    expect(p).not.toBeNull();
    expect(p!.width).toBeGreaterThan(0);
    expect(p!.height).toBeGreaterThan(0);
    const overlap = Math.max(0, Math.min(imageBounds!.x + imageBounds!.width, p!.x + p!.width) - Math.max(imageBounds!.x, p!.x)) *
      Math.max(0, Math.min(imageBounds!.y + imageBounds!.height, p!.y + p!.height) - Math.max(imageBounds!.y, p!.y));
    expect(overlap, "result image and reading panel occupy separate authored rows").toBeLessThan(2);
  }
}

async function finishResult(page: Page, label: string) {
  const more = page.getByRole("button", { name: "Читать дальше", exact: true });
  for (let step = 0; step < 40 && await more.isVisible(); step++) await more.click();
  await expect(more).toHaveCount(0);
  await expect(page.getByRole("button", { name: label, exact: true })).toBeVisible();
}

async function expectTouchTarget(target: import("@playwright/test").Locator, page: Page) {
  const bounds = await target.boundingBox();
  expect(bounds).not.toBeNull();
  expect(bounds!.width).toBeGreaterThanOrEqual(43);
  expect(bounds!.height).toBeGreaterThanOrEqual(43);
  const viewport = page.viewportSize()!;
  expect(Math.max(0, Math.min(bounds!.x + bounds!.width, viewport.width) - Math.max(bounds!.x, 0))).toBeGreaterThan(0);
  expect(Math.max(0, Math.min(bounds!.y + bounds!.height, viewport.height) - Math.max(bounds!.y, 0))).toBeGreaterThan(0);
  await expect(target).toBeInViewport({ ratio: 0.98 });
}

test("small remaining scenes show bounded artwork and confirm real choices", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const [scene, choice, label] of [
    ["inventory", "wms", "Дальше: баржа"],
    ["crane", "remote", "Дальше: последняя миля"],
    ["lastmile", "robot", "К вручению подарка"],
  ]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera&recipient=alva`);
    const briefing = page.locator("[data-scene-briefing]");
    await expect(briefing).toBeVisible();
    for (let step = 0; step < 30 && await briefing.getAttribute("data-reading") === "true"; step++)
      await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
    await expect(briefing).toHaveAttribute("data-reading", "false");
    await expectSceneGeometry(page);

    const hotspot = page.locator(`[data-hotspot="${choice}"]`);
    await expectTouchTarget(hotspot, page);
    await hotspot.click();
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expectSceneGeometry(page);
    const confirm = page.locator("[data-choice-confirm]");
    await expectTouchTarget(confirm, page);
    await confirm.click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    await expectSceneGeometry(page, true);
    await finishResult(page, label);
  }
});
