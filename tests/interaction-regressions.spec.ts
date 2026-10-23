import { expect, test, type Page } from "@playwright/test";
async function dismiss(page: Page) {
  for (let i = 0; i < 30; i++) {
    const card = page.getByRole("region", {
      name: "Условие задания",
      exact: true,
    });
    if (!(await card.count())) return;
    await card.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  }
  throw Error("Briefing did not finish");
}
for (const scene of ["compact", "inventory"]) {
  test(`${scene}: holding a choice then moving off it cannot start an unowned pan`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera`);
    await dismiss(page);
    const viewport = page.locator("[data-pan-viewport]");
    const before = await viewport.evaluate((el) => el.scrollLeft);
    const choice = page.locator("[data-hotspot]").first();
    await choice.dispatchEvent("pointerdown", {
      pointerId: 1,
      pointerType: "mouse",
      button: 0,
      buttons: 1,
      clientX: 100,
      clientY: 300,
    });
    const held = await viewport.evaluate((el) => el.scrollLeft);
    await viewport.dispatchEvent("pointermove", {
      pointerId: 1,
      pointerType: "mouse",
      buttons: 1,
      movementX: -80,
      clientX: 20,
      clientY: 300,
    });
    expect(await viewport.evaluate((el) => el.scrollLeft)).toBe(held);
    await viewport.dispatchEvent("pointerup", {
      pointerId: 1,
      pointerType: "mouse",
      buttons: 0,
    });
  });
}
for (const scene of ["carrier", "compact", "inventory"]) {
  test(`${scene}: resize preserves manually chosen camera position`, async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(
      scene === "carrier" ? "/" : `/scenes.html?scene=${scene}&parcel=camera`,
    );
    if (scene === "carrier")
      for (const id of ["professional", "alva", "camera"])
        await page.locator(`[data-choice="${id}"]`).click();
    await dismiss(page);
    const viewport = page.locator("[data-pan-viewport]");
    await page.mouse.move(300, 300);
    await page.mouse.down();
    await page.mouse.move(150, 300, { steps: 10 });
    await page.mouse.up();
    await page.waitForTimeout(300);
    const before = await viewport.evaluate((el) => el.scrollLeft);
    expect(before).toBeGreaterThan(50);
    await page.setViewportSize({ width: 430, height: 844 });
    await page.waitForTimeout(350);
    expect(
      Math.abs((await viewport.evaluate((el) => el.scrollLeft)) - before),
    ).toBeLessThan(3);
  });
}

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [1440, 900],
]) {
  test(`full playthrough with cancel, reread and restored results at ${width}`, async ({
    page,
  }) => {
    test.setTimeout(120000);
    await page.setViewportSize({ width, height });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto("/");
    for (const id of ["professional", "alva", "camera"])
      await page.locator(`[data-choice="${id}"]`).click();
    for (const [scene, choice] of [
      ["carrier", "crew"],
      ["compact", "auto"],
      ["inventory", "wms"],
      ["crane", "remote"],
      ["lastmile", "rover"],
    ]) {
      await dismiss(page);
      await page.getByRole("button", { name: "Условие", exact: true }).click();
      await dismiss(page);
      const pick = page.locator(
        scene === "carrier"
          ? `[data-carrier-choice="${choice}"]`
          : `[data-choice-id="${choice}"]`,
      );
      await pick.click();
      await expect(page.locator("[data-choice-cancel]")).toBeInViewport({
        ratio: 1,
      });
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator("[data-choice-confirm]")).toHaveCount(0);
      await pick.click();
      await page.locator("[data-choice-confirm]").click();
      const result = page.locator('[data-layout="result"]');
      await expect(result).toBeVisible();
      const scores = await page.locator("[data-score-key]").allTextContents();
      await page.reload();
      await expect(result).toBeVisible();
      expect(await page.locator("[data-score-key]").allTextContents()).toEqual(
        scores,
      );
      await expect(page.locator("[data-pan-viewport]")).toHaveCount(0);
      const next = page.getByRole("button", {
        name:
          scene === "carrier"
            ? "К следующей сцене"
            : scene === "lastmile"
              ? "Завершить"
              : "Продолжить",
        exact: true,
      });
      await expect(next).toBeInViewport({ ratio: 1 });
      await next.click();
    }
    expect(errors).toEqual([]);
  });
}

test("native touch hold stays dimmed, release and second swipe keep position", async ({
  browser,
}) => {
  const page = await browser.newPage({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
  });
  try {
    await page.goto("/scenes.html?scene=inventory&parcel=camera");
    await dismiss(page);
    const session = await page.context().newCDPSession(page);
    for (let round = 0; round < 2; round++) {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchStart",
        touchPoints: [{ x: 300, y: 300 }],
      });
      for (let x = 280; x >= 150; x -= 10) {
        await session.send("Input.dispatchTouchEvent", {
          type: "touchMove",
          touchPoints: [{ x, y: 300 }],
        });
        await page.evaluate(() => new Promise(requestAnimationFrame));
      }
      await page.waitForTimeout(600);
      await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(1);
      const held = await page
        .locator("[data-pan-viewport]")
        .evaluate((el) => el.scrollLeft);
      await session.send("Input.dispatchTouchEvent", {
        type: "touchEnd",
        touchPoints: [],
      });
      await page.waitForTimeout(700);
      expect(
        Math.abs(
          (await page
            .locator("[data-pan-viewport]")
            .evaluate((el) => el.scrollLeft)) - held,
        ),
      ).toBeLessThan(3);
      await expect(page.locator('[data-scene-panning="true"]')).toHaveCount(0);
    }
  } finally {
    await page.close();
  }
});
