import { imageAsset } from "../game/imageAssets";

/* Real artwork of every stage: the intro route sheet and the header progress
 * show the same stops, so the player recognises where they are. */
export const routeArt = {
  carrier: imageAsset("opening/route-v1/carrier.webp"),
  loading: imageAsset("opening/route-v1/loading.webp"),
  warehouse: imageAsset("opening/route-v1/warehouse.webp"),
  barge: imageAsset("opening/route-v1/barge.webp"),
  "last-mile": imageAsset("opening/route-v1/lastmile.webp"),
} as const;
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
