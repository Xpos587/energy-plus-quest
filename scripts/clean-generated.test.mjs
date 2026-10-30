import { test, expect } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, rmSync, utimesSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { scripts } from "../package.json";

test("generated cleanup preserves authored work, screenshots and delivery archives", () => {
  const root = mkdtempSync(join(tmpdir(), "quest-clean-"));
  const removed = ["dist/index.html", ".tmp-work/image-build-cache/codec-v2/result.cache", ".tmp-work/results/test/trace.zip"];
  const kept = [".tmp-work/results/test/screenshot.png", ".tmp-work/keep.mjs", "design/master.png", "public/art.webp", "docs/review.pdf", "release/energy-plus-quest-static.zip"];
  try {
    for (const file of [...removed, ...kept]) {
      mkdirSync(join(root, file, ".."), { recursive: true });
      writeFileSync(join(root, file), "preserve");
    }
    const clean = () => spawnSync("sh", ["-c", scripts["clean:generated"]], { cwd: root, encoding: "utf8" });
    expect(clean().status).toBe(0);
    for (const file of removed) expect(existsSync(join(root, file)), file).toBe(false);
    for (const file of kept) expect(existsSync(join(root, file)), file).toBe(true);
    expect(clean().status).toBe(0);
    rmSync(join(root, ".tmp-work"), { recursive: true });
    expect(clean().status).toBe(0);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("72-hour retention removes only stale scratch files and does not follow links", () => {
  const root = mkdtempSync(join(tmpdir(), "quest-retention-"));
  const old = new Date(Date.now() - 73 * 60 * 60 * 1000);
  const fresh = ".tmp-work/fresh/result.png";
  const stale = ".tmp-work/old/result.png";
  const source = "public/old-but-current.webp";
  try {
    for (const file of [fresh, stale, source, "outside/keep.png"]) {
      mkdirSync(join(root, file, ".."), { recursive: true });
      writeFileSync(join(root, file), "keep");
      if (file !== fresh) utimesSync(join(root, file), old, old);
    }
    symlinkSync(join(root, "outside"), join(root, ".tmp-work/link"));
    const clean = () => spawnSync("sh", ["-c", scripts["clean:stale"]], { cwd: root, encoding: "utf8" });
    expect(clean().status).toBe(0);
    expect(existsSync(join(root, stale))).toBe(false);
    expect(existsSync(join(root, ".tmp-work/old"))).toBe(false);
    for (const file of [fresh, source, "outside/keep.png"]) expect(existsSync(join(root, file)), file).toBe(true);
    rmSync(join(root, ".tmp-work"), { recursive: true });
    expect(clean().status).toBe(0);
    symlinkSync(join(root, "outside"), join(root, ".tmp-work"));
    expect(clean().status).toBe(0);
    expect(existsSync(join(root, "outside/keep.png"))).toBe(true);
  } finally { rmSync(root, { recursive: true, force: true }); }
});
