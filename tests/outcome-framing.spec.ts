import { expect, test } from "@playwright/test";

const cases = [
  ...["old", "old4", "near", "crew", "express"].map((choice) => ({
    scene: "carrier",
    choice,
    parcel: "camera",
    recipient: "alva",
  })),
  ...["place-1", "place-2", "place-3", "place-4"].map((choice) => ({
    scene: "compact",
    choice,
    parcel: "camera",
    recipient: "alva",
  })),
  ...Object.entries({
    inventory: ["entrance", "keeper", "wms", "alphabet"],
    crane: ["rush", "wait", "petr", "remote"],
    lastmile: ["helicopter", "rover", "robot", "pipe-carrier"],
  }).flatMap(([scene, choices]) =>
    choices.map((choice) => ({
      scene,
      choice,
      parcel: "camera",
      recipient: "alva",
    })),
  ),
  { scene: "inventory", choice: "alphabet", parcel: "boat", recipient: "alva" },
  {
    scene: "inventory",
    choice: "alphabet",
    parcel: "socks",
    recipient: "alva",
  },
  {
    scene: "lastmile",
    choice: "pipe-carrier",
    parcel: "boat",
    recipient: "alva",
  },
  {
    scene: "lastmile",
    choice: "helicopter",
    parcel: "camera",
    recipient: "arseniy",
  },
];
for (const width of [320, 390, 1440]) {
  test(`fullscreen result compositions at ${width}px`, async ({ page }, info) => {
    test.setTimeout(90000);
    await page.setViewportSize({
      width,
      height: width === 320 ? 568 : width === 390 ? 844 : 900,
    });
    for (const { scene, choice, parcel, recipient } of cases) {
      if (scene === "carrier") {
        await page.goto("/");
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        for (const id of ["professional", recipient, parcel])
          await page.locator(`[data-choice="${id}"]`).click();
      } else
        await page.goto(
          `/scenes.html?scene=${scene}&parcel=${parcel}&recipient=${recipient}`,
        );
      const reading = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
      await expect(reading).toBeVisible();
      for (let step = 0; step < 30 && await reading.isVisible(); step++) await reading.click();
      await page
        .locator(
          scene === "carrier"
            ? `[data-carrier-choice="${choice}"]`
            : `[data-choice-id="${choice}"]`,
        )
        .click();
      await page.locator("[data-choice-confirm]").click();
      await expect(page.locator("[data-pan-viewport]")).toHaveCount(scene === "compact" ? 0 : 1);
      const art = page.locator(
        scene === "carrier"
          ? "[data-result-art]"
          : scene === "compact"
            ? '[data-world-scene="compact"]'
            : "[data-scene-consequence]",
      );
      await expect(art).toBeVisible();
      await art
        .locator("img")
        .evaluateAll((images) =>
          Promise.all(
            images.map((image) => (image as HTMLImageElement).decode()),
          ),
        );
      if (width < 600) {
        const imageBox = await art.boundingBox();
        const panelBox = await page.locator("[data-sheet-panel]").boundingBox();
        expect(imageBox!.y).toBe(0);
        expect(imageBox!.height).toBe(page.viewportSize()!.height);
        expect(imageBox!.y + imageBox!.height).toBeGreaterThan(panelBox!.y);
      }
      await art.evaluate((el) => {
        el.scrollLeft = 100;
        el.scrollTop = 100;
      });
      expect(await art.evaluate((el) => el.scrollTop)).toBe(0);
      if (scene !== "compact") {
        expect(await art.evaluate((el) => el.scrollLeft)).toBe(
          await art.evaluate((el) => Math.min(100, el.scrollWidth - el.clientWidth)),
        );
      }
      await page.screenshot({
        path: info.outputPath(`${scene}-${choice}-${parcel}-${recipient}.png`),
      });
    }
  });
}
