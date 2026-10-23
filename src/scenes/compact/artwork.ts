import { imageAsset } from "../../game/imageAssets";
import type { ParcelId } from "../../game/types";

const assets: Record<ParcelId, Record<string, readonly [string, string]>> = {
  socks: {
    "place-1": [
      "socks-scatter",
      "Незакреплённые носки перемещаются при перевозке",
    ],
    "place-2": ["socks-dishes", "Носки закреплены на ящике с посудой"],
    "place-3": ["socks-niche", "Носки компактно закреплены между коробками"],
    "place-4": [
      "socks-space",
      "Маленький подарок занимает большое грузовое место",
    ],
    auto: ["socks-niche", "Носки компактно закреплены между коробками"],
  },
  camera: {
    "place-1": ["camera-dishes-broken", "Упавший фотоаппарат повредил тарелку"],
    "place-2": [
      "camera-dishes",
      "Фотоаппарат закреплён над посудой, сверху осталось свободное место",
    ],
    "place-3": [
      "camera-unload-three",
      "Три коробки временно убраны для доступа к закреплённому фотоаппарату",
    ],
    "place-4": [
      "camera-space",
      "Закреплённый фотоаппарат оставляет большую часть места пустой",
    ],
    auto: ["camera-niche", "Фотоаппарат безопасно закреплён в небольшой нише"],
  },
  boat: {
    "place-1": [
      "boat-axle",
      "Тяжёлая лодка над ящиками перегрузила заднюю ось",
    ],
    "place-2": ["boat-dishes", "Тяжёлая лодка раздавила посуду"],
    "place-3": [
      "boat-no-fit",
      "Лодка больше доступной ниши и не помещается в ней",
    ],
    "place-4": [
      "boat-reload",
      "Для вертикального размещения лодки пришлось выгрузить остальные грузы",
    ],
    auto: [
      "boat-upright",
      "Лодка закреплена вертикально рядом с упакованными подушками",
    ],
  },
};

export function compactArtwork(parcel: ParcelId, selectedId: string) {
  const entry = assets[parcel][selectedId];
  return entry
    ? { src: imageAsset(`compact-art/outcomes/${entry[0]}.png`), alt: entry[1] }
    : undefined;
}
