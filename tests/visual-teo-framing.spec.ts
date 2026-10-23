import { expect, test } from "@playwright/test";

for (const [width, height] of [[390, 844], [752, 875], [1440, 900]]) {
  test(`review scene framing at ${width}x${height}`, async ({ page }, info) => {
    await page.setViewportSize({ width, height });
    for (const scene of ["crane", "lastmile"]) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
      const stage = page.locator(`[data-world-scene="${scene}"]`);
      await expect(stage).toBeVisible();
      await page.screenshot({ path: info.outputPath(`${scene}-intro.png`) });
      const next = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
      for (let i = 0; i < 20 && await next.isVisible(); i++) await next.click();
      await page.screenshot({ path: info.outputPath(`${scene}-choice.png`) });
      if (scene === "crane" && width === 1440) {
        await expect(stage).toHaveAttribute("data-crane-overview", "true");
        const bounds = await stage.evaluate((el) => {
          const stage = el.getBoundingClientRect();
          const art = el.querySelector("[data-world-plane]")!.getBoundingClientRect();
          return {
            left: art.left - stage.left,
            top: art.top - stage.top,
            right: art.right - stage.left,
            bottom: art.bottom - stage.top,
            width: stage.width,
            height: stage.height,
          };
        });
        expect(bounds.left).toBeGreaterThanOrEqual(0);
        expect(bounds.top).toBeGreaterThanOrEqual(0);
        expect(bounds.right).toBeLessThanOrEqual(bounds.width);
        expect(bounds.bottom).toBeLessThanOrEqual(bounds.height);
      }
      if (scene === "lastmile") {
        const bounds = await stage.evaluate((el) => {
          const stage = el.getBoundingClientRect();
          const marker = el.querySelector('[data-hotspot="helicopter"]')!.getBoundingClientRect();
          return { top: marker.top - stage.top, bottom: marker.bottom - stage.top, height: stage.height };
        });
        expect(bounds.top).toBeGreaterThanOrEqual(0);
        expect(bounds.bottom).toBeLessThanOrEqual(bounds.height);
      }
    }
  });
}

for (const [width, height] of [[390, 844], [1440, 900]]) {
  test(`lastmile art zones remain selectable at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=alva");
    const stage = page.locator('[data-world-scene="lastmile"]');
    await expect(stage.locator('img[src*="choice-final-"]')).toHaveAttribute("src", /choice-final-(wide|tall)-v10\.webp/);
    for (const id of ["helicopter", "rover", "robot", "pipe-carrier"]) {
      const zone = stage.locator(`[data-lastmile-zone="${id}"]`);
      await expect(zone).toBeAttached();
      await expect(zone).toHaveAttribute("data-interactive", "true");
      const marker = stage.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport({ ratio: 1 });
      await marker.click();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      if (id !== "pipe-carrier") await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=alva");
    }
  });
}
