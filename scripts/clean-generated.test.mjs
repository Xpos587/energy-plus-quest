import { test, expect } from "bun:test";
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, rmSync } from "node:fs";
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
