import { mkdir } from "node:fs/promises";
import { chromium } from "@playwright/test";

const destination = "dist/review/ux-directions-2026-09-25";
await mkdir(destination, { recursive: true });
const browser = await chromium.launch();
const failures = [];
for (const [device, viewport] of Object.entries({
  phone: { width: 390, height: 844 },
  smallPhone: { width: 320, height: 568 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1440, height: 900 },
  landscape: { width: 844, height: 390 },
})) {
  for (const variant of ["brand"]) {
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    page.on("pageerror", (error) => failures.push(`${device}/${variant}: ${error.message}`));
    await page.goto(`http://127.0.0.1:4214/scenes.html?scene=compact&ux=${variant}`);
    if (device === "phone" || device === "desktop") await page.screenshot({ path: `${destination}/${device}-${variant}-intro.png` });
    await page.getByRole("button", { name: "Закрыть условие" }).click();
    await page.locator("[data-world-scene=compact] img, [data-world-scene=compact] image").first().waitFor({state:"attached"});
    await page.screenshot({ path: `${destination}/${device}-${variant}.png` });
    const metrics = await page.evaluate(() => {
      const plane = document.querySelector("[data-world-plane]").getBoundingClientRect();
      const view = document.querySelector("[data-world-scene=compact]").getBoundingClientRect();
      const markers = [...document.querySelectorAll("[data-hotspot]")].map((item) => {
        const rect = item.getBoundingClientRect();
        return { visible: rect.left >= 0 && rect.right <= innerWidth && rect.top >= 0 && rect.bottom <= innerHeight, width: rect.width };
      });
      return { plane: { left: plane.left, right: plane.right, width: plane.width }, view: { width: view.width }, markers, overflow: document.documentElement.scrollWidth > innerWidth + 1 };
    });
    if (metrics.overflow || metrics.markers.some((marker) => marker.width < 44 || (device !== "landscape" && !marker.visible))) failures.push(`${device}/${variant}: ${JSON.stringify(metrics)}`);
    await page.locator('[data-hotspot="place-2"]').click();
    if (device === "phone" || device === "desktop") await page.screenshot({ path: `${destination}/${device}-${variant}-choice.png` });
    const confirm = page.locator("[data-choice-confirm]");
    if (!(await confirm.isVisible())) failures.push(`${device}/${variant}: choice confirmation hidden`);
    await confirm.click();
    if (!(await page.locator("[data-result]").isVisible())) failures.push(`${device}/${variant}: result hidden`);
    if (device === "phone" || device === "desktop") await page.screenshot({ path: `${destination}/${device}-${variant}-result.png` });
    console.log(device, variant, JSON.stringify(metrics));
    await page.close();
  }
}
for (const scene of ["inventory", "crane", "lastmile"]) {
  for (const [device, viewport] of Object.entries({
    phone: { width: 390, height: 844 },
    desktop: { width: 1440, height: 900 },
  })) {
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    page.on("pageerror", (error) => failures.push(`${scene}/${device}: ${error.message}`));
    await page.goto(`http://127.0.0.1:4214/scenes.html?scene=${scene}&ux=brand`);
    await page.getByRole("button", { name: "Закрыть условие" }).click();
    await page.screenshot({ path: `${destination}/${scene}-${device}-brand.png` });
    const targets = page.locator("[data-hotspot]");
    if (!(await targets.count())) failures.push(`${scene}/${device}: no hotspots`);
    else {
      await targets.first().click();
      if (!(await page.locator("[data-choice-confirm]").isVisible())) failures.push(`${scene}/${device}: no confirmation`);
      await page.locator("[data-choice-confirm]").click();
      if (!(await page.locator("[data-result]").isVisible())) failures.push(`${scene}/${device}: no result`);
    }
    await page.close();
  }
}
await browser.close();
if (failures.length) {
  console.error(failures.join("\n"));
  process.exitCode = 1;
}
