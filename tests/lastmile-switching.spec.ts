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
    await page.locator("[data-scene-world] img").evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
    await expect(page.locator("[data-lastmile-label]")).toHaveCount(0);
    await page.screenshot({ path: info.outputPath("lastmile-choice.jpg"), type: "jpeg", quality: 65 });
    const selectVehicle = async (id: string) => {
      const target = page.locator(id === "robot" ? `[data-lastmile-zone="${id}"]` : `[data-hotspot="${id}"]`);
      await expect(page.locator(`[data-hotspot="${id}"]`)).toBeEnabled();
      // Real screen input on the vehicle, without a separate name-tag target.
      await expect(target).toBeInViewport();
      const box = (await target.boundingBox())!;
      const x = box.x + box.width / 2, y = box.y + box.height / 2;
      if (isMobile) await page.touchscreen.tap(x, y);
      else await page.mouse.click(x, y);
      await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", id);
      await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    };
    for (const id of ["helicopter", "rover", "robot", "pipe-carrier"]) await selectVehicle(id);
    // The same pending preview can be replaced from the accessible vehicle buttons.
    const helicopter = page.locator('[data-hotspot="helicopter"]');
    await helicopter.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", "helicopter");
    await selectVehicle("rover");
    await page.locator("[data-choice-cancel]")[activate]();
    await expect(page.locator('[data-hotspot="rover"]')).toBeFocused();
    await selectVehicle("pipe-carrier");
    await page.screenshot({ path: info.outputPath("lastmile-switching.png") });
    await page.locator("[data-choice-confirm]")[activate]();
    await expect(page.locator('[data-scene-consequence="lastmile-pipe-carrier-boat"]')).toBeVisible();
    await expect(page.locator("[data-lastmile-zone]")).toHaveCount(0);
  });
}
