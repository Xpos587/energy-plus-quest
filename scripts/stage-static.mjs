import assert from "node:assert/strict";
import { access, cp, mkdir, readFile, readdir } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { parseSync } from "rolldown/utils";

const media = /\.(?:avif|webp|png|jpe?g|gif|svg|ico|mp4|webm|woff2?|ttf|otf|mp3|ogg|wav)$/i;
async function files(root, prefix = "") {
  const entries = await readdir(join(root, prefix), { withFileTypes: true });
  return (await Promise.all(entries.map(entry => entry.isDirectory()
    ? files(root, `${prefix}${entry.name}/`) : [`${prefix}${entry.name}`]))).flat();
}

/** Copy only generated code and referenced media, never whole public directories. */
export async function stageStatic(source, destination, nginxConfig) {
  source = resolve(source);
  destination = resolve(destination);
  assert(destination !== source && !destination.startsWith(source + "/"), "Stage outside the build directory");
  const html = await readFile(join(source, "index.html"), "utf8");
  assert.match(html, /<script\b[^>]*type="module"[^>]*src="\.\/assets\/[^" ]+\.js"/, "Expected a standard minified multi-file build");
  assert(!/(?:src|href)=["'](?:https?:)?\/\//i.test(html), "Remote entrypoint dependency");
  const paths = await files(source);
  const codePaths = paths.filter(file => /^assets\/.*\.(?:js|css)$/.test(file));
  const texts = [html];
  const literals = new Set();
  for (const file of codePaths) {
    const text = await readFile(join(source, file), "utf8");
    texts.push(text);
    if (!file.endsWith(".js")) continue;
    const parsed = parseSync(file, text);
    assert.equal(parsed.errors.length, 0, `Cannot inspect ${file}`);
    const visit = node => {
      if (!node || typeof node !== "object") return;
      if (node.type === "Literal" && typeof node.value === "string") literals.add(node.value);
      if (node.type === "TemplateElement") literals.add(node.value.cooked ?? node.value.raw);
      for (const value of Object.values(node)) {
        if (Array.isArray(value)) value.forEach(visit);
        else if (value && typeof value === "object") visit(value);
      }
    };
    visit(parsed.program);
  }
  const text = texts.join("\n");
  const fragments = [...literals];
  const referenced = file => {
    if (file.startsWith("assets/")) return text.includes(basename(file));
    return text.includes(file) || fragments.some(value => value.includes(file)) ||
      (literals.has(basename(file)) && fragments.some(value => value.endsWith(dirname(file) + "/")));
  };
  const manifest = await readFile(join(source, "static-image-replacements.json"), "utf8")
    .catch(error => { if (error.code === "ENOENT") return "{}"; throw error; });
  const replaced = new Set();
  for (const [original, replacement] of Object.entries(JSON.parse(manifest))) {
    assert(typeof replacement === "string" && /^assets\/[^/]+\.webp$/.test(replacement), "Invalid optimized image replacement");
    assert(!original.split("/").includes("..") && !original.startsWith("/"), "Invalid original image path");
    await access(join(source, replacement));
    assert(referenced(replacement), `Unreferenced replacement: ${replacement}`);
    replaced.add(original);
  }
  const selected = paths.filter(file =>
    ["index.html", "README-DEPLOY.txt", "quest-cache.js"].includes(file) ||
    codePaths.includes(file) ||
    /^fonts\/(?:OFL[^/]*\.txt|LICENSE[^/]*)$/.test(file) ||
    (media.test(file) && !replaced.has(file) && referenced(file)),
  );
  // These streams are selected at runtime. Fail even in --stage-only packaging
  // if a missing source or an opaque reference would omit any device variant.
  for (const variant of ["mobile", "tablet", "desktop"]) {
    const file = `scene1-live/separated-routes/city-motion-${variant}.mp4`;
    assert(selected.includes(file), `Missing required city video in staging selection: ${file}`);
  }
  // Final screens use several context variants. A successful build must not
  // silently omit one when its runtime URL becomes dynamically constructed.
  const endings = [
    ...["alva", "khor", "arseniy"].flatMap(recipient =>
      ["socks", "boat", "camera"].map(parcel => `scene-art/resolution-v2/${recipient}-${parcel}.webp`)),
    ...["student", "professional"].flatMap(profile =>
      ["energy", "empathy", "efficiency", ...(profile === "student" ? ["future"] : [])]
        .map(type => `scene-art/certificates-v1/${profile}-${type}.webp`)),
  ];
  const replacements = JSON.parse(manifest);
  for (const file of endings) {
    const family = dirname(file);
    if (text.includes(family))
      assert(selected.includes(replacements[file] ?? file), `Missing required ending artwork in staging selection: ${file}`);
  }
  await mkdir(destination, { recursive: true });
  for (const file of selected) {
    await mkdir(dirname(join(destination, file)), { recursive: true });
    await cp(join(source, file), join(destination, file));
  }
  await cp(nginxConfig, join(destination, "nginx-joydelivery.conf"));
  console.log(`Staged ${selected.length} runtime/support files; excluded ${paths.length - selected.length} unused or replaced files.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const [, , source, destination, config] = process.argv;
  assert(source && destination && config, "Usage: stage-static.mjs DIST STAGE NGINX_CONFIG");
  await stageStatic(source, destination, config);
}
