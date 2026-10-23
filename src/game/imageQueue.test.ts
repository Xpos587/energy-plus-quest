import { afterEach, expect, it, vi } from "vitest";
import { prefetchImage, resetImageQueue } from "./imageAssets";

afterEach(() => {
  resetImageQueue();
  document.body.replaceChildren();
  vi.unstubAllGlobals();
});
it("waits for required current artwork and warms only one image at a time", () => {
  const active = document.createElement("img");
  active.src = "/current.webp";
  Object.defineProperty(active, "complete", {
    value: false,
    configurable: true,
  });
  document.body.append(active);
  prefetchImage("/next.webp");
  prefetchImage("/later.webp");
  expect(document.querySelector("[data-image-warmup]")).toBeNull();
  Object.defineProperty(active, "complete", { value: true });
  active.dispatchEvent(new Event("load"));
  const warmed = document.querySelector("[data-image-warmup] img");
  expect(warmed?.getAttribute("src")).toBe("/next.webp");
  expect(document.querySelectorAll("[data-image-warmup]")).toHaveLength(1);
  warmed?.dispatchEvent(new Event("load"));
  expect(
    document.querySelector("[data-image-warmup] img")?.getAttribute("src"),
  ).toBe("/later.webp");
});
it("does not warm when data saving is requested or request is cancelled", () => {
  vi.stubGlobal("navigator", { connection: { saveData: true } });
  prefetchImage("/no.webp");
  expect(document.querySelector("[data-image-warmup]")).toBeNull();
  vi.stubGlobal("navigator", {});
  const active = document.createElement("img");
  active.src = "/busy.webp";
  Object.defineProperty(active, "complete", { value: false });
  document.body.append(active);
  prefetchImage("/cancel.webp")?.();
  expect(document.querySelector("[data-image-warmup]")).toBeNull();
});
