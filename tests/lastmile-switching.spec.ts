import { expect, test } from "@playwright/test";

for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }, { width: 320, height: 568 }, { width: 844, height: 390 }]) {
  test(`last-mile previews switch without cancelling at ${viewport.width}x${viewport.height}`, async ({ page, isMobile }, info) => {
    await page.setViewportSize(viewport);
    await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=khor");
    const condition = page.getByRole("region", { name: "Условие задания", exact: true });
    for (let i = 0; i < 40 && await condition.isVisible(); i++)
      await condition.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
    await expect(condition).toHaveCount(0);
    await expect(page.locator("[data-artwork-ready=false]")).toHaveCount(0);
    const activate = isMobile ? "tap" : "click";
    for (const [kind, id] of [["label", "helicopter"], ["label", "rover"], ["zone", "robot"], ["label", "pipe-carrier"]]) {
      const target = page.locator(`[data-lastmile-${kind}="${id}"]`);
      await expect(target).toHaveAttribute("data-interactive", "true");
      await expect(page.locator(`[data-hotspot="${id}"]`)).toBeEnabled();
      // A vehicle's accessible button may overlap its own label on narrow screens.
      // Use real screen input: either surface must select the same vehicle.
      await expect(target).toBeInViewport();
      const box = (await target.boundingBox())!;
      const x = box.x + box.width / 2, y = box.y + box.height / 2;
      if (isMobile) await page.touchscreen.tap(x, y);
      else await page.mouse.click(x, y);
      await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", id);
      await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    }
    // The same pending preview can be replaced from the accessible vehicle buttons.
    const helicopter = page.locator('[data-hotspot="helicopter"]');
    await helicopter.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", "helicopter");
    await page.locator('[data-lastmile-label="rover"]')[activate]();
    await page.locator("[data-choice-cancel]")[activate]();
    await expect(page.locator('[data-hotspot="rover"]')).toBeFocused();
    await page.locator('[data-lastmile-label="pipe-carrier"]')[activate]();
    await page.screenshot({ path: info.outputPath("lastmile-switching.png") });
    await page.locator("[data-choice-confirm]")[activate]();
    await expect(page.locator('[data-scene-consequence="lastmile-pipe-carrier-boat"]')).toBeVisible();
    await expect(page.locator("[data-lastmile-zone]")).toHaveCount(0);
  });
}
