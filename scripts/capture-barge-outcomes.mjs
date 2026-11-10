// Scene 4 result stills capture the gift aboard just after departure begins, before the
// bow leaves the camera. Live house-style layers keep the still consistent with the animation.
// outcome-<id>.webp: wide drawing for phones/banners; outcome-<id>-rail.webp: the mid
// camera cut at 1.11:1 for the desktop rail (0.96…1.28:1); -portrait uses the tall camera.
// Check the hull's cover-safe bounds before overwriting any still.
// Needs a dev server WITHOUT hydrate: bunx vite --host 127.0.0.1 --port 4173 --strictPort
// Usage: bun scripts/capture-barge-outcomes.mjs [baseUrl] [wide|mid|tall]
import { chromium } from "playwright";
import sharp from "sharp";
import { craneArtwork } from "../src/scenes/crane/artwork";
import { craneDuration } from "../src/scenes/crane/consequence";

const base = process.argv[2] ?? "http://127.0.0.1:4173";
const only = process.argv[3];
const shots = {
  wide: { ...craneArtwork.wide, suffix: "" },
  mid: { ...craneArtwork.mid, suffix: "-rail" },
  tall: { ...craneArtwork.tall, suffix: "-portrait" },
};

/** Pad the story for the rail's cover crops, bounded by the original camera. */
async function railCrop(page, frameW, frameH) {
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
  for (const id of ["remote", "rush", "petr"]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1.5, serviceWorkers: "block" });
    const page = await context.newPage();
    // Install before navigation so RAF and performance.now share the same origin.
    await page.clock.install();
    await page.goto(`${base}/scenes.html?scene=crane&parcel=camera&recipient=alva`);
    const intro = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
    for (let n = 0; n < 20 && (await intro.isVisible().catch(() => false)); n++) await intro.click();
    await page.locator(`[data-hotspot="${id}"]`).evaluate((el) => el.click());
    // The drawing fills the frame alone, at its own size: no card, pins, skip button or camera crop.
    const frame = `[data-barge-art]{position:fixed!important;left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;z-index:9999}
        [data-barge-art]>div{left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;transition:none!important}
        [data-barge-art] [class*=skip],[data-barge-art] button{display:none!important}`;
    await page.addStyleTag({ content: frame });
    // This animation badge belongs to the far crane, outside the rail still; avoid a cut-off word.
    if (format === "mid") await page.addStyleTag({ content: "[data-barge-later]{display:none!important}" });
    await page.clock.pauseAt(Date.now() + 1000);
    await page.locator("[data-choice-confirm]").evaluate((el) => el.click());
    // 400 ms into the common 1600 ms departure: gift released, actor's reaction visible.
    await page.clock.runFor(craneDuration(id) - 1200);
    if (!await page.locator("[data-playing] [data-sailing] [data-layer=gift]").count())
      throw new Error(`${id}: expected the loaded barge departing`);
    await page.locator("[data-barge-art] img").evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
    const drawn = await page.locator("[data-barge-art]").getAttribute("data-barge-art");
    if (drawn !== format) throw new Error(`${id}: drew ${drawn}, not ${format}`);
    const clip = format === "mid" ? await railCrop(page, width, height) : { x: 0, y: 0, width, height };
    const hull = await page.locator('[data-sailing] img[data-layer=barge]').boundingBox();
    const inset = format === "mid" ? 0.0675 : 0;
    if (!hull || hull.x < clip.x + clip.width * inset || hull.y < clip.y + clip.height * inset ||
        hull.x + hull.width > clip.x + clip.width * (1 - inset) || hull.y + hull.height > clip.y + clip.height * (1 - inset))
      throw new Error(`${id}/${format}: hull leaves the cover-safe crop`);
    const png = await page.screenshot({ clip });
    await sharp(png).webp({ quality: 86, effort: 6 }).toFile(`public/scene-art/barge-v5/outcome-${id}${suffix}.webp`);
    console.log(id + suffix, "ok", JSON.stringify(clip, (_, v) => (typeof v === "number" ? Math.round(v) : v)));
    await context.close();
  }
}
await browser.close();
