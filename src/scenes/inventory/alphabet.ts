import type { SceneContext } from "../types";

// Alphabet order. Plaques run left to right, from receiving (А–Б) to dispatch (Ю–Я).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 0.2965, y: 0.1755 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 0.3732, y: 0.1936 },
  { label: "Л–М", letters: "ЛМ", x: 0.4538, y: 0.2068 },
  { label: "Н–У", letters: "НОПРСТУ", x: 0.536, y: 0.2209 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 0.6206, y: 0.2371 },
  { label: "Ю–Я", letters: "ЮЯ", x: 0.7103, y: 0.2549 },
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
