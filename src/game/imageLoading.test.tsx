import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { App } from "../App";
import { SAVE_KEY } from "./persistence";
import { outcomeArtwork } from "./artwork";
import { sceneChoiceImage } from "../scenes/artwork";

it("offers carrier artwork variants through one image instead of downloading two hidden images", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  localStorage.setItem(
    SAVE_KEY,
    JSON.stringify({
      version: 1,
      scope: "quest-image-test",
      state: {
        step: "outcome",
        profile: "student",
        recipient: "khor",
        parcel: "camera",
        carrier: "old",
      },
    }),
  );
  const host = document.createElement("div");
  const root = createRoot(host);
  try {
    await act(async () => root.render(<App />));
    const artwork = host.querySelector("[data-result-art]");
    expect(artwork?.querySelectorAll("img")).toHaveLength(1);
    const sources = [...(artwork?.querySelectorAll("source") ?? [])];
    expect(sources.some((source) => source.getAttribute("media")?.includes("max-width: 600px"))).toBe(true);
    expect(sources.some((source) => source.getAttribute("srcset")?.includes(outcomeArtwork.old.mobile))).toBe(true);
    expect(artwork?.querySelector("img")?.getAttribute("src")).toBe(outcomeArtwork.old.desktop);
    expect(
      document.querySelector('[data-image-warmup] img')?.getAttribute("src"),
    ).toBe(sceneChoiceImage("compact"));
  } finally {
    await act(async () => root.unmount());
    localStorage.clear();
    vi.unstubAllGlobals();
  }
});
