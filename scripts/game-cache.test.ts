import { describe, expect, test } from "bun:test";
import { runInNewContext } from "node:vm";
import { createGameWorker } from "./game-cache";

function worker(version = "one") {
  const stores = new Map<string, Map<string, Response>>();
  const events: Record<string, (event: any) => void> = {};
  let network: (request: Request) => Promise<Response> = async () => new Response("image", { headers: { "Content-Type": "image/webp" } });
  const caches = {
    async keys() { return [...stores.keys()]; },
    async delete(key: string) { return stores.delete(key); },
    async open(name: string) {
      const entries = stores.get(name) ?? new Map<string, Response>(); stores.set(name, entries);
      return {
        async match(request: any) { return entries.get(typeof request === "string" ? request : request.url)?.clone(); },
        async put(request: any, response: Response) { entries.set(typeof request === "string" ? request : request.url, response.clone()); },
        async keys() { return [...entries.keys()].map((url) => new Request(url)); },
        async delete(request: Request) { return entries.delete(request.url); },
      };
    },
  };
  runInNewContext(createGameWorker(version), {
    self: { registration: { scope: "https://game.test/project/" }, addEventListener(name: string, fn: any) { events[name] = fn; } },
    caches, fetch: (request: Request) => network(request), URL, URLSearchParams, Request, Response,
  });
  return {
    stores, events,
    network(fn: typeof network) { network = fn; },
    async request(path: string, headers?: HeadersInit, navigation = false) {
      let result: Promise<Response> | undefined;
      const request = new Request(`https://game.test${path}`, { headers });
      if (navigation) Object.defineProperty(request, "mode", { value: "navigate" });
      const pending: Promise<any>[] = [];
      events.fetch({ request, respondWith(value: Promise<Response>) { result = value; }, waitUntil(value: Promise<any>) { pending.push(value); } });
      if (!result) return undefined;
      const response = await result; await Promise.all(pending); return response;
    },
  };
}

