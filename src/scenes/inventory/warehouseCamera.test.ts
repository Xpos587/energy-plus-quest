import { describe, expect, it } from "vitest";
import contours from "./segmentedContours.json";
import { warehouseCamera } from "./warehouseCamera";

describe("warehouse camera preserves segmented targets", () => {
  it("fits a separate portrait coordinate plane instead of reusing wide source dimensions", () => {
    const portrait=structuredClone(contours);
    portrait.height=2034;
    for(const region of Object.values(portrait.regions))region.path=region.path.replace(/((?:M|L)\s+[\d.]+\s+)([\d.]+)/g,(_all,prefix,y)=>prefix+Number(y)*2);
    portrait.overviewRequiredBounds.top*=2;portrait.overviewRequiredBounds.bottom*=2;
    const camera=warehouseCamera({width:390,height:520},"boat",undefined,portrait);
    for(const key of ["entrance","alphabet-boat","keeper","wms"]as const)for(const point of portrait.regions[key].path.matchAll(/(?:M|L)\s+([\d.]+)\s+([\d.]+)/g)){
      expect(Number(point[1])*camera.scale+camera.left).toBeGreaterThanOrEqual(-1);
      expect(Number(point[1])*camera.scale+camera.left).toBeLessThanOrEqual(391);
      expect(Number(point[2])*camera.scale+camera.top).toBeGreaterThanOrEqual(-1);
      expect(Number(point[2])*camera.scale+camera.top).toBeLessThanOrEqual(521);
    }
  });
  for (const parcel of ["boat", "socks", "camera"] as const) {
    for (const [width, height] of [[320, 210], [390, 330], [820, 697], [1440, 600], [1920, 820], [1080, 836]]) {
      it(`${parcel}, ${width}×${height}: overview and each preview fit the full target`, () => {
        const keys = ["entrance", `alphabet-${parcel}`, "keeper", "wms"] as const;
        const overview = warehouseCamera({ width, height }, parcel);
        for (const key of keys) {
          const points = [...contours.regions[key].path.matchAll(/(?:M|L)\s+([\d.]+)\s+([\d.]+)/g)];
          const preview = warehouseCamera({ width, height }, parcel, key.startsWith("alphabet") ? "alphabet" : key);
          expect(preview.scale).toBeGreaterThanOrEqual(overview.scale);
          for (const camera of [overview, preview]) {
            for (const point of points) {
              const x = Number(point[1]) * camera.scale + camera.left;
              const y = Number(point[2]) * camera.scale + camera.top;
              expect(x).toBeGreaterThanOrEqual(-1);
              expect(y).toBeGreaterThanOrEqual(-1);
              expect(x).toBeLessThanOrEqual(width + 1);
              expect(y).toBeLessThanOrEqual(height + 1);
            }
          }
        }
      });
    }
  }
});
