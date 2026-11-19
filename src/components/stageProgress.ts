import { imageAsset } from "../game/imageAssets";

/* One illustration per stage (drawn in the live scenes' style) for the intro route sheet. */
export const routeArt = {
  carrier: imageAsset("opening/route-v2/carrier.webp"),
  loading: imageAsset("opening/route-v2/loading.webp"),
  warehouse: imageAsset("opening/route-v2/warehouse.webp"),
  barge: imageAsset("opening/route-v2/barge.webp"),
  "last-mile": imageAsset("opening/route-v2/lastmile-helipad.webp"),
} as const;
/* Stamp on the route sheet: its own picture, not a crop of a scene. */
export const routeStamp = imageAsset("opening/route-v2/stamp-helipad.webp");
/* One big object per stage (Teo, 03.11), so it still reads at 26 px on a phone
 * where the route pictures turn into noise. Shared by the header progress and
 * the intro route, so both show the same stops. */
export const stageIcons = {
  carrier: imageAsset("opening/stage-icons-v1/carrier.webp"),
  loading: imageAsset("opening/stage-icons-v1/loading.webp"),
  warehouse: imageAsset("opening/stage-icons-v1/warehouse.webp"),
  barge: imageAsset("opening/stage-icons-v1/barge.webp"),
  "last-mile": imageAsset("opening/stage-icons-v1/lastmile.webp"),
} as const;

export const progressSteps = [
  { id: "carrier", label: "Перевозчик" },
  { id: "loading", label: "Загрузка" },
  { id: "warehouse", label: "Склад" },
  { id: "barge", label: "Баржа" },
  { id: "last-mile", label: "Последняя миля" },
] as const;
