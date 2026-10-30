import { describe, expect, it } from "vitest";
import { sceneOutcomeImage } from "../artwork";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { SceneOutcomeArt } from "../SceneOutcomeArt";

describe("warehouse cargo artwork", () => {
  for (const branch of ["entrance", "alphabet", "keeper", "wms"]) {
    it(`${branch}: closed-box artwork for every gift and viewport`, () => {
      const context = { recipient: "alva", profile: "student" } as const;
      for (const parcel of ["boat", "socks", "camera"] as const) {
        const path = branch === "wms"
          ? `/scene-art/warehouse-v7/outcome-wms.webp`
          : `/scene-art/warehouse-v7/outcome-${branch === "alphabet" ? `alphabet-${parcel}` : branch}.webp`;
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
