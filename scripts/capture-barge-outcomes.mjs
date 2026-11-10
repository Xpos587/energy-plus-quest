// Scene 4 result stills are the last frame of each quay consequence, captured from the live
// house-style layers so the still matches the animation the player just watched.
// outcome-<id>.webp: the wide drawing, for full-width results (phones, wide banners).
// outcome-<id>-rail.webp: the tall drawing cut at 1.11:1 for the desktop rail box (0.96…1.28:1);
//   barge, near crane, ladder and ПРУ office sit in its central 86% so cover never cuts them.
// Needs a dev server WITHOUT hydrate: bunx vite --host 127.0.0.1 --port 4173 --strictPort
// Usage: bun scripts/capture-barge-outcomes.mjs [baseUrl] [wide|tall]
import { chromium } from "playwright";
import sharp from "sharp";
import { craneArtwork } from "../src/scenes/crane/artwork";

const base = process.argv[2] ?? "http://127.0.0.1:4173";
const only = process.argv[3];
// Milliseconds after confirm when each consequence has settled on its end pose.
// Upper bound per consequence; the capture steps a fake clock to the frame before it ends.
const at = { remote: 9000, rush: 11000, wait: 10000, petr: 12000 };
const shots = {
  wide: { width: 1942, height: 809, suffix: "" },
  tall: { width: 1024, height: 1536, suffix: "-rail" },
};

/** The rail crop: the story as drawn at the captured moment (office, Ivan, gift, near crane, ladder,
 * barge wherever it sailed), padded to fill 86.5% of a 1.11:1 cut, so 0.96…1.28:1 covers keep it whole. */
async function railCrop(page) {
  const { width: frameW, height: frameH } = craneArtwork.tall;
  const rects = await page.evaluate(() => [...document.querySelectorAll(
    "[data-barge-art] :is([data-layer=pru], [data-layer=office], [data-layer=gift], [data-layer=ladder], [data-layer=top], [data-layer=hook], [data-layer=walker]), [data-barge-art] [data-sailing] img[src*=barge]",
  )].map((e) => e.getBoundingClientRect()).filter((r) => r.width && r.height).map((r) => [r.left, r.top, r.right, r.bottom]));
  const x0 = Math.min(...rects.map((r) => r[0])), y0 = Math.min(...rects.map((r) => r[1]));
  const x1 = Math.min(frameW, Math.max(...rects.map((r) => r[2]))), y1 = Math.min(frameH, Math.max(...rects.map((r) => r[3])));
  const ratio = 1.11, safe = 0.865;
  const width = Math.min(frameW, frameH * ratio, Math.max((x1 - x0) / safe, ((y1 - y0) / safe) * ratio));
  const height = width / ratio;
  const clamp = (v, size, max) => Math.max(0, Math.min(max - size, v - size / 2));
  return { x: clamp((x0 + x1) / 2, width, frameW), y: clamp((y0 + y1) / 2, height, frameH), width, height };
}

const browser = await chromium.launch();
for (const [format, { width, height, suffix }] of Object.entries(shots).filter(([name]) => !only || name === only)) {
  for (const [id, ms] of Object.entries(at)) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1.5, serviceWorkers: "block" });
    const page = await context.newPage();
    await page.goto(`${base}/scenes.html?scene=crane&parcel=camera&recipient=alva`);
    const intro = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
    for (let n = 0; n < 20 && (await intro.isVisible().catch(() => false)); n++) await intro.click();
    await page.locator(`[data-hotspot="${id}"]`).click();
    // The drawing fills the frame alone, at its own size: no card, pins, skip button or camera crop.
    const frame = `[data-barge-art]{position:fixed!important;left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;z-index:9999}
        [data-barge-art]>div{left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;transition:none!important}
        [data-barge-art] [class*=skip],[data-barge-art] button{display:none!important}`;
    await page.addStyleTag({ content: frame });
    // A fake clock steps the consequence to exactly `ms`, whatever the machine load.
    await page.clock.install();
    await page.clock.pauseAt(Date.now() + 1000);
    await page.locator("[data-choice-confirm]").evaluate((el) => el.click());
    // Step to the last frame before the quay hands over to the result: the settled end pose.
    let end = 0;
    for (; end < ms && (await page.locator("[data-playing]").count()); end += 50) await page.clock.runFor(50);
    if (!end) throw new Error(`${id}: no consequence played`);
    await page.reload();
    for (let n = 0; n < 20 && (await intro.isVisible().catch(() => false)); n++) await intro.click();
    await page.locator(`[data-hotspot="${id}"]`).click();
    await page.addStyleTag({ content: frame });
    await page.clock.install();
    await page.clock.pauseAt(Date.now() + 1000);
    await page.locator("[data-choice-confirm]").evaluate((el) => el.click());
    await page.clock.runFor(end - 100);
    await page.locator("[data-barge-art] img").evaluateAll((images) => Promise.all(images.map((image) => image.decode().catch(() => {}))));
    const drawn = await page.locator("[data-barge-art]").getAttribute("data-barge-art");
    if (drawn !== format) throw new Error(`${id}: drew ${drawn}, not ${format}`);
    const clip = format === "tall" ? await railCrop(page) : { x: 0, y: 0, width, height };
    const png = await page.screenshot({ clip });
    await sharp(png).webp({ quality: 86, effort: 6 }).toFile(`public/scene-art/barge-v5/outcome-${id}${suffix}.webp`);
    console.log(id + suffix, "ok", JSON.stringify(clip, (_, v) => (typeof v === "number" ? Math.round(v) : v)));
    await context.close();
  }
}
await browser.close();
