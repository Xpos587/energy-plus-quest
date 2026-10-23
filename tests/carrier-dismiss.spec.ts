import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

test("map pan keeps the preview until explicit cancel", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "boat");
  await page.locator('[data-carrier-choice="near"]').click();
  await expect(page.locator('[data-choice-inspection="near"]')).toBeVisible();
  // Dispatch a real pointer sequence on exposed map space, away from controls.
  const point = await page.locator('[data-mode="live"]').evaluate((map) => {
    const rect = map.getBoundingClientRect();
    for (let y = Math.max(1, rect.top + 10); y < Math.min(innerHeight, rect.bottom); y += 20)
      for (let x = Math.max(1, rect.left + 10); x < Math.min(innerWidth, rect.right); x += 20) {
        const hit = document.elementFromPoint(x, y);
        if (hit && map.contains(hit) && !hit.closest('button, [data-choice-inspection]')) return { x, y };
      }
    throw new Error("No exposed map space");
  });
  await page.mouse.click(point.x, point.y);
  await expect(page.locator('[data-choice-inspection="near"]')).toBeVisible();
  await page.locator('[data-choice-cancel]').click();
  await expect(page.locator('[data-choice-inspection]')).toHaveCount(0);
  await expect(page.locator('[data-layout="result"]')).toHaveCount(0);
  const map = page.locator('[data-map-viewport]');
  await page.mouse.move(point.x, point.y);
  await page.mouse.wheel(0, -600);
  await expect.poll(async () => Number(await map.getAttribute('data-map-scale'))).toBeGreaterThan(1);
  const surface = page.locator('[data-map-surface]');
  const beforePan = await surface.boundingBox();
  await page.mouse.down();
  await page.mouse.move(point.x + 50, point.y + 40, { steps: 8 });
  await page.mouse.up();
  await expect.poll(async () => {
    const afterPan = await surface.boundingBox();
    return Math.abs(afterPan!.x - beforePan!.x) + Math.abs(afterPan!.y - beforePan!.y);
  }).toBeGreaterThan(10);
  await map.focus();
  await page.keyboard.press('Home');
  await expect(map).toHaveAttribute('data-map-scale', '1');
  await page.locator('[data-scene-choice="crew"]').click();
  await expect(page.locator('[data-choice-inspection="crew"]')).toBeVisible();
  await page.locator('[data-choice-confirm]').click();
  await expect(page.locator('[data-layout="result"][data-carrier="crew"]')).toBeVisible();
});
