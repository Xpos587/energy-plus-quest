import { createHash } from "node:crypto";
import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import type { Plugin, ResolvedConfig } from "vite";

/** Install only the minimal shell; retain illustrations only after a player requests them. */
export function createGameWorker(version: string, shell: string[] = ["index.html"]): string {
  return `"use strict";
const SCOPE = new URL(self.registration.scope);
const PREFIX = "energy-quest:" + encodeURIComponent(SCOPE.pathname) + ":";
const CACHE = PREFIX + ${JSON.stringify(version)};
const MAX_ENTRIES = 80;
let writes = Promise.resolve();
const SHELL = ${JSON.stringify(shell)};
const PINNED = new Set([SCOPE.href, ...SHELL.map((file) => new URL(file, SCOPE).href)]);

function expectedType(url) {
  if (/\\.(?:avif|webp|png|jpe?g|svg)$/i.test(url.pathname)) return /^image\\//i;
  if (/\\.(?:woff2?|ttf|otf)$/i.test(url.pathname)) return /^(?:font\\/|application\\/(?:font|x-font|octet-stream))/i;
  if (/\\.js$/i.test(url.pathname)) return /^(?:text|application)\\/javascript/i;
  if (/\\.css$/i.test(url.pathname)) return /^text\\/css/i;
  return null;
}
function cacheKey(value) {
  const url = new URL(typeof value === "string" ? value : value.url, SCOPE);
  if (url.searchParams.has("artwork-retry")) {
    // Keep unrelated query parameters and their original escaping byte-for-byte.
    url.search = url.search.slice(1).split("&").filter((part) => !new URLSearchParams(part).has("artwork-retry")).join("&");
  }
  return url.href;
}
async function matchResource(cache, key) {
  const cached = await cache.match(key);
  if (cached) return cached;
  // Read entries produced before retry normalization without invalidating the release cache.
  for (const old of await cache.keys()) {
    if (new URL(old.url).searchParams.has("artwork-retry") && cacheKey(old) === key) {
      const response = await cache.match(old);
      if (response) { await store(key, response); return response; }
    }
  }
}
function store(key, response) {
  key = cacheKey(key);
  const copy = response.clone();
  writes = writes.catch(() => {}).then(async () => {
    const cache = await caches.open(CACHE);
    await cache.put(key, copy);
    const keys = await cache.keys();
    const removable = keys.filter((key) => !PINNED.has(key.url));
    for (const stale of removable.slice(0, Math.max(0, keys.length - MAX_ENTRIES))) await cache.delete(stale);
  }).catch(() => {});
  return writes;
}
self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    for (const file of SHELL) {
      const url = new URL(file, SCOPE);
      const response = await fetch(new Request(url.href, { cache: "reload" }));
      const type = file === "index.html" ? /^text\\/html/i : expectedType(url);
      if (!response.ok || response.status !== 200 || !type || !type.test(response.headers.get("content-type") || "")) throw new Error("Game shell unavailable");
      await store(file === "index.html" ? SCOPE.href : url.href, response);
    }
  })());
});
self.addEventListener("message", (event) => {
  if (!event.data || event.data.type !== "QUEST_CACHE_VISITED" || !Array.isArray(event.data.urls)) return;
  const urls = event.data.urls.slice(0, MAX_ENTRIES).filter((value) => typeof value === "string").map((value) => {
    try { return new URL(value, SCOPE); } catch { return null; }
  }).filter((url) => url && url.origin === SCOPE.origin && url.pathname.startsWith(SCOPE.pathname) && !url.pathname.includes("/review/") && expectedType(url));
  event.waitUntil((async () => {
    const queue = [...new Set(urls.map((url) => url.href))];
    await Promise.all(Array.from({ length: Math.min(4, queue.length) }, async () => {
      while (queue.length) {
        const href = queue.shift();
        try {
          const response = await fetch(new Request(href, { cache: "force-cache" }));
          if (response.ok && response.status === 200 && expectedType(new URL(href)).test(response.headers.get("content-type") || "")) await store(href, response);
        } catch {}
      }
    }));
    if (event.ports && event.ports[0]) event.ports[0].postMessage({ type: "QUEST_CACHE_READY" });
  })());
});
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    await caches.open(CACHE);
    const names = (await caches.keys()).filter((name) => name.startsWith(PREFIX));
    const previous = names.filter((name) => name !== CACHE);
    await Promise.all(previous.slice(0, -1).map((name) => caches.delete(name)));
  })().catch(() => {}));
});
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== SCOPE.origin || !url.pathname.startsWith(SCOPE.pathname) || request.headers.has("range") || url.pathname.includes("/review/")) return;
  const navigation = request.mode === "navigate";
  const type = navigation ? /^text\\/html/i : expectedType(url);
  if (!type) return;
  const key = navigation ? SCOPE.href : cacheKey(request);
  event.respondWith((async () => {
    const cache = await caches.open(CACHE).catch(() => null);
    const cached = cache ? await matchResource(cache, key).catch(() => undefined) : undefined;
    if (!navigation && !url.searchParams.has("artwork-retry") && cached) return cached;
    try {
      const response = await fetch(request);
      if (response.ok && response.status === 200 && type.test(response.headers.get("content-type") || "")) event.waitUntil(store(key, response));
      return response;
    } catch (error) {
      if (cached) return cached;
      throw error;
    }
  })());
});
`;
}

/** Runs after HTML/single-file transforms; fingerprints the actual deployable release. */
export function gameCache(): Plugin {
  let config: ResolvedConfig;
  return {
    name: "quest-visited-resource-cache",
    apply: "build",
    configResolved(resolved) { config = resolved; },
    async closeBundle() {
      if (config.build.ssr || config.build.write === false) return;
      const output = path.resolve(config.root, config.build.outDir);
      const html = await readFile(path.join(output, "index.html"));
      const assets = await readdir(path.join(output, config.build.assetsDir)).catch(() => [] as string[]);
      const version = createHash("sha256").update(html).update(assets.sort().join("\n")).digest("hex").slice(0, 20);
      const shell = ["index.html", ...[...html.toString().matchAll(/(?:src|href)=["']([^"']+\.(?:js|css)(?:\?[^"']*)?)["']/g)].map((match) => match[1])];
      await writeFile(path.join(output, "quest-cache.js"), createGameWorker(version, [...new Set(shell)]));
    },
  };
}
