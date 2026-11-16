import { expect, test } from "@playwright/test";
import { mapCarrierIds } from "../src/game/carrierFacts";
import { openCarrier } from "./helpers/open-preparation";

for (const viewport of [
  { width: 320, height: 568 },
  { width: 568, height: 320 },
]) {
  test(`moving trucks accept real touch at ${viewport.width}x${viewport.height}`, async ({
    browser,
    baseURL,
  }, info) => {
    const page = await browser.newPage({
      baseURL,
      viewport,
      isMobile: true,
      hasTouch: true,
    });
    try {
      await page.emulateMedia({ reducedMotion: "no-preference" });
      const errors: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      await openCarrier(page, "professional", "khor", "socks");
      const map = page.locator("[data-map-viewport]");
      await expect(page.locator("[data-map-surface]")).toHaveAttribute(
        "data-motion-state",
        "playing",
      );
      const touch = await page.context().newCDPSession(page);
      for (const id of mapCarrierIds) {
        const truck = page.locator(`[data-carrier-choice="${id}"]`);
        let hit: { x: number; y: number } | null = null;
        // Reveal cropped trucks by dragging the map, never by focusing a hidden target.
        for (let attempt = 0; attempt < 8; attempt++) {
          const position = await truck.evaluate((element) => {
            const rig = element.getBoundingClientRect();
            const frame = element
              .closest("[data-map-viewport]")
              ?.getBoundingClientRect();
            if (!frame) throw new Error("Truck must be inside the map");
            const left = Math.max(0, frame.left),
              right = Math.min(innerWidth, frame.right);
            const top = Math.max(0, frame.top),
              bottom = Math.min(innerHeight, frame.bottom);
            const x =
              (Math.max(left, rig.left) + Math.min(right, rig.right)) / 2;
            const y =
              (Math.max(top, rig.top) + Math.min(bottom, rig.bottom)) / 2;
            const hit =
              x > left &&
              x < right &&
              y > top &&
              y < bottom &&
              element.contains(document.elementFromPoint(x, y));
            return {
              hit: hit ? { x, y } : null,
              start: { x: (left + right) / 2, y: (top + bottom) / 2 },
              dx: Math.max(
                -(right - left) * 0.3,
                Math.min(
                  (right - left) * 0.3,
                  (left + right - rig.left - rig.right) / 2,
                ),
              ),
              dy: Math.max(
                -(bottom - top) * 0.3,
                Math.min(
                  (bottom - top) * 0.3,
                  (top + bottom - rig.top - rig.bottom) / 2,
                ),
              ),
            };
          });
          if (position.hit) {
            hit = position.hit;
            break;
          }
          await touch.send("Input.dispatchTouchEvent", {
            type: "touchStart",
            touchPoints: [position.start],
          });
          for (let step = 1; step <= 6; step++) {
            await touch.send("Input.dispatchTouchEvent", {
              type: "touchMove",
              touchPoints: [
                {
                  x: position.start.x + (position.dx * step) / 6,
                  y: position.start.y + (position.dy * step) / 6,
                },
              ],
            });
          }
          await touch.send("Input.dispatchTouchEvent", {
            type: "touchEnd",
            touchPoints: [],
          });
          await expect(page.locator("[data-choice-inspection]")).toHaveCount(0);
        }
        if (!hit) throw new Error(`${id} must be reachable by touch`);
        await touch.send("Input.dispatchTouchEvent", {
          type: "touchStart",
          touchPoints: [hit],
        });
        await touch.send("Input.dispatchTouchEvent", {
          type: "touchEnd",
          touchPoints: [],
        });
        await expect(
          page.locator(`[data-carrier-inspection="${id}"]`),
        ).toBeVisible();
        await expect(page.locator("[data-carrier-tap-hint]")).toHaveCSS(
          "opacity",
          "0",
        );
        await expect(page.locator('[data-layout="result"]')).toHaveCount(0);
        await page.screenshot({
          path: info.outputPath(`${id}-touch-preview.png`),
        });
        await page.locator("[data-choice-cancel]").tap();
        await expect(page.locator("[data-choice-inspection]")).toHaveCount(0);
        await expect(map).toHaveAttribute("data-map-scale", "1");
      }
      expect(errors).toEqual([]);
    } finally {
      await page.close();
    }
  });
}
