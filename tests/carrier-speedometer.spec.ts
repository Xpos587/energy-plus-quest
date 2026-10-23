import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const [width, height] of [
  [320, 568],
  [390, 844],
  [844, 390],
  [1440, 900],
]) {
  test(`instrument prototype preserves confirmation at ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openCarrier(page, "professional", "arseniy", "boat");
    await page.goto("/?carrier-ui=speedometer");
    for (const [id, _speed, year] of [
      ["old", "36", "2011"],
      ["near", "17", "2021"],
      ["crew", "48", "2024"],
      ["old4", "27", "2013"],
    ]) {
      await page.locator(`[data-scene-choice="${id}"]`).click();
      const inspection = page.locator("[data-choice-inspection]");
      await expect(inspection.locator("[data-speedometer]")).toBeVisible();
      await expect(inspection).toContainText("Темп движения");
      await expect(inspection).not.toContainText("км/ч");
      await expect(inspection).toContainText(year);
      for (const attr of ["data-choice-cancel", "data-choice-confirm"])
        await expect(page.locator(`[${attr}]`)).toBeInViewport({ ratio: 1 });
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator(`[data-scene-choice="${id}"]`)).toBeFocused();
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      await expect(
        page.locator(`[data-layout="result"][data-carrier="${id}"]`),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Назад к машинам", exact: true })
        .click();
    }
    await page.locator('[data-scene-choice="express"]').click();
    await expect(page.locator("[data-speedometer]")).toHaveCount(0);
    await page.locator("[data-choice-cancel]").click();
    await page.locator('[data-scene-choice="crew"]').click();
    await expect(page.locator("[data-choice-inspection]")).toContainText(
      "Два водителя",
    );
    await page.locator("[data-choice-confirm]").click();
    await expect(
      page.locator('[data-layout="result"][data-carrier="crew"]'),
    ).toBeVisible();
  });
}

for (const [touch, prototype] of [
  [false, false],
  [true, false],
  [false, true],
  [true, true],
]) {
  test(`${prototype ? "prototype" : "main"} keeps manual ${touch ? "pinch and touch pan" : "wheel and mouse pan"} from inspection`, async ({
    browser,
  }) => {
    const page = await browser.newPage({
      viewport: { width: 390, height: 844 },
      isMobile: touch,
      hasTouch: touch,
    });
    try {
      await page.emulateMedia({ reducedMotion: "reduce" });
      await openCarrier(page, "professional", "arseniy", "boat");
      await page.goto(prototype ? "/?carrier-ui=speedometer" : "/");
      await page.locator('[data-scene-choice="crew"]').click();
      const map = page.locator("[data-map-viewport]");
      const surface = page.locator("[data-map-surface]");
      await expect(map).toHaveAttribute("data-map-scale", "2.4");
      const r = await map.boundingBox();
      if (!r) throw new Error("map missing");
      const x = r.x + r.width / 2,
        y = r.y + r.height / 2;
      const cdp = touch ? await page.context().newCDPSession(page) : undefined;
      if (cdp) {
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchStart",
          touchPoints: [
            { x: x - 30, y },
            { x: x + 30, y },
          ],
        });
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchMove",
          touchPoints: [
            { x: x - 70, y },
            { x: x + 70, y },
          ],
        });
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchEnd",
          touchPoints: [],
        });
      } else {
        await page.mouse.move(x, y);
        await page.mouse.wheel(0, -120);
      }
      await expect
        .poll(async () => Number(await map.getAttribute("data-map-scale")))
        .toBeGreaterThan(2.4);
      const before = await surface.evaluate(
        (el) => (el as HTMLElement).style.transform,
      );
      if (cdp) {
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchStart",
          touchPoints: [{ x, y }],
        });
        for (const offset of [20, 40, 60, 80])
          await cdp.send("Input.dispatchTouchEvent", {
            type: "touchMove",
            touchPoints: [{ x: x - offset, y }],
          });
        await cdp.send("Input.dispatchTouchEvent", {
          type: "touchEnd",
          touchPoints: [],
        });
      } else {
        await page.mouse.move(x, y);
        await page.mouse.down();
        await page.mouse.move(x - 80, y, { steps: 8 });
        await page.mouse.up();
      }
      await expect
        .poll(() =>
          surface.evaluate((el) => (el as HTMLElement).style.transform),
        )
        .not.toBe(before);
      // Existing pan behavior releases camera inspection; both variants must agree.
      await expect(
        page.locator('[data-carrier-inspection="crew"]'),
      ).toHaveCount(0);
      await page.locator('[data-scene-choice="crew"]').click();
      await expect(
        page.locator('[data-carrier-inspection="crew"]'),
      ).toBeVisible();
      await expect(page.locator("[data-speedometer]")).toHaveCount(1);
    } finally {
      await page.close();
    }
  });
}

test("the main inspection includes the live instrument without a parameter", async ({
  page,
}) => {
  await openCarrier(page);
  await page.locator('[data-scene-choice="near"]').click();
  await expect(page.locator("[data-speedometer]")).toBeVisible();
  await expect(page.locator("[data-choice-inspection]")).toContainText(
    "Темп движения",
  );
});
