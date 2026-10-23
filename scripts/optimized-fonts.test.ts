import { afterEach, expect, test } from "bun:test";
import { copyFile, mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { build, createServer } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";
import { fontCodepoints, optimizedFonts } from "./optimized-fonts";

const roots: string[] = [];
afterEach(async () => {
  await Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true, force: true })));
});

async function fixture() {
  const root = await mkdtemp(path.join(tmpdir(), "quest-font-test-"));
  roots.push(root);
  await mkdir(path.join(root, "src"));
  await mkdir(path.join(root, "public/fonts"), { recursive: true });
  for (const weight of ["regular", "medium", "bold"]) {
    const name = `normalidad-proxy-${weight}.woff2`;
    await copyFile(fileURLToPath(new URL(`../public/fonts/${name}`, import.meta.url)), path.join(root, "public/fonts", name));
  }
  await writeFile(path.join(root, "index.html"), '<script type="module" src="/src/main.js"></script>');
  await writeFile(path.join(root, "src/main.js"), 'import "./index.css"; console.log("Шрифт");');
  await writeFile(path.join(root, "src/index.css"), ["regular", "medium", "bold"].map((weight) => `@font-face { font-family: "Fixture-${weight}"; src: url("/fonts/normalidad-proxy-${weight}.woff2") format("woff2"); font-display: swap; }`).join("\n"));
  return root;
}

async function runBuild(root: string, singleFile = false) {
  const result = await build({
    root, configFile: false, base: "./", logLevel: "silent",
    plugins: [optimizedFonts(), ...(singleFile ? [viteSingleFile({ useRecommendedBuildConfig: false })] : [])],
    build: { write: false, assetsInlineLimit: 0, ...(singleFile ? { cssCodeSplit: false } : {}) },
  });
  if (Array.isArray(result) || !("output" in result)) throw new Error("Expected one output");
  return {
    assets: result.output.filter((item) => item.type === "asset" && item.fileName.endsWith(".woff2")),
    style: result.output.filter((item) => item.type === "asset" && (item.fileName.endsWith(".css") || item.fileName === "index.html")).map((item) => String(item.source)).join("\n"),
  };
}

test("font subsets keep Cyrillic, source symbols and unchanged originals; changing copy invalidates hashed URLs", async () => {
  const root = await fixture();
  const original = await readFile(path.join(root, "public/fonts/normalidad-proxy-regular.woff2"));
  const first = await runBuild(root);
  expect(first.assets).toHaveLength(3);
  expect(first.style).not.toContain("/fonts/");
  expect(first.style).not.toContain("__VITE_ASSET__");
  expect(first.style).toContain("font-display:swap");
  for (const asset of first.assets) {
    expect(asset.fileName).toMatch(/^assets\/optimized-normalidad-proxy-(regular|medium|bold)-[\w-]+\.woff2$/);
    expect(first.style).toContain(path.basename(asset.fileName));
    expect(Buffer.byteLength(asset.source)).toBeLessThan(original.length);
  }
  const firstReceipt = JSON.parse(await readFile(path.join(root, ".tmp-work/optimized-fonts.json"), "utf8"));
  expect(firstReceipt.fonts[0].codepoints).toContain("ё".codePointAt(0));
  expect(firstReceipt.fonts[0].codepoints).not.toContain("Ω".codePointAt(0));
  await writeFile(path.join(root, "src/new-copy.json"), JSON.stringify({ text: "Новый текст Ω" }));
  const second = await runBuild(root);
  const receipt = JSON.parse(await readFile(path.join(root, ".tmp-work/optimized-fonts.json"), "utf8"));
  expect(receipt.fonts[0].codepoints).toContain("Ω".codePointAt(0));
  expect(second.assets[0].fileName).not.toBe(first.assets[0].fileName);
  expect(await readFile(path.join(root, "public/fonts/normalidad-proxy-regular.woff2"))).toEqual(original);
}, 60_000);

test("nested and single-file CSS URLs resolve to emitted files", async () => {
  const root = await fixture();
  for (const singleFile of [false, true]) {
    const result = await runBuild(root, singleFile);
    const cssLocation = `https://example.test/projects/game/${singleFile ? "index.html" : "assets/index.css"}`;
    const urls = [...result.style.matchAll(/url\(["']?([^"')]+\.woff2)["']?\)/g)].map((match) => match[1]);
    expect(urls).toHaveLength(3);
    for (const url of urls) {
      const resolved = new URL(url, cssLocation);
      expect(resolved.pathname).toStartWith("/projects/game/assets/");
      expect(result.assets.some((asset) => `/projects/game/${asset.fileName}` === resolved.pathname)).toBe(true);
    }
  }
}, 60_000);

test("development CSS uses original fonts and broad alphabets cover future copy", async () => {
  expect(fontCodepoints("")).toContain("ё".codePointAt(0)!);
  expect(fontCodepoints("")).toContain("І".codePointAt(0)!);
  expect(fontCodepoints("Ω")).toContain("Ω".codePointAt(0)!);
  expect(fontCodepoints("\\u03A9")).toContain("Ω".codePointAt(0)!);
  const root = await fixture();
  const server = await createServer({ root, configFile: false, logLevel: "silent", plugins: [optimizedFonts()] });
  try {
    const css = await server.transformRequest("/src/index.css");
    expect(css?.code).toContain("/fonts/normalidad-proxy-regular.woff2");
    expect(css?.code).not.toContain("optimized-normalidad");
  } finally { await server.close(); }
});
