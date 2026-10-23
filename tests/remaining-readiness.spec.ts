import { expect, test } from "@playwright/test";

test("small remaining scenes show artwork immediately below the header", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const scene of ["inventory", "crane", "lastmile"]) {
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera&recipient=alva`);
    const art = page.locator("[data-world-plane]");
    const stage = page.locator("[data-world-scene]");
    await expect.poll(async () => {
      const a = await art.boundingBox();
      const s = await stage.boundingBox();
      return Math.abs(a!.y - s!.y);
    }).toBeLessThan(1);
    const before = await art.boundingBox();
    await page.locator("[aria-expanded]").click();
    expect(await art.boundingBox()).toEqual(before);
    await page.locator("[data-choice-id]").first().click();
    const next = page.getByRole("button", { name: scene === "lastmile" ? "Завершить" : "Продолжить", exact: true });
    await expect(next).toBeInViewport({ ratio: 1 });
  }
});
