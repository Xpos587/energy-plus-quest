// Scene 4 result stills are the last frame of each quay consequence, captured from the live
// house-style layers so the still matches the animation the player just watched.
// Needs a dev server: bunx vite --host 127.0.0.1 --port 4173 --strictPort
// Usage: bun scripts/capture-barge-outcomes.mjs [baseUrl]
import { chromium } from "playwright";
import sharp from "sharp";

const base = process.argv[2] ?? "http://127.0.0.1:4173";
// Milliseconds after confirm when each consequence has settled on its end pose.
const at = { remote: 4300, rush: 6350, wait: 5850, petr: 7150 };
const browser = await chromium.launch();
for (const [id, ms] of Object.entries(at)) {
  const context = await browser.newContext({ viewport: { width: 1942, height: 900 }, deviceScaleFactor: 1.5 });
  const page = await context.newPage();
  await page.goto(`${base}/scenes.html?scene=crane&parcel=camera&recipient=alva`);
  const intro = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && (await intro.isVisible().catch(() => false)); n++) await intro.click();
  await page.locator(`[data-hotspot="${id}"]`).click();
  // The wide art fills the frame alone: no card, pins or skip button over the quay.
  await page.addStyleTag({
    content:
      "[data-barge-art]{position:fixed!important;left:0!important;top:0!important;width:1942px!important;height:809px!important;z-index:9999} [data-barge-art] [class*=skip],[data-barge-art] button{display:none!important}",
  });
  await page.locator("[data-choice-confirm]").evaluate((el) => el.click());
  await page.waitForTimeout(ms);
  await page.evaluate(() => { window.requestAnimationFrame = () => 0; });
  await page.waitForTimeout(400);
  if ((await page.locator("[data-barge-art]").getAttribute("data-barge-art")) !== "wide") throw new Error(`${id}: not the wide art`);
  const png = await page.screenshot({ clip: { x: 0, y: 0, width: 1942, height: 809 } });
  await sharp(png).webp({ quality: 86, effort: 6 }).toFile(`public/scene-art/barge-v4/outcome-${id}.webp`);
  console.log(id, "ok");
  await context.close();
}
await browser.close();
