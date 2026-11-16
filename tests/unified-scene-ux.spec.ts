import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

test.use({ hasTouch: true });

const choices = {
  compact: ["place-1", "place-2", "place-3", "place-4", "auto"],
  inventory: ["entrance", "alphabet", "keeper", "wms"],
  crane: ["remote", "rush", "petr"],
  lastmile: ["helicopter", "rover", "robot", "pipe-carrier"],
};
async function readCondition(page: Page) {
  const condition = page.getByRole("region", { name: "Условие задания", exact: true });
  for (let i = 0; i < 40 && await condition.isVisible(); i++)
    await condition.getByRole("button", { name: /^(Далее|К выбору)$/ }).click();
  await expect(condition).toHaveCount(0);
}
async function settleArt(page: Page) {
  await expect(page.locator("[data-artwork-ready=false]")).toHaveCount(0);
  await page.locator("[data-scene-world] img").evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
}

for (const [width, height] of [[1440, 900], [390, 844], [320, 568], [844, 390], [568, 320]]) {
  test(`all choices preview, cancel, restore focus and confirm at ${width}x${height}`, async ({ page }, info) => {
    test.setTimeout(120000);
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    for (const [scene, ids] of Object.entries(choices)) {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      await readCondition(page);
      await settleArt(page);
      await expect(page.getByRole("button", { name: /анимаци/i })).toHaveCount(0);
      const question = page.locator('[data-testid="scene-question"]');
      const reminder = question.locator("[data-delivery-reminder]");
      await expect(reminder).toBeInViewport({ ratio: 1 });
      await expect(reminder).toContainText("Лодка для Хабта");
      await expect(reminder.locator("img")).toBeVisible();
      await page.screenshot({ path: info.outputPath(`${scene}-${width}-choice.png`) });
      const activate = width <= 600 ? "tap" : "click";
      for (const id of ids) {
        const target = page.locator(`[data-hotspot="${id}"]`);
        await expect(target).toBeInViewport({ ratio: 0.99 });
        const rect = await target.boundingBox();
        expect(rect!.width).toBeGreaterThanOrEqual(43.9);
        expect(rect!.height).toBeGreaterThanOrEqual(43.9);
        // Native touch on phones, pointer on desktop: overlays must not steal input.
        await target[activate]();
        const inspection = page.locator("[data-choice-inspection]");
        await expect(inspection).toHaveAttribute("data-choice-inspection", id);
        await expect(page.locator("[data-result-reader]")).toHaveCount(0);
        await expect(inspection.locator("[data-delivery-reminder]")).toBeInViewport({ ratio: 1 });
        await expect(page.locator("[data-choice-confirm]")).toBeInViewport({ ratio: 0.99 });
        await page.locator("[data-choice-cancel]")[activate]();
        await expect(target).toBeFocused();
        await expect(page.locator("[data-result-reader]")).toHaveCount(0);
      }
      await page.locator(`[data-hotspot="${ids.at(-1)}"]`)[activate]();
      await page.screenshot({ path: info.outputPath(`${scene}-${width}-preview.png`) });
      await page.locator("[data-choice-confirm]")[activate]();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      await expect(page.locator("[data-result-reader] [data-delivery-reminder]")).toBeInViewport({ ratio: 1 });
      await expect(page.locator("[data-score-delta]")).toHaveCount(1);
      const reading = page.locator("[data-result-reading]");
      if (await page.locator('[data-result-reader][data-continuous=true]').count() &&
          await reading.evaluate(node => node.scrollHeight > node.clientHeight + 1)) {
        await expect(reading).toHaveCSS("overflow-y", "auto");
        await reading.focus();
        await page.keyboard.press("End");
        await expect.poll(() => reading.evaluate(node => node.scrollTop + node.clientHeight >= node.scrollHeight - 1)).toBe(true);
        await reading.evaluate(node => { node.scrollTop = 0; });
      }
      await page.locator("[data-scene-consequence] img").evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
      await page.screenshot({ path: info.outputPath(`${scene}-${width}-result.png`) });
      await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
      await expect(page.locator(`[data-hotspot="${ids.at(-1)}"]`)).toBeFocused();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    }
  });
}

