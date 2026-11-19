import { expect, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

for (const [scene, choice] of [
  ["crane", "petr"],
  ["carrier", "express"],
  ["compact", "place-2"],
  ["inventory", "wms"],
  ["lastmile", "rover"],
]) {
  test(`${scene} result actions fill their row without clipping`, async ({ page }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.setViewportSize({ width: 418, height: 920 });
    if (scene === "carrier") {
      await openCarrier(page, "professional", "khor", "camera");
      await pickCarrier(page, "express");
    } else {
      await page.goto(`/scenes.html?scene=${scene}&parcel=camera&recipient=khor`);
      const briefing = page.locator("[data-scene-briefing]");
      for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++) {
        await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
      }
      await page.locator(`[data-hotspot="${choice}"]`).click();
    }
    await page.locator("[data-choice-confirm]").click();
    const footer = page.locator("[data-result-reader] footer");
    await expect(footer).toBeVisible({ timeout: 15000 });
    await page.evaluate(() => document.fonts.ready);

    for (const [width, height, textSize] of [[480, 960], [418, 920], [390, 844], [600, 960], [320, 568], [568, 320], [1440, 900], [320, 568, 32]]) {
      await test.step(`${width}x${height}${textSize ? " enlarged text" : ""}`, async () => {
        await page.setViewportSize({ width, height });
        if (textSize) await footer.evaluate((el, size) => {
          for (const node of [el, ...el.querySelectorAll("button")]) {
            (node as HTMLElement).style.setProperty("font-size", `${size}px`, "important");
          }
        }, textSize);
        // Let responsive <picture> sources follow the resized viewport before decode.
        await page.evaluate(() => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
        await expect(page.locator("[data-artwork-ready=false]")).toHaveCount(0);
        await page.locator("[data-scene-world] img").evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
        await footer.scrollIntoViewIfNeeded();
        const geometry = await footer.evaluate(el => ({
          footer: el.getBoundingClientRect().toJSON(),
          buttons: [...el.querySelectorAll("button")].map(button => button.getBoundingClientRect().toJSON()),
        }));
        const [back, next] = geometry.buttons;
        expect(geometry.buttons).toHaveLength(2);
        if (scene === "crane") {
          await page.screenshot({ path: info.outputPath(`crane-${width}${textSize ? "-large-text" : ""}.jpg`), type: "jpeg", quality: 65 });
        }
        // A metrics row spanning all tracks must not leave an unused action column.
        expect(Math.abs(back.x - geometry.footer.x)).toBeLessThan(1);
        expect(Math.abs(next.right - geometry.footer.right)).toBeLessThan(1);
        expect(Math.abs(back.width - next.width)).toBeLessThan(1);
        if (Math.abs(back.x - next.x) >= 1) {
          expect(Math.abs(back.y - next.y)).toBeLessThan(1);
          expect(Math.abs(back.height - next.height)).toBeLessThan(1);
        } else {
          expect(Math.abs(back.width - geometry.footer.width)).toBeLessThan(1);
        }
        for (const button of await footer.locator("button").all()) {
          const box = (await button.boundingBox())!;
          expect(box.height).toBeGreaterThanOrEqual(44);
          expect(box.width).toBeGreaterThanOrEqual(44);
          await button.scrollIntoViewIfNeeded();
          await expect(button).toBeInViewport({ ratio: 1 });
          expect(await button.evaluate(el => el.scrollWidth <= el.clientWidth + 1 && el.scrollHeight <= el.clientHeight + 1)).toBe(true);
          if (!textSize && width <= 600 && height > 450) {
            expect(await button.evaluate(el => {
              const label = el.querySelector('[data-next-label] > span') ?? el.querySelector('span')!;
              const range = document.createRange();
              range.selectNodeContents(label);
              return new Set([...range.getClientRects()].map(r => Math.round(r.top))).size;
            }), 'Ordinary-size action label stays on one line').toBe(1);
          }
          expect(await button.evaluate(el => {
            const bounds = el.getBoundingClientRect();
            const range = document.createRange();
            range.selectNodeContents(el.querySelector("span")!);
            return [...range.getClientRects()].every(rect => rect.left >= bounds.left && rect.right <= bounds.right && rect.top >= bounds.top && rect.bottom <= bounds.bottom);
          })).toBe(true);
        }
      });
    }
  });
}

test("boat outside the truck keeps both workers and the whole trolley in frame", async ({ page }, info) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const [width, height] of [[568, 320], [390, 844], [320, 568], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=compact&parcel=boat&recipient=alva");
    const briefing = page.locator("[data-scene-briefing]");
    for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
      await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
    await page.locator('[data-hotspot="place-3"]').click();
    await page.locator("[data-choice-confirm]").click();
    const image = page.locator("[data-failure-art] img");
    await image.evaluate((img: HTMLImageElement) => img.decode());
    await expect(image).toHaveCSS('object-fit', 'contain');
    if (width < height) await expect.poll(() => image.evaluate((img: HTMLImageElement) => {
      const box = img.getBoundingClientRect();
      return Math.abs(box.width / box.height - img.naturalWidth / img.naturalHeight);
    })).toBeLessThan(0.01);
    const panel = page.locator('[data-sheet-panel]');
    expect((await panel.boundingBox())!.y + (await panel.boundingBox())!.height).toBeLessThanOrEqual(height + 1);
    if (width === 320 || height <= 400) {
      // A real scroll must expose the action, not click's hidden-ancestor auto-scroll.
      await panel.hover({ position: { x: 4, y: 4 } });
      await page.mouse.wheel(0, 2000);
      await expect(page.locator('[data-result-reader] footer button').last()).toBeInViewport({ ratio: 1 });
    }
    await page.screenshot({ path: info.outputPath(`boat-${width}.jpg`), type: "jpeg", quality: 65 });
    const more = page.getByRole("button", { name: "Читать дальше", exact: true });
    for (let n = 0; n < 30 && await more.isVisible(); n++) await more.click();
    for (const name of ["Изменить выбор", "Дальше: склад"])
      await expect(page.getByRole("button", { name, exact: true })).toBeInViewport({ ratio: 1 });
  }
});

