import { test, expect } from "bun:test";
import { mkdtemp, mkdir, writeFile, readFile, rm, access } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { stageStatic } from "./stage-static.mjs";

test("ships dynamic runtime media and licenses without publishing reference pages or source maps", async () => {
  const root = await mkdtemp(join(tmpdir(), "quest-stage-test-"));
  const source = join(root, "build");
  const stage = join(root, "stage");
  const fixture = {
    "index.html": '<script type="module" src="./assets/index-abcdefgh.js"></script>',
    "README-DEPLOY.txt": "deployment instructions",
    "quest-cache.js": "/* cache worker */",
    "assets/index-abcdefgh.js": 'const image = "assets/optimized-original-abcdefgh.webp"; const warehouse="scene-world/warehouse.webp"; const font="fonts/example.woff2"; const movies=["city-motion-mobile.mp4","city-motion-tablet.mp4","city-motion-desktop.mp4"].map(name=>"scene1-live/separated-routes/"+name);',
    "assets/unused-image.webp": "unused derivative",
    "scene-world/unused.webp": "unused original",
    "assets/index-abcdefgh.js.map": '{"sourcesContent":["private source"]}',
    "fonts/LICENSE.txt": "font license",
    "fonts/example.woff2": "font",
    "scene-world/warehouse.webp": "warehouse",
    "static-image-replacements.json": JSON.stringify({"scene-art/original.png":"assets/optimized-original-abcdefgh.webp"}),
    "scene-art/original.png": "editable original",
    "assets/optimized-original-abcdefgh.webp": "runtime image",
    "scene1-live/separated-routes/city-motion-mobile.mp4": "video",
    "scene1-live/separated-routes/city-motion-tablet.mp4": "tablet video",
    "scene1-live/separated-routes/city-motion-desktop.mp4": "desktop video",
    "review/carriers/closer-blue.png": "inspection",
    "review/carriers/index.html": "private reference page",
    "review/unrelated/photo.png": "unrelated reference",
  };
  try {
    for (const [file, body] of Object.entries(fixture)) {
      const path = join(source, file);
      await mkdir(path.slice(0, path.lastIndexOf("/")), { recursive: true });
      await writeFile(path, body);
    }
    const config = join(root, "nginx.conf");
    await writeFile(config, "location /game/ { }");
    await stageStatic(source, stage, config);
    for (const file of ["index.html", "README-DEPLOY.txt", "quest-cache.js", "fonts/LICENSE.txt", "fonts/example.woff2", "scene-world/warehouse.webp", ...["mobile", "tablet", "desktop"].map(variant => `scene1-live/separated-routes/city-motion-${variant}.mp4`)]) {
      expect(await readFile(join(stage, file), "utf8")).toBe(fixture[file]);
    }
    for (const file of ["assets/unused-image.webp", "scene-world/unused.webp", "review/carriers/closer-blue.png", "scene-art/original.png", "static-image-replacements.json", "assets/index-abcdefgh.js.map", "review/carriers/index.html", "review/unrelated/photo.png"]) {
      expect(await access(join(stage, file)).then(() => true, () => false)).toBe(false);
    }
    expect(await readFile(join(stage, "nginx-joydelivery.conf"), "utf8")).toBe("location /game/ { }");
    expect(await readFile(join(stage, "assets/optimized-original-abcdefgh.webp"), "utf8")).toBe("runtime image");
    await rm(join(source, "assets/optimized-original-abcdefgh.webp"));
    await expect(stageStatic(source, join(root, "broken-stage"), config)).rejects.toThrow();
  } finally { await rm(root, { recursive: true, force: true }); }
});

