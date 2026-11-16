import { expect, test, type Locator, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

const text = async (page: Page) => (await page.locator("[data-result-reading]").innerText()).replace(/\s+/g, " ").trim();

async function rotate(page: Page, width: number, height: number) {
  await page.setViewportSize({ width, height });
  await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
}

for (const size of [{ width: 320, height: 568 }, { width: 390, height: 844 }]) {
  test(`reading survives phone rotation at ${size.width}x${size.height}`, async ({ page }) => {
    test.setTimeout(60000);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await rotate(page, size.height, size.width);
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.clear();
      const scope = "quest-rotation-test";
      localStorage.setItem("energy-quest-save-v1", JSON.stringify({ version: 1, scope,
        state: { step: "outcome", profile: "professional", recipient: "alva", parcel: "camera", carrier: "crew" },
      }));
      for (const key of ["intro-seen", "remaining"]) localStorage.setItem(`${scope}:${key}`, "true");
      localStorage.setItem(`${scope}:scenes`, JSON.stringify({ progress: {
        sceneIndex: 1, phase: "result", finished: false, answers: { compact: "auto", inventory: "wms" },
      } }));
    });
    await page.reload();
    await expect(page.locator('[data-outcome-scene="inventory"]')).toBeVisible();
    const further = page.getByRole("button", { name: "Читать дальше", exact: true });
    const baseline: string[] = [];
    for (let n = 0; n < 40; n++) {
      baseline.push(await text(page));
      if (!await further.isVisible()) break;
      await further.click();
    }
    const complete = baseline.join(" ");
    expect(baseline.length).toBeGreaterThan(1);
    await page.reload();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    let covered = 0;
    for (let n = 0; n < 40; n++) {
      const part = await text(page);
      const start = complete.indexOf(part);
      expect(start, `unknown reading fragment: ${part}`).toBeGreaterThanOrEqual(0);
      expect(start, "rotation must not skip unread narrative").toBeLessThanOrEqual(covered + 1);
      covered = Math.max(covered, start + part.length);
      if (!await further.isVisible()) break;
      await further.click();
      await rotate(page, ...(n % 2 === 0 ? [size.width, size.height] : [size.height, size.width]) as [number, number]);
    }
    expect(covered).toBe(complete.length);
    await expect(page.getByRole("button", { name: "Дальше: баржа", exact: true })).toBeInViewport({ ratio: 0.98 });
  });
}


async function reachable(button: Locator, context = "") {
  await expect(button).toBeVisible();
  await expect(button).toBeEnabled();
  await expect(button, context).toBeInViewport({ ratio: 0.98 });
  await expect.poll(() => button.evaluate(element => {
    const box = element.getBoundingClientRect();
    const hit = document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2);
    return hit === element || element.contains(hit);
  })).toBe(true);
}

async function proceed(page: Page, label: string) {
  const reader = page.locator("[data-result-reader]");
  const further = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 40 && await further.isVisible(); n++) await further.click();
  await reader.getByRole("button", { name: label, exact: true }).click();
}

for (const size of [{ width: 320, height: 568 }, { width: 390, height: 844 }]) {
  test(`inspection controls survive rotation at ${size.width}x${size.height}`, async ({ page }, info) => {
    test.setTimeout(90000);
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.emulateMedia({ reducedMotion: "reduce" });
    await rotate(page, size.width, size.height);
    await openCarrier(page, "professional", "alva", "boat");
    for (const [scene, choice] of [["carrier", "crew"], ["compact", "auto"], ["inventory", "wms"], ["crane", "remote"]]) {
      const target = page.locator(scene === "carrier" ? `[data-carrier-choice="${choice}"]` : `[data-hotspot="${choice}"]`);
      if (scene !== "carrier") {
        await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
        const briefing = page.locator("[data-scene-briefing]");
        for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
          await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
      }
      if (scene === "carrier") await pickCarrier(page, "crew");
      else {
        await expect(target).toBeVisible();
        await expect(target).toBeEnabled();
        await target.focus();
        await page.keyboard.press("Enter");
      }
      const card = page.locator("[data-choice-inspection]");
      await expect(card).toBeVisible();
      const selection = await card.getAttribute("data-choice-inspection");
      for (const [width, height] of [[size.height, size.width], [size.width, size.height]]) {
        await rotate(page, width, height);
        await expect(card).toHaveAttribute("data-choice-inspection", selection!);
        await reachable(card.locator("[data-choice-confirm]"), `${scene} confirm at ${width}x${height}`);
        await reachable(card.locator("[data-choice-cancel]"), `${scene} cancel at ${width}x${height}`);
        const copy = card.getByRole("region", { name: "Описание варианта" });
        if (await copy.count() && await copy.evaluate(el => el.scrollHeight > el.clientHeight + 1)) {
          expect(await copy.evaluate(el => getComputedStyle(el).overflowY)).toBe("auto");
          await copy.evaluate(el => { el.scrollTop = 0; });
          await copy.hover();
          await page.mouse.wheel(0, 400);
          await expect.poll(() => copy.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
          await copy.evaluate(el => { el.scrollTop = 0; });
          await copy.focus();
          await page.keyboard.press("End");
          await expect.poll(() => copy.evaluate(el => el.scrollTop)).toBeGreaterThan(0);
        }
      }
      await page.screenshot({ path: info.outputPath(`${scene}-rotated.png`) });
      await page.keyboard.press("Escape");
      await expect(card).toHaveCount(0);
      await expect(target).toBeFocused();
      await page.keyboard.press("Enter");
      await reachable(card.locator("[data-choice-confirm]"));
      await card.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      await proceed(page, scene === "carrier" ? "Дальше: погрузка" : scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
    }
    await expect(page.locator('[data-scene="lastmile"]')).toBeVisible();
    expect(errors).toEqual([]);
  });
}
