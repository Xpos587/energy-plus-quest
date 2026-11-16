import { expectNoInteractionDecorations } from './helpers/interaction-decorations';
import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function expectScreenIdentity(page: Page) {
  const heading = page.locator("h1");
  await expect(heading).toHaveCount(1);
  const title = await heading.evaluate(node => {
    const copy = node.cloneNode(true) as HTMLElement;
    copy.querySelectorAll("small").forEach(label => label.remove());
    return copy.textContent!.trim().replace(/\s+/g, " ");
  });
  await expect(page).toHaveTitle(`${title} — Доставляем радость`);
  await expect(page.locator("head > title")).toHaveCount(1);
}

async function readBriefing(page: Page) {
  await expectScreenIdentity(page);
  const briefing = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && (await briefing.getAttribute("data-reading")) === "true"; n++) {
    await briefing.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
  }
  await expect(briefing).toHaveAttribute("data-reading", "false");
  await expectNoInteractionDecorations(page);
}

async function finishResult(page: Page, nextLabel: string) {
  const reader = page.locator("[data-result-reader]");
  await expect(reader).toBeVisible({ timeout: 15000 });
  await expectScreenIdentity(page);
  const further = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 40 && await further.isVisible(); n++) {
    await expect(further).toBeInViewport({ ratio: 0.98 });
    await expectNoInteractionDecorations(page);
    await further.click();
  }
  const next = reader.getByRole("button", { name: nextLabel, exact: true });
  await expect(next).toBeInViewport({ ratio: 0.98 });
  await expectNoInteractionDecorations(page);
  await next.click();
}

for (const route of [
  { profile: "professional", recipient: "alva", parcel: "camera", carrier: "crew", lastmile: "pipe-carrier" },
  { profile: "student", recipient: "khor", parcel: "boat", carrier: "old4", lastmile: "helicopter" },
  { profile: "professional", recipient: "arseniy", parcel: "socks", carrier: "near", lastmile: "rover" },
] as const) {
test(`${route.parcel}/${route.lastmile} reaches certificate, restores progress and restarts`, async ({ page }, info) => {
  test.setTimeout(90000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await openCarrier(page, route.profile, route.recipient, route.parcel);
  await expectScreenIdentity(page);
  await pickCarrier(page, route.carrier);
  await page.locator("[data-choice-confirm]").click();
  await finishResult(page, "Дальше: погрузка");

  for (const [scene, choice] of [["compact", "auto"], ["inventory", "wms"], ["crane", "remote"], ["lastmile", route.lastmile]]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    await readBriefing(page);
    const marker = page.locator(`[data-hotspot="${choice}"]`);
    await expect(marker).toBeVisible();
    await expect(marker).toBeEnabled();
    await marker.focus();
    await expect(marker).toBeFocused();
    await expectNoInteractionDecorations(page);
    await page.keyboard.press("Enter");
    await expect(page.locator("[data-choice-inspection]")).toBeVisible();
    await expect(page.locator("[data-result-reader]")).toHaveCount(0);
    await expectNoInteractionDecorations(page);
    await expect(page.locator("[data-choice-confirm]")).toBeInViewport({ ratio: 0.98 });
    await page.locator("[data-choice-confirm]").click();
    await expect(page.locator("[data-result-reader]")).toBeVisible({ timeout: 15000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    // Result text can appear before its asynchronously decoded illustration.
    await page.locator("[data-scene-consequence] img").evaluateAll(images =>
      Promise.all(images.map(image => (image as HTMLImageElement).decode())),
    );
    await page.screenshot({ path: info.outputPath(`${scene}-result.png`) });
    if (scene === "inventory") {
      await page.reload();
      await expect(page.locator('[data-scene="inventory"] [data-result-reader]')).toBeVisible();
    }
    await finishResult(page, scene === "lastmile" ? "К вручению подарка" : scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
  }
  await expect(page.locator("[data-journey-ending]")).toBeVisible();
  await expectScreenIdentity(page);
  await expectNoInteractionDecorations(page);
  await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
  await expect(page.locator("[data-logist-certificate]")).toBeVisible();
  await expectScreenIdentity(page);
  await expect(page.locator("[data-certificate-totals] [data-metric]")).toHaveCount(3);
  await expectNoInteractionDecorations(page);
  await page.locator("[data-certificate-art]").evaluate((image: HTMLImageElement) => image.decode());
  await page.screenshot({ path: info.outputPath("certificate.png") });
  await page.reload();
  await expect(page.locator("[data-logist-certificate]")).toBeVisible();
  await expectScreenIdentity(page);
  await page.getByRole("button", { name: /заново/i }).click();
  await expect(page.locator("[data-intro-enter]")).toBeVisible();
  await page.locator("[data-intro-enter]").click();
  await page.locator("[data-intro-next]").click();
  await page.locator("[data-intro-start]").click();
  await expect(page.locator('[data-choice="professional"]')).toBeVisible();
  await expect(page.locator("[data-result-reader], [data-logist-certificate]")).toHaveCount(0);
  expect(errors).toEqual([]);
});
}