test.each(["dynamic-reference", "mobile", "tablet", "desktop"])("refuses a package with omitted city video: %s", async (missing) => {
  const root = await mkdtemp(join(tmpdir(), "quest-stage-video-"));
  const source = join(root, "build");
  const stage = join(root, "stage");
  const directory = "scene1-live/separated-routes/";
  try {
    await mkdir(join(source, "assets"), { recursive: true });
    await mkdir(join(source, directory), { recursive: true });
    await writeFile(join(source, "index.html"), '<script type="module" src="./assets/index-video.js"></script>');
    const script = missing === "dynamic-reference"
      ? 'const asset=name=>"scene1-live/separated-routes/"+name; const movie=asset(`city-motion-${variant}.mp4`);'
      : 'const movies=["city-motion-mobile.mp4","city-motion-tablet.mp4","city-motion-desktop.mp4"].map(name=>"scene1-live/separated-routes/"+name);';
    await writeFile(join(source, "assets/index-video.js"), script);
    for (const variant of ["mobile", "tablet", "desktop"]) {
      if (variant !== missing) await writeFile(join(source, directory, `city-motion-${variant}.mp4`), `${variant} video`);
    }
    const config = join(root, "nginx.conf");
    await writeFile(config, "location /game/ { }");
    await expect(stageStatic(source, stage, config)).rejects.toThrow("Missing required city video");
    expect(await access(stage).then(() => true, () => false)).toBe(false);
  } finally { await rm(root, { recursive: true, force: true }); }
});

test("refuses an inline/debug export instead of silently sending the wrong format", async () => {
  const root = await mkdtemp(join(tmpdir(), "quest-stage-invalid-"));
  try {
    await writeFile(join(root, "index.html"), "<script>console.log('inline')</script>");
    await expect(stageStatic(root, `${root}-stage`, "unused.conf")).rejects.toThrow("multi-file build");
  } finally { await rm(root, { recursive: true, force: true }); }
});

test("ships every ending image referenced by the real screen sources and rejects omissions", async () => {
  const { transformSync } = await import("esbuild");
  const root = await mkdtemp(join(tmpdir(), "quest-stage-endings-"));
  const source = join(root, "build");
  const families = {
    "resolution-v2": ["alva", "khor", "arseniy"].flatMap(recipient => ["socks", "boat", "camera"].map(parcel => `${recipient}-${parcel}`)),
    "certificates-v1": ["student-energy", "student-empathy", "student-efficiency", "student-future", "professional-energy", "professional-empathy", "professional-efficiency"],
  };
  try {
    await mkdir(join(source, "assets"), { recursive: true });
    await writeFile(join(source, "index.html"), '<script type="module" src="./assets/index-endings.js"></script>');
    let script = 'const videos=["scene1-live/separated-routes/city-motion-mobile.mp4","scene1-live/separated-routes/city-motion-tablet.mp4","scene1-live/separated-routes/city-motion-desktop.mp4"];';
    for (const file of ["../src/scenes/resolutionArtwork.ts", "../src/scenes/LogistCertificate.tsx"]) {
      const code = await readFile(new URL(file, import.meta.url), "utf8");
      script += transformSync(code, { loader: "tsx", format: "iife" }).code;
    }
    await writeFile(join(source, "assets/index-endings.js"), script);
    await mkdir(join(source, "scene1-live/separated-routes"), { recursive: true });
    for (const variant of ["mobile", "tablet", "desktop"])
      await writeFile(join(source, `scene1-live/separated-routes/city-motion-${variant}.mp4`), "video");
    const images = Object.entries(families).flatMap(([family, names]) => names.map(name => `scene-art/${family}/${name}.webp`));
    for (const file of images) {
      await mkdir(join(source, file, ".."), { recursive: true });
      await writeFile(join(source, file), "image");
    }
    const config = join(root, "nginx.conf");
    await writeFile(config, "location /game/ { }");
    await stageStatic(source, join(root, "stage"), config);
    for (const file of images) expect(await readFile(join(root, "stage", file), "utf8")).toBe("image");
    for (const file of images) {
      await rm(join(source, file));
      await expect(stageStatic(source, join(root, "broken"), config)).rejects.toThrow("Missing required ending artwork");
      await writeFile(join(source, file), "image");
    }
  } finally { await rm(root, { recursive: true, force: true }); }
});
