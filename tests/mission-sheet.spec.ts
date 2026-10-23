import { expect, test } from "@playwright/test";
test("tablet sheet preserves copy, supports dragging and keeps actions accessible", async ({
  page,
}) => {
  await page.setViewportSize({ width: 749, height: 794 });
  await page.goto("/scenes.html?scene=compact&parcel=camera&recipient=alva");
  const toggle = page.locator("button[aria-expanded]");
  if ((await toggle.getAttribute("aria-expanded")) === "false")
    await toggle.click();
  const original = await page
    .locator('[data-testid="scene-intro"]')
    .textContent();
  await expect(page.locator("[data-progress-caption]")).toBeVisible();
  const box = (await toggle.boundingBox())!;
  await page.mouse.move(box.x + 30, box.y + 15);
  await page.mouse.down();
  await page.mouse.move(box.x + 30, box.y + 65, { steps: 5 });
  await page.mouse.up();
  await expect(toggle).toHaveAttribute("aria-expanded", "false");
  await page.locator("[data-sheet-panel]").evaluate(async (el) => {
    await Promise.all(
      el.getAnimations().map((animation) => animation.finished.catch(() => {})),
    );
  });
  const collapsed = (await toggle.boundingBox())!;
  await page.mouse.move(collapsed.x + 30, collapsed.y + 20);
  await page.mouse.down();
  await page.mouse.move(collapsed.x + 30, collapsed.y - 25, { steps: 5 });
  await page.mouse.up();
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator('[data-testid="scene-intro"]')).toHaveText(
    original!,
  );
  await toggle.focus();
  await page.keyboard.press("Escape");
  await expect(toggle).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(toggle).toHaveAttribute("aria-expanded", "true");
  await expect(page.locator('[data-choice-id="auto"]')).toHaveText(
    "Определить место автоматически",
  );
  await page.locator('[data-choice-id="auto"]').click();
  await expect(
    page.getByRole("button", { name: "Продолжить", exact: true }),
  ).toBeInViewport();
});

for (const width of [734, 749, 900, 1024, 1100, 390, 320]) {
  test(`carrier result fills width and leaves art fixed at ${width}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: width === 734 ? 709 : 794 });
    await page.goto("/");
    for (const id of ["professional", "alva", "socks"])
      await page.locator(`[data-choice="${id}"]`).click();
    await page.locator('[data-carrier-choice="near"]').click();
    await expect(
      page.getByRole("heading", { name: "Счастье уже близко!" }),
    ).toBeVisible();
    const panel = page.locator("[data-sheet-panel]");
    const bounds = (await panel.boundingBox())!;
    expect(bounds.x).toBe(0);
    expect(bounds.width).toBe(width);
    const art = page.locator('[data-outcome-art]');
    const before = await art.boundingBox();
    await page.locator("button[aria-expanded]").click();
    expect(await art.boundingBox()).toEqual(before);
    await expect(
      page.getByRole("button", { name: "К следующей сцене" }),
    ).toBeInViewport();
  });
}

for (const [width, height] of [
  [320, 568],
  [375, 667],
  [734, 709],
]) {
  test(`loading keeps artwork and choices usable at ${width}x${height}`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=compact&parcel=socks&recipient=alva");
    const toggle = page.locator("button[aria-expanded]");
    await expect(toggle).toHaveAttribute("aria-expanded", "true");
    const art = page.locator('[data-world-scene="compact"]');
    const before = await art.boundingBox();
    expect(before!.width).toBe(width);
    await expect(page.locator('[data-choice-id="auto"]')).toBeInViewport();
    await toggle.click();
    expect(await art.boundingBox()).toEqual(before);
    await expect(page.locator('[data-testid="scene-intro"]')).toBeVisible();
    await page.locator('[data-choice-id="auto"]').click();
    expect(await art.boundingBox()).toEqual(before);
    await expect(
      page.getByRole("button", { name: "Продолжить", exact: true }),
    ).toBeInViewport();
  });
}
