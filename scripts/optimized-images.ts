import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { runInNewContext } from "node:vm";
import { transformSync } from "esbuild";
import { parseSync } from "rolldown/utils";
import sharp from "sharp";
import { desktopDetailQuality, preserveDesktopOriginal } from "./image-detail";
import { loadFlowersMasters, type FlowersAliases } from "./flowers-masters";
import { loadConventionalImages, interpolateConventional } from "./conventional-images";
import type { Plugin, ResolvedConfig } from "vite";
import { cachedImageEncode } from "./image-codec-cache";

const virtualId = "virtual:optimized-images";
const resolvedId = `\0${virtualId}`;
const responsiveId = "virtual:responsive-images";
const resolvedResponsiveId = `\0${responsiveId}`;
const thumbnailId = "virtual:thumbnail-images";
const resolvedThumbnailId = `\0${thumbnailId}`;
const raster = /\.(png|jpe?g|webp)$/i;
const choicePath = /\/design\/scene-01\/assets\/current\/choices\/[^/]+\.webp$/;
const publicRoots = [
  "scene-art",
  "compact-art",
  "review/carrier-art-2026-09-27",
  "opening",
];

interface ImageReceipt {
  source: string;
  sourceBytes: number;
  optimizedBytes: number;
  width: number;
  height: number;
  cacheHit: boolean;
  flowersMaster?: string;
  conventionalInterpolationWidth?: number;
  flowersMasterDimensions?: { width?: number; height?: number };
  avifBytes?: number;
  variants?: { width: number; avifBytes: number; webpBytes: number }[];
}

async function imageFiles(
  directory: string,
  recursive: boolean,
): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true }).catch(
    (error: NodeJS.ErrnoException) => {
      if (error.code === "ENOENT") return [];
      throw error;
    },
  );
  const files = await Promise.all(
    entries.map(async (entry) => {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory() && recursive) return imageFiles(file, true);
      return entry.isFile() && raster.test(entry.name) ? [file] : [];
    }),
  );
  return files.flat().sort();
}

interface RuntimeImages {
  images: Set<string>;
}

function visitNodes(value: unknown, visit: (node: Record<string, any>) => void) {
  if (!value || typeof value !== "object") return;
  const node = value as Record<string, any>;
  visit(node);
  for (const child of Object.values(node)) {
    if (Array.isArray(child)) child.forEach((entry) => visitNodes(entry, visit));
    else if (child && typeof child === "object") visitNodes(child, visit);
  }
}

