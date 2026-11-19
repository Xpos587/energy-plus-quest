import { execFile } from "node:child_process";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import sharp from "sharp";
import type { Plugin, ResolvedConfig } from "vite";
import { rankName } from "../src/scenes/certificateExport.ts";

export { rankName };
/** Absolute game address for share links, previews and the story footer (vite.config.ts defines it for the client). */
export const publicUrl = () => {
  const base = new URL(process.env.PUBLIC_URL || "https://e-plus.media/specprojects/joydelivery/");
  if (!base.pathname.endsWith("/")) base.pathname += "/";
  return base.href;
};

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
const escape = (text: string) => text.replace(/[&<>"]/g, (c) => `&#${c.charCodeAt(0)};`);

/* Data URIs: stage-static publishes only index.html and card.jpg from r/<id>/. */
const certificateLead = "Участник игры «Доставляем радость» получил звание";
/* Every glyph the page draws besides the rank, for the inlined font subsets. */
const sharePageText = `Сертификат СЕРТИФИКАТ ${certificateLead} Пройти игру самому`;
export type SharePageAssets = { art: string; brand: string; regular: string; bold: string };
const diamond = `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cpath d='M16 0 32 16 16 32 0 16z' fill='%23ff6500'/%3E%3C/svg%3E")`;

/* The recipient sees the sender's certificate (same paper, frame and corners as the
   downloadable story image in certificateExport.ts), third person, no player data. */
export function sharePage(rank: string, pageUrl: string, assets: SharePageAssets) {
  const image = `${pageUrl}card.jpg`;
  const title = `${certificateLead} «${rank}»`;
  const description = "Сертификат игры «Доставляем радость» от «Энергии+» и «Газпромнефть‑Снабжения». Пройдите игру сами и узнайте, какой вы логист.";
  return `<!doctype html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>${escape(title)}</title>
<meta name="description" content="${escape(description)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Доставляем радость — Энергия+">
<meta property="og:url" content="${escape(pageUrl)}">
<meta property="og:title" content="${escape(title)}">
<meta property="og:description" content="${escape(description)}">
<meta property="og:image" content="${escape(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${escape(`Сертификат: звание «${rank}»`)}">
<meta property="vk:image" content="${escape(image)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="../../brand/favicon-32.png" sizes="32x32">
<style>
@font-face{font-family:"Roboto Condensed";src:url(${assets.regular}) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Roboto Condensed";src:url(${assets.bold}) format("woff2");font-weight:700;font-display:swap}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;min-height:100vh;min-height:100dvh;display:grid;place-items:center;padding:32px 16px;background:#edf3f8;color:#123750;font-family:"Roboto Condensed",Verdana,sans-serif;text-align:center}
main{width:min(1040px,100%);display:grid;justify-items:center;gap:32px}
.certificate{position:relative;width:100%;display:grid;align-items:center;gap:clamp(24px,4vw,48px);padding:clamp(36px,5vw,64px) clamp(24px,5vw,64px);background:#fffdf7;border:4px solid #07629c;box-shadow:inset 0 0 0 8px #fffdf7,inset 0 0 0 9px #07629c,0 24px 64px rgb(18 55 80/.14)}
.certificate::before{--d:clamp(22px,3vw,32px);content:"";position:absolute;inset:calc(var(--d)/-2 - 2px);pointer-events:none;background:${diamond} 0 0/var(--d) no-repeat,${diamond} 100% 0/var(--d) no-repeat,${diamond} 0 100%/var(--d) no-repeat,${diamond} 100% 100%/var(--d) no-repeat}
.text{display:grid;justify-items:center}
.brand{display:block;width:min(400px,100%);height:auto}
/* Classic certificate heading: light caps between hairlines, so the rank stays the headline. */
h1{display:flex;align-items:center;gap:.6em;margin:clamp(24px,4vw,44px) 0 0;color:#07629c;font-size:clamp(24px,2.6vw,32px);font-weight:400;line-height:1;letter-spacing:.08em;text-transform:uppercase}
h1::before,h1::after{content:"";width:clamp(32px,5vw,64px);height:1px;background:linear-gradient(90deg,transparent,#07629c)}
h1::after{margin-left:-.08em;transform:scaleX(-1)}
.lead{max-width:20em;margin:16px 0 0;font-size:clamp(18px,2vw,23px);line-height:1.35}
.rank{margin:12px 0 0;color:#07629c;font-size:clamp(32px,4.4vw,52px);font-weight:700;line-height:1.08}
.rank::after{content:"";display:block;width:72px;height:3px;margin:20px auto 0;background:#ff6500}
.art{display:block;width:100%;max-width:440px;height:auto;justify-self:center;border-radius:6px}
.cta{display:inline-flex;align-items:center;min-height:48px;padding:12px 28px;border:1px solid #4d86b1;border-radius:10px;background:#fff;color:#075d9b;font-size:19px;font-weight:700;text-decoration:none}
.cta:hover{background:#eef5fa}
/* Project policy (tests/interaction-decorations.spec.ts): focus ring without outline. */
.cta:focus-visible{outline:none;box-shadow:0 0 0 3px #edf3f8,0 0 0 6px #ff6500}
@media (min-width:760px){.certificate{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.art{order:-1}}
</style>
</head>
<body>
<main>
<article class="certificate">
<div class="text">
<img class="brand" src="${assets.brand}" width="484" height="66" alt="Энергия+ и Газпромнефть‑Снабжение">
<h1>Сертификат</h1>
<p class="lead">${certificateLead}</p>
<p class="rank">${escape(rank)}</p>
</div>
<img class="art" src="${assets.art}" width="720" height="720" alt="">
</article>
<a class="cta" href="../../">Пройти игру самому</a>
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
      if (config.mode === "test" || config.build.ssr || config.build.write === false) return;
      const base = publicUrl();
      const scenario = await readFile(path.join(config.root, "docs/scenario.md"), "utf8");
      const output = path.resolve(config.root, config.build.outDir);
      const work = await mkdtemp(path.join(tmpdir(), "quest-share-"));
      try {
        const ranks = shareCards.map((card) => {
          const block = scenario.match(new RegExp(`id="${titleIds[card.type]}"[^\\n]*\\n> (.+)`));
          if (!block) throw new Error(`Missing scenario title ${titleIds[card.type]}`);
          return rankName(block[1]);
        });
        const fonttools = ["tool", "run", "--from", "fonttools==4.65.0", "--with", "brotli==1.2.0"];
        const fonts = Object.fromEntries(await Promise.all((["regular", "bold"] as const).map(async (weight) => {
          const source = path.join(config.publicDir, `fonts/normalidad-proxy-${weight}.woff2`);
          /* Containers lack system fonts and librsvg/pango cannot read WOFF2: the card renders with a TTF copy. */
          const ttf = path.join(work, `${weight}.ttf`);
          await run("uv", [...fonttools, "fonttools", "ttLib.woff2", "decompress", source, "-o", ttf]);
          /* The page inlines a subset of its own glyphs: r/<id>/ publishes only index.html and card.jpg. */
          const subset = path.join(work, `${weight}.woff2`);
          await run("uv", [...fonttools, "pyftsubset", source, `--text=${sharePageText}${ranks.join("")}`, "--flavor=woff2", `--output-file=${subset}`]);
          return [weight, { ttf, woff2: `data:font/woff2;base64,${(await readFile(subset)).toString("base64")}` }];
        }))) as Record<"regular" | "bold", { ttf: string; woff2: string }>;
        const text = (markup: string, weight: "regular" | "bold", size: number, width: number, color: string, spacing = 0) =>
          sharp({ text: { text: `<span foreground="${color}" letter_spacing="${spacing * 1024}">${markup}</span>`, font: `Roboto Condensed ${weight === "bold" ? "Bold" : ""} ${size}`, fontfile: fonts[weight].ttf, width, align: "centre", rgba: true, wrap: "word" } }).png().toBuffer();
        const lockup = path.join(config.publicDir, "brand/quest-brand-lockup.svg");
        const brand = await sharp(lockup, { density: 300 }).resize(470).png().toBuffer();
        const brandUri = `data:image/svg+xml;base64,${(await readFile(lockup)).toString("base64")}`;
        /* Same paper, double frame and orange corner diamonds as the story image (certificateExport.ts). */
        const frame = Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
<rect x="26" y="26" width="1148" height="578" fill="none" stroke="#07629c" stroke-width="4"/>
<rect x="36.5" y="36.5" width="1127" height="557" fill="none" stroke="#07629c"/>
${[[26, 26], [1174, 26], [26, 604], [1174, 604]].map(([x, y]) => `<rect x="${x - 11}" y="${y - 11}" width="22" height="22" fill="#ff6500" transform="rotate(45 ${x} ${y})"/>`).join("")}
</svg>`);
        const size = async (input: Buffer) => (await sharp(input).metadata()) as { width: number; height: number };
        /* Text column right of the artwork, centred vertically like a certificate's body. */
        const column = 560;
        /* Same heading as the page: light blue caps between hairlines fading outwards. */
        const caps = await text("СЕРТИФИКАТ", "regular", 32, column, "#07629c", 2.5);
        const capsSize = await size(caps);
        const rule = 64 + 20;
        const hairline = (x: number, flip: boolean) => `<rect x="${x}" y="${Math.round(capsSize.height * 0.55)}" width="64" height="1.5" fill="url(#${flip ? "r" : "l"})"/>`;
        const title = await sharp(Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${capsSize.width + 2 * rule}" height="${capsSize.height}">
<defs><linearGradient id="l"><stop offset="0" stop-color="#07629c" stop-opacity="0"/><stop offset="1" stop-color="#07629c"/></linearGradient><linearGradient id="r"><stop offset="0" stop-color="#07629c"/><stop offset="1" stop-color="#07629c" stop-opacity="0"/></linearGradient></defs>
${hairline(0, false)}${hairline(capsSize.width + 2 * rule - 64, true)}
</svg>`)).composite([{ input: caps, left: rule, top: 0 }]).png().toBuffer();
        for (const [index, card] of shareCards.entries()) {
          const rank = ranks[index];
          const pageUrl = new URL(`r/${card.id}/`, base).href;
          const art = path.join(config.publicDir, card.art);
          const blocks = [
            { input: brand, gap: 0 },
            { input: title, gap: 38 },
            { input: await text(certificateLead, "regular", 27, column - 60, "#123750"), gap: 24 },
            { input: await text(escape(rank), "bold", 58, column, "#07629c"), gap: 20 },
            { input: Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="72" height="4"><rect width="72" height="4" fill="#ff6500"/></svg>'), gap: 24 },
          ];
          const sizes = await Promise.all(blocks.map(({ input }) => size(input)));
          let top = Math.round((630 - sizes.reduce((sum, { height }, i) => sum + height + blocks[i].gap, 0)) / 2);
          const directory = path.join(output, "r", card.id);
          await mkdir(directory, { recursive: true });
          await sharp({ create: { width: 1200, height: 630, channels: 3, background: "#fffdf7" } })
            .composite([
              { input: await sharp(art).resize(500, 500).toBuffer(), left: 70, top: 65 },
              { input: frame, left: 0, top: 0 },
              ...blocks.map(({ input, gap }, i) => {
                top += gap;
                const placed = { input, left: Math.round(880 - sizes[i].width / 2), top };
                top += sizes[i].height;
                return placed;
              }),
            ])
            .jpeg({ quality: 86, mozjpeg: true })
            .toFile(path.join(directory, "card.jpg"));
          const artUri = `data:image/webp;base64,${(await sharp(art).resize(720, 720).webp({ quality: 78 }).toBuffer()).toString("base64")}`;
          await writeFile(path.join(directory, "index.html"),
            sharePage(rank, pageUrl, { art: artUri, brand: brandUri, regular: fonts.regular.woff2, bold: fonts.bold.woff2 }));
        }
      } finally {
        await rm(work, { recursive: true, force: true });
      }
    },
  };
}
