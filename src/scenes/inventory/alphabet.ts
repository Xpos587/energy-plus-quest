import type { SceneContext } from "../types";

// Alphabet order. Plaques run from dispatch (right) back to receiving (left).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 1124 / 1672, y: 534 / 941 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 1055 / 1672, y: 514 / 941 },
  { label: "Л–М", letters: "ЛМ", x: 798 / 1672, y: 462 / 941 },
  { label: "Н–У", letters: "НОПРСТУ", x: 730 / 1672, y: 441 / 941 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 481 / 1672, y: 383 / 941 },
  { label: "Ю–Я", letters: "ЮЯ", x: 418 / 1672, y: 365 / 941 },
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
