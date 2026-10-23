import { expect, test } from "@playwright/test";

test("warehouse picture markers and text choices remain usable across viewport sizes", async ({ page }) => {
  for (const [width, height] of [[320, 568], [390, 844], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=inventory&parcel=socks&recipient=alva");
    await page.locator("[data-world-plane] picture img").evaluate((image: HTMLImageElement) => image.decode());
    for (const id of ["entrance", "alphabet", "keeper", "wms"]) {
      const marker = page.locator(`[data-hotspot="${id}"]`);
      await expect(marker).toBeInViewport();
      await marker.click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
      const answer = page.locator(`[data-scene-choice="${id}"]`);
      await expect(answer).toBeVisible();
      await answer.click();
      await expect(page.locator("[data-scene-consequence]")).toHaveAttribute("data-scene-consequence", id === "alphabet" ? "inventory-alphabet-socks" : `inventory-${id}`);
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
    }
  }
});
