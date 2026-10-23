import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { IllustratedCityMap } from "./IllustratedCityMap";

describe("carrier targets", () => {
  it("places choices on the media plane, without thumbnail cards", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <IllustratedCityMap onSelect={() => {}} />,
    );
    const surface = host.querySelector("[data-map-surface]");
    expect(surface?.querySelectorAll("[data-carrier-choice]").length).toBe(4);
    expect(
      surface
        ?.querySelector('[data-carrier-choice="old"]')
        ?.getAttribute("style"),
    ).toContain(`left:${carrierFrame(0)[0][0] * 100}%`);
    expect(host.querySelector("fieldset")).toBeNull();
  });
});

import { act } from "react";
import { createRoot } from "react-dom/client";
import { vi } from "vitest";
import { carrierFrame } from "../game/carrierTracking";
import trackingFrames from "../game/carrierTracking.json";

it("shows a static close-up with reduced motion and restores overview for Express", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: true, addEventListener() {}, removeEventListener() {} }));
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width: 720, height: 500, left: 0, top: 0 } as DOMRect);
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<IllustratedCityMap onSelect={() => {}} selectedId="crew" />));
    expect(host.querySelector("video")).toBeNull();
    expect(host.querySelector("[data-map-viewport]")?.getAttribute("data-map-scale")).toBe("2.4");
    const surface = host.querySelector("[data-map-surface]") as HTMLElement;
    const selectedView = surface.style.transform;
    await act(async () => root.render(<IllustratedCityMap onSelect={() => {}} selectedId="express" />));
    expect(host.querySelector("[data-map-viewport]")?.getAttribute("data-map-scale")).toBe("1");
    expect(surface.style.transform).not.toBe(selectedView);
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});

it("uses displayed media time, preserves IDs on click, and wraps the loop", async () => {
  vi.useFakeTimers();
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addEventListener() {},
    removeEventListener() {},
  }));
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width: 720, height: 500, left: 0, top: 0 } as DOMRect);
  let callback: VideoFrameRequestCallback | undefined;
  HTMLVideoElement.prototype.requestVideoFrameCallback = vi.fn((next) => {
    callback = next;
    return 1;
  });
  HTMLVideoElement.prototype.cancelVideoFrameCallback = vi.fn();
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const select = vi.fn();
  await act(async () => root.render(<IllustratedCityMap onSelect={select} />));
  // Motion starts after the visible poster has finished loading.
  for (const image of host.querySelectorAll("img")) {
    Object.defineProperty(image, "complete", { value: true });
  }
  await act(async () => host.querySelector("img")?.dispatchEvent(new Event("load")));
  const target = host.querySelector(
    '[data-carrier-choice="crew"]',
  ) as HTMLButtonElement;
  await act(async () =>
    callback?.(0, { mediaTime: 12.125 } as VideoFrameCallbackMetadata),
  );
  expect(parseFloat(target.style.left)).toBeCloseTo(
    carrierFrame(12.125)[2][0] * 100,
    5,
  );
  expect(parseFloat(target.style.top)).toBeCloseTo(
    carrierFrame(12.125)[2][1] * 100,
    5,
  );
  expect(carrierFrame(trackingFrames.length / 24)).toEqual(carrierFrame(0));
  expect(carrierFrame(0.041)).toEqual(carrierFrame(0));
  expect(carrierFrame(1 / 24)).not.toEqual(carrierFrame(0));
  await act(async () => target.click());
  expect(select).toHaveBeenCalledWith("crew");
  const surface = host.querySelector("[data-map-surface]") as HTMLElement;
  const original = surface.style.transform;
  const pauseCount = vi.mocked(HTMLMediaElement.prototype.pause).mock.calls.length;
  await act(async () => root.render(<IllustratedCityMap onSelect={select} selectedId="crew" />));
  await act(async () => vi.advanceTimersByTime(1000));
  expect(host.querySelector("[data-map-viewport]")?.getAttribute("data-map-scale")).toBe("2.4");
  const selectedView = surface.style.transform;
  await act(async () => callback?.(0, { mediaTime: 15 } as VideoFrameCallbackMetadata));
  expect(surface.style.transform).not.toBe(selectedView);
  expect(vi.mocked(HTMLMediaElement.prototype.pause).mock.calls.length).toBe(pauseCount);
  await act(async () => root.render(<IllustratedCityMap onSelect={select} />));
  await act(async () => vi.advanceTimersByTime(1000));
  expect(surface.style.transform).toBe(original);
  await act(async () => root.unmount());
  host.remove();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});
