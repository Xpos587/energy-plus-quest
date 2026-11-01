import { expect, test } from "@playwright/test";
import { openInventory } from "./inventory-fixture";

test("warehouse picture targets work by pointer and keyboard across viewport sizes", async ({ page }) => {
  for (const [width, height] of [[320, 568], [390, 844], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await openInventory(page, "socks");
    for (const id of ["entrance", "alphabet", "keeper", "wms"]) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport();
      await marker.click();
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
      await expect(marker).toBeVisible();
      await marker.focus();
      await page.keyboard.press("Enter");
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
    }
  }
});
