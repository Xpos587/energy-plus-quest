import { execFile } from "node:child_process";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import sharp from "sharp";
import type { Plugin, ResolvedConfig } from "vite";
import { certificateCopy } from "../src/scenes/certificateExport";

const run = promisify(execFile);
/* Same scenario blocks as endingCopy.ts titles; types valid per profile as in logistType. */
const titleIds = { future: "3AC343FF", energy: "70146CB8", empathy: "5A9BBBF0", efficiency: "2385D203" };
export const shareCards = [
  ...(["future", "energy", "empathy", "efficiency"] as const).map((type) => ({ profile: "student", type })),
  ...(["energy", "empathy", "efficiency"] as const).map((type) => ({ profile: "professional", type })),
].map(({ profile, type }) => ({
  id: `${profile}-${type}`,
  type,
  art: `scene-art/certificates-v1/${profile}-${type}.webp`,
}));
const description = "Мой результат в игре «Доставляем радость» от «Энергии+» и «Газпромнефть‑Снабжения». Пройдите и узнайте, какой логист вы.";
const escape = (text: string) => text.replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);

export function sharePage(title: string, pageUrl: string) {
  const image = `${pageUrl}card.jpg`;
  return `<!doctype html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>${escape(title)} — Доставляем радость</title>
<meta name="description" content="${escape(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Доставляем радость — Энергия+">
<meta property="og:url" content="${escape(pageUrl)}">
<meta property="og:title" content="${escape(title)}">
<meta property="og:description" content="${escape(description)}">
<meta property="og:image" content="${escape(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${escape(title)}">
<meta property="vk:image" content="${escape(image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../../brand/favicon-32.png" sizes="32x32">
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#003ca6;font-family:"Roboto Condensed",Verdana,sans-serif;color:#fff;text-align:center}
main{max-width:720px;padding:24px}
img{width:100%;height:auto;border-radius:16px}
h1{font-size:clamp(28px,6vw,44px);margin:24px 0 8px}
p{font-size:20px;margin:0 0 24px}
a{display:inline-block;padding:16px 32px;border-radius:12px;background:#ff5500;color:#fff;font-size:22px;font-weight:700;text-decoration:none}
</style>
</head>
<body>
<main>
<img src="card.jpg" width="1200" height="630" alt="">
<h1>${escape(title)}</h1>
<p>Узнайте, какой логист вы.</p>
<a href="../../">Пройти игру</a>
</main>
</body>
</html>
`;
}

/** Link previews for share buttons: one public page and 1200×630 card per result, no player data. */
export function sharePages(): Plugin {
  let config: ResolvedConfig;
  return {
    name: "quest-share-pages",
    apply: "build",
    configResolved(resolved) {
      config = resolved;
    },
    async closeBundle() {
      if (config.build.ssr || config.build.write === false) return;
      const base = new URL(process.env.PUBLIC_URL || "https://e-plus.media/specprojects/joydelivery/");
      if (!base.pathname.endsWith("/")) base.pathname += "/";
      const scenario = await readFile(path.join(config.root, "docs/scenario.md"), "utf8");
      const output = path.resolve(config.root, config.build.outDir);
      const work = await mkdtemp(path.join(tmpdir(), "quest-share-"));
      try {
        /* Containers lack system fonts and librsvg/pango cannot read WOFF2: render with a TTF copy. */
        const font = path.join(work, "bold.ttf");
        await run("uv", ["tool", "run", "--from", "fonttools==4.65.0", "--with", "brotli==1.2.0",
          "fonttools", "ttLib.woff2", "decompress", path.join(config.publicDir, "fonts/normalidad-proxy-bold.woff2"), "-o", font]);
        const text = (markup: string, size: number, width: number) =>
          sharp({ text: { text: `<span foreground="white">${markup}</span>`, font: `Roboto Condensed Bold ${size}`, fontfile: font, width, rgba: true, wrap: "word" } }).png().toBuffer();
        const brand = await sharp(path.join(config.publicDir, "brand/quest-brand-lockup.svg"), { density: 300 }).resize(440).png().toBuffer();
        const brandHeight = (await sharp(brand).metadata()).height!;
        for (const card of shareCards) {
          const block = scenario.match(new RegExp(`id="${titleIds[card.type]}"[^\\n]*\\n> (.+)`));
          if (!block) throw new Error(`Missing scenario title ${titleIds[card.type]}`);
          const title = certificateCopy({ type: card.type, title: block[1], paragraphs: [], callToAction: "" })[0];
          const pageUrl = new URL(`r/${card.id}/`, base).href;
          const titleImage = await text(escape(title), 64, 470);
          const titleHeight = (await sharp(titleImage).metadata()).height!;
          const cta = await text("Узнайте, какой логист вы →", 30, 440);
          const ctaMeta = await sharp(cta).metadata();
          const shapes = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
<rect x="36" y="36" width="476" height="${brandHeight + 36}" rx="16" fill="#fff"/>
<rect x="48" y="${560 - ctaMeta.height! - 36}" width="${ctaMeta.width! + 48}" height="${ctaMeta.height! + 36}" rx="14" fill="#ff5500"/>
</svg>`);
          const art = await sharp(path.join(config.publicDir, card.art)).resize(630, 630).toBuffer();
          const directory = path.join(output, "r", card.id);
          await mkdir(directory, { recursive: true });
          await sharp({ create: { width: 1200, height: 630, channels: 3, background: "#003ca6" } })
            .composite([
              { input: art, left: 570, top: 0 },
              { input: shapes, left: 0, top: 0 },
              { input: brand, left: 54, top: 54 },
              { input: titleImage, left: 48, top: Math.round(36 + brandHeight + 36 + (560 - ctaMeta.height! - 36 - (36 + brandHeight + 36) - titleHeight) / 2) },
              { input: cta, left: 72, top: 560 - ctaMeta.height! - 18 },
            ])
            .jpeg({ quality: 86, mozjpeg: true })
            .toFile(path.join(directory, "card.jpg"));
          await writeFile(path.join(directory, "index.html"), sharePage(title, pageUrl));
        }
      } finally {
        await rm(work, { recursive: true, force: true });
      }
    },
  };
}
