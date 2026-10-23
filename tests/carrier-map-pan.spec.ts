import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const touch of [false, true]) {
  test(`carrier map zooms and pans with ${touch ? "touch" : "mouse and keyboard"}`, async ({
    browser,
  }) => {
    const page = await browser.newPage({
      viewport: { width: 375, height: 667 },
      isMobile: touch,
      hasTouch: touch,
    });
    try {
      await page.emulateMedia({ reducedMotion: "reduce" });
      await openCarrier(page, "professional", "alva", "boat");
      const map = page.locator("[data-map-viewport]");
      const surface = page.locator("[data-map-surface]");
      await expect(map).toHaveAttribute("data-map-scale", "1");
      const box = await map.boundingBox();
      expect(box).not.toBeNull();
      const x = box!.x + box!.width / 2;
      const y = box!.y + box!.height / 2;

      if (touch) {
        const session = await page.context().newCDPSession(page);
        await session.send("Input.dispatchTouchEvent", {
          type: "touchStart",
          touchPoints: [{ x: x - 30, y }, { x: x + 30, y }],
        });
        await session.send("Input.dispatchTouchEvent", {
          type: "touchMove",
          touchPoints: [{ x: x - 90, y }, { x: x + 90, y }],
        });
        await session.send("Input.dispatchTouchEvent", {
          type: "touchEnd",
          touchPoints: [],
        });
      } else {
        await page.mouse.move(x, y);
        await page.mouse.wheel(0, -250);
      }
      await expect.poll(async () => Number(await map.getAttribute("data-map-scale"))).toBeGreaterThan(1);
      const beforePan = await surface.evaluate((el) => (el as HTMLElement).style.transform);

      if (touch) {
        const session = await page.context().newCDPSession(page);
        await session.send("Input.dispatchTouchEvent", {
          type: "touchStart",
          touchPoints: [{ x, y }],
        });
        for (let offset = 20; offset <= 100; offset += 20) {
          await session.send("Input.dispatchTouchEvent", {
            type: "touchMove",
            touchPoints: [{ x: x - offset, y }],
          });
        }
        await session.send("Input.dispatchTouchEvent", {
          type: "touchEnd",
          touchPoints: [],
        });
      } else {
        await page.mouse.move(x, y);
        await page.mouse.down();
        await page.mouse.move(x - 100, y, { steps: 8 });
        await page.mouse.up();
      }
      await expect.poll(() => surface.evaluate((el) => (el as HTMLElement).style.transform)).not.toBe(beforePan);

      if (!touch) {
        await map.focus();
        const beforeKey = await surface.evaluate((el) => (el as HTMLElement).style.transform);
        await page.keyboard.press("ArrowLeft");
        await expect.poll(() => surface.evaluate((el) => (el as HTMLElement).style.transform)).not.toBe(beforeKey);
      }

      await page.getByRole("button", { name: "Вернуть карту", exact: true }).click();
      await expect(map).toHaveAttribute("data-map-scale", "1");
      await page.locator('[data-scene-choice="crew"]').click();
      await expect(page.locator("[data-choice-inspection]")).toBeVisible();
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator('[data-layout="result"][data-carrier="crew"]')).toBeVisible();
    } finally {
      await page.close();
    }
  });
}
