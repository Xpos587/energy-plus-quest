import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, readdir, rename, rm, stat, utimes, writeFile } from "node:fs/promises";
import path from "node:path";

type Info = { width: number; height: number };
type Encoded = { data: Buffer; info: Info };
const limit = 256 * 1024 * 1024;
const writers = new Map<string, Promise<unknown>>();

async function serialized<T>(directory: string, write: () => Promise<T>): Promise<T> {
  const previous = writers.get(directory) ?? Promise.resolve();
  const current = previous.catch(() => {}).then(write);
  writers.set(directory, current);
  try { return await current; }
  finally { if (writers.get(directory) === current) writers.delete(directory); }
}

/** Stores only the encoded result, never another copy of the source image. */
export async function cachedImageEncode(
  directory: string,
  identity: string,
  source: Buffer,
  produce: () => Promise<Encoded>,
  maxBytes = limit,
): Promise<Encoded & { cacheHit: boolean }> {
  if (!Number.isSafeInteger(maxBytes) || maxBytes < 1) throw new Error("Invalid image cache budget");
  const fingerprint = createHash("sha256").update(source).digest("hex");
  const key = createHash("sha256").update(identity).update("\0").update(fingerprint).digest("hex");
  const file = path.join(directory, `${key}.cache`);
  try {
    const bytes = await readFile(file);
    if (bytes.subarray(0, 4).toString() !== "QIC1") throw new Error("Invalid cache header");
    const length = bytes.readUInt32BE(4);
    if (length > 4096 || length < 1 || bytes.length < 8 + length) throw new Error("Incomplete cache header");
    const header = JSON.parse(bytes.subarray(8, 8 + length).toString());
    const data = bytes.subarray(8 + length);
    if (header.fingerprint !== fingerprint || header.bytes !== data.length ||
        !Number.isInteger(header.width) || header.width < 1 ||
        !Number.isInteger(header.height) || header.height < 1 || bytes.length > maxBytes) {
      throw new Error("Incomplete or stale image cache");
    }
    const now = new Date();
    await utimes(file, now, now).catch(() => {});
    return { data, info: { width: header.width, height: header.height }, cacheHit: true };
  } catch {
    // A missing, interrupted or obsolete cache is rebuilt from the actual input.
  }
  const result = await produce();
  const header = Buffer.from(JSON.stringify({ fingerprint, bytes: result.data.length, ...result.info }));
  const prefix = Buffer.alloc(8);
  prefix.write("QIC1");
  prefix.writeUInt32BE(header.length, 4);
  const bytes = Buffer.concat([prefix, header, result.data]);
  if (bytes.length <= maxBytes) await serialized(directory, async () => {
    await mkdir(directory, { recursive: true });
    const lock = path.join(directory, ".write-lock");
    try { await mkdir(lock); }
    catch (error) {
      // Another build is writing. Return its own encoded result without adding
      // cache bytes; no wait loop, duplicate source or budget race is needed.
      if ((error as NodeJS.ErrnoException).code === "EEXIST") return;
      throw error;
    }
    try {
    const entries = await Promise.all((await readdir(directory, { withFileTypes: true }))
      .filter(entry => entry.isFile() && entry.name.endsWith(".cache"))
      .map(async entry => { const name = path.join(directory, entry.name); return { name, ...await stat(name) }; }));
    let total = entries.reduce((sum, entry) => sum + entry.size, 0);
    // Remove this key as well: a truncated result must not consume two budgets.
    for (const entry of entries.sort((a, b) => a.mtimeMs - b.mtimeMs)) {
      if (entry.name !== file && total + bytes.length <= maxBytes) continue;
      await rm(entry.name, { force: true });
      total -= entry.size;
    }
    const temporary = path.join(directory, `${key}.${process.pid}.${randomUUID()}.tmp`);
    try {
      await writeFile(temporary, bytes);
      await rename(temporary, file); // One atomic publication includes metadata and bytes.
    } finally { await rm(temporary, { force: true }); }
    } finally { await rm(lock, { recursive: true, force: true }); }
  });
  return { ...result, cacheHit: false };
}
