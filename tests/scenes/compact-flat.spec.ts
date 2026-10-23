import { expect, test } from "@playwright/test";

test("flat loading spaces stay visible, distinct and touchable at every viewport", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/scenes.html?scene=compact&parcel=camera");
  await page.getByRole("button", { name: "К сцене", exact: true }).click();
  const stage = page.locator('[data-world-scene="compact"]');
  await expect(stage.locator('[data-cargo-view="side-2d"]')).toBeVisible();
  const buttons = stage.locator("button[data-hotspot]");
  await expect(buttons).toHaveCount(4);
  const boxes = [];
  for (const button of await buttons.all()) {
    await button.focus();
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
    const box = await button.boundingBox();
    if (!box) throw new Error("Loading control has no bounds");
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.height).toBeGreaterThanOrEqual(44);
    expect(box.x).toBeGreaterThanOrEqual(0);
    expect(box.x + box.width).toBeLessThanOrEqual(
      page.viewportSize()?.width ?? 0,
    );
    expect(
      await button.evaluate((node) => {
        const b = node.getBoundingClientRect();
        return node.contains(
          document.elementFromPoint(b.x + b.width / 2, b.y + b.height / 2),
        );
      }),
    ).toBe(true);
    boxes.push({
      ...box,
      x: box.x + (await stage.evaluate((node) => node.scrollLeft)),
    });
  }
  for (const [i, a] of boxes.entries()) {
    for (const b of boxes.slice(i + 1)) {
      expect(
        a.x + a.width <= b.x ||
          b.x + b.width <= a.x ||
          a.y + a.height <= b.y ||
          b.y + b.height <= a.y,
      ).toBe(true);
    }
  }
  await page.screenshot({
    path: testInfo.outputPath("compact-flat.png"),
    fullPage: true,
  });
  const second = stage.locator('[data-hotspot="place-2"]');
  await second.focus();
  await expect(stage.locator('[data-loading-zone="place-2"]')).toHaveAttribute(
    "data-focused",
    "true",
  );
  await expect(second).toHaveAttribute("aria-pressed", "false");
  await second.press("Enter");
  await expect(second).toHaveAttribute("aria-pressed", "true");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(errors).toEqual([]);
});
