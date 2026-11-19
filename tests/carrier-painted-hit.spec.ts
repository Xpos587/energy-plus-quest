import { expect, test } from "@playwright/test";
import manifest from "../src/components/cityV4Manifest.json" with { type: "json" };
import { openCarrier } from "./helpers/open-preparation";

for (const touch of [false, true]) {
  test(`${touch ? "touch" : "mouse"} selects the painted carrier dial and cab`, async ({ browser, baseURL }) => {
    const page = await browser.newPage({ baseURL, hasTouch: touch, viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
    try {
      // Sample the actual painted points, not the button whose geometry is under test.
      await page.addInitScript((frames) => {
        const points: Record<string, [number, number]> = {};
        Object.defineProperty(window, "carrierPaint", { value: points });
        const proto = CanvasRenderingContext2D.prototype;
        const arc = proto.arc;
        proto.arc = function (x, y, r, start, end, ccw) {
          if (r === 15 && x === 0 && y === -21 && this.canvas.hasAttribute("data-carrier-effects")) {
            const transform = this.getTransform();
            // Near is the first dial drawn; capture each new frame's first dial.
            points.dial ??= [transform.e, transform.f - 32 * transform.d];
          }
          return arc.call(this, x, y, r, start, end, ccw);
        };
        const clear = proto.clearRect;
        proto.clearRect = function (x, y, w, h) {
          if (this.canvas.hasAttribute("data-carrier-effects")) { delete points.dial; delete points.cab; }
          return clear.call(this, x, y, w, h);
        };
        const draw = proto.drawImage;
        proto.drawImage = function (...args: unknown[]) {
          const [image, x, y, w, h, dx, dy, dw, dh] = args;
          if (image instanceof HTMLImageElement && image.src.includes("trucks-wide") && frames.some(f => f[0] === x && f[1] === y && f[2] === w && f[3] === h) && this.canvas.hasAttribute("data-carrier-effects")) {
            const p = this.getTransform().transformPoint(new DOMPoint(Number(dx) + Number(dw) * .5, Number(dy) + Number(dh) * .35));
            points.cab = [p.x, p.y];
          }
          Reflect.apply(draw, this, args);
        };
      }, manifest.plates.wide.sprites.trucks["near-cab"]);
      for (const part of ["dial", "cab", "moving dial"] as const) {
        const moving = part === "moving dial";
        if (moving) await page.emulateMedia({ reducedMotion: "no-preference" });
        await openCarrier(page);
        const surface = page.locator("[data-map-surface]");
        await expect(surface).toHaveAttribute("data-motion-reason", moving ? "ready" : "reduced-motion");
        if (moving) await expect(surface).toHaveAttribute("data-motion-state", "playing");
        // Compare the stable pose at the maximum user zoom, too.
        if (part === "cab") {
          await page.locator('[data-carrier-choice="near"]').focus();
          for (let n = 0; n < 5; n++) await page.locator("[data-map-viewport]").press("+");
          await expect(page.locator("[data-map-viewport]")).toHaveAttribute("data-map-scale", "4");
        }
        const paintedPoint = () => page.waitForFunction((key) => {
          const { carrierPaint } = window as Window & { carrierPaint?: Record<string, [number, number]> };
          const p = carrierPaint?.[key];
          const canvas = document.querySelector<HTMLCanvasElement>("[data-carrier-effects]");
          if (!p || !canvas) return null;
          const box = canvas.getBoundingClientRect();
          return { x: box.left + p[0] * box.width / canvas.width, y: box.top + p[1] * box.height / canvas.height };
        }, moving ? "dial" : part).then(handle => handle.jsonValue());
        if (moving) {
          const initial = await paintedPoint();
          await expect.poll(paintedPoint).not.toEqual(initial);
        }
        const point = await paintedPoint();
        if (touch) await page.touchscreen.tap(point.x, point.y);
        else await page.mouse.click(point.x, point.y);
        await expect(page.locator('[data-carrier-inspection="near"]'), part).toBeVisible();
      }
    } finally {
      await page.close();
    }
  });
}
