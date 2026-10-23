import { expect, test } from "bun:test";
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { cachedImageEncode } from "./image-codec-cache";

async function fixture(run: (directory: string) => Promise<void>) {
  const directory = await mkdtemp(path.join(tmpdir(), "image-cache-"));
  try { await run(directory); } finally { await rm(directory, { recursive: true, force: true }); }
}
const result = (value: string) => ({ data: Buffer.from(value), info: { width: 12, height: 8 } });

test("warm hits retain result dimensions and never duplicate or re-encode the source", () => fixture(async directory => {
  const source = Buffer.alloc(512 * 1024, 7);
  let calls = 0;
  const produce = async () => { calls++; return result("small encoded result"); };
  expect((await cachedImageEncode(directory, "photo.webp/webp88", source, produce)).cacheHit).toBe(false);
  const hit = await cachedImageEncode(directory, "photo.webp/webp88", source, produce);
  expect(hit.cacheHit).toBe(true);
  expect(hit.info).toEqual({ width: 12, height: 8 });
  expect(hit.data.toString()).toBe("small encoded result");
  expect(calls).toBe(1);
  const names = await readdir(directory);
  expect(names).toHaveLength(1);
  expect(names[0]).not.toContain("source.bin");
  expect((await readFile(path.join(directory, names[0]))).length).toBeLessThan(1024);
}));

test("changed input bytes or codec cannot reuse a same-path result", () => fixture(async directory => {
  const first = await cachedImageEncode(directory, "same/photo.webp/webp88", Buffer.from("old"), async () => result("old encoding"));
  const changed = await cachedImageEncode(directory, "same/photo.webp/webp88", Buffer.from("new"), async () => result("new encoding"));
  const codec = await cachedImageEncode(directory, "same/photo.webp/avif80", Buffer.from("new"), async () => result("avif encoding"));
  expect(first.cacheHit).toBe(false);
  expect(changed.cacheHit).toBe(false);
  expect(changed.data.toString()).toBe("new encoding");
  expect(codec.cacheHit).toBe(false);
  expect(codec.data.toString()).toBe("avif encoding");
}));

test("bounded writes evict prior results and oversized results are not persisted", () => fixture(async directory => {
  for (const name of ["one", "two", "three"]) {
    await cachedImageEncode(directory, name, Buffer.from(name), async () => result("x".repeat(100)), 350);
  }
  let bytes = 0;
  for (const name of await readdir(directory)) bytes += (await readFile(path.join(directory, name))).length;
  expect(bytes).toBeLessThanOrEqual(350);
  const before = await readdir(directory);
  const huge = await cachedImageEncode(directory, "huge", Buffer.from("huge"), async () => result("x".repeat(400)), 350);
  expect(huge.data.length).toBe(400);
  expect(await readdir(directory)).toEqual(before);
}));

test("interrupted and truncated publications never produce cache hits", () => fixture(async directory => {
  const source = Buffer.from("source");
  await cachedImageEncode(directory, "image/codec", source, async () => result("correct"));
  const [name] = await readdir(directory);
  const complete = await readFile(path.join(directory, name));
  await writeFile(path.join(directory, name), complete.subarray(0, complete.length - 3));
  await writeFile(path.join(directory, "abandoned.tmp"), Buffer.from("unpublished fragment"));
  const restored = await cachedImageEncode(directory, "image/codec", source, async () => result("recovered"));
  expect(restored.cacheHit).toBe(false);
  expect(restored.data.toString()).toBe("recovered");
  const hit = await cachedImageEncode(directory, "image/codec", source, async () => { throw new Error("should not encode"); });
  expect(hit.cacheHit).toBe(true);
  expect(hit.data.toString()).toBe("recovered");
}));

test("concurrent encoded writes obey one shared cache budget", () => fixture(async directory => {
  await Promise.all(Array.from({ length: 6 }, (_, index) => cachedImageEncode(
    directory, String(index), Buffer.from(String(index)), async () => result("x".repeat(100)), 400,
  )));
  const files = await readdir(directory);
  expect(files.every(name => name.endsWith(".cache"))).toBe(true);
  let bytes = 0;
  for (const name of files) bytes += (await readFile(path.join(directory, name))).length;
  expect(bytes).toBeLessThanOrEqual(400);
}));

test("another process holding the writer lock cannot inflate the cache", () => fixture(async directory => {
  await mkdir(path.join(directory, ".write-lock"));
  const output = await cachedImageEncode(directory, "another-process", Buffer.from("source"), async () => result("encoded"));
  expect(output.data.toString()).toBe("encoded");
  expect(output.cacheHit).toBe(false);
  expect(await readdir(directory)).toEqual([".write-lock"]);
}));
