import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { splitTextPages, useTextPages } from "./useTextPages";

it("finds an oversized sentence's page breaks without measuring every word", () => {
  const word = "слово ";
  const source = word.repeat(128);
  const fits = vi.fn((text: string) => text.length <= 32 * word.length);
  expect(splitTextPages(source, 260, fits)).toEqual(Array(4).fill(word.repeat(32)));
  expect(fits.mock.calls.length).toBeLessThan(40);
});

it("measures each candidate once per pagination pass and remeasures after resize", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const source = "Первое предложение. Второе предложение. Третье предложение. Четвёртое предложение.";
  let width = 200;
  let largestBatch = 0;
  const measurements = new Map<HTMLElement, string[]>();
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockImplementation(() => width);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (this: HTMLElement) {
    let height = 30;
    if (this.tagName === "P" && this.style.visibility === "hidden") {
      largestBatch = Math.max(largestBatch, this.parentElement!.querySelectorAll('p[style*="visibility: hidden"]').length);
      const measured = measurements.get(this) ?? [];
      measured.push(this.innerHTML);
      measurements.set(this, measured);
      height = Math.ceil((this.textContent?.trim().length ?? 0) / (width / 200 * 15)) * 10;
    }
    return { x: 0, y: 0, top: 0, left: 0, right: width, bottom: height, width, height, toJSON: () => ({}) };
  });
  function Reader() {
    const { body, pages } = useTextPages([source], true, true, false, false, false, false, 0, true);
    return <div ref={body} style={{ padding: 0, borderWidth: 0, maxHeight: 30 }}>
      <output>{JSON.stringify(pages)}</output>
    </div>;
  }
  const host = document.createElement("div");
  const root = createRoot(host);
  const pages = (): string[] => JSON.parse(host.querySelector("output")?.textContent ?? "[]");
  try {
    await act(async () => root.render(<Reader />));
    expect(pages().join("")).toBe(source);
    expect(pages()).toHaveLength(2);
    expect(largestBatch).toBeGreaterThan(1);
    const passesBeforeResize = measurements.size;
    width = 400;
    await act(async () => window.dispatchEvent(new Event("resize")));
    expect(pages()).toEqual([source]);
    expect(measurements.size).toBeGreaterThan(passesBeforeResize);
    for (const measured of measurements.values()) {
      expect(measured.length).toBeGreaterThan(0);
      expect(measured.length).toBe(new Set(measured).size);
    }
  } finally {
    await act(async () => root.unmount());
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});
