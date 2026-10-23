import { expect, test } from "bun:test";
import { createHash } from "node:crypto";
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { hydrate, safePath, validateManifest, type Manifest } from "./media-artifacts";

const sha256 = (data: Uint8Array | string) => createHash("sha256").update(data).digest("hex");
async function fixture(run: (root: string, manifest: Manifest, stop: () => void) => Promise<void>, link = false) {
  const temporary = await mkdtemp(path.join(tmpdir(), "media-test-"));
  let server: ReturnType<typeof Bun.serve> | undefined;
  try {
    const source = path.join(temporary, "source");
    const root = path.join(temporary, "root");
    await mkdir(path.join(source, "public"), { recursive: true });
    await mkdir(root);
    await writeFile(path.join(source, "public/media.txt"), "original media");
    if (link) { await rm(path.join(source, "public/media.txt")); await symlink("../../outside", path.join(source, "public/media.txt")); }
    const archive = path.join(temporary, "fixture.tar.gz");
    expect(spawnSync("tar", ["-czf", archive, "-C", source, "public/media.txt"]).status).toBe(0);
    const bytes = await readFile(archive);
    server = Bun.serve({ port: 0, fetch: () => new Response(bytes) });
    const manifest: Manifest = { version: 1, repository: "Xpos587/energy-plus-quest", release: "media-baseline-2026-10-23", archives: [{ name: "fixture.tar.gz", url: `http://localhost:${server.port}/fixture.tar.gz`, sha256: sha256(bytes), bytes: bytes.length, files: [{ path: "public/media.txt", bytes: 14, sha256: sha256("original media") }] }] };
    await run(root, manifest, () => server?.stop(true));
  } finally { server?.stop(true); await rm(temporary, { recursive: true, force: true }); }
}

test("rejects traversal, ambiguous names and duplicate paths", () => {
  for (const value of ["../x", "/x", "a/../x", "a//b", "a/./b", "C:/x", "a\\b", "a\nb"]) expect(() => safePath(value)).toThrow("Unsafe media path");
  safePath("public/media with spaces.png");
});

test("hydrates missing and modified files, then verifies offline without download", async () => fixture(async (root, manifest, stop) => {
  await expect(hydrate(root, manifest, true)).rejects.toThrow("Missing or changed media");
  await hydrate(root, manifest);
  expect(await readFile(path.join(root, "public/media.txt"), "utf8")).toBe("original media");
  await writeFile(path.join(root, "public/media.txt"), "corrupt media!");
  await hydrate(root, manifest);
  stop();
  await hydrate(root, manifest);
  await hydrate(root, manifest, true);
}));

test("rejects archive integrity failure before changing target", async () => fixture(async (root, manifest) => {
  manifest.archives[0].sha256 = "0".repeat(64);
  await expect(hydrate(root, manifest)).rejects.toThrow("Archive integrity mismatch");
  await expect(readFile(path.join(root, "public/media.txt"))).rejects.toThrow();
}));

test("rejects unlisted archive entries and wrong extracted hashes", async () => fixture(async (root, manifest) => {
  manifest.archives[0].files[0].path = "public/different.txt";
  await expect(hydrate(root, manifest)).rejects.toThrow("Unexpected or nonregular");
  manifest.archives[0].files[0].path = "public/media.txt";
  manifest.archives[0].files[0].sha256 = "0".repeat(64);
  await expect(hydrate(root, manifest)).rejects.toThrow("Extracted media integrity mismatch");
}));

test("rejects archived symlinks", async () => fixture(async (root, manifest) => {
  await expect(hydrate(root, manifest)).rejects.toThrow("Unexpected or nonregular");
}, true));

test("refuses symlink parent and destination", async () => fixture(async (root, manifest) => {
  await symlink(tmpdir(), path.join(root, "public"));
  await expect(hydrate(root, manifest)).rejects.toThrow("Unsafe media parent");
  await rm(path.join(root, "public"));
  await mkdir(path.join(root, "public"));
  await symlink(path.join(root, "outside"), path.join(root, "public/media.txt"));
  await expect(hydrate(root, manifest)).rejects.toThrow("Unsafe media destination");
}));

test("manifest rejects duplicated paths", async () => fixture(async (_root, manifest) => {
  manifest.archives[0].files.push(manifest.archives[0].files[0]);
  expect(() => validateManifest(manifest)).toThrow("Duplicate media path");
}));
