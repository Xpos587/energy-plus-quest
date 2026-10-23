import { expect, type Page, test } from "@playwright/test";

async function readBriefing(page: Page) {
  const next = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
  await expect(next).toBeVisible();
  for (let i = 0; i < 20 && (await next.isVisible()); i++) await next.click();
}
for (const scene of ["compact", "inventory", "crane", "lastmile"]) {
  test(`${scene}: every choice is readable and can be cancelled`, async ({
    page,
  }, info) => {
    await page.goto(`/scenes.html?scene=${scene}&parcel=socks`);
    await readBriefing(page);
    const choices = page.locator("[data-choice-id]:not([data-callout-target])");
    const ids = await choices.evaluateAll((els) =>
      els.map((el) => el.getAttribute("data-choice-id")!),
    );
    for (const id of ids) {
      const choice = page.locator(
        `[data-choice-id="${id}"]:not([data-callout-target])`,
      );
      await choice.click();
      await expect(page.locator("[data-choice-inspection]")).toBeVisible();
      await expect(page.locator("[data-result]")).toHaveCount(0);
      const other = page.locator('[data-choice-id]:not([aria-pressed="true"]):not([data-hotspot]):not([data-callout-target])');
      for (const el of await other.all()) await expect(el).toBeHidden();
      for (const selector of [
        "[data-choice-confirm]",
        "[data-choice-cancel]",
      ]) {
        await expect(page.locator(selector)).toBeInViewport({ ratio: 1 });
        expect(
          (await page.locator(selector).boundingBox())!.height,
        ).toBeGreaterThanOrEqual(44);
      }
      if (id !== "auto" && (await choice.isVisible())) {
        const overlap = await page.evaluate((id) => {
          const card = document
            .querySelector("[data-choice-inspection]")!
            .getBoundingClientRect();
          const marker = document
            .querySelector(
              `[data-choice-id="${id}"]:not([data-callout-target])`,
            )!
            .getBoundingClientRect();
          return (
            Math.max(
              0,
              Math.min(card.right, marker.right) -
                Math.max(card.left, marker.left),
            ) *
            Math.max(
              0,
              Math.min(card.bottom, marker.bottom) -
                Math.max(card.top, marker.top),
            )
          );
        }, id);
        expect(overlap).toBe(0);
      }
      await page.screenshot({ path: info.outputPath(`${scene}-${id}.png`) });
      await page.locator("[data-choice-cancel]").click();
      await expect(choice).toBeFocused();
    }
    await page
      .locator(`[data-choice-id="${ids.at(-1)}"]:not([data-callout-target])`)
      .click();
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result]")).toBeVisible();
    await expect(page.locator("[data-choice-inspection]")).toHaveCount(0);
  });
}
test("lastmile: helicopter visible below header without panning on phones", async ({
  page,
}, info) => {
  test.skip((page.viewportSize()?.width ?? 0) > 600);
  await page.goto("/scenes.html?scene=lastmile&parcel=camera");
  await readBriefing(page);
  await expect(page.locator('[data-hotspot="helicopter"]')).toBeInViewport({
    ratio: 1,
  });
  const rotor = await page
    .locator("[data-helicopter-main-rotor]")
    .boundingBox();
  expect(rotor!.x).toBeGreaterThanOrEqual(0);
  expect(rotor!.x + rotor!.width).toBeLessThanOrEqual(
    page.viewportSize()!.width,
  );
  expect(rotor!.y).toBeGreaterThan(115);
  await page.screenshot({ path: info.outputPath("helicopter-overview.png") });
});

test("carrier: inspect every option, resize, cancel and confirm explicitly", async ({
  page,
}, info) => {
  await page.goto("/");
  for (const id of ["professional", "alva", "camera"])
    await page.locator(`[data-choice="${id}"]`).click();
  await readBriefing(page);
  for (const id of ["crew", "near", "old", "express"]) {
    const choice = page.locator(`[data-carrier-choice="${id}"]`);
    await choice.click();
    await expect(page.locator("[data-score-key]")).toHaveCount(0);
    for (const other of await page
      .locator('[data-carrier-choice]:not([aria-pressed="true"])')
      .all())
      await expect(other).toBeHidden();
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
      ratio: 1,
    });
    await expect(page.locator("[data-choice-cancel]")).toBeInViewport({
      ratio: 1,
    });
    await page.screenshot({ path: info.outputPath(`carrier-${id}.png`) });
    await page.locator("[data-choice-inspection] h3").press("Escape");
    await expect(choice).toBeFocused();
  }
  await page.locator('[data-carrier-choice="crew"]').click();
  await page.setViewportSize({ width: 320, height: 568 });
  await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
    ratio: 1,
  });
  await page.setViewportSize({ width: 844, height: 390 });
  await expect(page.locator("[data-choice-confirm]")).toBeInViewport({
    ratio: 1,
  });
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-score-key]")).toHaveCount(3);
});

test('compact: camera starts at the cab on the right and can pan left', async ({ page }, info) => {
  await page.goto('/scenes.html?scene=compact&parcel=camera');
  const stage = page.locator('[data-world-scene="compact"]');
  await expect(stage).toBeVisible();
  await expect.poll(() => stage.evaluate(el => Math.abs(el.scrollWidth - el.clientWidth - el.scrollLeft))).toBeLessThanOrEqual(1);
  await readBriefing(page);
  await page.screenshot({ path: info.outputPath('compact-cab-start.png') });
  const max = await stage.evaluate(el => el.scrollWidth - el.clientWidth);
  if (max > 0) {
    await stage.focus();
    await stage.press('Home');
    await stage.press('ArrowLeft');
    await expect.poll(() => stage.evaluate(el => el.scrollLeft)).toBeLessThan(max);
  }
});

test('result card fills available width with balanced gutters after resizing', async ({page},info)=>{
  await page.goto('/');
  for(const id of ['professional','alva','boat']) await page.locator(`[data-choice="${id}"]`).click();
  await readBriefing(page);
  await page.locator('[data-carrier-choice="near"]').click();
  await page.locator('[data-choice-confirm]').click();
  const card=page.locator('[data-sheet-panel]');
  for(const [width,height] of [[1920,1080],[2560,1440],[1280,650],[844,390],[751,709],[734,709],[390,844],[320,568]]) {
    await page.setViewportSize({width,height});
    await expect(card).toBeInViewport({ratio:1});
    const box=await card.boundingBox();
    if(!box) throw new Error('Result card is missing');
    const gutter=width>750?20:12;
    expect(box.x).toBeCloseTo(gutter,0);
    expect(width-box.x-box.width).toBeCloseTo(gutter,0);
    for(const button of await card.getByRole('button').all()) {
      if(await button.isVisible()) await expect(button).toBeInViewport({ratio:1});
    }
    expect(await card.evaluate(el=>el.scrollWidth<=el.clientWidth+1)).toBe(true);
    const art=await page.locator('[data-result-art]').boundingBox();
    expect(art?.height).toBe(height);
    await page.screenshot({path:info.outputPath(`result-card-${width}.png`)});
  }
});
