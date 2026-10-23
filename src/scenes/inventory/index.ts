import { parcelNames } from "../names";
import { scenarioParagraph } from "../../game/scenarioDocument";
import type { SceneContext, SceneDefinition, SceneOption } from "../types";
import { inventoryAlphabet } from "./alphabet";
import { InventoryArt } from "./InventoryArt";
import { warehouseZone } from "./warehouseZones";

const branches = [
  {
    id: "entrance",
    label: "4FCD4F75",
    results: ["126E10DA"],
    scoreId: "24A59A28",
    score: { energy: -2, empathy: -1, efficiency: 0 },
  },
  {
    id: "alphabet",
    label: "26CAA917",
    results: ["01E19BE1"],
    scoreId: "0DDE5C3A",
    score: { energy: -3, empathy: 0, efficiency: -1 },
  },
  {
    id: "keeper",
    label: "50B1777D",
    results: ["4341C888-text", "7CABB462"],
    scoreId: "3B214E47",
    score: { energy: 1, empathy: 4, efficiency: -3 },
  },
  {
    id: "wms",
    label: "277603D2",
    results: ["7DC9A705", "757D6707"],
    scoreId: "385D8024",
    score: { energy: 4, empathy: 4, efficiency: 5 },
  },
] as const;

export function inventoryOptions(context: SceneContext): SceneOption[] {
  const name = parcelNames[context.parcel];
  const resolve = (id: string) =>
    scenarioParagraph(id)
      .replaceAll("(сюрприза)", name.genitive)
      .replaceAll("(сюрприз)", name.accusative)
      .replaceAll("(подарок)", name.accusative)
      .replaceAll("(подарке)", name.prepositional)
      .replaceAll("(подарка)", name.genitive)
      .replace(
        "в середине/в конце (в зависимости от первой буквы слова названия подарка – Н, Л, Ф)",
        inventoryAlphabet[context.parcel].resultPosition,
      );
  return branches.map(({ id, label, results, scoreId, score }) => ({
    id,
    label: resolve(label),
    accessibleDescription: warehouseZone(id, context).description,
    result: results.map(resolve),
    score: { ...score },
    sourceIds: [label, ...results, scoreId],
  }));
}

export const inventoryScene: SceneDefinition = {
  id: "inventory",
  number: 3,
  title: scenarioParagraph("4A260F2F", "structure").replace("Сцена 3. ", ""),
  product: scenarioParagraph("312158D0", "structure").replace("Целевой продукт: ", ""),
  intro: () => [scenarioParagraph("769F13F3")],
  options: inventoryOptions,
  Art: InventoryArt,
};
