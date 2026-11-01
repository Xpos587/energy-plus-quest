import type { SceneContext } from "../types";

// Alphabet order. Plaques run left to right, from receiving (А–Б) to dispatch (Ю–Я).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 0.347, y: 0.8239 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 0.4383, y: 0.7743 },
  { label: "Л–М", letters: "ЛМ", x: 0.5296, y: 0.7247 },
  { label: "Н–У", letters: "НОПРСТУ", x: 0.6208, y: 0.6751 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 0.7121, y: 0.6255 },
  { label: "Ю–Я", letters: "ЮЯ", x: 0.8034, y: 0.5759 },
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
