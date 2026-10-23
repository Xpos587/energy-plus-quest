import { expect, test } from "@playwright/test";

test("hint repeats until pan and a stationary held gesture keeps cards transparent", async ({
  page,
}, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/scenes.html?scene=compact&parcel=camera");
  const condition = page.getByRole("region", {
    name: "Условие задания",
    exact: true,
  });
  for (let i = 0; i < 30 && (await condition.isVisible()); i++) {
    await condition.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  }
  const hint = page.getByRole("status").filter({ hasText: "Листайте сцену" });
  const viewport = page.locator("[data-pan-viewport]");
  await expect(hint).toBeVisible();
  await expect(page.getByTestId("scene-question")).toHaveCSS("opacity", "1");
  await expect(hint).toHaveCSS("opacity", "1");
  await page.waitForTimeout(6200);
  await expect(hint).toBeVisible();
  const before = await viewport.evaluate((el) => el.scrollLeft);
  await expect
    .poll(() => viewport.evaluate((el) => el.scrollLeft))
    .not.toBe(before);
  const size = page.viewportSize();
  if (!size) throw new Error("Missing viewport size");
  const x = Math.round(size.width * 0.7),
    y = Math.round(size.height * 0.5);
  const session = await page.context().newCDPSession(page);
  if (info.project.name === "mobile-chromium") {
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x, y }],
    });
    for (let dx = 10; dx <= 100; dx += 10) {
      await session.send("Input.dispatchTouchEvent", {
        type: "touchMove",
        touchPoints: [{ x: x - dx, y }],
      });
      await page.evaluate(() => new Promise(requestAnimationFrame));
    }
  } else {
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x - 100, y, { steps: 10 });
  }
  await expect(hint).toHaveCount(0);
  await page.waitForTimeout(1100);
  const question = page.getByTestId("scene-question");
  await expect(question).toHaveCSS("opacity", "0.28");
  await page.screenshot({ path: info.outputPath("held-pan.png") });
  if (info.project.name === "mobile-chromium")
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
  else await page.mouse.up();
  await expect(question).toHaveCSS("opacity", "1");
  await expect(hint).toHaveCount(0);
});
