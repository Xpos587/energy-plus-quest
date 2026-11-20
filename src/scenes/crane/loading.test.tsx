import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { CraneArt } from "./CraneArt";
const context = {
  parcel: "camera",
  recipient: "alva",
  profile: "student",
} as const;
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});
it("keeps the whole quay hidden until the last sprite decodes, and retries failed layers", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockReturnValue({
    x: 0,
    y: 0,
    left: 0,
    top: 0,
    right: 1080,
    bottom: 844,
    width: 1080,
    height: 844,
    toJSON() {},
  });
  let release!: () => void;
  const delayed = new Promise<void>((resolve) => {
    release = resolve;
  });
  let fail = false;
  let releaseOffice!: () => void;
  const office = new Promise<void>((resolve) => {
    releaseOffice = resolve;
  });
  Object.defineProperty(HTMLImageElement.prototype, "decode", {
    configurable: true,
    value: vi.fn(function (this: HTMLImageElement) {
      if (
        this.src.includes("/mid/barge.webp") &&
        !this.src.includes("artwork-retry=2")
      )
      {
        if (!fail) return delayed;
        // A really broken image: done loading, no pixels (a swapped request would still be loading).
        Object.defineProperty(this, "complete", { configurable: true, value: true });
        return Promise.reject(new Error("network"));
      }
      if (this.src.includes("/mid/occluder.webp")) return office;
      return Promise.resolve();
    }),
  });
  const host = document.createElement("div"),
    root = createRoot(host);
  document.body.append(host);
  try {
    const render = () => (
      <CraneArt context={context} showResult={false} onSelect={() => {}} />
    );
    await act(async () => root.render(render()));
    const plane = () =>
      host.querySelector("[data-barge-art] > div") as HTMLElement;
    expect(plane().style.visibility).toBe("hidden");
    await act(async () =>
      root.render(
        <CraneArt context={context} showResult={false} playing="remote" />,
      ),
    );
    await act(async () => release());
    expect(plane().style.visibility).toBe("hidden");
    await act(async () => releaseOffice());
    expect(plane().style.visibility).toBe("visible");
    expect(document.querySelector("[data-artwork-status]")).toBeNull();
    await act(async () => root.render(null));
    fail = true;
    await act(async () => root.render(render()));
    // The first failure retries silently (artwork-retry=1); only a second one shows the plate.
    expect(plane().style.visibility).toBe("hidden");
    expect(
      document.querySelector('[data-artwork-status="error"]'),
    ).not.toBeNull();
    await act(async () =>
      document
        .querySelector<HTMLButtonElement>("[data-artwork-status] button")!
        .click(),
    );
    expect(plane().style.visibility).toBe("visible");
    expect(
      host.querySelector('[data-layer="barge"]')!.getAttribute("src"),
    ).toContain("artwork-retry=2");
  } finally {
    await act(async () => root.unmount());
    host.remove();
    delete (HTMLImageElement.prototype as Partial<HTMLImageElement>).decode;
  }
});
