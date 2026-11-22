import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function resume(page: Page, scene: "inventory" | "crane", session?: string) {
  await page.goto("/");
  await page.evaluate(({ scene, session }) => {
    localStorage.clear();
    const scope = "quest-recovery-test";
    localStorage.setItem("energy-quest-save-v1", JSON.stringify({ version: 1, scope,
      state: { step: "outcome", profile: "professional", recipient: "alva", parcel: "camera", carrier: "crew" },
    }));
    localStorage.setItem(`${scope}:intro-seen`, "true");
    localStorage.setItem(`${scope}:remaining`, "true");
    localStorage.setItem(`${scope}:scenes`, session ?? JSON.stringify({
      progress: { sceneIndex: scene === "crane" ? 2 : 1, phase: "result", finished: false,
        answers: { compact: "auto", inventory: "wms", ...(scene === "crane" ? { crane: "remote" } : {}) },
      },
    }));
  }, { scene, session });
}

for (const scene of ["inventory", "crane"] as const) {
  test(`${scene} artwork retries after a failed responsive image`, async ({ page }, info) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await resume(page, scene);
    // Scene 4 keeps the live quay on the result (client Fedya 22.11): its plate is the image to fail.
    const pattern = scene === "crane" ? /barge-v7\/desk\/plate/ : /outcome-wms/;
    let failures = 0;
    await page.route(pattern, route => { failures++; return route.abort(); });
    await page.reload();
    const art = page.locator(scene === "crane" ? "[data-barge-art]" : `[data-outcome-scene="${scene}"]`);
    await expect(art.locator('[data-artwork-status="error"]')).toBeVisible();
    expect(failures).toBeGreaterThan(0);
    await page.unroute(pattern);
    await art.getByRole("button", { name: "Повторить", exact: true }).click();
    await expect(art.locator("[data-artwork-status]")).toHaveCount(0);
    await art.locator("img").first().evaluate((image: HTMLImageElement) => image.decode());
    expect(await art.locator("img").first().evaluate((image: HTMLImageElement) => image.naturalWidth)).toBeGreaterThan(0);
    await expect(page.getByRole("button", { name: "Изменить выбор", exact: true })).toBeEnabled();
    await page.screenshot({ path: info.outputPath(`${scene}-recovered.png`) });
    await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
    await expect(page.locator("[data-result-reader]")).toHaveCount(0);
  });
}

async function readBriefing(page: Page) {
  const panel = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && await panel.getAttribute("data-reading") === "true"; n++)
    await panel.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  await expect(panel).toHaveAttribute("data-reading", "false");
}

async function proceed(page: Page, label: string) {
  const reader = page.locator("[data-result-reader]");
  const further = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 40 && await further.isVisible(); n++) await further.click();
  await reader.getByRole("button", { name: label, exact: true }).click();
}

for (const kind of ["game", "scene"] as const) {
  test(`corrupt ${kind} saves recover to a playable starting point`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    for (const saved of ["{broken-json", JSON.stringify(kind === "game"
      ? { version: 1, scope: "quest-invalid-game", state: { step: "outcome", profile: "unknown" } }
      : { progress: { sceneIndex: 999, phase: "result", answers: {}, finished: true } })]) {
      await resume(page, "crane", saved);
      if (kind === "game") {
        await page.evaluate(saved => localStorage.setItem("energy-quest-save-v1", saved), saved);
      }
      await page.reload();
      if (kind === "game") {
        await expect(page.locator("[data-intro-enter]")).toBeVisible();
        await page.locator("[data-intro-enter]").click();
        await page.locator("[data-intro-next]").click();
        await page.locator("[data-intro-start]").click();
        await page.locator('[data-choice="professional"]').click();
        await expect(page.locator('[data-preparation-step="recipient"]')).toBeVisible();
      } else {
        await expect(page.locator('[data-scene="compact"]')).toBeVisible();
        expect(await page.evaluate(() => JSON.parse(localStorage.getItem("energy-quest-save-v1")!).state))
          .toMatchObject({ profile: "professional", recipient: "alva", parcel: "camera", carrier: "crew" });
        await readBriefing(page);
        await page.locator('[data-hotspot="auto"]').focus();
        await page.keyboard.press("Enter");
        await page.locator("[data-choice-confirm]").click();
        await expect(page.locator("[data-result-reader]")).toBeVisible();
      }
    }
    expect(errors).toEqual([]);
  });
}

test("disabled browser storage still allows the complete journey and restart", async ({ page }) => {
  test.setTimeout(90000);
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.addInitScript(() => {
    for (const method of ["getItem", "setItem", "removeItem"])
      Object.defineProperty(Storage.prototype, method, {
        configurable: true,
        value() { throw new DOMException("Storage disabled for recovery check", "SecurityError"); },
      });
  });
  await openCarrier(page, "professional", "alva", "camera");
  await pickCarrier(page, "crew");
  await page.locator("[data-choice-confirm]").click();
  await proceed(page, "Дальше: погрузка");
  for (const [scene, choice] of [["compact", "auto"], ["inventory", "wms"], ["crane", "remote"], ["lastmile", "rover"]]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await readBriefing(page);
    const target = page.locator(`[data-hotspot="${choice}"]`);
    await expect(target).toBeVisible();
    await expect(target).toBeEnabled();
    await target.focus();
    await expect(target).toBeFocused();
    await page.keyboard.press("Enter");
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible();
    await proceed(page, scene === "lastmile" ? "К вручению подарка" : scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
  }
  await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
  await expect(page.locator("[data-certificate-totals] strong")).toHaveText(["7", "8", "10"]);
  await page.getByRole("button", { name: /заново/i }).click();
  await expect(page.locator("[data-intro-enter]")).toBeVisible();
  await page.reload();
  await expect(page.locator("[data-intro-enter]")).toBeVisible();
  expect(errors).toEqual([]);
});
