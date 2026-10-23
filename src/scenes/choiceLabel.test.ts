import { expect, it } from "vitest";
import { choiceLabel } from "./choiceLabel";

it.each([
  ["3) Спросить у кладовщика", "Спросить у кладовщика"],
  ["4) Воспользоваться системой", "Воспользоваться системой"],
  ["Место №2. Над посудой", "Над посудой"],
  ["№1 У входа", "У входа"],
  ["За 2 часа", "За 2 часа"],
])("removes only editorial numbering from %s", (source, expected) => {
  expect(choiceLabel(source)).toBe(expected);
});