for (const width of [390, 320]) {
  test(`cards remain readable and operable with 200% text at ${width}px`, async ({ page }) => {
    test.setTimeout(90000);
    await page.setViewportSize({ width, height: width === 320 ? 568 : 844 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    const doubleText = async (selector: string) => {
      await page.locator(selector).evaluate(root => {
        const nodes = [root, ...root.querySelectorAll("*")].filter(node => node instanceof HTMLElement);
        const sizes = nodes.map(node => parseFloat(getComputedStyle(node).fontSize));
        nodes.forEach((node, index) => node.style.fontSize = `${sizes[index] * 2}px`);
        window.dispatchEvent(new Event("resize"));
      });
    };
    for (const [scene, ids] of Object.entries({ carrier: ["express"], ...choices })) {
      if (scene === "carrier") await openCarrier(page, "professional", "khor", "boat");
      else await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor`);
      await readCondition(page);
      await settleArt(page);
      await doubleText('[data-testid="scene-question"]');
      if (scene === "lastmile") {
        for (const id of ids) {
          for (const attribute of ["data-hotspot", "data-lastmile-label"]) {
            await page.locator(`[${attribute}="${id}"]`).click();
            await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", id);
            await page.locator("[data-choice-cancel]").click();
          }
        }
      }
      if (scene === "carrier") await pickCarrier(page, "express");
      else await page.locator(`[data-hotspot="${ids.at(-1)}"]`).click();
      await doubleText('[data-choice-inspection]');
      const description = page.getByRole("region", { name: "Описание варианта", exact: true });
      expect(await description.evaluate(node => node.clientHeight)).toBeGreaterThan(35);
      const confirm = page.locator('[data-choice-confirm]');
      await confirm.scrollIntoViewIfNeeded();
      await expect(confirm).toBeInViewport({ ratio: 0.98 });
      await confirm.click();
      await expect(page.locator('[data-result-reader]')).toBeVisible({ timeout: 15000 });
      await doubleText('[data-result-reader]');
      const reading = page.locator('[data-result-reading]');
      await expect.poll(() => reading.evaluate(node => node.clientHeight / parseFloat(getComputedStyle(node).lineHeight))).toBeGreaterThanOrEqual(1.9);
      await reading.scrollIntoViewIfNeeded();
      await expect(reading).toBeInViewport();
      if (!await page.locator('[data-continuous=true]').count()) {
        await expect.poll(() => reading.evaluate(node => node.scrollHeight <= node.clientHeight + 1)).toBe(true);
      }
      expect(await reading.evaluate(node => {
        const reader = node.closest('[data-result-reader]')!;
        return reader.querySelector('h1')!.getBoundingClientRect().bottom <= node.getBoundingClientRect().top + 1 &&
          node.getBoundingClientRect().bottom <= reader.querySelector('footer')!.getBoundingClientRect().top + 1;
      })).toBe(true);
      expect(await page.locator('[data-score-key] em').evaluateAll(labels =>
        labels.every(node => node.scrollHeight <= node.clientHeight + 1 && node.scrollWidth <= node.clientWidth + 1))).toBe(true);
      const back = page.getByRole('button', { name: 'Изменить выбор', exact: true });
      await back.scrollIntoViewIfNeeded();
      await expect(back).toBeInViewport({ ratio: 0.98 });
      await expect.poll(() => page.locator('[data-result-reader]').evaluate(node => node.scrollWidth <= node.clientWidth + 1)).toBe(true);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    }
  });
}

for (const parcel of ["boat", "camera", "socks"] as const) {
  test(`${parcel}: carrier uses the real gift in task, preview and result`, async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await openCarrier(page, "student", "khor", parcel);
    const question = page.locator('[data-testid="scene-question"] [data-delivery-reminder]');
    await expect(question).toHaveAttribute("data-parcel", parcel);
    const source = await question.locator("img").getAttribute("src");
    await pickCarrier(page, "express");
    await expect(page.locator('[data-choice-inspection] [data-delivery-reminder] img')).toHaveAttribute("src", source!);
    await page.locator("[data-choice-cancel]").click();
    await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    await pickCarrier(page, "express");
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator('[data-result-reader] [data-delivery-reminder] img')).toHaveAttribute("src", source!);
    await expect(page.locator('[data-result-reader] [data-delivery-reminder]')).toBeInViewport({ ratio: 1 });
  });
}