async function runtimeImages(root: string): Promise<RuntimeImages | undefined> {
  async function source(relative: string) {
    return readFile(path.join(root, relative), "utf8").catch((error: NodeJS.ErrnoException) => {
      if (error.code === "ENOENT") return undefined;
      throw error;
    });
  }
  function syntax(filename: string, text: string) {
    const parsed = parseSync(filename, text);
    if (parsed.errors.length) throw new Error("Unable to parse runtime artwork: " + filename);
    return parsed.program;
  }
  const manifestText = await source("src/scenes/worldManifest.json");
  // Small external fixtures have no game manifest and exercise every source.
  if (!manifestText) return undefined;
  const manifest = JSON.parse(manifestText);
  const framing = JSON.parse(await source("src/scenes/crane/outcomeFraming.json") ?? "{}");
  const images = new Set<string>();
  visitNodes(manifest, (node) => {
    if (typeof node.image === "string") images.add(node.image);
  });
  for (const frame of Object.values(framing) as { file: string }[])
    images.add("scene-art/outcomes/" + frame.file);

  // Execute only the pure artwork resolvers with imageAsset replaced by identity.
  // Their real conditionals remain the source of truth for every context variant.
  const craneFamily = await source("src/scenes/crane/artworkFamily.ts");
  const craneArtwork = await source("src/scenes/crane/artwork.ts");
  const craneLayers = await source("src/scenes/crane/layers.ts");
  const lastmileFamily = await source("src/scenes/lastmile/artworkFamily.ts");
  function resolver(text: string) {
    const exports = {};
    const context = {
      exports,
      module: { exports },
      require(id: string) {
        if (id.endsWith("/imageAssets")) return { imageAsset: (file: string) => file };
        if (id === "./worldManifest.json") return manifest;
        if (id === "./crane/outcomeFraming.json") return framing;
        if (id === "./crane/artworkFamily" && craneFamily) return resolver(craneFamily);
        if (id === "./crane/artwork" && craneArtwork) return resolver(craneArtwork);
        if (id === "./layers" && craneLayers) return resolver(craneLayers);
        if (id === "./lastmile/artworkFamily" && lastmileFamily) return resolver(lastmileFamily);
        throw new Error("Unexpected dependency in pure artwork resolver: " + id);
      },
    };
    runInNewContext(transformSync(text, { loader: "ts", format: "cjs" }).code, context, { timeout: 1000 });
    return context.module.exports as Record<string, (...args: any[]) => any>;
  }
  const artwork = await source("src/scenes/artwork.ts");
  if (artwork) {
    const types = await source("src/game/types.ts");
    if (!types) throw new Error("Runtime artwork requires game context types");
    const ids = new Map<string, string[]>();
    visitNodes(syntax("types.ts", types), (node) => {
      if (node.type !== "TSTypeAliasDeclaration") return;
      const literals = node.typeAnnotation.type === "TSUnionType"
        ? node.typeAnnotation.types : [node.typeAnnotation];
      if (literals.every((type: any) => type.type === "TSLiteralType" && typeof type.literal.value === "string"))
        ids.set(node.id.name, literals.map((type: any) => type.literal.value));
    });
    for (const name of ["ParcelId", "RecipientId", "ProfileId"])
      if (!ids.get(name)?.length) throw new Error("Missing runtime context variants: " + name);
    const scene = resolver(artwork);
    if (lastmileFamily) {
      const family = resolver(lastmileFamily);
      for (const parcel of ids.get("ParcelId")!)
        for (const recipient of ids.get("RecipientId")!)
          images.add(family.lastmileFlightImage({ parcel, recipient }));
      for (const recipient of ids.get("RecipientId")!)
        for (const format of ["wide", "tall"])
          images.add(family.lastmileChoiceImage(format, recipient));
    }
    // Scene 4 picks one of several layered quay drawings at runtime by screen ratio:
    // admit its plate and every sprite the generated layer table names.
    if (craneArtwork)
      visitNodes(resolver(craneArtwork).craneArtwork ?? {}, (node) => {
        for (const value of Object.values(node))
          if (typeof value === "string" && /^scene-art\/.*\.webp$/.test(value)) images.add(value);
      });
    if (!scene.sceneOutcomeImage) throw new Error("Missing sceneOutcomeImage resolver");
    for (const [sceneId, views] of Object.entries(manifest.scenes ?? {}) as [string, any][]) {
      if (sceneId === "compact") continue;
      const selected = new Set<string>();
      visitNodes(views, (node) => {
        if (Array.isArray(node.hotspots)) for (const hotspot of node.hotspots) selected.add(hotspot.id);
      });
      for (const selectedId of selected)
        for (const parcel of ids.get("ParcelId")!)
          for (const recipient of ids.get("RecipientId")!)
            for (const profile of ids.get("ProfileId")!)
              images.add(scene.sceneOutcomeImage(sceneId, selectedId, { parcel, recipient, profile }));
    }
  }
  const compact = await source("src/scenes/compact/artwork.ts");
  if (compact) {
    // The tuple values are the literal image names; no wildcard directory admission.
    visitNodes(syntax("compact.ts", compact), (node) => {
      if (node.type !== "VariableDeclarator" || node.id.name !== "assets") return;
      visitNodes(node.init, (tuple) => {
        if (tuple.type === "ArrayExpression" && tuple.elements.length === 2 &&
            tuple.elements.every((item: any) => item?.type === "Literal" && typeof item.value === "string"))
          images.add("compact-art/outcomes/" + tuple.elements[0].value + ".png");
      });
    });
  }
  // Literal asset tables used by SVG compositions and the illustrated ending.
  // Read only these runtime modules, not entire artwork directories.
  for (const filename of ["src/scenes/compact/resultArtwork.ts", "src/scenes/compact/CompactArt.tsx", "src/scenes/compact/CargoBay.tsx", "src/scenes/resolutionArtwork.ts", "src/scenes/LogistCertificate.tsx"]) {
    const text = await source(filename);
    if (!text) continue;
    visitNodes(syntax(filename, text), (node) => {
      if (node.type === "Literal" && typeof node.value === "string" && /^\/?(?:scene-art|compact-art)\/.*\.(?:png|webp|jpe?g)$/.test(node.value))
        images.add(node.value.replace(/^\//, ""));
    });
  }
  for (const filename of ["src/game/artwork.ts", "src/components/IllustratedCityMap.tsx", "src/components/GameIntro.tsx"]) {
    const text = await source(filename);
    if (!text) continue;
    visitNodes(syntax(filename, text), (node) => {
      if (node.type === "CallExpression" && node.callee.type === "Identifier" && node.callee.name === "imageAsset" &&
          node.arguments[0]?.type === "Literal" && typeof node.arguments[0].value === "string")
        images.add(node.arguments[0].value);
    });
  }
  // Current choice compositions live outside the historical world manifest.
  // Read the pure object exports, rather than admitting whole art directories.
  for (const filename of ["src/scenes/lastmile/expandedArtwork.ts", "src/scenes/crane/choiceArtwork.ts"]) {
    const text = await source(filename);
    if (!text) continue;
    visitNodes(syntax(filename, text), (node) => {
      if (node.type === "Property" && node.key.name === "image" && typeof node.value.value === "string")
        images.add(node.value.value);
    });
  }
  const world = await source("src/scenes/WorldArt.tsx");
  if (world) visitNodes(syntax("WorldArt.tsx", world), (node) => {
    if (node.type === "CallExpression" && node.callee.name === "imageAsset" && node.arguments[0]?.type === "Literal")
      images.add(node.arguments[0].value);
  });
  const facts = await source("src/game/carrierFacts.ts");
  const inspection = await source("src/components/CarrierInspection.tsx");
  if (facts && inspection) {
    const ids: string[] = [];
    visitNodes(syntax("carrierFacts.ts", facts), (node) => {
      if (node.type === "VariableDeclarator" && node.id.name === "mapCarrierIds" && node.init.type === "ArrayExpression")
        for (const entry of node.init.elements) {
          if (entry.type !== "Literal" || typeof entry.value !== "string") throw new Error("Nonliteral carrier ID");
          ids.push(entry.value);
        }
    });
    if (!ids.length) throw new Error("Missing mapCarrierIds");
    visitNodes(syntax("CarrierInspection.tsx", inspection), (node) => {
      if (node.type !== "CallExpression" || node.callee.name !== "imageAsset") return;
      const template = node.arguments[0];
      if (template?.type !== "TemplateLiteral" || template.expressions.length !== 1 || template.expressions[0].name !== "id")
        throw new Error("Unsupported carrier inspection artwork expression");
      for (const id of ids) images.add(template.quasis[0].value.cooked + id + template.quasis[1].value.cooked);
    });
  }
  return { images };
}

function isRuntimeImage(original: string, manifest: RuntimeImages | undefined) {
  return !manifest || manifest.images.has(original);
}

/** Originals remain untouched. Every build derives assets and lets Vite hash their content. */
export function optimizedImages(): Plugin {
  let config: ResolvedConfig;
  let enabled = false;
  let flowersMasters: FlowersAliases = new Map();
  let conventionalImages = new Map<string, number>();
  const sourceBuffer = async (file: string) => {
    const master = flowersMasters.get(file);
    const source = await readFile(master ?? file);
    if (!master) return conventionalImages.has(file)
      ? interpolateConventional(source, conventionalImages.get(file)!) : source;
    // Native8192 masters remain lossless artifacts. Runtime encodes use bounded
    // derivatives from that master, never a resized historical source.
    const relative = path.relative(config.root, file).replaceAll(path.sep, "/");
    const longest = relative.startsWith("design/") || relative.includes("/opening/") ? 1600
      : /\/(?:certificates-v1|resolution-v2)\//.test(relative) ? 2560 : 5120;
    const metadata = await sharp(source).metadata();
    return Math.max(metadata.width ?? 0, metadata.height ?? 0) > longest
      ? sharp(source).resize({ width: longest, height: longest, fit: "inside", withoutEnlargement: true }).png().toBuffer()
      : source;
  };
  const references = new Set<string>();
  const replacements = new Map<string, string>();
  const receipt: ImageReceipt[] = [];
  const choices = new Map<
    string,
    Promise<{ full: string; thumbnail: string }>
  >();
  let publicModules:
    | Promise<{ optimized: string; responsive: string }>
    | undefined;

  async function cachedEncode(
    file: string,
    codec: string,
    produce: (source: Buffer) => Promise<Buffer>,
    input?: Buffer,
  ) {
    const source = input ?? (await readFile(file));
    const relative = path.relative(config.root, file).replaceAll(path.sep, "/");
    return cachedImageEncode(
      path.join(config.root, ".tmp-work/image-build-cache/codec-v2"),
      `${relative}\0${codec}`,
      source,
      async () => {
        const data = await produce(source);
        const metadata = await sharp(data).metadata();
        return { data, info: { width: metadata.width!, height: metadata.height! } };
      },
    );
  }

  async function convert(file: string, maxWidth?: number) {
    const source = await sourceBuffer(file);
    const keepNativePixels = !maxWidth && !conventionalImages.has(file) && preserveDesktopOriginal(path.relative(config.publicDir, file).replaceAll(path.sep, "/"));
    const keepOriginal = keepNativePixels && (await sharp(source).metadata()).format === "webp";
    const {
      data: optimized,
      info,
      cacheHit,
    } = await cachedEncode(
      file,
      "webp-full-" + (maxWidth ?? "original") + (keepOriginal ? "-preserved-v1" : keepNativePixels ? "-native-q98-v1" : ""),
      async (input) => {
        if (keepOriginal) return input;
        let pipeline = sharp(input);
        const metadata = await pipeline.metadata();
        if (maxWidth)
          pipeline = pipeline.resize({
            width: maxWidth,
            withoutEnlargement: true,
          });
        const { data, info } = await pipeline
          .webp({ quality: keepNativePixels ? 98 : 88, alphaQuality: 100, effort: 4 })
          .toBuffer({ resolveWithObject: true });
        return metadata.format === "webp" &&
          metadata.width === info.width &&
          metadata.height === info.height &&
          input.length < data.length
          ? input
          : data;
      },
      source,
    );
    const masterMetadata = flowersMasters.has(file) ? await sharp(flowersMasters.get(file)!).metadata() : undefined;
    receipt.push({
      source: path.relative(config.publicDir, file).replaceAll(path.sep, "/"),
      sourceBytes: source.length,
      optimizedBytes: optimized.length,
      width: info.width,
      height: info.height,
      cacheHit,
      conventionalInterpolationWidth: !flowersMasters.has(file) ? conventionalImages.get(file) : undefined,
      flowersMaster: flowersMasters.get(file) ? path.relative(config.root, flowersMasters.get(file)!).replaceAll(path.sep, "/") : undefined,
      flowersMasterDimensions: masterMetadata ? { width: masterMetadata.width, height: masterMetadata.height } : undefined,
    });
    return optimized;
  }

  function choiceAssets(
    file: string,
    emit: (source: Buffer, name: string) => string,
  ) {
    let pending = choices.get(file);
    if (!pending) {
      pending = (async () => {
        const full = emit(
          await convert(file, 768),
          `optimized-${path.parse(file).name}.webp`,
        );
        const thumbnail = emit(
          await convert(file, 128),
          `thumbnail-${path.parse(file).name}.webp`,
        );
        references.add(full);
        references.add(thumbnail);
        return { full, thumbnail };
      })();
      choices.set(file, pending);
    }
    return pending;
  }

  return {
    name: "quest-optimized-images",
    enforce: "pre",
    configResolved(resolved) {
      config = resolved;
      enabled = config.command === "build" && config.mode !== "test";
    },
    async buildStart() {
      references.clear();
      replacements.clear();
      receipt.length = 0;
      choices.clear();
      publicModules = undefined;
      flowersMasters = enabled ? await loadFlowersMasters(config.root) : new Map();
      conventionalImages = enabled ? await loadConventionalImages(config.root) : new Map();
      if (flowersMasters.size) sharp.concurrency(1);
      for (const [original, master] of flowersMasters) {
        this.addWatchFile(original);
        this.addWatchFile(master);
      }
    },
    resolveId(id) {
      if (id === virtualId) return resolvedId;
      if (id === responsiveId) return resolvedResponsiveId;
      if (id === thumbnailId) return resolvedThumbnailId;
    },
    async load(id) {
      if (id === resolvedThumbnailId) {
        if (!enabled) return "export default {};";
        let files = await imageFiles(
          path.join(config.root, "design/scene-01/assets/current/choices"),
          false,
        );
        const artworkFile = path.join(config.root, "src/game/artwork.ts");
        const artwork = await readFile(artworkFile, "utf8").catch((error: NodeJS.ErrnoException) => {
          if (error.code === "ENOENT") return undefined;
          throw error;
        });
        if (artwork) {
          const parsed = parseSync("artwork.ts", artwork);
          if (parsed.errors.length) throw new Error("Unable to parse choice artwork imports");
          const imported = new Set<string>();
          visitNodes(parsed.program, (node) => {
            if (node.type === "ImportDeclaration" && typeof node.source.value === "string")
              imported.add(path.resolve(path.dirname(artworkFile), node.source.value));
          });
          files = files.filter((file) => imported.has(file));
        }
        const entries: string[] = [];
        for (const file of files) {
          this.addWatchFile(file);
          const assets = await choiceAssets(file, (source, name) =>
            this.emitFile({ type: "asset", name, source }),
          );
          entries.push(
            `[import.meta.ROLLUP_FILE_URL_${assets.full}]:import.meta.ROLLUP_FILE_URL_${assets.thumbnail}`,
          );
        }
        return `export default {${entries.join(",")}};`;
      }
      if (id === resolvedId || id === resolvedResponsiveId) {
        if (!enabled) return "export default {};";
        if (!publicModules)
          publicModules = (async () => {
            const runtime = await runtimeImages(config.root);
            const groups = await Promise.all(
              publicRoots.map(async (root) => {
                const directory = path.join(config.publicDir, root);
                return imageFiles(directory, true);
              }),
            );
            // Filter before emitting: an entry in the fallback lookup itself
            // keeps an asset reachable, even when no game screen requests it.
            const files = groups.flat().filter((file) =>
              isRuntimeImage(
                path.relative(config.publicDir, file).replaceAll(path.sep, "/"),
                runtime,
              ),
            ).sort();
            const entries: string[] = new Array(files.length);
            const responsiveEntries: string[] = new Array(files.length);
            let next = 0;
            // Bounded jobs avoid saturating memory on the large panorama sources.
            await Promise.all(
              Array.from({ length: Math.min(2, files.length) }, async () => {
                while (next < files.length) {
                  const index = next++;
                  const file = files[index];
                  this.addWatchFile(file);
                  const source = await convert(file);
                  const reference = this.emitFile({
                    type: "asset",
                    name: `optimized-${path.parse(file).name}.webp`,
                    source,
                  });
                  references.add(reference);
                  const original = path
                    .relative(config.publicDir, file)
                    .replaceAll(path.sep, "/");
                  replacements.set(original, reference);
                  entries[index] =
                    `${JSON.stringify(original)}:import.meta.ROLLUP_FILE_URL_${reference}`;
                  if (!isRuntimeImage(original, runtime)) continue;
                  const metadata = await sharp(source).metadata();
                  const width = metadata.width!;
                  const height = metadata.height!;
                  const sizes = [1280, 1600].filter((size) => size < width);
                  const variants: {
                    width: number;
                    avifBytes: number;
                    webpBytes: number;
                  }[] = [];
                  const avifParts: string[] = [];
                  const webpParts: string[] = [];
                  let fullAvif = "";
                  let desktopAvif = "";
                  const desktopWebp = preserveDesktopOriginal(original)
                    ? `,desktopWebp:import.meta.ROLLUP_FILE_URL_${reference}` : "";
                  // Encode each derivative from the editable original, never from
                  // an already lossy WebP. Panoramas retain their intrinsic ratio.
                  const originalBuffer = await sourceBuffer(file);
                  const detailQuality = desktopDetailQuality(original);
                  if (detailQuality) {
                    const detail = await cachedEncode(file, "desktop-avif-q80-e4-v1", (input) =>
                      sharp(input).avif({ quality: detailQuality, effort: 4 }).toBuffer(), originalBuffer);
                    const detailReference = this.emitFile({ type: "asset", name: `desktop-detail-${path.parse(file).name}.avif`, source: detail.data });
                    references.add(detailReference);
                    desktopAvif = `,desktopAvif:import.meta.ROLLUP_FILE_URL_${detailReference}`;
                  }
                  for (const size of [...sizes, width]) {
                    const resize = size === width ? undefined : size;
                    let avifPipeline = sharp(originalBuffer);
                    let webpPipeline = sharp(originalBuffer);
                    if (resize) {
                      avifPipeline = avifPipeline.resize({
                        width: resize,
                        withoutEnlargement: true,
                      });
                      webpPipeline = webpPipeline.resize({
                        width: resize,
                        withoutEnlargement: true,
                      });
                    }
                    const avifResult = await cachedEncode(
                      file,
                      "avif-" + size,
                      () =>
                        avifPipeline
                          .avif({ quality: 60, effort: 4 })
                          .toBuffer(),
                      originalBuffer,
                    );
                    const avif = avifResult.data;
                    const currentReceipt = receipt.find(
                      (item) => item.source === original,
                    )!;
                    currentReceipt.cacheHit &&= avifResult.cacheHit;
                    const avifReference = this.emitFile({
                      type: "asset",
                      name: `optimized-${path.parse(file).name}${resize ? `-${size}` : ""}.avif`,
                      source: avif,
                    });
                    references.add(avifReference);
                    const avifUrl = `import.meta.ROLLUP_FILE_URL_${avifReference}`;
                    avifParts.push(`${avifUrl}+${JSON.stringify(` ${size}w`)}`);
                    let webpReference = reference;
                    let webpBytes = source.length;
                    if (resize) {
                      const webpResult = await cachedEncode(
                        file,
                        "webp-" + size,
                        () =>
                          webpPipeline
                            .webp({ quality: 80, alphaQuality: 100, effort: 4 })
                            .toBuffer(),
                        originalBuffer,
                      );
                      const webp = webpResult.data;
                      currentReceipt.cacheHit &&= webpResult.cacheHit;
                      webpBytes = webp.length;
                      webpReference = this.emitFile({
                        type: "asset",
                        name: `optimized-${path.parse(file).name}-${size}.webp`,
                        source: webp,
                      });
                      references.add(webpReference);
                      variants.push({
                        width: size,
                        avifBytes: avif.length,
                        webpBytes,
                      });
                    } else {
                      fullAvif = avifUrl;
                      const imageReceipt = receipt.find(
                        (item) => item.source === original,
                      );
                      if (imageReceipt) {
                        imageReceipt.avifBytes = avif.length;
                        imageReceipt.variants = variants;
                      }
                    }
                    webpParts.push(
                      `import.meta.ROLLUP_FILE_URL_${webpReference}+${JSON.stringify(` ${size}w`)}`,
                    );
                  }
                  responsiveEntries[index] =
                    `${JSON.stringify(original)}:{avif:${fullAvif}${desktopAvif}${desktopWebp},avifSrcSet:[${avifParts.join(",")}].join(", "),webpSrcSet:[${webpParts.join(",")}].join(", "),width:${width},height:${height}}`;
                }
              }),
            );
            return {
              optimized: `export default {${entries.join(",")}};`,
              responsive: `export default {${responsiveEntries.filter(Boolean).join(",")}};`,
            };
          })();
        const modules = await publicModules;
        return id === resolvedId ? modules.optimized : modules.responsive;
      }
      const file = id.split("?")[0];
      if (enabled && choicePath.test(file)) {
        this.addWatchFile(file);
        const assets = await choiceAssets(file, (source, name) =>
          this.emitFile({ type: "asset", name, source }),
        );
        return `export default import.meta.env.BASE_URL + import.meta.ROLLUP_FILE_URL_${assets.full};`;
      }
      if (enabled && flowersMasters.has(file)) {
        const reference = this.emitFile({ type: "asset", name: `flowers-${path.parse(file).name}.webp`, source: await convert(file) });
        references.add(reference);
        return `export default import.meta.env.BASE_URL + import.meta.ROLLUP_FILE_URL_${reference};`;
      }
    },
    resolveFileUrl({ referenceId, fileName }) {
      // Runtime prefixes BASE_URL; keep these paths relative to the HTML page,
      // including when scripts are inlined for the customer's publishing tool.
      if (references.has(referenceId)) return JSON.stringify(fileName);
    },
    generateBundle() {
      if (!enabled) return;
      this.emitFile({
        type: "asset",
        fileName: "static-image-replacements.json",
        source: JSON.stringify(Object.fromEntries(
          [...replacements].map(([original, reference]) => [original, this.getFileName(reference)]),
        )),
      });
    },
    async closeBundle() {
      if (!enabled) return;
      const directory = path.join(config.root, ".tmp-work");
      await mkdir(directory, { recursive: true });
      await writeFile(
        path.join(directory, "optimized-images.json"),
        `${JSON.stringify({ images: receipt.sort((a, b) => a.source.localeCompare(b.source)) }, null, 2)}\n`,
      );
    },
  };
}
