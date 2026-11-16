import { expect, test } from "@playwright/test";
import { openCarrier } from "./helpers/open-preparation";

test("screen titles follow the opening, preparation, choice and result", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("[data-intro-page=cover] main img").first()).toHaveAttribute("fetchpriority", "high");
  await expect(page).toHaveTitle("Доставляем радость — Энергия+");
  await page.locator("[data-intro-enter]").click();
  await expect(page).toHaveTitle(/^Путь одной посылки —/);
  await page.locator("[data-intro-next]").click();
  await expect(page).toHaveTitle(/^Маршрутный лист —/);
  await page.locator("[data-intro-start]").click();
  for (const id of ["professional", "khor", "boat"]) {
    const heading = await page.locator("h1").innerText();
    await expect(page).toHaveTitle(`${heading} — Доставляем радость`);
    await page.locator(`[data-choice="${id}"]`).click();
  }
  await expect(page.getByRole("heading", { level: 1, name: "Выбор перевозчика" })).toHaveCount(1);
  await expect(page).toHaveTitle("Выбор перевозчика — Доставляем радость");
  await page.locator('[data-carrier-choice="near"]').focus();
  await page.keyboard.press("Enter");
  await page.locator("[data-choice-confirm]").click();
  await expect(page.locator("[data-result-reader] h1")).toHaveCount(1);
  await expect(page.getByRole("button", { name: /анимаци/i })).toHaveCount(0);
  const resultTitle = await page.title();
  expect(resultTitle).not.toBe("Выбор перевозчика — Доставляем радость");
  await page.reload();
  await expect(page).toHaveTitle(resultTitle);
  await expect(page.locator("head > title")).toHaveCount(1);
  await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
  await expect(page).toHaveTitle("Выбор перевозчика — Доставляем радость");
});

test("respects OS reduced motion without a page pause control; only helicopter blades animate", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await openCarrier(page);
  await expect(page.getByRole("button", { name: /анимаци/i })).toHaveCount(0);
  await page.evaluate(() => localStorage.setItem("energy-quest-motion-paused", "true"));
  await page.reload();
  await expect(page.locator("[data-map-surface]")).toHaveAttribute("data-motion-state", "playing");
  expect(await page.evaluate(() => localStorage.getItem("energy-quest-motion-paused"))).toBeNull();
  const target = page.locator('[data-carrier-choice="old4"]');
  const position = await target.getAttribute("style");
  await expect.poll(() => target.getAttribute("style")).not.toBe(position);

  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator("[data-map-surface]")).toHaveAttribute("data-motion-reason", "reduced-motion");
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/scenes.html?scene=lastmile&parcel=boat&recipient=khor");
  const sprites = page.locator("[data-lastmile-motion]");
  await expect(sprites).toBeVisible();
  const state = () => sprites.evaluate(root => {
    const staticSprites = [...root.children].filter(node => node.tagName === "IMG");
    const rotor = root.querySelector(":scope > div > img")!;
    return {
      staticTransforms: staticSprites.map(node => getComputedStyle(node).transform),
      rotorAnimation: getComputedStyle(rotor).animationName,
      rotorTransform: getComputedStyle(rotor).transform,
    };
  });
  await expect.poll(async () => (await state()).rotorAnimation).toContain("rotor");
  const initialRotor = (await state()).rotorTransform;
  expect((await state()).staticTransforms).toEqual(["none", "none", "none", "none"]);
  await expect.poll(async () => (await state()).rotorTransform).not.toBe(initialRotor);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect.poll(async () => (await state()).rotorAnimation).toBe("none");
});
