import { expect, test, type Locator, type Page } from "@playwright/test";

async function readBriefing(page: Page) {
  const briefing = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++) {
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  }
  await expect(briefing).toHaveAttribute("data-reading", "false");
}

async function expectPressFeedback(page: Page, button: Locator) {
  await button.hover();
  const before = await button.evaluate(el => getComputedStyle(el).filter);
  await page.mouse.down();
  try {
    expect(await button.evaluate(el => el.matches(":active"))).toBe(true);
    expect(await button.evaluate(el => getComputedStyle(el).filter)).not.toBe(before);
  } finally {
    await page.mouse.move(1, 1);
    await page.mouse.up();
  }
}

test("compact previews explain the place, switch without committing and keep actions in view", async ({ page }, info) => {
  for (const viewport of [{ width: 320, height: 568 }, { width: 568, height: 320 }, { width: 1440, height: 900 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/scenes.html?scene=compact&parcel=socks&recipient=khor");
    await page.locator('[data-hotspot="place-1"]').click();
    const card = page.locator("[data-choice-inspection]");
    await expect(card).toContainText("Над ящиками с гирями у задних дверей. Креплений нет.");
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({ ratio: 1 });
    await expectPressFeedback(page, page.locator("[data-choice-confirm]"));
    // Narrow artwork frames one place; return to the overview before switching.
    // The desktop rail must still allow switching with the preview open.
    if (viewport.width < 901) {
      await page.locator("[data-choice-cancel]").click();
      await expect(page.locator('[data-hotspot="place-1"]')).toBeFocused();
    }
    await page.locator('[data-hotspot="place-2"]').click();
    await expect(card).toHaveCount(1);
    await expect(card).toContainText("Над ящиком с посудой, до самой крыши. На стенке есть стропы.");
    await expect(card).not.toContainText("Креплений нет.");
    await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({ ratio: 1 });
    await page.screenshot({ path: info.outputPath(`compact-${viewport.width}.jpg`), type: "jpeg", quality: 65 });
    if (viewport.width < 901) await page.locator("[data-choice-cancel]").click();
    await page.locator('[data-hotspot="auto"]').click();
    await expect(card).toContainText("Compact");
    await page.locator("[data-choice-cancel]").click();
    await expect(card).toHaveCount(0);
  }
});

test("barge text has no reveal delay after the scene, including repeat and reduced motion", async ({ page }) => {
  test.setTimeout(60000);
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/scenes.html?scene=crane&parcel=socks&recipient=khor");
  await readBriefing(page);
  for (const motion of ["no-preference", "no-preference", "reduce"] as const) {
    await page.emulateMedia({ reducedMotion: motion });
    await page.locator('[data-hotspot="remote"]').click();
    await page.locator("[data-choice-confirm]").click();
    const reader = page.locator("[data-result-reader]");
    // Preserve the quay consequence; only the subsequent text reveal is immediate.
    await expect(reader).toBeVisible({ timeout: 15000 });
    const blocks = reader.locator("[data-result-narrative] > *, [data-result-feedback]");
    expect(await blocks.count()).toBeGreaterThanOrEqual(3);
    expect(await blocks.evaluateAll(nodes => nodes.every(el => getComputedStyle(el).opacity === "1" && el.getAnimations().length === 0))).toBe(true);
    const revise = reader.getByRole("button", { name: "Изменить выбор", exact: true });
    await expectPressFeedback(page, revise);
    await revise.click();
  }
});

test("certificate actions respond to a press and the close target is thumb-sized", async ({ page }, info) => {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.clear();
    const scope = "quest-emil-feedback";
    localStorage.setItem("energy-quest-save-v1", JSON.stringify({ version: 1, scope, state: {
      step: "outcome", profile: "student", recipient: "alva", parcel: "socks", carrier: "old",
      scores: { energy: 0, empathy: 0, efficiency: 0 },
    } }));
    for (const key of ["remaining", "intro-seen", "ending-profile"]) localStorage.setItem(`${scope}:${key}`, "true");
    localStorage.setItem(`${scope}:scenes`, JSON.stringify({ progress: {
      sceneIndex: 3, phase: "result", finished: true,
      answers: { compact: "place-1", inventory: "entrance", crane: "rush", lastmile: "helicopter" },
    } }));
  });
  await page.reload();
  const trigger = page.locator("[data-certificate-actions]");
  await expectPressFeedback(page, trigger);
  for (const viewport of [{ width: 390, height: 844 }, { width: 320, height: 568 }]) {
    await page.setViewportSize(viewport);
    await trigger.click();
    const dialog = page.getByRole("dialog", { name: "Поделиться званием" });
    const close = dialog.getByRole("button", { name: "Закрыть", exact: true });
    const bounds = await close.boundingBox();
    expect(bounds!.width).toBeGreaterThanOrEqual(44);
    expect(bounds!.height).toBeGreaterThanOrEqual(44);
    await expect(close).toBeInViewport({ ratio: 1 });
    await expect(dialog).toBeVisible();
    await page.screenshot({ path: info.outputPath(`share-${viewport.width}.jpg`), type: "jpeg", quality: 65 });
    await page.keyboard.press("Escape");
    await expect(dialog).not.toBeVisible();
    await expect(trigger).toBeFocused();
  }
});
