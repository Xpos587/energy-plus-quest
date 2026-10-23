import { expect, test } from "@playwright/test";

const choices = ["entrance", "alphabet", "keeper", "wms"] as const;

test("warehouse markers lead to the matching result and allow a new choice", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  for (const [width, height] of [[320, 568], [390, 844], [844, 390], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/scenes.html?scene=inventory&parcel=socks&recipient=alva");
    await page.locator("[data-world-plane] > picture img").evaluate((image: HTMLImageElement) => image.decode());
    const annotations = page.locator("[data-world-plane] > [data-warehouse-annotations]");
    await expect(annotations.locator("[data-warehouse-zone]")).toHaveCount(4);
    await expect(annotations.locator("text, rect")).toHaveCount(0);
    for (const id of choices) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport();
      await marker.click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
      await expect(page.locator(`[data-scene-choice="${id}"]`)).toBeVisible();
      await expect(page.locator("[data-scene-consequence]")).toHaveCount(0);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  }
  expect(errors).toEqual([]);
});

test("warehouse zones are static and the visible keeper target selects its result", async ({ page, isMobile }) => {
  await page.goto("/scenes.html?scene=inventory&parcel=socks&recipient=alva");
  const zone = page.locator('[data-warehouse-zone="keeper"]');
  await expect(zone).toHaveAttribute("data-interactive", "true");
  expect(await zone.evaluate(element => getComputedStyle(element).animationName)).toBe("none");
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(await zone.evaluate(element => getComputedStyle(element).animationName)).toBe("none");
  if (isMobile) {
    // The 44 px keeper marker intentionally covers the small silhouette on phones.
    await page.locator('[data-hotspot="keeper"]').click();
  } else {
    await zone.click();
  }
  await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", "inventory-keeper");
});
