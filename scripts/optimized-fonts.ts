import { execFile } from "node:child_process";
import { mkdtemp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import type { Plugin, ResolvedConfig } from "vite";

const run = promisify(execFile);
const fontNames = ["regular", "medium", "bold"].map(
  (weight) => `normalidad-proxy-${weight}.woff2`,
);
const sourceExtension = /\.(?:tsx?|jsx?|json|css|html)$/;
const script = fileURLToPath(new URL("./subset-fonts.py", import.meta.url));

interface FontReceipt {
  source: string;
  sourceBytes: number;
  optimizedBytes: number;
  codepoints: number[];
}

async function sourceFiles(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true }).catch(
    (error: NodeJS.ErrnoException) => {
      if (error.code === "ENOENT") return [];
      throw error;
    },
  );
  return (
    await Promise.all(
      entries.map(async (entry) => {
        const file = path.join(directory, entry.name);
        if (entry.isDirectory()) return sourceFiles(file);
        return entry.isFile() && sourceExtension.test(entry.name) ? [file] : [];
      }),
    )
  ).flat();
}

/** Broad alphabets preserve future Russian/Latin copy; current source adds other symbols. */
export function fontCodepoints(text: string): number[] {
  const points = new Set<number>();
  for (const [start, end] of [
    [0x20, 0x024f], // Basic Latin, Latin-1 and Latin Extended A/B.
    [0x0400, 0x052f], // Cyrillic, including ё and neighbouring alphabets.
    [0x1c80, 0x1c8f],
    [0x2de0, 0x2dff],
    [0xa640, 0xa69f],
    [0x2000, 0x206f], // Punctuation and spacing.
    [0x20a0, 0x20cf], // Currency signs.
    [0x2190, 0x21ff], // Arrows used in UI copy.
  ]) {
    for (let point = start; point <= end; point++) points.add(point);
  }
  const decoded = text.replace(/\\u(?:\{([\da-f]{1,6})\}|([\da-f]{4}))/gi,
    (match, scalar: string | undefined, unit: string | undefined) => {
      const point = Number.parseInt(scalar ?? unit!, 16);
      if (point > 0x10ffff) return match;
      return scalar ? String.fromCodePoint(point) : String.fromCharCode(point);
    });
  for (const character of decoded) points.add(character.codePointAt(0)!);
  return [...points].sort((a, b) => a - b);
}

/** Build-time derivatives go through Vite's CSS asset URLs, including relative/single-file builds. */
export function optimizedFonts(): Plugin {
  let config: ResolvedConfig;
  let enabled = false;
  const urls = new Map<string, string>();
  const references: string[] = [];
  let receipt: FontReceipt[] = [];
  return {
    name: "quest-optimized-fonts",
    enforce: "pre",
    configResolved(resolved) {
      config = resolved;
      enabled = config.command === "build" && config.mode !== "test";
    },
    async buildStart() {
      urls.clear();
      references.length = 0;
      receipt = [];
      if (!enabled) return;
      const files = await sourceFiles(path.join(config.root, "src"));
      const html = path.join(config.root, "index.html");
      files.push(html);
      for (const file of files) this.addWatchFile(file);
      const text = (await Promise.all(files.map((file) => readFile(file, "utf8")))).join("\n");
      const directory = await mkdtemp(path.join(tmpdir(), "quest-fonts-"));
      try {
        const fonts = fontNames.map((name) => ({
          name,
          source: path.join(config.publicDir, "fonts", name),
          output: path.join(directory, name),
        }));
        const manifest = path.join(directory, "subset.json");
        await writeFile(manifest, JSON.stringify({ fonts, unicodes: fontCodepoints(text) }));
        // PEP 723 pins the subsetter; uv caches its isolated environment across builds.
        const { stdout } = await run("uv", ["run", "--script", script, manifest], {
          maxBuffer: 4 * 1024 * 1024,
        });
        receipt = JSON.parse(stdout).fonts;
        for (const font of fonts) {
          this.addWatchFile(font.source);
          const reference = this.emitFile({
            type: "asset",
            name: `optimized-${font.name}`,
            source: await readFile(font.output),
          });
          references.push(reference);
          // This is the CSS asset marker consumed by Vite's own URL renderer.
          // Its final URL is relative to the stylesheet or HTML, rather than /fonts/.
          urls.set(`/fonts/${font.name}`, `__VITE_ASSET__${reference}__`);
        }
      } finally {
        await rm(directory, { recursive: true, force: true });
      }
    },
    transform(code, id) {
      if (!enabled || !id.split("?")[0].endsWith(".css")) return;
      return code.replace(/url\(\s*(["']?)(\/fonts\/normalidad-proxy-(?:regular|medium|bold)\.woff2)\1\s*\)/g,
        (match, _quote, url: string) => {
          const asset = urls.get(url);
          return asset ? `url("${asset}")` : match;
        });
    },
    generateBundle: {
      // Inlined CSS must resolve font URLs from the HTML page, not assets/index.css.
      // Run after single-file's normal generateBundle hook has moved styles inline.
      order: "post",
      handler(_options, bundle) {
        if (!enabled) return;
        const names = new Map(references.map((reference) => {
          const fileName = this.getFileName(reference);
          return [path.basename(fileName), `${config.base}${fileName}`];
        }));
        for (const item of Object.values(bundle)) {
          if (item.type !== "asset" || !item.fileName.endsWith(".html")) continue;
          item.source = String(item.source).replace(/url\(\s*(["']?)([^"')]+\.woff2)\1\s*\)/g,
            (match, _quote, url: string) => {
              const replacement = names.get(url.replace(/^\.\//, ""));
              return replacement ? `url("${replacement}")` : match;
            });
        }
      },
    },
    async closeBundle() {
      if (!enabled) return;
      const directory = path.join(config.root, ".tmp-work");
      await mkdir(directory, { recursive: true });
      await writeFile(path.join(directory, "optimized-fonts.json"), `${JSON.stringify({ fonts: receipt }, null, 2)}\n`);
    },
  };
}
