import { expect, test, type Page } from "@playwright/test";

const scenes = ["compact", "inventory", "crane", "lastmile"] as const;
const sizes = [
  { width: 320, height: 568 },
  { width: 390, height: 844 },
  { width: 844, height: 390 },
  { width: 1440, height: 900 },
];
const choices = {
  compact: ["place-1", "place-2", "place-3", "place-4", "auto"],
  inventory: ["entrance", "alphabet", "keeper", "wms"],
  crane: ["remote", "rush", "wait", "petr"],
  lastmile: ["helicopter", "rover", "robot", "pipe-carrier"],
} as const;
const parcels = ["boat", "camera", "socks"] as const;

async function assertFixedPage(page: Page, stage: string) {
  const defects = await page.evaluate((stage) => {
    const frame = document.querySelector<HTMLElement>("[data-interaction], [data-layout='result']");
    const panel = frame?.querySelector<HTMLElement>("[data-sheet-panel]");
    const errors: string[] = [];
    if (document.documentElement.scrollHeight > innerHeight + 1)
      errors.push(`page scrolls ${document.documentElement.scrollHeight - innerHeight}px`);
    if (panel && panel.scrollHeight > panel.clientHeight + 1)
      errors.push(`panel scrolls ${panel.scrollHeight - panel.clientHeight}px`);
    for (const button of panel?.querySelectorAll<HTMLButtonElement>("button") ?? []) {
      if (getComputedStyle(button).visibility !== "visible") continue;
      const rect = button.getBoundingClientRect();
      if (rect.top < -1 || rect.bottom > innerHeight + 1 || rect.left < -1 || rect.right > innerWidth + 1)
        errors.push(`${button.textContent?.trim().slice(0, 30)} outside viewport at ${Math.round(rect.bottom)}`);
      if (button.scrollHeight > button.clientHeight + 1 || button.scrollWidth > button.clientWidth + 1)
        errors.push(`${button.textContent?.trim().slice(0, 30)} text clips`);
    }
    return errors.map((error) => `${stage}: ${error}`);
  }, stage);
  expect(defects).toEqual([]);
}

async function enterChoice(page: Page) {
  for (let index = 0; index < 30; index++) {
    const briefing = page.locator("[data-scene-briefing]");
    const forward = briefing.getByRole("button", { name: /^(Далее|К выбору)$/ });
    if (!(await forward.isVisible())) break;
    await forward.click();
    if ((await briefing.getAttribute("data-reading")) === "false") break;
  }
  await expect(page.locator("[data-scene-choice], [data-hotspot]").first()).toBeVisible();
}

for (const size of sizes) {
  for (const scene of scenes) {
    test(`${scene} fits ${size.width}×${size.height} without page or choice scrolling`, async ({ page }) => {
      await page.setViewportSize(size);
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.goto(`/scenes.html?scene=${scene}&parcel=boat&recipient=khor&profile=professional`);
      await enterChoice(page);
      await assertFixedPage(page, `${scene} choice ${size.width}×${size.height}`);
      await page.locator("[data-world-scene] img").evaluateAll(async (images) => {
        await Promise.all(images.map((image) => (image as HTMLImageElement).decode().catch(() => undefined)));
      });
      await page.screenshot({ path: `/tmp/quest-fit-${scene}-${size.width}x${size.height}.png` });
      await page.locator("[data-scene-choice], [data-hotspot]").first().click();
      if (scene === "crane") await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-layout='result']")).toBeVisible();
      await page.screenshot({ path: `/tmp/quest-fit-result-${scene}-${size.width}x${size.height}.png` });
      await assertFixedPage(page, `${scene} result ${size.width}×${size.height}`);
    });
  }
}

for (const size of [{ width: 320, height: 568 }, { width: 844, height: 390 }]) {
  for (const scene of scenes) {
    for (const parcel of parcels) {
      test(`${scene}: every ${parcel} outcome fits ${size.width}×${size.height}`, async ({ page }) => {
        test.setTimeout(120_000);
        await page.setViewportSize(size);
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.goto(`/scenes.html?scene=${scene}&parcel=${parcel}&recipient=khor&profile=professional`);
        await enterChoice(page);
        await assertFixedPage(page, `${scene}/${parcel} choice ${size.width}×${size.height}`);
        for (const option of choices[scene]) {
          await page.locator(`[${scene === "crane" ? "data-hotspot" : "data-scene-choice"}="${option}"]`).click();
          if (scene === "crane") await page.locator("[data-choice-confirm]").click();
          await expect(page.locator("[data-layout='result']")).toBeVisible();
          if (scene === "inventory" && (option === "keeper" || option === "wms" || option === "alphabet") && parcel === "boat" && size.width === 320) {
            await page.locator("[data-scene-consequence] img").evaluateAll(async (images) => {
              await Promise.all(images.map((image) => (image as HTMLImageElement).decode().catch(() => undefined)));
            });
            await page.screenshot({ path: `/tmp/quest-fit-result-inventory-${option}-320x568.png` });
          }
          await assertFixedPage(page, `${scene}/${parcel}/${option} result ${size.width}×${size.height}`);
          await page.getByRole("button", { name: "Изменить выбор", exact: true }).click();
          await expect(page.locator(`[${scene === "crane" ? "data-hotspot" : "data-scene-choice"}="${option}"]`)).toBeVisible();
          await assertFixedPage(page, `${scene}/${parcel}/${option} return ${size.width}×${size.height}`);
        }
      });
    }
  }
}
