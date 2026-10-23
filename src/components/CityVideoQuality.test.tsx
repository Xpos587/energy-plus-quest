import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { IllustratedCityMap } from "./IllustratedCityMap";

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

it.each([
  [1920, 1080, 1, false, false, "desktop"],
  [320, 480, 1, false, false, "mobile"],
  [390, 844, 1, false, false, "mobile"],
  [390, 844, 2, false, false, "tablet"],
  [390, 844, 3, false, false, "desktop"],
  [390, 844, 3, false, true, "tablet"],
  [1920, 1080, 2, true, false, "tablet"],
  [2560, 1440, 2, true, false, "tablet"],
  [1517, 900, 2.5, false, false, "desktop", true],
] as const)("selects source for %sx%s at DPR%s (saveData=%s, coarse=%s)", async (width, height, dpr, limited, coarse, variant, slowTransfer: boolean = false) => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("devicePixelRatio", dpr);
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: coarse && query === "(pointer: coarse)", addEventListener() {}, removeEventListener() {} }));
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width, height, left: 0, top: 0 } as DOMRect);
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  if (slowTransfer) vi.stubGlobal("performance", {
    now: performance.now.bind(performance),
    getEntriesByType: (type: string) => type === "resource" ? [{ transferSize: 60000, encodedBodySize: 50000, duration: 2000 }] : [],
  });
  const connection = Object.getOwnPropertyDescriptor(navigator, "connection");
  Object.defineProperty(navigator, "connection", { configurable: true, value: { saveData: limited, effectiveType: "4g", downlink: 10 } });
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<IllustratedCityMap onSelect={() => {}} />));
    for (const image of host.querySelectorAll("img")) Object.defineProperty(image, "complete", { value: true });
    await act(async () => host.querySelector("img")?.dispatchEvent(new Event("load")));
    const video = host.querySelector("video")!;
    expect(video.getAttribute("src") ?? "").toContain(`city-motion-${variant}.mp4`);
    video.currentTime = 27;
    const src = video.getAttribute("src");
    await act(async () => root.render(<IllustratedCityMap onSelect={() => {}} selectedId="crew" />));
    expect(host.querySelector("video")).toBe(video);
    expect(video.getAttribute("src")).toBe(src);
    expect(video.currentTime).toBe(27);
  } finally {
    await act(async () => root.unmount());
    host.remove();
    if (connection) Object.defineProperty(navigator, "connection", connection);
    else Reflect.deleteProperty(navigator, "connection");
  }
});
