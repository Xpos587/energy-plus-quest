import { expect, test } from "@playwright/test";

for (const scene of ["crane", "lastmile", "inventory"]) {
  test(`${scene}: inspection keeps alternative labels visible`, async ({
    page,
  }) => {
    await page.goto(`/scenes.html?scene=${scene}&parcel=camera&recipient=alva`);
    for (let step = 0; step < 20; step++) {
      if (!(await page.getByTestId("scene-intro").isVisible())) break;
      await page.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
    }
    await page.locator("[data-pan-viewport]").dispatchEvent("scene-pan-start");
    const markers = page.locator("[data-hotspot]");
    const widths = await markers.evaluateAll((items) =>
      items.map((item) => item.getBoundingClientRect().width),
    );
    await markers.first().scrollIntoViewIfNeeded();
    await markers.first().click();
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expect(
      page.locator('[data-hotspot][aria-pressed="false"]').first(),
    ).toBeDisabled();
    const state = await markers.evaluateAll((items) =>
      items.map((item) => ({
        selected: item.getAttribute("aria-pressed") === "true",
        visibility: getComputedStyle(item).visibility,
        opacity: Number(getComputedStyle(item).opacity),
        width: item.getBoundingClientRect().width,
        caption: getComputedStyle(item.lastElementChild!).display,
      })),
    );
    for (const [index, item] of state.entries()) {
      if (item.selected) continue;
      expect(item.visibility).toBe("visible");
      expect(item.caption).not.toBe("none");
      expect(item.opacity).toBeGreaterThan(0);
      expect(item.opacity).toBeLessThan(1);
      expect(item.width).toBeCloseTo(widths[index], 0);
    }
    await page.screenshot({
      path: `.tmp-work/choice-labels-${scene}-${test.info().project.name}-inspection.png`,
    });
    await page.locator("[data-choice-cancel]").click();
    await expect(page.locator("[data-choice-inspection]")).toHaveCount(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    if (scene === "lastmile")
      await expect(page.locator('[data-hotspot="robot"]')).toHaveText(
        /Тележка/,
      );
    if (scene === "crane") {
      await expect(page.locator('[data-hotspot="rush"]')).toHaveText(
        /Попросить Ивана/,
      );
      await expect(page.locator('[data-hotspot="petr"]')).toHaveText(
        /Попросить Петра/,
      );
    }
    await page.screenshot({
      path: `.tmp-work/choice-labels-${scene}-${test.info().project.name}.png`,
    });
  });
}
