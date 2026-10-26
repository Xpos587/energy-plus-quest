import { afterEach, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import vm from "node:vm";
import sharp from "sharp";
import { build, createServer } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

test("reviewed Flowers masters replace runtime pixels without changing canonical source files", async () => {
  const root=await fixture();
  await mkdir(path.join(root,"src/media"),{recursive:true});
  await mkdir(path.join(root,"public/flowers-2pass-2026-10-20"),{recursive:true});
  await mkdir(path.join(root,"docs/reviews"),{recursive:true});
  await sharp({create:{width:3200,height:800,channels:4,background:{r:230,g:25,b:15,alpha:0.4}}}).png().toFile(path.join(root,"public/flowers-2pass-2026-10-20/FTEST.png"));
  await writeFile(path.join(root,"docs/reviews/flowers-fixture.json"),JSON.stringify({decision:"accepted_for_runtime",passes:2}));
  await writeFile(path.join(root,"src/media/flowers-masters.json"),JSON.stringify({"public/scene-art/panorama.png":{master:"public/flowers-2pass-2026-10-20/FTEST.png",passes:2,reviewReceipt:"docs/reviews/flowers-fixture.json"}}));
  const result=await runBuild(root);
  expect(result.responsive["scene-art/panorama.png"].width).toBe(3200);
  expect((await sharp(path.join(root,"public/scene-art/panorama.png")).metadata()).width).toBe(1600);
  const output=result.output.find(x=>x.type==="asset"&&x.fileName===result.images["scene-art/panorama.png"].replace(/^\.\//,""));
  expect(output?.type).toBe("asset");
  if(output?.type==="asset")expect((await sharp(Buffer.from(output.source)).metadata()).hasAlpha).toBe(true);
});

const roots: string[] = [];
afterEach(async () => {
  await Promise.all(
    roots.splice(0).map((root) => rm(root, { recursive: true, force: true })),
  );
});

async function fixture() {
  const root = await mkdtemp(path.join(tmpdir(), "quest-images-"));
  roots.push(root);
  await mkdir(path.join(root, "public/scene-art"), { recursive: true });
  await mkdir(path.join(root, "design/scene-01/assets/current/choices"), {
    recursive: true,
  });
  await writeFile(
    path.join(root, "index.html"),
    '<script type="module" src="/main.js"></script>',
  );
  await writeFile(
    path.join(root, "main.js"),
    'import images from "virtual:optimized-images"; import responsive from "virtual:responsive-images"; import thumbnails from "virtual:thumbnail-images"; import choice from "./design/scene-01/assets/current/choices/choice.webp"; globalThis.imageMap = images; globalThis.responsive = responsive; globalThis.choice = choice; globalThis.thumbnails = thumbnails;',
  );
  await sharp({
    create: {
      width: 1600,
      height: 400,
      channels: 4,
      background: { r: 120, g: 80, b: 20, alpha: 0.4 },
    },
  })
    .png()
    .toFile(path.join(root, "public/scene-art/panorama.png"));
  await sharp({
    create: {
      width: 1400,
      height: 900,
      channels: 4,
      background: { r: 10, g: 90, b: 50, alpha: 0.5 },
    },
  })
    .webp({ lossless: true })
    .toFile(
      path.join(root, "design/scene-01/assets/current/choices/choice.webp"),
    );
  return root;
}

async function runBuild(root: string, singleFile = false) {
  const module = await import("./optimized-images").catch(() => null);
  expect(module?.optimizedImages).toBeFunction();
  const result = await build({
    root,
    configFile: false,
    base: "./",
    logLevel: "silent",
    plugins: [
      module!.optimizedImages(),
      ...(singleFile
        ? [viteSingleFile({ useRecommendedBuildConfig: false })]
        : []),
    ],
    build: {
      write: false,
      minify: false,
      assetsInlineLimit: 0,
      ...(singleFile ? { cssCodeSplit: false } : {}),
    },
  });
  if (Array.isArray(result) || !("output" in result))
    throw new Error("Expected one build");
  const code = singleFile
    ? String(
        result.output.find(
          (item) => item.fileName === "index.html" && item.type === "asset",
        )!.source,
      ).match(/<script[^>]*>([\s\S]*?)<\/script>/)![1]
    : result.output
        .filter((item) => item.type === "chunk")
        .map((item) => item.code)
        .join("\n");
  const context = {
    document: { createElement: () => ({ relList: { supports: () => true } }) },
  } as Record<string, any>;
  vm.runInNewContext(code, context);
  return {
    output: result.output,
    images: context.imageMap as Record<string, string>,
    responsive: context.responsive as Record<
      string,
      {
        avif: string;
        avifSrcSet: string;
        webpSrcSet: string;
        width: number;
        height: number;
      }
    >,
    choice: context.choice as string,
    thumbnails: context.thumbnails as Record<string, string>,
  };
}

test("build emits full-size alpha panoramas, resized choices and relative hashed paths; source replacement invalidates URLs", async () => {
  const root = await fixture();
  const first = await runBuild(root);
  const url = first.images["scene-art/panorama.png"];
  const packagingMap = first.output.find(item => item.type === "asset" && item.fileName === "static-image-replacements.json");
  expect(packagingMap?.type).toBe("asset");
  if (packagingMap?.type !== "asset") throw new Error("Missing packaging replacements");
  expect(JSON.parse(String(packagingMap.source))["scene-art/panorama.png"]).toBe(url);
  const responsive = first.responsive["scene-art/panorama.png"];
  expect(responsive.width).toBe(1600);
  expect(responsive.height).toBe(400);
  expect(responsive.avif).toMatch(/^assets\/optimized-panorama-[\w-]+\.avif$/);
  for (const [srcset, format] of [
    [responsive.avifSrcSet, "avif"],
    [responsive.webpSrcSet, "webp"],
  ]) {
    const candidates = srcset.split(", ");
    expect(candidates).toHaveLength(2);
    for (const candidate of candidates) {
      const [file, width] = candidate.split(" ");
      expect(file.endsWith(`.${format}`)).toBe(true);
      const asset = first.output.find(
        (item) => item.type === "asset" && item.fileName === file,
      )!;
      if (asset.type !== "asset")
        throw new Error("Missing responsive image asset");
      const meta = await sharp(asset.source).metadata();
      expect(meta.width).toBe(Number.parseInt(width));
      expect(meta.height).toBe(meta.width! / 4);
      expect(meta.hasAlpha).toBe(true);
    }
  }
  expect(url).toMatch(/^assets\/optimized-panorama-[\w-]+\.webp$/);
  const panorama = first.output.find(
    (item) => item.type === "asset" && item.fileName === url,
  )!;
  expect(panorama.type).toBe("asset");
  if (panorama.type !== "asset") throw new Error("Missing image asset");
  const metadata = await sharp(panorama.source).metadata();
  expect(metadata.width).toBe(1600);
  expect(metadata.height).toBe(400);
  expect(metadata.hasAlpha).toBe(true);
  expect(first.choice).toStartWith("./assets/");
  const choice = first.output.find(
    (item) =>
      item.type === "asset" &&
      item.fileName === first.choice.replace(/^\.\//, ""),
  )!;
  if (choice.type !== "asset") throw new Error("Missing choice image");
  expect((await sharp(choice.source).metadata()).width).toBe(768);
  const thumbnailUrl = first.thumbnails[first.choice.replace(/^\.\//, "")];
  expect(thumbnailUrl).toStartWith("assets/");
  const thumbnail = first.output.find(
    (item) =>
      item.type === "asset" &&
      item.fileName === thumbnailUrl.replace(/^\.\//, ""),
  )!;
  if (thumbnail.type !== "asset") throw new Error("Missing thumbnail");
  const thumbnailMetadata = await sharp(thumbnail.source).metadata();
  expect(thumbnailMetadata.width).toBe(128);
  expect(thumbnailMetadata.height).toBe(82);
  expect(thumbnailMetadata.hasAlpha).toBe(true);
  const cached = await runBuild(root);
  expect(cached.images).toEqual(first.images);
  const cachedReceipt = JSON.parse(
    await readFile(path.join(root, ".tmp-work/optimized-images.json"), "utf8"),
  );
  expect(
    cachedReceipt.images.every((image: any) => image.cacheHit === true),
  ).toBe(true);
  await sharp({
    create: {
      width: 1600,
      height: 400,
      channels: 4,
      background: { r: 30, g: 120, b: 80, alpha: 0.4 },
    },
  })
    .png()
    .toFile(path.join(root, "public/scene-art/panorama.png"));
  const replaced = await runBuild(root);
  expect(replaced.images["scene-art/panorama.png"]).not.toBe(url);
  expect(replaced.responsive["scene-art/panorama.png"].avifSrcSet).not.toBe(
    responsive.avifSrcSet,
  );
  expect(replaced.responsive["scene-art/panorama.png"].webpSrcSet).not.toBe(
    responsive.webpSrcSet,
  );
  const receipt = JSON.parse(
    await readFile(path.join(root, ".tmp-work/optimized-images.json"), "utf8"),
  );
  expect(
    receipt.images.find(
      (image: any) => image.source === "scene-art/panorama.png",
    ).cacheHit,
  ).toBe(false);
  expect(
    receipt.images.some(
      (image: any) =>
        image.source === "scene-art/panorama.png" &&
        image.sourceBytes > 0 &&
        image.optimizedBytes > 0,
    ),
  ).toBe(true);
});

test("singlefile retains external images with page-relative paths for nested deployment", async () => {
  const root = await fixture();
  const result = await runBuild(root, true);
  expect(
    new URL(
      result.images["scene-art/panorama.png"],
      "https://example.com/special/game/index.html",
    ).pathname,
  ).toStartWith("/special/game/assets/");
  expect(result.choice).toStartWith("./assets/");
  expect(
    new URL(
      result.thumbnails[result.choice.replace(/^\.\//, "")],
      "https://example.com/special/game/index.html",
    ).pathname,
  ).toStartWith("/special/game/assets/");
  expect(
    new URL(
      result.responsive["scene-art/panorama.png"].avif,
      "https://example.com/special/game/index.html",
    ).pathname,
  ).toStartWith("/special/game/assets/");
  expect(
    new URL(result.choice, "https://example.com/special/game/index.html")
      .pathname,
  ).toStartWith("/special/game/assets/");
});

test("development serves originals through an empty image map", async () => {
  const root = await fixture();
  const { optimizedImages } = await import("./optimized-images");
  const server = await createServer({
    root,
    configFile: false,
    plugins: [optimizedImages()],
    server: { middlewareMode: true },
    logLevel: "silent",
  });
  try {
    expect(
      (await server.ssrLoadModule("virtual:optimized-images")).default,
    ).toEqual({});
    expect(
      (await server.ssrLoadModule("virtual:responsive-images")).default,
    ).toEqual({});
    expect(
      (await server.ssrLoadModule("virtual:thumbnail-images")).default,
    ).toEqual({});
  } finally {
    await server.close();
  }
});

test("already compressed WebP never grows through recompression", async () => {
  const root = await fixture();
  const pixels = Buffer.alloc(96 * 96 * 3);
  let seed = 42;
  for (let i = 0; i < pixels.length; i++) {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    pixels[i] = seed >>> 24;
  }
  const original = await sharp(pixels, {
    raw: { width: 96, height: 96, channels: 3 },
  })
    .webp({ quality: 35 })
    .toBuffer();
  await writeFile(path.join(root, "public/scene-art/small.webp"), original);
  const result = await runBuild(root);
  const emitted = result.output.find(
    (item) =>
      item.type === "asset" &&
      item.fileName === result.images["scene-art/small.webp"],
  )!;
  if (emitted.type !== "asset") throw new Error("Missing image asset");
  expect(emitted.source.length).toBeLessThanOrEqual(original.length);
  expect(
    result.responsive["scene-art/small.webp"].avifSrcSet.split(", "),
  ).toHaveLength(1);
});

test("wide sources include both smaller variants without enlarging originals", async () => {
  const root = await fixture();
  await sharp({
    create: { width: 2500, height: 1000, channels: 3, background: "#ac9761" },
  })
    .png()
    .toFile(path.join(root, "public/scene-art/wide.png"));
  const result = await runBuild(root);
  const responsive = result.responsive["scene-art/wide.png"];
  expect(
    responsive.avifSrcSet
      .split(", ")
      .map((candidate) => candidate.split(" ")[1]),
  ).toEqual(["1280w", "1600w", "2500w"]);
  expect(
    responsive.webpSrcSet
      .split(", ")
      .map((candidate) => candidate.split(" ")[1]),
  ).toEqual(["1280w", "1600w", "2500w"]);
  for (const candidate of responsive.avifSrcSet.split(", ")) {
    const [file, width] = candidate.split(" ");
    const asset = result.output.find(
      (item) => item.type === "asset" && item.fileName === file,
    )!;
    if (asset.type !== "asset") throw new Error("Missing wide variant");
    const metadata = await sharp(asset.source).metadata();
    expect(metadata.width).toBe(Number.parseInt(width));
    expect(metadata.height).toBe(metadata.width! * 0.4);
  }
});

test("game manifest excludes historical images from every emitted asset and replacement map", async () => {
  const root = await fixture();
  await mkdir(path.join(root, "src/scenes/crane"), { recursive: true });
  await writeFile(
    path.join(root, "src/scenes/worldManifest.json"),
    JSON.stringify({
      scenes: { example: { desktop: { image: "scene-art/panorama.png" } } },
    }),
  );
  await writeFile(
    path.join(root, "src/scenes/crane/outcomeFraming.json"),
    "{}",
  );
  await sharp({
    create: { width: 64, height: 32, channels: 3, background: "#305050" },
  })
    .png()
    .toFile(path.join(root, "public/scene-art/historical.png"));
  const result = await runBuild(root);
  expect(result.images["scene-art/historical.png"]).toBeUndefined();
  expect(result.output.some((item) => item.fileName.includes("historical"))).toBe(false);
  expect(result.responsive["scene-art/historical.png"]).toBeUndefined();
  expect(result.responsive["scene-art/panorama.png"].width).toBe(1600);
});

test("outcome versions follow the runtime artwork source and exclude replaced historical versions", async () => {
  const root = await fixture();
  await mkdir(path.join(root, "src/scenes/crane"), { recursive: true });
  await mkdir(path.join(root, "public/scene-art/outcomes"), {
    recursive: true,
  });
  await mkdir(path.join(root, "src/game"), { recursive: true });
  await writeFile(path.join(root, "src/game/types.ts"), 'export type ParcelId="socks"; export type RecipientId="khor"; export type ProfileId="student";');
  await writeFile(path.join(root, "src/scenes/worldManifest.json"), JSON.stringify({scenes:{inventory:{desktop:{hotspots:[{id:"wms"}]}},lastmile:{desktop:{hotspots:[{id:"rover"}]}}}}));
  await writeFile(
    path.join(root, "src/scenes/crane/outcomeFraming.json"),
    "{}",
  );
  for (const file of [
    "inventory-wms-v8.webp",
    "inventory-wms-v9.webp",
    "lastmile-rover-v3.png",
    "lastmile-rover-v4.png",
    "inventory-unused-v8.webp",
    "lastmile-unused-v3.png",
  ]) {
    await sharp({
      create: { width: 64, height: 32, channels: 3, background: "#305050" },
    }).toFile(path.join(root, "public/scene-art/outcomes", file));
  }
  const artwork = (inventory: number, lastmile: number) =>
    'export function sceneOutcomeImage(scene, selectedId) { return `scene-art/outcomes/${scene}-${selectedId}${scene === "lastmile" ? "-v' +
    lastmile +
    '.png" : scene === "inventory" ? "-v' +
    inventory +
    '.webp" : "-v4.webp"}`; }';
  await writeFile(path.join(root, "src/scenes/artwork.ts"), artwork(8, 3));
  const current = await runBuild(root);
  expect(current.images["scene-art/outcomes/inventory-unused-v8.webp"]).toBeUndefined();
  expect(current.images["scene-art/outcomes/lastmile-unused-v3.png"]).toBeUndefined();
  expect(
    current.responsive["scene-art/outcomes/inventory-wms-v8.webp"],
  ).toBeDefined();
  expect(
    current.responsive["scene-art/outcomes/lastmile-rover-v3.png"],
  ).toBeDefined();
  expect(
    current.responsive["scene-art/outcomes/lastmile-rover-v4.png"],
  ).toBeUndefined();
  expect(
    current.responsive["scene-art/outcomes/inventory-wms-v9.webp"],
  ).toBeUndefined();
  await writeFile(path.join(root, "src/scenes/artwork.ts"), artwork(9, 4));
  const replaced = await runBuild(root);
  expect(
    replaced.responsive["scene-art/outcomes/inventory-wms-v9.webp"],
  ).toBeDefined();
  expect(
    replaced.responsive["scene-art/outcomes/lastmile-rover-v4.png"],
  ).toBeDefined();
  expect(
    replaced.responsive["scene-art/outcomes/inventory-wms-v8.webp"],
  ).toBeUndefined();
  expect(
    replaced.responsive["scene-art/outcomes/lastmile-rover-v3.png"],
  ).toBeUndefined();
});

test("edited choice refreshes both full-size and thumbnail content URLs", async () => {
  const root = await fixture();
  const before = await runBuild(root);
  const oldThumbnail = before.thumbnails[before.choice.replace(/^\.\//, "")];
  await sharp({
    create: {
      width: 1400,
      height: 900,
      channels: 4,
      background: { r: 180, g: 50, b: 10, alpha: 0.5 },
    },
  })
    .webp({ lossless: true })
    .toFile(
      path.join(root, "design/scene-01/assets/current/choices/choice.webp"),
    );
  const after = await runBuild(root);
  expect(after.choice).not.toBe(before.choice);
  expect(after.thumbnails[after.choice.replace(/^\.\//, "")]).not.toBe(
    oldThumbnail,
  );
  expect(after.thumbnails[before.choice.replace(/^\.\//, "")]).toBeUndefined();
});

test("only artwork reachable from runtime tuples, carrier IDs and context variants is converted", async () => {
  const root = await fixture();
  for (const filename of [
    "src/scenes/worldManifest.json",
    "src/scenes/crane/outcomeFraming.json",
    "src/scenes/crane/artworkFamily.ts",
    "src/scenes/lastmile/artworkFamily.ts",
    "src/scenes/resolutionArtwork.ts",
    "src/scenes/LogistCertificate.tsx",
    "src/scenes/compact/resultArtwork.ts",
    "src/scenes/compact/CompactArt.tsx",
    "src/scenes/compact/CargoBay.tsx",
    "src/scenes/crane/choiceArtwork.ts",
    "src/scenes/lastmile/expandedArtwork.ts",
    "src/scenes/WorldArt.tsx",
    "src/scenes/artwork.ts",
    "src/scenes/compact/artwork.ts",
    "src/game/types.ts",
    "src/game/artwork.ts",
    "src/game/carrierFacts.ts",
    "src/components/CarrierInspection.tsx",
    "src/components/IllustratedCityMap.tsx",
  ]) {
    await mkdir(path.dirname(path.join(root, filename)), { recursive: true });
    await writeFile(path.join(root, filename), await readFile(path.resolve(filename)));
  }
  const included = [
    "compact-art/outcomes/socks-niche.png",
    "review/carrier-art-2026-09-27/closer-old.png",
    "scene-art/carrier-results-2026-10-02/old-wide-v8.webp",
    "scene-art/lastmile-family-v1/choice-final-tall-v10.webp",
    "scene-art/lastmile-family-v1/revision-2/flight-boat.webp",
    "scene-art/lastmile-family-v1/revision-2/flight-parcel-arseniy.webp",
    "scene-art/lastmile-family-v1/revision-4/choice-tall-khor.webp",
    "scene-art/lastmile-family-v1/revision-4/choice-wide-alva.webp",
    "scene-art/lastmile-family-v1/revision-4/choice-tall-arseniy.webp",
    "scene-art/resolution-v2/khor-boat.webp",
    "scene-art/certificates-v1/student-energy.webp",
    "compact-art/camera-zone2-v53.png",
    "compact-art/compact-environment-v53-portrait.png",
    "scene-art/barge-family-v1/choice-neutral-wide-v7.webp",
    "scene-art/warehouse-corrections-2026-10-20/overview-receiving-parallel-labels-v1.png",
    "scene-art/warehouse-polish-2026-10-17/alphabet.webp",
    "scene-art/warehouse-revision-3-2026-10-18/wms-stylized-v3.png",
    "scene-art/lastmile-family-v1/helicopter-ground-khor-parcel-v6.webp",
  ];
  const excluded = [
    "scene-art/inventory-horizontal-v1.png",
    "compact-art/outcomes/unused.png",
    "review/carrier-art-2026-09-27/closer-unused.png",
    "scene-art/outcomes/inventory-unused-v8.webp",
    "scene-art/outcomes/lastmile-unused-v3.png",
  ];
  await sharp({ create: { width: 64, height: 32, channels: 3, background: "#305050" } })
    .webp().toFile(path.join(root, "design/scene-01/assets/current/choices/unused-choice.webp"));
  for (const filename of [...included, ...excluded]) {
    await mkdir(path.dirname(path.join(root, "public", filename)), { recursive: true });
    await sharp({ create: { width: 64, height: 32, channels: 3, background: "#305050" } })
      .toFile(path.join(root, "public", filename));
  }
  const result = await runBuild(root);
  for (const filename of included) expect(result.images[filename], filename).toBeDefined();
  for (const filename of excluded) expect(result.images[filename]).toBeUndefined();
  expect(result.output.some((item) => item.fileName.includes("unused"))).toBe(false);
});

test.each(["scene-art/warehouse-revision-4-2026-10-18/overview-r4-v11-local.png", "scene-art/warehouse-revision-3-2026-10-18/wms-stylized-v3.png", "compact-art/camera-zone2-v36.png", "scene-art/barge-family-v1/petr-boat-v13.png", "scene-art/lastmile-family-v1/revision-2/flight-boat.webp", "scene-art/resolution-v2/khor-boat.webp", "scene-art/certificates-v1/student-energy.webp"])("reviewed desktop detail emits a separate encode without changing mobile srcset: %s", async (relative) => {
  const root = await fixture();
  const filename = path.join(root, "public", relative);
  await mkdir(path.dirname(filename), { recursive: true });
  await sharp({ create: { width: 1700, height: 850, channels: 3, background: "#445566" } }).png().toFile(filename);
  const result = await runBuild(root);
  const variants = result.responsive[relative] as any;
  expect(variants.desktopAvif).toMatch(/desktop-detail.*\.avif$/);
  expect(variants.avifSrcSet).not.toContain("desktop-detail");
  expect(variants.webpSrcSet).not.toContain("desktop-detail");
  const asset = result.output.find(item => item.fileName === variants.desktopAvif);
  expect(asset?.type).toBe("asset");
  if (asset?.type === "asset") expect((await sharp(Buffer.from(asset.source)).metadata()).width).toBe(1700);
});

test.each(["scene-art/lastmile-family-v1/choice-final-tall-v10.webp", "scene-art/lastmile-family-v1/revision-4/choice-tall-khor.webp"])("resolution-limited map retains byte-identical desktop WebP and mobile AVIF: %s", async (relative) => {
  const root = await fixture();
  await mkdir(path.dirname(path.join(root, "public", relative)), { recursive: true });
  const source = await sharp({ create: { width: 948, height: 1659, channels: 3, background: "#768492" } }).webp({ quality: 100 }).toBuffer();
  await writeFile(path.join(root, "public", relative), source);
  const result = await runBuild(root);
  const variant = result.responsive[relative] as any;
  expect(variant.desktopWebp).toBe(result.images[relative]);
  const asset = result.output.find(item => item.fileName === variant.desktopWebp);
  if (asset?.type !== "asset") throw new Error("Missing original desktop asset");
  expect(Buffer.from(asset.source).equals(source)).toBe(true);
  expect(variant.avifSrcSet).toContain("948w");
});
