import { createReadStream, createWriteStream } from "node:fs";
import { copyFile, lstat, mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import { createHash } from "node:crypto";
import { tmpdir } from "node:os";
import path from "node:path";
import { Readable, Transform } from "node:stream";
import { pipeline } from "node:stream/promises";
import { spawnSync } from "node:child_process";

type FileRecord = { path: string; sha256: string; bytes: number };
type Archive = { name: string; url: string; sha256: string; bytes: number; files: FileRecord[] };
export type Manifest = { version: 1; repository: string; release: string; archives: Archive[] };

export function safePath(value: unknown): asserts value is string {
  if (typeof value !== "string" || !value || value.includes("\\") || /[\x00-\x1f\x7f]/.test(value) || value.startsWith("/") || /^[A-Za-z]:/.test(value) || value.split("/").some((part) => !part || part === "." || part === "..")) {
    throw new Error(`Unsafe media path: ${JSON.stringify(value)}`);
  }
}

export function validateManifest(input: unknown): Manifest {
  const manifest = input as Manifest;
  if (!manifest || manifest.version !== 1 || manifest.repository !== "Xpos587/energy-plus-quest" || !manifest.release || !Array.isArray(manifest.archives)) throw new Error("Invalid media manifest header");
  const paths = new Set<string>();
  const names = new Set<string>();
  const integrity = (record: { sha256: string; bytes: number }) => {
    if (!record || !/^[a-f0-9]{64}$/.test(record.sha256) || !Number.isSafeInteger(record.bytes) || record.bytes < 0) throw new Error("Invalid media integrity record");
  };
  for (const archive of manifest.archives) {
    safePath(archive.name);
    if (archive.name.includes("/") || !archive.name.endsWith(".tar.gz") || names.has(archive.name)) throw new Error("Invalid or duplicate archive name");
    names.add(archive.name);
    integrity(archive);
    if (!["http:", "https:"].includes(new URL(archive.url).protocol) || !Array.isArray(archive.files) || !archive.files.length) throw new Error("Invalid media archive");
    for (const file of archive.files) {
      safePath(file.path);
      integrity(file);
      if (paths.has(file.path)) throw new Error(`Duplicate media path: ${file.path}`);
      paths.add(file.path);
    }
  }
  for (const name of paths) for (let parent = path.posix.dirname(name); parent !== "."; parent = path.posix.dirname(parent)) if (paths.has(parent)) throw new Error(`Media file is also a directory: ${parent}`);
  return manifest;
}

async function assertParents(root: string, relative: string, create = false) {
  for (const segment of relative.split("/").slice(0, -1)) {
    root = path.join(root, segment);
    if (create) await mkdir(root).catch((error) => { if (error.code !== "EEXIST") throw error; });
    try {
      const stat = await lstat(root);
      if (!stat.isDirectory() || stat.isSymbolicLink()) throw new Error(`Unsafe media parent: ${root}`);
    } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
  }
}

export async function matches(file: string, record: { bytes: number; sha256: string }): Promise<boolean> {
  try {
    const stat = await lstat(file);
    if (!stat.isFile() || stat.isSymbolicLink() || stat.size !== record.bytes) return false;
    const hash = createHash("sha256");
    for await (const chunk of createReadStream(file)) hash.update(chunk);
    return hash.digest("hex") === record.sha256;
  } catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") return false; throw error; }
}

function tar(args: string[]): string {
  const result = spawnSync("tar", args, { encoding: "utf8", maxBuffer: 32 * 1024 * 1024, env: { ...process.env, LC_ALL: "C", TAR_OPTIONS: "" } });
  if (result.error || result.status !== 0) throw new Error(`tar failed: ${result.error?.message ?? result.stderr}`);
  return result.stdout;
}

export async function hydrate(root: string, manifest: Manifest, verifyOnly = false): Promise<void> {
  manifest = validateManifest(manifest);
  for (const archive of manifest.archives) {
    const needed: FileRecord[] = [];
    for (const file of archive.files) {
      await assertParents(root, file.path);
      if (!(await matches(path.join(root, file.path), file))) needed.push(file);
    }
    if (!needed.length) continue;
    if (verifyOnly) throw new Error(`Missing or changed media: ${needed.map((file) => file.path).join(", ")}. Run bun scripts/media-artifacts.ts to hydrate.`);
    const temporary = await mkdtemp(path.join(tmpdir(), "energy-media-"));
    try {
      const downloaded = path.join(temporary, "archive.tar.gz");
      const response = await fetch(archive.url);
      if (!response.ok || !response.body) throw new Error(`Download failed: ${archive.name} (HTTP ${response.status})`);
      let received = 0;
      const limit = new Transform({ transform(chunk, _encoding, callback) {
        received += chunk.length;
        callback(received > archive.bytes ? new Error(`Archive exceeds expected size: ${archive.name}`) : null, chunk);
      } });
      await pipeline(Readable.fromWeb(response.body as never), limit, createWriteStream(downloaded));
      if (!(await matches(downloaded, archive))) throw new Error(`Archive integrity mismatch: ${archive.name}`);
      const entries = tar(["-tzf", downloaded, "--quoting-style=literal"]).replace(/\n$/, "").split("\n");
      const types = tar(["-tvzf", downloaded, "--quoting-style=literal"]).replace(/\n$/, "").split("\n");
      const allowed = new Set(archive.files.map((file) => file.path));
      if (entries.length !== allowed.size || types.length !== entries.length) throw new Error(`Archive entries mismatch: ${archive.name}`);
      for (let i = 0; i < entries.length; i++) {
        safePath(entries[i]);
        if (!allowed.delete(entries[i]) || !types[i].startsWith("-")) throw new Error(`Unexpected or nonregular archive entry: ${entries[i]}`);
      }
      const extracted = path.join(temporary, "extracted");
      await mkdir(extracted);
      tar(["-xzf", downloaded, "-C", extracted, "--no-same-owner", "--no-same-permissions"]);
      for (const file of archive.files) if (!(await matches(path.join(extracted, file.path), file))) throw new Error(`Extracted media integrity mismatch: ${file.path}`);
      for (const file of needed) {
        await assertParents(root, file.path, true);
        const target = path.join(root, file.path);
        // Remove a leaf symlink instead of allowing copyFile to follow it.
        const existing = await lstat(target).catch((error) => { if (error.code !== "ENOENT") throw error; return undefined; });
        if (existing && (!existing.isFile() || existing.isSymbolicLink())) throw new Error(`Unsafe media destination: ${file.path}`);
        await copyFile(path.join(extracted, file.path), target);
      }
      console.log(`Hydrated ${needed.length} files from ${archive.name}`);
    } finally { await rm(temporary, { recursive: true, force: true }); }
  }
}

if (import.meta.main) {
  try {
    if (process.argv.slice(2).some((arg) => arg !== "--verify")) throw new Error("Usage: bun scripts/media-artifacts.ts [--verify]");
    const root = path.resolve(import.meta.dir, "..");
    const manifestPath = path.join(root, "media-artifacts.json");
    const raw = await readFile(manifestPath, "utf8").catch((error) => { if (error.code === "ENOENT") throw new Error(`Missing media manifest: ${manifestPath}`); throw error; });
    await hydrate(root, validateManifest(JSON.parse(raw)), process.argv.includes("--verify"));
    console.log("Media files verified.");
  } catch (error) { console.error((error as Error).message); process.exitCode = 1; }
}
