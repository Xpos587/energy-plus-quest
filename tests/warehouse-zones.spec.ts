import { expect, test } from "@playwright/test";
import { openInventory } from "./inventory-fixture";

const choices = ["entrance", "alphabet", "keeper", "wms"] as const;

test("warehouse markers lead to the matching result and allow a new choice", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  for (const [width, height] of [[320, 568], [390, 844], [844, 390], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openInventory(page, "socks");
    const annotations = page.locator("[data-world-plane] > [data-warehouse-annotations]");
    await expect(annotations.locator("[data-warehouse-zone]")).toHaveCount(4);
    await expect(annotations.locator("text, rect:not([mask], mask > rect)")).toHaveCount(0);
    for (const id of choices) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport();
      await marker.click();
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
      await expect(page.locator(`[data-hotspot="${id}"]`)).toBeVisible();
      await expect(page.locator("[data-scene-consequence]")).toHaveCount(0);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
  }
  expect(errors).toEqual([]);
});

test("phones choose on the warehouse itself, with no button row (call 05.11)", async ({ page }) => {
  for (const [width, height] of [[320, 568], [390, 844], [440, 956]]) {
    await page.setViewportSize({ width, height });
    await openInventory(page);
    await expect(page.locator("[data-scene-choice]")).toHaveCount(0);
    for (const id of choices) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport();
      const box = await marker.boundingBox();
      expect(box!.width).toBeGreaterThanOrEqual(44);
      expect(box!.height).toBeGreaterThanOrEqual(44);
      await marker.click();
      await expect(page.locator("[data-choice-confirm]")).toBeInViewport({ ratio: 1 });
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-boat" : `inventory-${id}`);
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});

test("warehouse zones are static and the visible keeper target selects its result", async ({ page }) => {
  await openInventory(page, "socks");
  const zone = page.locator('[data-warehouse-zone="keeper"]');
  await expect(zone).toHaveAttribute("data-interactive", "true");
  expect(await zone.evaluate(element => getComputedStyle(element).animationName)).toBe("none");
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(await zone.evaluate(element => getComputedStyle(element).animationName)).toBe("none");
  // The invisible 44 px keyboard button sits over the small silhouette and selects the same choice.
  await page.locator('[data-hotspot="keeper"]').click();
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", "inventory-keeper");
});
