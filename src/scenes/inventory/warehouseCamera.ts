import contours from "./segmentedContours.json";
import type { ParcelId } from "../../game/types";

/** Fit the actual segmented objects, leaving expendable outer walls outside the frame. */
export function warehouseCamera(stage: { width: number; height: number }, parcel: ParcelId, selected?: string, drawing: typeof contours = contours) {
  const keys = ["entrance", `alphabet-${parcel}`, "keeper", "wms"] as const;
  const regions = keys.map(key => drawing.regions[key]);
  const bounds = (items: typeof regions) => {
    const points = items.flatMap(region => [...region.path.matchAll(/(?:M|L)\s+([\d.]+)\s+([\d.]+)/g)].map(match => ({ x: Number(match[1]), y: Number(match[2]) })));
    return { left: Math.min(...points.map(p => p.x)), right: Math.max(...points.map(p => p.x)), top: Math.min(...points.map(p => p.y)), bottom: Math.max(...points.map(p => p.y)) };
  };
  const overview = bounds(regions);
  // Reserve room for the 44px badge targets, including the keeper badge beside
  // his head rather than moving it onto a different object to avoid clipping.
  const badgeMargin = 100;
  for (const region of regions) {
    overview.left = Math.min(overview.left, region.anchor.x * drawing.width - badgeMargin);
    overview.right = Math.max(overview.right, region.anchor.x * drawing.width + badgeMargin);
    overview.top = Math.min(overview.top, region.anchor.y * drawing.height - badgeMargin);
    overview.bottom = Math.max(overview.bottom, region.anchor.y * drawing.height + badgeMargin);
  }
  // Non-interactive scene information is still needed to understand the task.
  // Keep the intake sign below the header rather than cropping to objects only.
  const required = drawing.overviewRequiredBounds;
  overview.left = Math.min(overview.left, required.left);
  overview.right = Math.max(overview.right, required.right);
  overview.top = Math.min(overview.top, required.top);
  overview.bottom = Math.max(overview.bottom, required.bottom);
  const padding = Math.min(24, stage.width * 0.04);
  const fit = (box: typeof overview) => Math.min((stage.width - padding * 2) / (box.right - box.left), (stage.height - padding * 2) / (box.bottom - box.top));
  const contain = Math.min(stage.width / drawing.width, stage.height / drawing.height);
  const cover = Math.max(stage.width / drawing.width, stage.height / drawing.height);
  const overviewScale = Math.max(contain, Math.min(cover, fit(overview)));
  const selectedKey = selected === "alphabet" ? `alphabet-${parcel}` : selected;
  const selectedRegion = regions[keys.findIndex(key => key === selectedKey)];
  const box = selectedRegion ? bounds([selectedRegion]) : overview;
  const scale = selectedRegion ? Math.max(overviewScale, Math.min(overviewScale * 2, fit(box))) : overviewScale;
  const offset = (stageSize: number, sourceSize: number, center: number) => {
    const planeSize = sourceSize * scale;
    if (planeSize <= stageSize) return (stageSize - planeSize) / 2;
    return Math.max(stageSize - planeSize, Math.min(0, stageSize / 2 - center * scale));
  };
  return { scale, left: offset(stage.width, drawing.width, (box.left + box.right) / 2), top: offset(stage.height, drawing.height, (box.top + box.bottom) / 2) };
}