describe("visited game resource cache", () => {
  test("retains a successful retry under the canonical image URL for offline reload", async () => {
    const app = worker();
    const requests: string[] = [];
    app.network(async (request) => {
      requests.push(request.url);
      return new Response("retried image", { headers: { "Content-Type": "image/webp" } });
    });
    await app.request("/project/assets/scene.webp?v=2&artwork-retry=1");
    expect(requests).toEqual(["https://game.test/project/assets/scene.webp?v=2&artwork-retry=1"]);
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/assets/scene.webp?v=2"))?.text()).toBe("retried image");
    await expect(app.request("/project/assets/scene.webp?v=3")).rejects.toThrow("offline");
  });
  test("keeps visited illustration available after the connection disappears", async () => {
    const app = worker();
    expect(await (await app.request("/project/assets/scene.webp"))?.text()).toBe("image");
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/assets/scene.webp"))?.text()).toBe("image");
    await expect(app.request("/project/assets/unvisited.webp")).rejects.toThrow("offline");
  });
  test("keeps retry keys from the previous worker readable without changing other query escaping", async () => {
    const app = worker();
    const entries = new Map<string, Response>();
    entries.set("https://game.test/project/assets/scene.webp?label=a%20b&artwork-retry=3", new Response("legacy retry", { headers: { "Content-Type": "image/webp" } }));
    app.stores.set("energy-quest:%2Fproject%2F:one", entries);
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/assets/scene.webp?label=a%20b"))?.text()).toBe("legacy retry");
    expect(entries.has("https://game.test/project/assets/scene.webp?label=a%20b")).toBe(true);
    await expect(app.request("/project/assets/scene.webp?label=a+b")).rejects.toThrow("offline");
  });
  test("a retry fetches its original URL and replaces a previously cached illustration", async () => {
    const app = worker();
    await app.request("/project/assets/scene.webp");
    const requests: string[] = [];
    app.network(async (request) => { requests.push(request.url); return new Response("fresh retry", { headers: { "Content-Type": "image/webp" } }); });
    expect(await (await app.request("/project/assets/scene.webp?artwork-retry=2"))?.text()).toBe("fresh retry");
    expect(requests).toEqual(["https://game.test/project/assets/scene.webp?artwork-retry=2"]);
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/assets/scene.webp"))?.text()).toBe("fresh retry");
  });
  test("never caches HTML masquerading as an image or failed requests", async () => {
    const app = worker();
    app.network(async () => new Response("fallback", { headers: { "Content-Type": "text/html" } }));
    await app.request("/project/assets/missing.webp");
    expect([...app.stores.values()].flatMap((store) => [...store.keys()])).toHaveLength(0);
    app.network(async () => new Response("failed", { status: 404, headers: { "Content-Type": "image/webp" } }));
    await app.request("/project/assets/missing.webp");
    expect([...app.stores.values()].flatMap((store) => [...store.keys()])).toHaveLength(0);
  });
  test("leaves video, ranges, review and external paths to browser networking", async () => {
    const app = worker();
    expect(await app.request("/project/map.mp4")).toBeUndefined();
    expect(await app.request("/project/assets/scene.webp", { Range: "bytes=0-100" })).toBeUndefined();
    expect(await app.request("/project/review/scene.webp")).toBeUndefined();
    expect(await app.request("/outside/scene.webp")).toBeUndefined();
  });
  test("does not take control of already open game sessions or bulk-precache branches", () => {
    const script = createGameWorker("one");
    expect(script).not.toContain("skipWaiting");
    expect(script).not.toContain("clients.claim");
    expect(script).not.toContain("addAll");
  });
  test("prepares only the minimal HTML shell on install", async () => {
    const app = worker();
    const requests: string[] = [];
    app.network(async (request) => {
      requests.push(request.url);
      return new Response("shell", { headers: { "Content-Type": "text/html" } });
    });
    let completed: Promise<any> | undefined;
    app.events.install({ waitUntil(promise: Promise<any>) { completed = promise; } });
    await completed;
    expect(requests).toEqual(["https://game.test/project/index.html"]);
    expect(app.stores.get("energy-quest:%2Fproject%2F:one")?.has("https://game.test/project/")).toBe(true);
  });
  test("warms requested first-visit images without controlling the initial page", async () => {
    const app = worker();
    const requests: string[] = [];
    app.network(async (request) => { requests.push(request.url); return new Response("visited", { headers: { "Content-Type": "image/webp" } }); });
    let completed: Promise<any> | undefined;
    const messages: unknown[] = [];
    app.events.message({
      data: { type: "QUEST_CACHE_VISITED", urls: ["https://game.test/project/assets/current.webp?v=2&artwork-retry=1", "https://game.test/project/map.mp4", "https://foreign.test/photo.webp"] },
      ports: [{ postMessage(value: unknown) { messages.push(value); } }],
      waitUntil(promise: Promise<any>) { completed = promise; },
    });
    await completed;
    expect(requests).toEqual(["https://game.test/project/assets/current.webp?v=2&artwork-retry=1"]);
    expect(messages).toEqual([{ type: "QUEST_CACHE_READY" }]);
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/assets/current.webp?v=2"))?.text()).toBe("visited");
  });
  test("bounds resource storage and keeps two release caches", async () => {
    const app = worker("new");
    app.stores.set("energy-quest:%2Fproject%2F:old", new Map());
    app.stores.set("energy-quest:%2Fproject%2F:recent", new Map());
    let completion: Promise<any> | undefined;
    app.events.activate({ waitUntil(promise: Promise<any>) { completion = promise; } });
    await completion;
    expect([...app.stores.keys()]).toEqual(["energy-quest:%2Fproject%2F:recent", "energy-quest:%2Fproject%2F:new"]);
    for (let index = 0; index < 85; index++) await app.request(`/project/assets/${index}.webp`);
    expect(app.stores.get("energy-quest:%2Fproject%2F:new")?.size).toBe(80);
  });
  test("uses fresh navigation HTML online and retains a shell for offline reload", async () => {
    const app = worker();
    app.network(async () => new Response("release one", { headers: { "Content-Type": "text/html" } }));
    await app.request("/project/", undefined, true);
    app.network(async () => new Response("release two", { headers: { "Content-Type": "text/html" } }));
    expect(await (await app.request("/project/", undefined, true))?.text()).toBe("release two");
    app.network(async () => { throw new Error("offline"); });
    expect(await (await app.request("/project/", undefined, true))?.text()).toBe("release two");
  });
});
