// Blender layers -> runtime sprites for scene 4 (barge v4).
//   bun design/scene-04/blender-v4/export.mjs [OUT] [OUTCOMES]
// Reads OUT/{format}/*.png (rendered at SS x format px) and OUT/manifest.json,
// writes public/scene-art/barge-v4/{format}/*.webp, outcome-*.webp, and the
// generated geometry table src/scenes/crane/layers.ts (format px units).
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const here = path.dirname(new URL(import.meta.url).pathname);
const root = path.resolve(here, "../../..");
const OUT = path.resolve(process.argv[2] ?? path.join(here, "out"));
const OUTCOMES = process.argv[3] ? path.resolve(process.argv[3]) : undefined;
const base = "scene-art/barge-v4";
const pub = path.join(root, "public", base);
const manifest = JSON.parse(await readFile(path.join(OUT, "manifest.json"), "utf8"));
const S = 1.5; // render supersampling: png px per format px
const FORMATS = ["wide", "desk", "mid", "tall"];
const SPRITES = ["ivan", "ladder", "far", "gift", "barge", "smoke", "hook", "box"];
const FRAMES = manifest.scene.slews.length;
const COLS = 4;
const r1 = (v) => Math.round(v * 10) / 10;

async function alphaBox(file) {
  const { data, info } = await sharp(file).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  let x0 = info.width, y0 = info.height, x1 = -1, y1 = -1;
  for (let y = 0; y < info.height; y++)
    for (let x = 0; x < info.width; x++)
      if (data[(y * info.width + x) * 4 + 3] > 2) {
        if (x < x0) x0 = x;
        if (x > x1) x1 = x;
        if (y < y0) y0 = y;
        if (y > y1) y1 = y;
      }
  const pad = 3;
  return {
    left: Math.max(0, x0 - pad), top: Math.max(0, y0 - pad),
    right: Math.min(info.width, x1 + 1 + pad), bottom: Math.min(info.height, y1 + 1 + pad),
  };
}
const union = (a, b) => ({
  left: Math.min(a.left, b.left), top: Math.min(a.top, b.top),
  right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom),
});
const rect = (b) => ({ x: r1(b.left / S), y: r1(b.top / S), w: r1((b.right - b.left) / S), h: r1((b.bottom - b.top) / S) });
const webp = (img) => img.webp({ quality: 92, alphaQuality: 100, effort: 5 });

const sc = manifest.scene;
function tipWorld(deg) {
  const a = (deg * Math.PI) / 180;
  const [lx, ly, lz] = sc.tip;
  return [sc.pivot[0] + lx * Math.cos(a) - ly * Math.sin(a), sc.pivot[1] + lx * Math.sin(a) + ly * Math.cos(a), sc.pivot[2] + lz];
}

const table = {};
for (const name of FORMATS) {
  const src = path.join(OUT, name);
  const dst = path.join(pub, name);
  await mkdir(dst, { recursive: true });
  const m = manifest[name];
  await webp(sharp(path.join(src, "plate.png"))).toFile(path.join(dst, "plate.webp"));
  const sprites = {};
  for (const sprite of SPRITES) {
    const file = path.join(src, `${sprite}.png`);
    const b = await alphaBox(file);
    await webp(sharp(file).extract({ left: b.left, top: b.top, width: b.right - b.left, height: b.bottom - b.top }))
      .toFile(path.join(dst, `${sprite}.webp`));
    sprites[sprite] = { src: `${base}/${name}/${sprite}.webp`, ...rect(b) };
  }
  // Slewing top: every frame cropped to one shared box, packed in a 4-column grid.
  const files = Array.from({ length: FRAMES }, (_, i) => path.join(src, `top-${String(i).padStart(2, "0")}.png`));
  let box;
  for (const file of files) {
    const b = await alphaBox(file);
    box = box ? union(box, b) : b;
  }
  const fw = box.right - box.left, fh = box.bottom - box.top;
  const rows = Math.ceil(FRAMES / COLS);
  const tiles = await Promise.all(files.map(async (file, i) => ({
    input: await sharp(file).extract({ left: box.left, top: box.top, width: fw, height: fh }).png().toBuffer(),
    left: (i % COLS) * fw, top: Math.floor(i / COLS) * fh,
  })));
  await webp(sharp({ create: { width: fw * COLS, height: fh * rows, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } } })
    .composite(tiles)).toFile(path.join(dst, "top.webp"));
  table[name] = {
    width: m.width,
    height: m.height,
    plate: `${base}/${name}/plate.webp`,
    sprites,
    top: { src: `${base}/${name}/top.webp`, ...rect(box), cols: COLS, rows },
    // World metres -> format px: [u, v] = affine @ [x, y, z, 1] (orthographic camera).
    affine: m.affine,
    anchors: m.anchors,
  };
}

if (OUTCOMES)
  for (const id of ["remote", "rush", "wait", "petr"])
    await sharp(path.join(OUTCOMES, `outcome-${id}.png`)).webp({ quality: 90, effort: 5 }).toFile(path.join(pub, `outcome-${id}.webp`));

const world = {
  // World metres (x along the quay, y inland, z up); hook sprites hang at `hookAttach` over the gift.
  gift: sc.gift.map((v) => Math.round(v * 1000) / 1000),
  hookAttach: Math.round(sc.hookAttach * 1000) / 1000,
  deck: sc.deck.map((v) => Math.round(v * 1000) / 1000),
  barge: sc.barge,
  slews: sc.slews,
  // Boom head (cable start) for every top frame.
  tips: sc.slews.map((deg) => tipWorld(deg).map((v) => Math.round(v * 1000) / 1000)),
};
const text = `// Generated by design/scene-04/blender-v4/export.mjs from the Blender quay. Do not edit.
// Units: format px for the drawing, world metres for \`craneWorld\`.
export const craneWorld = ${JSON.stringify(world)} as const;

export const craneLayers = ${JSON.stringify(table, null, 1)} as const;
`;
await writeFile(path.join(root, "src/scenes/crane/layers.ts"), text);
console.log("exported", Object.keys(table).join(", "), OUTCOMES ? "+ outcomes" : "");
