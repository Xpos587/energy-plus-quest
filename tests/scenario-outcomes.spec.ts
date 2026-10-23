import { expect, test } from "@playwright/test";

for (const scene of ["inventory", "crane", "lastmile"]) {
  test(`${scene}: every result is fullscreen and directly pannable without a preview dialog`, async ({
    page,
  }, info) => {
    const ids =
      scene === "inventory"
        ? ["entrance", "alphabet", "keeper", "wms"]
        : scene === "crane"
          ? ["rush", "wait", "petr", "remote"]
          : ["helicopter", "rover", "robot", "pipe-carrier"];
    for (const id of ids) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
      const next = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
      await expect(next).toBeVisible();
      for (let i = 0; i < 30 && (await next.isVisible()); i++)
        await next.click();
      await page
        .locator(`[data-choice-id="${id}"]:not([data-callout-target])`)
        .click();
      await page.locator("[data-choice-confirm]").click();
      await expect(
        page.getByRole("button", {
          name: "Рассмотреть результат",
          exact: true,
        }),
      ).toHaveCount(0);
      await expect(page.locator("[data-outcome-preview]")).toHaveCount(0);
      const art = page.locator("[data-scene-consequence]");
      const image = art.locator("img");
      await image.evaluate((el: HTMLImageElement) => el.decode());
      const box = await image.boundingBox();
      const viewport = page.viewportSize()!;
      expect(box!.y).toBeLessThanOrEqual(0);
      expect(box!.y + box!.height).toBeGreaterThanOrEqual(viewport.height - 1);
      expect(box!.x).toBeLessThanOrEqual(0);
      expect(box!.x + box!.width).toBeGreaterThanOrEqual(viewport.width - 1);
      const max = await art.evaluate((el) => el.scrollWidth - el.clientWidth);
      if (max > 2) {
        await expect
          .poll(() =>
            art.evaluate((el) =>
              Math.abs(el.scrollLeft - (el.scrollWidth - el.clientWidth) / 2),
            ),
          )
          .toBeLessThanOrEqual(1);
        await art.focus();
        await art.press("ArrowRight");
        await expect
          .poll(() => art.evaluate((el) => el.scrollLeft))
          .toBeGreaterThan(max / 2 + 1);
        await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(1);
      }
      await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(0);
      await expect(page.locator('[data-sheet-panel]')).toHaveCSS('opacity', '1');
      await page.screenshot({ path: info.outputPath(`${scene}-${id}.png`) });
      await expect(page.locator("[data-result]")).toBeVisible();
    }
  });
}

test("near-fit 16:10 scenes do not instruct users to pan a few pixels", async ({
  page,
}) => {
  test.skip(page.viewportSize()!.width !== 1440);
  for (const scene of ["crane", "lastmile"]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera`);
    const next = page.getByRole("button", { name: /^(Далее|К выбору)$/ });
    await expect(next).toBeVisible();
    for (let i = 0; i < 30 && (await next.isVisible()); i++) await next.click();
    await expect(
      page.getByRole("status").filter({ hasText: "Листайте сцену" }),
    ).toHaveCount(0);
  }
});

test("carrier results fill the viewport and pan directly, including automatic selection", async ({
  page,
}, info) => {
  for (const id of ["crew", "near", "old", "express"]) {
    await page.goto("/");
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    for (const item of ["professional", "alva", "camera"])
      await page.locator(`[data-choice="${item}"]`).click();
    const next = page.getByRole("button", {
      name: /^(Далее|К сцене|К выбору)$/,
    });
    await expect(next).toBeVisible();
    for (let i = 0; i < 30 && (await next.isVisible()); i++) await next.click();
    await page.locator(`[data-carrier-choice="${id}"]`).click();
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.getByRole("button", { name: "Рассмотреть результат", exact: true }),
    ).toHaveCount(0);
    const art = page.locator("[data-result-art]");
    await art.locator("img").evaluate((el: HTMLImageElement) => el.decode());
    const box = await art.locator("img").boundingBox();
    expect(box!.y).toBeLessThanOrEqual(0);
    expect(box!.height).toBeGreaterThanOrEqual(page.viewportSize()!.height);
    const max = await art.evaluate((el) => el.scrollWidth - el.clientWidth);
    if (max > 2) {
      await expect
        .poll(() =>
          art.evaluate((el) =>
            Math.abs(el.scrollLeft - (el.scrollWidth - el.clientWidth) / 2),
          ),
        )
        .toBeLessThanOrEqual(1);
      await art.focus();
      await art.press("ArrowLeft");
      await expect
        .poll(() => art.evaluate((el) => el.scrollLeft))
        .toBeLessThan(max / 2 - 1);
      await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(1);
    }
    await expect(
      page.getByRole("button", { name: "К следующей сцене", exact: true }),
    ).toBeInViewport({ ratio: 1 });
    await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(0);
    await expect(page.locator('[data-sheet-panel]')).toHaveCSS('opacity', '1');
    await page.screenshot({ path: info.outputPath(`carrier-${id}.png`) });
  }
});

test('context-specific artwork also fills every edge', async ({ page }, info) => {
  for (const [scene, id, parcel, recipient] of [
    ['inventory', 'alphabet', 'camera', 'alva'],
    ['inventory', 'alphabet', 'socks', 'alva'],
    ['lastmile', 'pipe-carrier', 'camera', 'alva'],
    ['lastmile', 'pipe-carrier', 'socks', 'alva'],
    ['lastmile', 'helicopter', 'camera', 'arseniy'],
  ]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}`);
    const next=page.getByRole('button',{name:/^(Далее|К выбору)$/});
    await expect(next).toBeVisible();
    for(let i=0;i<30 && await next.isVisible();i++) await next.click();
    await page.locator(`[data-choice-id="${id}"]:not([data-callout-target])`).click();
    await page.locator('[data-choice-confirm]').click();
    const image=page.locator('[data-scene-consequence] img');
    await image.evaluate((el:HTMLImageElement)=>el.decode());
    const box=await image.boundingBox();
    const viewport=page.viewportSize()!;
    expect(box!.y).toBeLessThanOrEqual(0);
    expect(box!.y+box!.height).toBeGreaterThanOrEqual(viewport.height-1);
    expect(box!.x).toBeLessThanOrEqual(0);
    expect(box!.x+box!.width).toBeGreaterThanOrEqual(viewport.width-1);
    await page.screenshot({path:info.outputPath(`${scene}-${id}-${parcel}-${recipient}.png`)});
  }
});
