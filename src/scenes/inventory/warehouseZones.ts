import type { SceneContext } from "../types";
import { inventoryAlphabet, warehouseShelfRanges } from "./alphabet";
export { warehouseShelfRanges } from "./alphabet";

export type WarehouseChoice = "entrance" | "alphabet" | "keeper" | "wms";
export const warehouseChoices: WarehouseChoice[] = [
  "entrance",
  "alphabet",
  "keeper",
  "wms",
];

export function warehouseZone(id: WarehouseChoice, context: SceneContext) {
  const gift = inventoryAlphabet[context.parcel];
  const range = warehouseShelfRanges.find((range) =>
    range.letters.includes(gift.letter),
  );
  if (!range) throw new Error(`Missing warehouse shelf for ${gift.letter}`);
  const zones = {
    entrance: {
      label: "У приёмки",
      description: "Свободные ячейки у приёмки, слева на плане склада.",
      points: "91,339 169,326 238,364 221,428 125,415 91,387",
      labelX: 0.17,
      labelY: 0.745,
    },
    alphabet: {
      label: `Стеллаж ${range.label}`,
      description: `Стеллаж ${range.label}, буква ${gift.letter}. Алфавит начинается слева, у приёмки.`,
      points:
        context.parcel === "camera"
          ? "272,199 294,204 294,331 272,324"
          : context.parcel === "socks"
            ? "413,246 439,253 439,352 413,345"
            : "451,254 478,261 478,365 451,358",
      labelX: gift.x,
      labelY: gift.y - 0.075,
    },
    keeper: {
      label: "Кладовщик",
      description: "Опытный кладовщик, справа от стеллажей.",
      points: "797,293 826,291 846,322 846,396 816,408 794,388 787,329",
      labelX: 0.82,
      labelY: 0.717,
    },
    wms: {
      label: "Система WMS",
      description:
        "Компьютерный терминал системы управления складом, внизу у отгрузки.",
      points: "654,464 688,426 741,448 746,494 723,531 661,511",
      labelX: 0.7,
      labelY: 0.948,
    },
  };
  return zones[id];
}
