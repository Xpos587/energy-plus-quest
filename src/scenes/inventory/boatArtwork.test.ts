import { describe, expect, it } from "vitest";
import { sceneChoiceImage, sceneOutcomeImage } from "../artwork";
import manifest from "../worldManifest.json";
import wide from "./segmentedContours.json";
import tall from "./segmentedContours.mobile.json";
import { existsSync } from "node:fs";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { SceneOutcomeArt } from "../SceneOutcomeArt";

describe("warehouse cargo artwork", () => {
  it("uses the selected A uniform in both registered choice plates", () => {
    expect(sceneChoiceImage("inventory")).toBe("/scene-art/inventory-master-v16.webp");
    for (const [format, contours, suffix] of [["desktop", wide, ""], ["mobile", tall, "-tall"]] as const) {
      const path = `scene-art/inventory-master-v16${suffix}.webp`;
      expect(manifest.scenes.inventory[format].image).toBe(path);
      expect(contours.source).toBe(path);
      expect(existsSync(`public/${path}`)).toBe(true);
    }
  });
  for (const branch of ["entrance", "alphabet", "keeper", "wms"]) {
    it(`${branch}: closed-box artwork for every gift and viewport`, () => {
      const context = { recipient: "alva", profile: "student" } as const;
      for (const parcel of ["boat", "socks", "camera"] as const) {
        const path = `/scene-art/warehouse-results-v3/outcome-${branch === "alphabet" ? `alphabet-${parcel}` : branch}.webp`;
        expect(
          sceneOutcomeImage("inventory", branch, { ...context, parcel }),
        ).toBe(path);
        const host = document.createElement("div");
        host.innerHTML = renderToStaticMarkup(createElement(SceneOutcomeArt, {
          scene: "inventory", selectedId: branch, context: { ...context, parcel },
        }));
        expect(host.querySelector("img")?.getAttribute("src")).toBe(path);
        expect(host.querySelector("source[media]")).toBeNull();
        expect(host.querySelector("[data-desktop-panorama]")).toBeNull();
      }
    });
  }
});
