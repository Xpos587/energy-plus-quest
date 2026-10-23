import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { CompactArt } from "./CompactArt";

const context = {
  parcel: "camera",
  recipient: "alva",
  profile: "student",
} as const;

describe("Compact flat cargo bay", () => {
  it.each(["old", "old4", "crew", "express"] as const)(
    "keeps the %s carrier color on the cutaway truck",
    (carrier) => {
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(
        <CompactArt context={{ ...context, carrier }} showResult={false} onSelect={() => {}} />,
      );
      expect(host.querySelectorAll('image[filter][mask]')).toHaveLength(1);
      expect(host.querySelector(carrier === "old4"
        ? 'filter > feColorMatrix[type="matrix"]'
        : 'feColorMatrix[type="hueRotate"]')).not.toBeNull();
      expect(host.querySelectorAll("button[data-hotspot]")).toHaveLength(4);
    },
  );

  it("shows the enlarged boat in the failed rear-axle result", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <CompactArt context={{ ...context, parcel: "boat" }} selectedId="place-1" showResult />,
    );
    expect(host.querySelector("image")?.getAttribute("href")).toContain("boat-zone1-axle-v53.png");
  });

  it("exposes four separate empty spaces as native controls, alongside occupied cargo", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <CompactArt context={context} showResult={false} onSelect={() => {}} />,
    );
    expect(host.querySelector('[data-cargo-view="side-2d"]')).not.toBeNull();
    expect(host.querySelectorAll("button[data-hotspot]")).toHaveLength(4);
    expect(host.querySelectorAll("[data-loading-zone]")).toHaveLength(4);
    expect(host.querySelector("image")?.getAttribute("href")).toContain(
      "compact-art/compact-environment-v54-wide.png",
    );
    const spaces = [
      ...host.querySelectorAll<SVGRectElement>("rect[data-loading-zone]"),
    ].map((node) => ({
      x: Number(node.getAttribute("x")),
      y: Number(node.getAttribute("y")),
      width: Number(node.getAttribute("width")),
      height: Number(node.getAttribute("height")),
    }));
    expect(spaces).toHaveLength(4);
    for (const [i, a] of spaces.entries()) {
      for (const b of spaces.slice(i + 1)) {
        expect(
          a.x + a.width <= b.x ||
            b.x + b.width <= a.x ||
            a.y + a.height <= b.y ||
            b.y + b.height <= a.y,
        ).toBe(true);
      }
    }
  });

  it("previews pending selection without locking, and locks all controls on result", async () => {
    const host = document.createElement("div");
    const root = createRoot(host);
    const chosen: string[] = [];
    Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
    try {
      await act(async () =>
        root.render(
          <CompactArt
            context={context}
            selectedId="place-2"
            showResult={false}
            onSelect={(id) => chosen.push(id)}
          />,
        ),
      );
      const button = host.querySelector<HTMLButtonElement>(
        '[data-hotspot="place-3"]',
      );
      if (!button) throw new Error("Missing third loading place");
      expect(button.disabled).toBe(false);
      await act(async () => button.click());
      expect(chosen).toEqual(["place-3"]);
      await act(async () =>
        root.render(
          <CompactArt
            context={context}
            selectedId="place-3"
            showResult
            onSelect={(id) => chosen.push(id)}
          />,
        ),
      );
      expect(host.querySelectorAll("button:disabled")).toHaveLength(4);
      await act(async () => button.click());
      expect(chosen).toEqual(["place-3"]);
      expect(
        host
          .querySelector('[data-loading-zone="place-3"]')
          ?.getAttribute("data-active"),
      ).toBe("true");
    } finally {
      await act(async () => root.unmount());
    }
  });
});
