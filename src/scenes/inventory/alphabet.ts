import type { SceneContext } from "../types";

// Physical plaque centres, left to right from receiving towards dispatch.
export const warehouseShelfRanges = [
  { label: "А–Б", letters: "АБ", x: 360 / 1546, y: 337 / 1017 },
  { label: "В–К", letters: "ВГДЕЁЖЗИЙК", x: 419 / 1546, y: 357 / 1017 },
  { label: "Л–М", letters: "ЛМ", x: 654 / 1546, y: 420 / 1017 },
  { label: "Н–У", letters: "НОПРСТУ", x: 711 / 1546, y: 440 / 1017 },
  { label: "Ф–Э", letters: "ФХЦЧШЩЪЫЬЭ", x: 963 / 1546, y: 504 / 1017 },
  { label: "Ю–Я", letters: "ЮЯ", x: 1020 / 1546, y: 523 / 1017 },
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
