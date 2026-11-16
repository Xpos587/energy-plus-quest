import { expect, test, type Page } from "@playwright/test";
import { openCarrier, pickCarrier } from "./helpers/open-preparation";

async function briefing(page: Page) {
  const panel = page.locator("[data-scene-briefing]");
  for (let n = 0; n < 30 && await panel.getAttribute("data-reading") === "true"; n++)
    await panel.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ }).click();
}

async function proceed(page: Page, label: string) {
  const reader = page.locator("[data-result-reader]");
  const further = reader.getByRole("button", { name: "Читать дальше", exact: true });
  for (let n = 0; n < 40 && await further.isVisible(); n++) await further.click();
  await reader.getByRole("button", { name: label, exact: true }).click();
}

async function savedAnswers(page: Page) {
  return page.evaluate(() => {
    const { scope } = JSON.parse(localStorage.getItem("energy-quest-save-v1")!);
    return JSON.parse(localStorage.getItem(`${scope}:scenes`)!).progress.answers;
  });
}

test("revised decisions survive reload without adding discarded scores", async ({ page }) => {
  test.setTimeout(90000);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await openCarrier(page, "professional", "alva", "camera");
  await pickCarrier(page, "crew");
  await page.locator("[data-choice-confirm]").click();
  await proceed(page, "Дальше: погрузка");
  const answers: Record<string, string> = {};

  for (const [scene, original, revised] of [
    ["compact", "place-1", "auto"],
    ["inventory", "entrance", "wms"],
    ["crane", "rush", "remote"],
    ["lastmile", "robot", "rover"],
  ]) {
    await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
    for (const choice of [original, revised]) {
      await briefing(page);
      const target = page.locator(`[data-hotspot="${choice}"]`);
      await expect(target).toBeVisible();
      await expect(target).toBeEnabled();
      await target.focus();
      await expect(target).toBeFocused();
      await page.keyboard.press("Enter");
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-result-reader]")).toBeVisible();
      if (choice === original) {
        await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
        await expect(page.locator("[data-result-reader]")).toHaveCount(0);
        await expect.poll(() => savedAnswers(page)).toEqual(answers);
        await page.reload();
        await expect(page.locator(`[data-scene="${scene}"]`)).toBeVisible();
        await expect(page.locator("[data-result-reader]")).toHaveCount(0);
      }
    }
    answers[scene] = revised;
    await expect.poll(() => savedAnswers(page)).toEqual(answers);
    await page.reload();
    await expect(page.locator(`[data-scene="${scene}"] [data-result-reader]`)).toBeVisible();
    await expect.poll(() => savedAnswers(page)).toEqual(answers);
    await proceed(page, scene === "lastmile" ? "К вручению подарка" : scene === "compact" ? "Дальше: склад" : scene === "inventory" ? "Дальше: баржа" : "Дальше: последняя миля");
  }
  await page.getByRole("button", { name: "Узнать, какой вы логист" }).click();
  // Crew + camera/auto + WMS + remote crane + rover = raw 10/15/23, final 7/8/10.
  const totals = page.locator("[data-certificate-totals] strong");
  await expect(totals).toHaveText(["7", "8", "10"]);
  await page.reload();
  await expect(totals).toHaveText(["7", "8", "10"]);
});
