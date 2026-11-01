import type { SceneContext } from "../types";

// Alphabet order. Plaques run left to right, from receiving (А–Б) to dispatch (Ю–Я).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 0.2952, y: 0.264 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 0.3344, y: 0.2544 },
  { label: "Л–М", letters: "ЛМ", x: 0.4518, y: 0.2257 },
  { label: "Н–У", letters: "НОПРСТУ", x: 0.491, y: 0.2161 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 0.6085, y: 0.1875 },
  { label: "Ю–Я", letters: "ЮЯ", x: 0.6476, y: 0.1779 },
] as const;

export const inventoryAlphabet = {
  camera: { letter: "Ф", resultPosition: "в конце", x: warehouseShelfRanges[4].x, y: warehouseShelfRanges[4].y },
  socks: { letter: "Н", resultPosition: "в середине", x: warehouseShelfRanges[3].x, y: warehouseShelfRanges[3].y },
  boat: { letter: "Л", resultPosition: "в середине", x: warehouseShelfRanges[2].x, y: warehouseShelfRanges[2].y },
} as const satisfies Record<
  SceneContext["parcel"],
  {
    letter: string;
    resultPosition: string;
    x: number;
    y: number;
  }
>;
