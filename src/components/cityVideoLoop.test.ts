import { expect, it, vi } from "vitest";
import { startCityVideoLoop } from "./cityVideoLoop";

function decoder() {
  const video = document.createElement("video");
  Object.defineProperties(video, {
    duration: { value: 64 },
    readyState: { value: 4, configurable: true },
  });
  video.play = vi.fn().mockResolvedValue(undefined);
  video.pause = vi.fn();
  let id = 0;
  const callbacks = new Map<number, VideoFrameRequestCallback>();
  video.requestVideoFrameCallback = callback => { callbacks.set(++id, callback); return id; };
  video.cancelVideoFrameCallback = callback => { callbacks.delete(callback); };
  return { video, frame(time: number) {
    video.currentTime = time;
    const pending = [...callbacks.values()];
    callbacks.clear();
    pending.forEach(callback => callback(0, { mediaTime: time } as VideoFrameCallbackMetadata));
  } };
}

it("starts cold decoder warmup three seconds early and does not hold a frame before warmup completes", () => {
  const first = decoder();
  const second = decoder();
  const stop = startCityVideoLoop(first.video, second.video, vi.fn(), vi.fn());
  try {
    first.frame(61);
    expect(second.video.play).toHaveBeenCalledTimes(1);
    first.frame(63.958333);
    expect(first.video.pause).not.toHaveBeenCalled();
    expect(first.video.hasAttribute("data-city-video")).toBe(true);
    second.frame(0);
    expect(second.video.pause).toHaveBeenCalledTimes(1);
    expect(first.video.hasAttribute("data-city-video")).toBe(true);
  } finally { stop(); }
});

it("keeps the active decoder running until the warmed standby finishes seeking to zero", () => {
  const first = decoder();
  const second = decoder();
  const stop = startCityVideoLoop(first.video, second.video, vi.fn(), vi.fn());
  try {
    first.frame(61);
    second.frame(.041667);
    Object.defineProperty(second.video, "seeking", { configurable: true, value: true });
    first.frame(63.958333);
    expect(first.video.pause).not.toHaveBeenCalled();
    expect(first.video.hasAttribute("data-city-video")).toBe(true);
    Object.defineProperty(second.video, "seeking", { configurable: true, value: false });
    first.frame(0);
    first.frame(63.958333);
    expect(first.video.pause).toHaveBeenCalledTimes(1);
    second.frame(0);
    expect(second.video.hasAttribute("data-city-video")).toBe(true);
  } finally { stop(); }
});

it("hands visibility and tracking to a decoded standby frame, then recycles the old decoder", () => {
  const first = decoder();
  const second = decoder();
  const paint = vi.fn();
  const stop = startCityVideoLoop(first.video, second.video, paint, vi.fn());
  first.frame(61);
  second.frame(0);
  first.frame(63.958333);
  expect(second.video.play).toHaveBeenCalled();
  expect(first.video.hasAttribute("data-city-video")).toBe(true);
  expect(second.video.hasAttribute("data-city-video")).toBe(false);
  second.frame(0);
  expect(second.video.hasAttribute("data-city-video")).toBe(true);
  expect(first.video.hasAttribute("data-city-video")).toBe(false);
  expect(paint).toHaveBeenLastCalledWith(0);
  expect(first.video.pause).toHaveBeenCalled();
  expect(first.video.currentTime).toBe(0);
  first.frame(0);
  expect(paint).toHaveBeenCalledTimes(3);
  second.frame(61);
  first.frame(0);
  second.frame(63.958333);
  first.frame(0);
  expect(first.video.hasAttribute("data-city-video")).toBe(true);
  stop();
});

it("keeps native looping when the standby is unavailable and pauses both on cleanup", () => {
  const first = decoder();
  const second = decoder();
  Object.defineProperty(second.video, "readyState", { value: 0 });
  const paint = vi.fn();
  const fail = vi.fn();
  const stop = startCityVideoLoop(first.video, second.video, paint, fail);
  second.video.dispatchEvent(new Event("error"));
  first.frame(63.958333);
  first.frame(0);
  expect(first.video.hasAttribute("data-city-video")).toBe(true);
  expect(second.video.play).not.toHaveBeenCalled();
  expect(paint).toHaveBeenLastCalledWith(0);
  expect(fail).not.toHaveBeenCalled();
  stop();
  expect(first.video.pause).toHaveBeenCalled();
  expect(second.video.pause).toHaveBeenCalled();
});

it("warms the standby near the seam and holds the outgoing final frame until replacement", () => {
  const first = decoder();
  const second = decoder();
  const paint = vi.fn();
  const handoff = vi.fn();
  const stop = startCityVideoLoop(first.video, second.video, paint, vi.fn(), handoff);
  first.frame(63.5);
  second.frame(0);
  expect(second.video.pause).toHaveBeenCalledTimes(1);
  expect(first.video.hasAttribute("data-city-video")).toBe(true);
  expect(paint).toHaveBeenLastCalledWith(63.5);
  first.frame(63.958333);
  expect(first.video.pause).toHaveBeenCalled();
  expect(first.video.currentTime).toBe(63.958333);
  second.frame(0);
  expect(handoff).toHaveBeenCalledTimes(1);
  expect(second.video.hasAttribute("data-city-video")).toBe(true);
  expect(paint).toHaveBeenLastCalledWith(0);
  stop();
});

it("does not switch to an unpresented frame and cancels a handoff when hidden", () => {
  const first = decoder();
  const second = decoder();
  const paint = vi.fn();
  const hidden = Object.getOwnPropertyDescriptor(document, "hidden");
  Object.defineProperty(document, "hidden", { configurable: true, value: false });
  const stop = startCityVideoLoop(first.video, second.video, paint, vi.fn());
  try {
    first.frame(61);
    second.frame(0);
    first.frame(63.958333);
    expect(second.video.style.opacity).toBe("0");
    Object.defineProperty(document, "hidden", { configurable: true, value: true });
    document.dispatchEvent(new Event("visibilitychange"));
    second.frame(0);
    expect(first.video.hasAttribute("data-city-video")).toBe(true);
    expect(paint).toHaveBeenCalledTimes(2);
    expect(first.video.pause).toHaveBeenCalled();
    expect(second.video.pause).toHaveBeenCalled();
    Object.defineProperty(document, "hidden", { configurable: true, value: false });
    document.dispatchEvent(new Event("visibilitychange"));
    expect(first.video.play).toHaveBeenCalledTimes(2);
  } finally {
    stop();
    if (hidden) Object.defineProperty(document, "hidden", hidden);
    else Reflect.deleteProperty(document, "hidden");
  }
});

it("resumes the native loop if a standby decoder never presents its frame", () => {
  vi.useFakeTimers();
  const first = decoder();
  const second = decoder();
  const stop = startCityVideoLoop(first.video, second.video, vi.fn(), vi.fn());
  try {
    first.frame(61);
    second.frame(0);
    first.frame(63.958333);
    vi.advanceTimersByTime(500);
    expect(first.video.play).toHaveBeenCalledTimes(2);
    expect(first.video.hasAttribute("data-city-video")).toBe(true);
    second.frame(0);
    expect(second.video.hasAttribute("data-city-video")).toBe(false);
  } finally { stop(); vi.useRealTimers(); }
});
