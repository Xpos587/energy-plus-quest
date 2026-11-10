// Records each barge consequence from the tap to the result screen (Playwright video) and
// writes a contact sheet of key frames. Usage: bun scripts/record-barge-outcomes.mjs <baseURL> <outDir> [tag]
import { chromium } from "playwright";
import { execFileSync } from "node:child_process";
import { mkdirSync, renameSync, rmSync } from "node:fs";
const [base = "http://127.0.0.1:4174", out = ".tmp-work/barge-anim", tag = ""] = process.argv.slice(2);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
for (const [w, h] of [[1440, 900], [390, 844]]) for (const id of ["remote", "rush", "petr"]) {
  const tmp = `${out}/raw-${id}-${w}`;
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, serviceWorkers: "block", recordVideo: { dir: tmp, size: { width: w, height: h } } });
  const page = await ctx.newPage();
  const t0 = Date.now();
  await page.goto(`${base}/scenes.html?scene=crane&parcel=camera&recipient=alva`);
  const next = page.getByRole("button", { name: /^(Далее|К выбору|К сцене)$/ });
  for (let n = 0; n < 20 && (await next.isVisible()); n++) await next.click();
  await page.locator(`[data-hotspot="${id}"]`).click();
  await page.waitForTimeout(700);
  // Let every cast sprite decode first so the recording shows the art, not loading gaps.
  await page.waitForLoadState("networkidle");
  const tap = (Date.now() - t0) / 1000;
  await page.locator("[data-choice-confirm]").click();
  await page.locator("[data-scene-consequence] img").waitFor({ timeout: 20000 });
  const result = (Date.now() - t0) / 1000;
  await page.waitForTimeout(2200);
  const video = await page.video().path();
  await ctx.close();
  const name = `${out}/${id}-${w}x${h}${tag}`;
  renameSync(video, `${name}.webm`);
  rmSync(tmp, { recursive: true, force: true });
  // Key frames: every 0.5 s from the tap to 1.5 s after the result appears.
  const from = Math.max(0, tap - 0.2), span = result + 1.5 - from;
  const n = Math.ceil(span / 0.5);
  const cols = w > h ? 4 : 8;
  execFileSync("ffmpeg", ["-v", "error", "-y", "-ss", String(from), "-t", String(span), "-i", `${name}.webm`,
    "-vf", `fps=2,scale=${w > h ? 480 : 195}:-1,drawtext=text='%{pts\\:hms}':x=6:y=6:fontsize=14:fontcolor=white:box=1:boxcolor=black@0.6,tile=${cols}x${Math.ceil(n / cols)}`,
    "-frames:v", "1", `${name}-sheet.jpg`]);
  console.log(id, `${w}x${h}`, `tap ${tap.toFixed(1)}s result ${result.toFixed(1)}s (${(result - tap).toFixed(1)}s)`);
}
await browser.close();
