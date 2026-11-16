import { expectNoInteractionDecorations } from './helpers/interaction-decorations';
import { expect, test, type Locator, type Page } from "@playwright/test";

/** Tab like a player: never use locator.focus() to bypass the tab order. */
async function activate(page: Page, target: Locator) {
  await expect(target).toBeVisible();
  await expect(target).toBeEnabled();
  for (let n = 0; n < 60; n++) {
    if (await target.evaluate(element => element === document.activeElement)) break;
    await page.keyboard.press("Tab");
    await expect(page.locator(":focus")).toHaveCSS("text-decoration-line", "none");
  }
  await expect(target).toBeFocused();
  await expectNoInteractionDecorations(page);
  await expect(target).toHaveCSS("text-decoration-line", "none");
  await expect(target).toBeInViewport({ ratio: 0.9 });
  await page.keyboard.press("Enter");
}

async function finishResult(page: Page, label: string) {
  const reader = page.locator("[data-result-reader]");
  await expect(reader).toBeVisible();
  const further = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 40 && await further.isVisible(); n++) await activate(page, further);
  await activate(page, reader.getByRole("button", { name: label, exact: true }));
}

for (const viewport of [{ width: 320, height: 568 }, { width: 844, height: 390 }]) {
  test(`keyboard-only robot journey at ${viewport.width}x${viewport.height}`, async ({ page }, info) => {
    test.setTimeout(90000);
    await page.setViewportSize(viewport);
    await page.emulateMedia({ reducedMotion: "reduce" });
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto("/");
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
    await page.reload();
    for (const selector of ["[data-intro-enter]", "[data-intro-next]", "[data-intro-start]"])
      await activate(page, page.locator(selector));
    for (const choice of ["student", "arseniy", "socks"])
      await activate(page, page.locator(`[data-choice="${choice}"]`));
    await activate(page, page.locator('[data-carrier-choice="near"]'));
    await activate(page, page.locator("[data-choice-confirm]"));
    await finishResult(page, "Дальше: погрузка");

    for (const [scene, choice] of [["compact", "place-4"], ["inventory", "keeper"], ["crane", "petr"], ["lastmile", "robot"]]) {
      await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
      const briefing = page.locator("[data-scene-briefing]");
      for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
        await activate(page, briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }));
      await activate(page, page.locator(`[data-hotspot="${choice}"]`));
      await activate(page, page.locator("[data-choice-confirm]"));
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      await page.locator("[data-scene-consequence] img").evaluateAll(images =>
        Promise.all(images.map(image => (image as HTMLImageElement).decode())),
      );
      await page.screenshot({ path: info.outputPath(`${scene}.png`) });
      await finishResult(page, scene === "lastmile" ? "К вручению подарка" : scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
    }
    await activate(page, page.getByRole("button", { name: "Узнать, какой вы логист" }));
    await expect(page.locator("[data-logist-certificate]")).toBeVisible();
    const share = page.getByRole("button", { name: "Поделиться", exact: true });
    await activate(page, share);
    await page.keyboard.press("Escape");
    await expect(share).toBeFocused();
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expectNoInteractionDecorations(page);
    expect(errors).toEqual([]);
  });
}
