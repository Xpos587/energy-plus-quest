import type { SceneContext } from "../types";

// Alphabet order. Plaques run left to right, from receiving (А–Б) to dispatch (Ю–Я).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 0.3398, y: 0.7841 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 0.4301, y: 0.735 },
  { label: "Л–М", letters: "ЛМ", x: 0.5205, y: 0.6858 },
  { label: "Н–У", letters: "НОПРСТУ", x: 0.6108, y: 0.6367 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 0.7012, y: 0.5876 },
  { label: "Ю–Я", letters: "ЮЯ", x: 0.7915, y: 0.5385 },
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
