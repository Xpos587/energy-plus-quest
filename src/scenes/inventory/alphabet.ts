import type { SceneContext } from "../types";

// Alphabet order. Plaques run left to right, from receiving (А–Б) to dispatch (Ю–Я).
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 514 / 1672, y: 618 / 941 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 608 / 1672, y: 618 / 941 },
  { label: "Л–М", letters: "ЛМ", x: 789 / 1672, y: 618 / 941 },
  { label: "Н–У", letters: "НОПРСТУ", x: 883 / 1672, y: 618 / 941 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 1064 / 1672, y: 618 / 941 },
  { label: "Ю–Я", letters: "ЮЯ", x: 1158 / 1672, y: 618 / 941 },
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
