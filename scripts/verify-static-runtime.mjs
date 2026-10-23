import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { join, relative } from "node:path";

// Deployment transport check, not a browser/gameplay test. Verify the exact
// extracted archive against Nginx; browser smoke testing is a separate step.
const [, , target, directory] = process.argv;
assert(target && directory, "Usage: verify-static-runtime.mjs URL EXTRACTED_DIRECTORY");
const base = new URL(target);
assert(base.pathname.endsWith("/"), "Target URL must end in /");

async function request(path, options = {}) {
  return fetch(new URL(path, base), { redirect: "manual", signal: AbortSignal.timeout(15000), ...options });
}
function mime(file) {
  if (/\.m?js$/i.test(file)) return /^(?:application|text)\/javascript\b/i;
  if (/\.css$/i.test(file)) return /^text\/css\b/i;
  if (/\.html$/i.test(file)) return /^text\/html\b/i;
  if (/\.(?:avif|webp|png|jpe?g|gif|svg|ico)$/i.test(file)) return /^image\//i;
  if (/\.(?:woff2?|ttf|otf)$/i.test(file)) return /^(?:font\/|application\/(?:font|x-font|octet-stream))/i;
  if (/\.(?:mp4|webm)$/i.test(file)) return /^video\//i;
  return null;
}
const withoutSlash = new URL(base.href);
withoutSlash.pathname = withoutSlash.pathname.slice(0, -1);
withoutSlash.search = "release-check=1";
const redirect = await fetch(withoutSlash, { redirect: "manual", signal: AbortSignal.timeout(15000) });
assert.equal(redirect.status, 301, "Canonical slash redirect");
const redirected = new URL(redirect.headers.get("location"), withoutSlash);
assert.equal(redirected.origin, base.origin, "Redirect must preserve public scheme, host and port behind a proxy");
assert.equal(redirected.pathname, base.pathname);
assert.equal(redirected.search, withoutSlash.search, "Redirect must preserve query");

const home = await request("");
assert.equal(home.status, 200);
assert.match(home.headers.get("content-type") ?? "", /^text\/html/);
assert.match(home.headers.get("cache-control") ?? "", /no-cache/);
const html = await home.text();
assert.equal(html, await readFile(join(directory, "index.html"), "utf8"), "Served HTML must be the extracted build");
const scripts = [...html.matchAll(/<script\b[^>]*\bsrc="([^"]+)"/g)].map(match => match[1]);
const styles = [...html.matchAll(/<link\b[^>]*href="([^"]+\.css)"/g)].map(match => match[1]);
assert(scripts.length && styles.length, "External JS and CSS entrypoints expected");
for (const path of [...scripts, ...styles]) {
  const url = new URL(path, base);
  assert.equal(url.origin, base.origin, "All entrypoints must be local");
  assert(url.pathname.startsWith(base.pathname), "Entrypoint escaped the subdirectory");
  const response = await request(path);
  assert.equal(response.status, 200, path);
  assert.match(response.headers.get("content-type") ?? "", mime(path), path);
  assert.equal(response.headers.get("x-content-type-options"), "nosniff", path);
  const body = await response.text();
  assert(!/^\s*(?:<!doctype|<html)/i.test(body), `HTML returned for ${path}`);
  assert.equal(body, await readFile(join(directory, decodeURIComponent(url.pathname.slice(base.pathname.length))), "utf8"), `Wrong body for ${path}`);
}

async function files(root) {
  const entries = await readdir(root, { withFileTypes: true });
  return (await Promise.all(entries.map(entry => entry.isDirectory() ? files(join(root, entry.name)) : [join(root, entry.name)]))).flat();
}
const paths = (await files(directory)).map(path => relative(directory, path));
const queue = [...paths];
await Promise.all(Array.from({ length: 12 }, async () => {
  while (queue.length) {
    const file = queue.shift();
    const response = await request(file.split("/").map(encodeURIComponent).join("/"), { method: "HEAD" });
    assert.equal(response.status, 200, `Missing archive file: ${file}`);
    const expected = mime(file);
    if (expected) assert.match(response.headers.get("content-type") ?? "", expected, `MIME: ${file}`);
    if (file === "quest-cache.js") assert.match(response.headers.get("cache-control") ?? "", /no-cache/);
    if (/^assets\/.*-[\w-]{8,}\.(?:js|css|webp|avif|woff2?)$/.test(file)) assert.match(response.headers.get("cache-control") ?? "", /immutable/);
  }
}));
for (const file of ["assets/missing.js", "assets/missing.css", "scene-art/missing.webp", "missing.mjs", "missing-route"]) {
  const response = await request(file);
  assert.equal(response.status, 404, `Missing ${file} must not fall back to game HTML`);
}
const video = paths.find(file => /city-motion-mobile\.mp4$/.test(file));
assert(video, "Map video must be included");
const range = await request(video, { headers: { Range: "bytes=0-63" } });
assert.equal(range.status, 206, "Video byte-range support");
assert.match(range.headers.get("content-range") ?? "", /^bytes 0-63\//);
await range.arrayBuffer();
const compressed = await request(scripts[0], { headers: { "Accept-Encoding": "gzip" } });
assert.equal(compressed.headers.get("content-encoding"), "gzip", "JavaScript compression");
await compressed.arrayBuffer();
assert(!paths.some(path => /^review\/.*\.html$/i.test(path)), "Reference pages leaked into the archive");
console.log(`Nginx HTTP checks passed: ${paths.length} files, entrypoint bodies/MIME, slash redirect, missing-file 404, gzip, video ranges. Browser gameplay is checked separately.`);
