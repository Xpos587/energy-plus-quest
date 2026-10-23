import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

for (const touch of [false, true]) {
  for (const id of ["old", "near", "crew", "old4"]) {
    test(`map truck ${id} stays unpainted, keyboard focus remains: touch=${touch}`, async ({
      browser,
    }) => {
      const context = await browser.newContext({
        baseURL: test.info().project.use.baseURL,
        viewport: { width: 1440, height: 900 },
        hasTouch: touch,
      });
      const page = await context.newPage();
      await openCarrier(page, "professional", "arseniy", "boat");
      const target = page.locator(`[data-carrier-choice="${id}"]`);
      const unpainted = async () => {
        await expect(target).toHaveCSS("background-color", "rgba(0, 0, 0, 0)");
        await expect(target).toHaveCSS("border-width", "0px");
        await expect(target).toHaveCSS("box-shadow", "none");
        await expect(target).not.toHaveCSS("outline-color", "rgb(0, 60, 166)");
      };
      await unpainted();
      await target.hover({ force: true });
      await unpainted();
      await page.locator(`[data-scene-choice="${id}"]`).click();
      await expect(target).toHaveAttribute("aria-pressed", "true");
      await unpainted();
      await page.locator("[data-choice-cancel]").click();
      // A real keyboard transition makes :focus-visible apply to the map button.
      await target.focus();
      await page.keyboard.press("Tab");
      await page.keyboard.press("Shift+Tab");
      await expect(target).toBeFocused();
      await unpainted();
      await expect(target).toHaveCSS("outline-style", "solid");
      await expect(target).not.toHaveCSS("outline-width", "0px");
      await expect(target).toHaveCSS("outline-color", "rgb(255, 122, 51)");
      await page.keyboard.press("Enter");
      await expect(page.locator("[data-choice-inspection]")).toBeVisible();
      await page.locator("[data-choice-cancel]").click();
      if (touch) {
        await page
          .locator("[data-city-video]")
          .evaluate((v: HTMLVideoElement) => v.pause());
        await page.waitForTimeout(600);
        // The floating choice card may cover a truck's center; tap an actually
        // exposed part of its hit area rather than forcing a tap onto the card.
        const point = await target.evaluate((element) => {
          const box = element.getBoundingClientRect();
          for (const fy of [0.5, 0.25, 0.75]) {
            for (const fx of [0.5, 0.25, 0.75]) {
              const x = box.x + box.width * fx;
              const y = box.y + box.height * fy;
              if (document.elementFromPoint(x, y) === element) return { x, y };
            }
          }
          return null;
        });
        if (!point) throw new Error("Truck has no exposed touch target");
        await page.touchscreen.tap(point.x, point.y);
        await expect(page.locator("[data-choice-inspection]")).toBeVisible();
        await unpainted();
      }
      await context.close();
    });
  }
}
