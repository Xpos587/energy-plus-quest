import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { ArtworkLoading } from "./ArtworkLoading";
import { useArtworkLoading } from "./useArtworkLoading";

vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
afterEach(() => vi.restoreAllMocks());

function Artwork({ src }: { src: string }) {
  const art = useArtworkLoading(src);
  return (
    <div data-status={art.status}>
      <img
        ref={art.ref}
        src={art.src}
        onLoad={art.onLoad}
        onError={art.onError}
        alt="Artwork"
      />
      <ArtworkLoading status={art.status} onRetry={art.retry} />
    </div>
  );
}

it("tracks load, failure, retry and a changed illustration without stale readiness", async () => {
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Artwork src="/first.webp" />));
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("loading");
    expect(host.querySelector('[role="status"]')?.textContent).toContain(
      "Загружаем иллюстрацию",
    );
    expect(host.querySelector("button")).toBeNull();
    await act(async () =>
      host.querySelector("img")?.dispatchEvent(new Event("load")),
    );
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("ready");
    expect(host.querySelector('[role="status"]')).toBeNull();
    await act(async () => root.render(<Artwork src="/second.webp" />));
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("loading");
    await act(async () =>
      host.querySelector("img")?.dispatchEvent(new Event("error")),
    );
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("error");
    expect(host.querySelector("button")?.textContent).toBe("Повторить");
    await act(async () => host.querySelector("button")?.click());
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("loading");
    expect(host.querySelector("img")?.getAttribute("src")).toMatch(
      /^\/second.webp\?artwork-retry=/,
    );
    await act(async () =>
      host.querySelector("img")?.dispatchEvent(new Event("load")),
    );
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("ready");
  } finally {
    await act(async () => root.unmount());
  }
});

it("recognizes cached SVG artwork without waiting for a missed SVG load event", async () => {
  vi.spyOn(HTMLImageElement.prototype, "complete", "get").mockReturnValue(true);
  vi.spyOn(HTMLImageElement.prototype, "naturalWidth", "get").mockReturnValue(
    1040,
  );
  function SvgArtwork() {
    const art = useArtworkLoading<SVGImageElement>("/cached-svg.webp");
    return (
      <svg data-status={art.status} aria-hidden="true">
        <image
          ref={art.ref}
          href={art.src}
          onLoad={art.onLoad}
          onError={art.onError}
        />
      </svg>
    );
  }
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(<SvgArtwork />));
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("ready");
  } finally {
    await act(async () => root.unmount());
  }
});

it("recognizes a cached image whose load event already fired", async () => {
  vi.spyOn(HTMLImageElement.prototype, "complete", "get").mockReturnValue(true);
  vi.spyOn(HTMLImageElement.prototype, "naturalWidth", "get").mockReturnValue(
    1040,
  );
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Artwork src="/cached.webp" />));
    expect(host.firstElementChild?.getAttribute("data-status")).toBe("ready");
  } finally {
    await act(async () => root.unmount());
  }
});
