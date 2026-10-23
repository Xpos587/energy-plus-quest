import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { chromium } from "playwright";

const optimized = process.argv[2] ?? "http://127.0.0.1:4318/";
const baseline = process.argv[3];
const browser = await chromium.launch({ headless: true });
const results = [];
const scope = "quest-image-browser";
const previous = { compact: "place-3", inventory: "wms", crane: "remote", lastmile: "rover" };
async function pageFor(url, viewport, progress, context = {}, throttle = false) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.addInitScript(({ scope, progress, context }) => {
    const state = { step: "outcome", profile: "student", recipient: "khor", parcel: "camera", carrier: "old", ...context };
    if (progress !== "preparation") {
      localStorage.setItem("energy-quest-save-v1", JSON.stringify({ version: 1, scope, state }));
      if (progress) {
        localStorage.setItem(`${scope}:remaining`, "true");
        localStorage.setItem(`${scope}:scenes`, JSON.stringify({ progress }));
      }
    }
  }, { scope, progress, context });
  if (throttle) {
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Network.enable");
    await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
    await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 100, downloadThroughput: 200000, uploadThroughput: 200000 });
  }
  return { page, errors, url };
}
async function loadedImages(page) {
  await page.waitForFunction(() => [...document.images].every((image) => image.complete && image.naturalWidth > 0));
  await page.evaluate(() => Promise.all([...document.images].map((image) => image.decode())));
}
function progress(index, phase, selectedId) {
  const scenes = Object.keys(previous);
  const answers = Object.fromEntries(scenes.slice(0, index).map((scene) => [scene, previous[scene]]));
  if (phase === "result") answers[scenes[index]] = selectedId;
  return { sceneIndex: index, phase, answers, finished: false };
}
try {
  for (const [label, url] of [...(baseline ? [["before", baseline]] : []), ["after", optimized]]) {
    for (const screen of ["preparation", undefined]) {
      const { page, errors } = await pageFor(url, { width: 375, height: 667 }, screen, {}, true);
      const started = Date.now();
      await page.goto(url, { waitUntil: "load" });
      await loadedImages(page);
      const data = await page.evaluate(() => ({
        images: [...document.images].map((image) => ({ path: new URL(image.currentSrc).pathname, width: image.naturalWidth, height: image.naturalHeight })),
        resources: performance.getEntriesByType("resource").map((resource) => ({ path: new URL(resource.name).pathname, bytes: resource.encodedBodySize, initiator: resource.initiatorType, end: Math.round(resource.responseEnd) })),
      }));
      assert.deepEqual(errors, []);
      if (label === "after" && screen !== "preparation") {
        assert.equal(await page.locator("[data-result-art] img").count(), 1);
        const requests = data.resources.filter((resource) => /optimized-old-(desktop|mobile)/.test(resource.path));
        assert.equal(requests.length, 1);
        assert.match(requests[0].path, /old-mobile/);
      }
      results.push({ label, screen: screen ?? "carrier-result", elapsedMs: Date.now() - started, ...data });
      await page.close();
    }
  }
  const branches = [
    [1, "inventory", ["entrance", "keeper", "wms", "alphabet"]],
    [2, "crane", ["rush", "wait", "petr", "remote"]],
    [3, "lastmile", ["helicopter", "rover", "robot", "pipe-carrier"]],
  ];
  let checked = 0;
  for (const [index, scene, choices] of branches) {
    for (const selectedId of choices) {
      const contexts = selectedId === "alphabet" ? [{ parcel: "camera" }, { parcel: "socks" }, { parcel: "boat" }]
        : selectedId === "helicopter" ? [{ recipient: "arseniy" }, { recipient: "khor" }]
        : scene === "lastmile" && selectedId === "pipe-carrier" ? [{ parcel: "camera" }, { parcel: "boat" }] : [{}];
      for (const context of contexts) {
        const { page, errors } = await pageFor(optimized, { width: 375, height: 667 }, progress(index, "result", selectedId), context);
        await page.goto(optimized, { waitUntil: "load" });
        await loadedImages(page);
        const image = page.locator("[data-scene-consequence] > picture img");
        assert.match(await image.getAttribute("src"), /assets\/optimized-/);
        assert.deepEqual(errors, []);
        await page.close();
        checked++;
      }
    }
  }
  for (const parcel of ["camera", "socks", "boat"]) {
    for (const selectedId of ["place-1", "place-2", "place-3", "place-4", "auto"]) {
      const { page, errors } = await pageFor(optimized, { width: 375, height: 667 }, progress(0, "result", selectedId), { parcel });
      await page.goto(optimized, { waitUntil: "load" });
      for (let i = 0; i < 12 && await page.locator("[data-compact-consequence]").count() === 0; i++) {
        await page.getByRole("button", { name: "Следующий фрагмент", exact: true }).click();
      }
      const image = page.locator("[data-compact-consequence] img");
      await image.waitFor();
      await loadedImages(page);
      assert.match(await image.getAttribute("src"), /assets\/optimized-/);
      assert.deepEqual(errors, []);
      await page.close();
      checked++;
    }
  }
  const { page, errors } = await pageFor(optimized, { width: 320, height: 568 }, progress(1, "choice"));
  let blocked = false;
  await page.route("**/assets/optimized-inventory-barge-style-v6-*", async (route) => {
    if (!blocked) { blocked = true; await route.abort("failed"); } else await route.continue();
  });
  await page.goto(optimized);
  await page.locator('[data-artwork-status="error"]').waitFor();
  await page.getByRole("button", { name: "Повторить", exact: true }).click();
  await page.waitForFunction(() => !document.querySelector("[data-artwork-status]"));
  assert.deepEqual(errors, []);
  await page.close();
  await mkdir(".tmp-work/image-optimization", { recursive: true });
  await writeFile(".tmp-work/image-optimization/browser.json", JSON.stringify({ conditions: "375×667, cold cache, latency 100ms, 200000 bytes/s both directions", checkedOutcomeBranches: checked, retryPassed: true, results }, null, 2));
  console.log(JSON.stringify({ checkedOutcomeBranches: checked, retryPassed: true, timings: results.map(({ label, screen, elapsedMs, resources }) => ({ label, screen, elapsedMs, imageBytes: resources.filter((resource) => /\.(avif|png|webp)$/.test(resource.path)).reduce((sum, resource) => sum + resource.bytes, 0) })) }, null, 2));
} finally {
  await browser.close();
}
