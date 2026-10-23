import type { SceneContext } from "../types";
import contours from "./segmentedContours.json";
import mobileContours from "./segmentedContours.mobile.json";
import type { WarehouseChoice } from "./warehouseZones";

/** Object boundaries and badge positions use the current illustration's native pixels. */
export type WarehouseComposition = "wide" | "tall";
export function warehouseDrawing(composition: WarehouseComposition = "wide") {
  return composition === "tall" ? mobileContours : contours;
}
export function warehouseContour(id: WarehouseChoice, parcel: SceneContext["parcel"], composition: WarehouseComposition = "wide") {
  const key = id === "alphabet" ? `alphabet-${parcel}` as const : id;
  return { ...warehouseDrawing(composition).regions[key], key };
}
export function warehouseCallouts(parcel: SceneContext["parcel"], composition: WarehouseComposition = "wide") {
  return {
    entrance: warehouseContour("entrance", parcel, composition).anchor,
    alphabet: warehouseContour("alphabet", parcel, composition).anchor,
    keeper: warehouseContour("keeper", parcel, composition).anchor,
    wms: warehouseContour("wms", parcel, composition).anchor,
  };
}
