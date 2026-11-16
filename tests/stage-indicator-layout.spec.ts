import { expect, type Locator, test } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function checkProgress(header: Locator, step: number) {
  const progress = header.locator("[data-scene-progress]");
  await expect(progress).toBeVisible();
  await expect(progress).toHaveAttribute(
    "aria-label",
    new RegExp(`^Этап ${step} из 5:`),
  );
  const stops = progress.locator("i");
  await expect(stops).toHaveCount(5);
  await expect(stops.nth(step - 1)).toHaveAttribute("data-leg", "current");
  const geometry = await header.evaluate((el) => {
    const h = el.getBoundingClientRect();
    const p = el.querySelector("[data-scene-progress]")!;
    const current = p
      .querySelector('i[data-leg="current"]')!
      .getBoundingClientRect();
    return {
      top: current.top - h.top,
      bottom: h.bottom - current.bottom,
      logoGap:
        p.getBoundingClientRect().left -
        el.querySelector("[data-brand-lockup]")!.getBoundingClientRect().right,
      right: h.right - p.getBoundingClientRect().right,
      circles: [...p.querySelectorAll("i")].map((i) => {
        const r = i.getBoundingClientRect();
        return {
          width: r.width,
          height: r.height,
          top: r.top - h.top,
          bottom: h.bottom - r.bottom,
        };
      }),
    };
  });
  // The active ring needs breathing room, not a taller header or a clipped circle.
  expect(geometry.top).toBeGreaterThanOrEqual(3.9);
  expect(geometry.bottom).toBeGreaterThanOrEqual(3.9);
  expect(Math.abs(geometry.top - geometry.bottom)).toBeLessThanOrEqual(1);
  expect(geometry.logoGap).toBeGreaterThanOrEqual(8);
  expect(geometry.right).toBeGreaterThanOrEqual(8);
  for (const circle of geometry.circles) {
    expect(circle.width).toBe(circle.height);
    expect(circle.top).toBeGreaterThanOrEqual(3.9);
    expect(circle.bottom).toBeGreaterThanOrEqual(3.9);
  }
}

for (const [index, [scene, choice]] of [
  ["carrier", "express"],
  ["compact", "place-1"],
  ["inventory", "alphabet"],
  ["crane", "rush"],
  ["lastmile", "helicopter"],
].entries()) {
  test(`${scene} progress fits the choice and result headers`, async ({
    page,
  }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    if (scene === "carrier") {
      await openCarrier(page, "professional", "alva", "boat");
    } else {
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=alva`);
      const next = page.getByRole("button", {
        name: /^(Далее|К выбору|К сцене)$/,
      });
      if (scene !== "compact") await expect(next).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      for (let n = 0; n < 30 && (await next.isVisible()); n++)
        await next.click();
      await expect(page.locator("[data-scene-briefing]")).toHaveAttribute(
        "data-reading",
        "false",
      );
    }
    await page.evaluate(() => document.fonts.ready);
    const header = page.locator("[data-scene-briefing] > div:first-child");
    await header
      .locator("img")
      .evaluateAll((imgs) =>
        Promise.all(imgs.map((img) => (img as HTMLImageElement).decode())),
      );
    await header.screenshot({ path: info.outputPath("choice.png") });
    const { width, height } = page.viewportSize()!;
    const portraitCompact = width <= 900 && height >= width;
    expect((await header.boundingBox())!.height).toBe(
      portraitCompact ? 48 : 56,
    );
    await checkProgress(header, index + 1);

    if (scene === "carrier") await pickCarrier(page, "express");
    else {
      // The scene can pan while idle; keyboard activation does not wait for a stationary target.
      await page.locator(`[data-hotspot="${choice}"]`).focus();
      await page.keyboard.press("Enter");
    }
    if (scene !== "lastmile")
      await page.locator("[data-choice-confirm]").click();
    const resultHeader = page.locator("[data-header-result]");
    await expect(resultHeader).toBeVisible({ timeout: 15_000 });
    await resultHeader
      .locator("img")
      .evaluateAll((imgs) =>
        Promise.all(imgs.map((img) => (img as HTMLImageElement).decode())),
      );
    await resultHeader.screenshot({ path: info.outputPath("result.png") });
    expect((await resultHeader.boundingBox())!.height).toBe(
      width <= 600 || portraitCompact ? 48 : 56,
    );
    if (width <= 600)
      await expect(resultHeader.locator("[data-scene-progress]")).toBeHidden();
    else await checkProgress(resultHeader, index + 1);
  });
}
