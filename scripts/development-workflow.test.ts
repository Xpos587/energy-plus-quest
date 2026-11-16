import { expect, test } from "bun:test";
import { mkdtemp, mkdir, writeFile, appendFile, readFile, rm } from "node:fs/promises";
import { resolve, join, dirname } from "node:path";
import { spawnSync } from "node:child_process";
import { createServer, resolveConfig } from "vite";
import { scripts } from "../package.json";

const root = resolve(import.meta.dirname, "..");

test("dev servers ignore generated output, including inside a scratch worktree", async () => {
  const parent = join(root, ".tmp-work/workflow-tests");
  await mkdir(parent, { recursive: true });
  const fixture = await mkdtemp(join(parent, "watch-"));
  try {
    for (const name of ["vite.config.ts", "vite.scenes.config.ts"]) {
      const config = await resolveConfig({ configFile: join(root, name) }, "serve");
      const ignored = config.server.watch?.ignored;
      expect(Array.isArray(ignored), name).toBe(true);
      const patterns = (ignored as string[]).map(pattern => pattern.replace(root, fixture));
      for (const directory of [".tmp-work", "build", "release", "test-results", "playwright-report"]) {
        expect(patterns).toContain(`${fixture}/${directory}/**`);
        await mkdir(join(fixture, directory), { recursive: true });
        await writeFile(join(fixture, directory, "generated.html"), "scratch");
      }
      const source = join(fixture, "src/main.ts");
      await mkdir(dirname(source), { recursive: true });
      await writeFile(source, "export default 1;");
      const server = await createServer({ configFile: false, root: fixture, server: { port: 0, watch: { ignored: patterns } } });
      try {
        await server.listen();
        const deadline = Date.now() + 3000;
        while (!server.watcher.getWatched()[dirname(source)]?.includes("main.ts")) {
          if (Date.now() > deadline) throw new Error("Source file is not watched");
          await Bun.sleep(10);
        }
        const changed = new Promise<string>((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error("Source changes no longer reach Vite")), 3000);
          server.watcher.once("change", file => { clearTimeout(timeout); resolve(file); });
        });
        await appendFile(source, "\n// edited");
        expect(await changed).toBe(source);
        const watched = Object.keys(server.watcher.getWatched());
        expect(watched.some(directory => directory.startsWith(join(fixture, ".tmp-work")))).toBe(false);
        expect(watched.some(directory => directory.startsWith(join(fixture, "release")))).toBe(false);
      } finally { await server.close(); }
    }
  } finally { await rm(fixture, { recursive: true, force: true }); }
});

test("dev CSS updates wait for a complete write and skip the build-only source loader", async () => {
  const parent = join(root, ".tmp-work/workflow-tests");
  await mkdir(parent, { recursive: true });
  const fixture = await mkdtemp(join(parent, "partial-write-"));
  try {
    const source = join(fixture, "src/style.module.css");
    await mkdir(dirname(source), { recursive: true });
    await writeFile(source, ".zone { fill: blue; }");
    const config = await resolveConfig({ configFile: join(root, "vite.config.ts") }, "serve");
    const watch = { ...config.server.watch, ignored: (config.server.watch?.ignored as string[]).map(pattern => pattern.replace(root, fixture)) };
    const server = await createServer({ configFile: false, root: fixture, logLevel: "silent", server: { port: 0, watch } });
    try {
      await server.listen();
      await server.transformRequest("/src/style.module.css");
      const deadline = Date.now() + 3000;
      while (!server.watcher.getWatched()[dirname(source)]?.includes("style.module.css")) {
        if (Date.now() > deadline) throw new Error("CSS is not watched");
        await Bun.sleep(10);
      }
      const updated = new Promise<string>((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error("No CSS update")), 3000);
        server.watcher.once("change", async () => {
          clearTimeout(timeout);
          try { resolve(await readFile(source, "utf8")); }
          catch (error) { reject(error); }
        });
      });
      await writeFile(source, "");
      await Bun.sleep(60); // Simulate an editor's truncate-then-write save.
      await writeFile(source, ".zone { fill: coral; }");
      expect(await updated).toContain("coral");
      expect(config.plugins.some(plugin => plugin.name === "quest-frozen-ui")).toBe(false);
    } finally { await server.close(); }
  } finally { await rm(fixture, { recursive: true, force: true }); }
});

test("check build skips public media copies without changing production", async () => {
  const configFile = join(root, "vite.config.ts");
  const check = await resolveConfig({ configFile, mode: "test" }, "build");
  const production = await resolveConfig({ configFile }, "build");
  expect(check.build.copyPublicDir).toBe(false);
  expect(production.build.copyPublicDir).toBe(true);
});

test("quick E2E requires a file and lists only the selected project", () => {
  expect(scripts["test:e2e:quick"]).toBeTruthy();
  const run = (...args: string[]) => spawnSync("bun", ["run", "test:e2e:quick", ...args], { cwd: root, encoding: "utf8" });
  expect(run().status).toBe(2);
  expect(run("--list").status).toBe(2);
  const listed = run("tests/scene.spec.ts", "--list");
  expect(listed.status).toBe(0);
  expect(listed.stdout).toContain("[desktop-chromium]");
  expect(listed.stdout).not.toContain("[mobile-chromium]");
  expect(listed.stdout).not.toContain("layout.spec.ts");
});