test("enlarged result text uses both lines despite fractional layout rounding", async ({ page }, info) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/scenes.html?scene=compact&parcel=boat&recipient=alva");
  const briefing = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  await page.locator('[data-hotspot="place-3"]').click();
  await page.locator("[data-choice-confirm]").click();
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => {
    const original = [...document.querySelectorAll('body, body *')]
      .filter((e): e is HTMLElement => e instanceof HTMLElement)
      .map(e => [e, parseFloat(getComputedStyle(e).fontSize), parseFloat(getComputedStyle(e).lineHeight)] as const);
    for (const [e, size, line] of original) {
      e.style.setProperty('font-size', `${size * 2}px`, 'important');
      if (Number.isFinite(line)) e.style.setProperty('line-height', `${line * 2}px`, 'important');
    }
  });
  const prose = page.locator('[data-result-reading]');
  await expect.poll(() => prose.evaluate(e =>
    e.firstElementChild!.getBoundingClientRect().height / parseFloat(getComputedStyle(e).lineHeight),
  )).toBeGreaterThanOrEqual(1.99);
  expect(await prose.evaluate(e => e.scrollHeight <= e.clientHeight + 1)).toBe(true);
  await page.locator('[data-sheet-panel]').hover({ position: { x: 4, y: 4 } });
  await page.mouse.wheel(0, 2000);
  await expect(page.locator('[data-result-reader] footer button').last()).toBeInViewport({ ratio: 1 });
  await page.screenshot({ path: info.outputPath('text200.jpg'), type: 'jpeg', quality: 65 });
});

test("short-phone warehouse keeper retains head and raised hand", async ({ page }, info) => {
  await page.setViewportSize({ width: 320, height: 568 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/scenes.html?scene=inventory&parcel=boat&recipient=alva");
  const briefing = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  await page.locator('[data-hotspot="keeper"]').click();
  await page.locator("[data-choice-confirm]").click();
  const image = page.locator('[data-scene-consequence="inventory-keeper"] img');
  await image.evaluate((img: HTMLImageElement) => img.decode());
  await expect(image).toHaveCSS('object-fit', 'contain');
  await page.screenshot({ path: info.outputPath('keeper-320.jpg'), type: 'jpeg', quality: 65 });
});

test("lastmile outcome stills cover the frame with tall revision-20 art", async ({ page }, info) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const [width, height] of [[320, 568], [390, 844], [768, 1024], [1440, 900]]) {
    await page.setViewportSize({ width, height });
    await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=alva");
    const briefing = page.locator("[data-scene-briefing]");
    for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
      await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
    for (const choice of ["robot", "rover", "helicopter"]) {
      await page.locator(`[data-hotspot="${choice}"]`).click();
      await page.locator("[data-choice-confirm]").click();
      if (choice === "helicopter") {
        const more = page.getByRole("button", { name: "Читать дальше", exact: true });
        for (let n = 0; n < 20 && !await page.locator('[data-delivery-leg="ground"]').count(); n++) await more.click();
      }
      const image = page.locator("[data-scene-consequence] img");
      await image.evaluate((img: HTMLImageElement) => img.decode());
      // R20 stills are outpainted to 1672x2200, so they cover without pale bands.
      await expect(image).toHaveCSS("object-fit", "cover");
      expect(await image.evaluate((img: HTMLImageElement) => [img.naturalWidth, img.naturalHeight])).toEqual([1672, 2200]);
      await page.screenshot({ path: info.outputPath(`lastmile-${width}-${choice}.jpg`), type: "jpeg", quality: 65 });
      const back = page.getByRole("button", { name: "Изменить выбор", exact: true });
      await expect(back).toBeInViewport({ ratio: 1 });
      await back.click();
    }
  }
});

for (const width of [320, 1440]) {
  test.describe(`crane artwork at ${width}px`, () => {
    test.use({ hasTouch: width === 320 });
    test("actors work without text plaques", async ({ page }, info) => {
      await page.setViewportSize({ width, height: width === 320 ? 568 : 900 });
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.goto("/scenes.html?scene=crane&parcel=camera&recipient=khor");
      const briefing = page.locator("[data-scene-briefing]");
      for (let n = 0; n < 30 && await briefing.getAttribute("data-reading") === "true"; n++)
        await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
      await expect(page.locator("[data-artwork-ready=false]")).toHaveCount(0);
      await page.locator("[data-scene-world] img").evaluateAll(images => Promise.all(images.map(image => (image as HTMLImageElement).decode())));
      await expect(page.locator("[data-barge-label]")).toHaveCount(0);
      await page.screenshot({ path: info.outputPath("crane-choice.jpg"), type: "jpeg", quality: 75 });
      for (const id of ["remote", "rush", "petr"]) {
        const target = page.locator(`[data-hotspot="${id}"]`);
        await expect(target).toHaveAttribute("aria-label", /\S+/);
        await target[width === 320 ? "tap" : "click"]();
        await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", id);
        await page.locator("[data-choice-cancel]").click();
        await expect(target).toBeFocused();
      }
      await page.keyboard.press("Enter");
      await expect(page.locator("[data-choice-inspection]")).toHaveAttribute("data-choice-inspection", "petr");
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
    });
  });
}
