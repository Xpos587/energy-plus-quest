// Scene 4 result stills capture the gift loaded aboard the moored barge. Live house-style layers keep the still consistent with the animation.
// Owner 22.11: one composition everywhere. outcome-<id>.webp: the whole desktop drawing; outcome-<id>-rail.webp:
// the same drawing cut at 1.11:1 for the desktop rail (0.96…1.28:1).
// Check the hull's cover-safe bounds before overwriting any still.
// Needs a dev server WITHOUT hydrate: bunx vite --host 127.0.0.1 --port 4173 --strictPort
// Usage: bun scripts/capture-barge-outcomes.mjs [baseUrl] [full|rail]
import { chromium } from "playwright";
import sharp from "sharp";
import { writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { craneArtwork } from "../src/scenes/crane/artwork";
import { craneDuration } from "../src/scenes/crane/consequence";

const base = process.argv[2] ?? "http://127.0.0.1:4173";
const only = process.argv[3];
const shots = {
  full: { ...craneArtwork.desk, suffix: "" },
  rail: { ...craneArtwork.desk, suffix: "-rail" },
};

/** Pad the story for the rail's cover crops, bounded by the original camera. */
async function railCrop(page, frameW, frameH) {
  const rects = await page.evaluate(() => [...document.querySelectorAll(
    // v6: the ПРУ is far left of the barge crane; the near-square rail keeps the loading end whole.
    "[data-barge-art] :is([data-layer=far], [data-layer=gift], [data-layer=ladder], [data-layer=top], [data-layer=hook], [data-layer=walker]), [data-barge-art] img[data-layer=barge]",
  )].map((e) => e.getBoundingClientRect()).filter((r) => r.width && r.height).map((r) => [r.left, r.top, r.right, r.bottom]));
  const x0 = Math.min(...rects.map((r) => r[0])), y0 = Math.min(...rects.map((r) => r[1]));
  const x1 = Math.min(frameW, Math.max(...rects.map((r) => r[2]))), y1 = Math.min(frameH, Math.max(...rects.map((r) => r[3])));
  const ratio = 1.11, safe = 0.85; // v6: hull sits on the crop edge at 0.865 (float ties)
  const width = Math.min(frameW, frameH * ratio, Math.max((x1 - x0) / safe, ((y1 - y0) / safe) * ratio));
  const height = width / ratio;
  const clamp = (v, size, max) => Math.max(0, Math.min(max - size, v - size / 2));
  return { x: clamp((x0 + x1) / 2, width, frameW), y: clamp((y0 + y1) / 2, height, frameH), width, height };
}

const receipts = [];
const browser = await chromium.launch();
for (const [shot, { width, height, suffix }] of Object.entries(shots).filter(([name]) => !only || name === only)) {
  for (const id of ["remote", "rush", "petr"]) {
    const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 2, serviceWorkers: "block" });
    const page = await context.newPage();
    // Install before navigation so RAF and performance.now share the same origin.
    await page.clock.install();
    await page.goto(`${base}/scenes.html?scene=crane&parcel=camera&recipient=alva`);
    await page.locator("[data-hotspot]").first().waitFor({ state: "attached" });
    await page.locator(`[data-hotspot="${id}"]`).click();
    // The drawing fills the frame alone, at its own size: no card, pins, skip button or camera crop.
    const frame = `[data-barge-art]{position:fixed!important;left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;z-index:9999}
        [data-barge-art]>div{left:0!important;top:0!important;width:${width}px!important;height:${height}px!important;transition:none!important}
        [data-barge-art] [class*=skip],[data-barge-art] button{display:none!important}`;
    await page.addStyleTag({ content: frame });
    // This animation badge belongs to the far crane, outside the rail still; avoid a cut-off word.
    if (shot === "rail") await page.addStyleTag({ content: "[data-barge-later]{display:none!important}" });
    await page.locator(`[data-barge-art="desk"] > div`).waitFor({ state: "visible" });
    await page.clock.pauseAt(Date.now() + 1000);
    await page.locator("[data-choice-confirm]").evaluate((el) => el.click());
    // Just before the end: gift released on the moored barge, reaction visible.
    await page.clock.runFor(craneDuration(id) - 300);
    if (!await page.locator("[data-playing] img[data-layer=gift]").count())
      throw new Error(`${id}: expected the gift loaded aboard`);
    await page.locator("[data-barge-art] img").evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
    const visibility = await page.locator("[data-barge-art] > div").evaluate((plane) => getComputedStyle(plane).visibility);
    // Only the quay itself: the result card below may still miss the very stills being captured.
    if (visibility !== "visible" || await page.locator("[data-barge-art] [data-artwork-status]").count())
      throw new Error(`${id}/${shot}: scene is not ready; refuse an empty/error still`);
    const drawn = await page.locator("[data-barge-art]").getAttribute("data-barge-art");
    if (drawn !== "desk") throw new Error(`${id}: drew ${drawn}, not desk`);
    const clip = shot === "rail" ? await railCrop(page, width, height) : { x: 0, y: 0, width, height };
    const hull = await page.locator('[data-barge-art] img[data-layer=barge]').boundingBox();
    const inset = shot === "rail" ? 0.0675 : 0;
    // v7: the stern runs off the drawing's own edge (mid/wide); only the in-picture sides need the cover-safe air.
    const cut = (edge, frameEdge) => Math.abs(edge - frameEdge) < 1;
    if (!hull || (hull.x < clip.x + clip.width * inset && !cut(hull.x, 0)) || (hull.y < clip.y + clip.height * inset && !cut(hull.y, 0)) ||
        (hull.x + hull.width > clip.x + clip.width * (1 - inset) && !cut(hull.x + hull.width, width)) ||
        (hull.y + hull.height > clip.y + clip.height * (1 - inset) && !cut(hull.y + hull.height, height)))
      throw new Error(`${id}/${shot}: hull leaves the cover-safe crop ${JSON.stringify({ clip, hull })}`);
    const png = await page.screenshot({ clip });
    const output = `public/scene-art/barge-v7/outcome-${id}${suffix}.webp`;
    const encoded = await sharp(png).webp({ quality: 92, effort: 6 }).toBuffer();
    const metadata = await sharp(encoded).metadata();
    await writeFile(output, encoded);
    receipts.push({ output, shot, id, clip, hull, inset, width: metadata.width, height: metadata.height,
      sha256: createHash("sha256").update(encoded).digest("hex") });
    console.log(id + suffix, "ok", JSON.stringify(clip, (_, v) => (typeof v === "number" ? Math.round(v) : v)));
    await context.close();
  }
}
await browser.close();
if (process.env.BARGE_CAPTURE_RECEIPT) await writeFile(process.env.BARGE_CAPTURE_RECEIPT, JSON.stringify(receipts, null, 2) + "\n");
