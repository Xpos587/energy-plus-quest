import { parcelNames } from "../names";
import { source } from "../source";
import type { SceneContext, SceneDefinition, SceneOption } from "../types";
import { InventoryArt } from "./InventoryArt";

const branches = [
  {
    id: "entrance",
    label: "p355",
    results: ["p356"],
    scoreId: "p359",
    score: { energy: -2, empathy: -1, efficiency: 0 },
  },
  {
    id: "alphabet",
    label: "p361",
    results: ["p363"],
    scoreId: "p365",
    score: { energy: -3, empathy: 0, efficiency: -1 },
  },
  {
    id: "keeper",
    label: "p367",
    results: ["p369", "p371"],
    scoreId: "p373",
    score: { energy: 1, empathy: 4, efficiency: -3 },
  },
  {
    id: "wms",
    label: "p375",
    results: ["p377", "p379"],
    scoreId: "p381",
    score: { energy: 4, empathy: 4, efficiency: 5 },
  },
];

export function inventoryOptions(context: SceneContext): SceneOption[] {
  const name = parcelNames[context.parcel];
  const resolve = (id: string) =>
    source(id)
      .replaceAll("(сюрприза)", name.genitive)
      .replaceAll("(сюрприз)", name.accusative)
      .replaceAll("(подарок)", name.accusative)
      .replaceAll("(подарке)", name.prepositional)
      .replaceAll("(подарка)", name.genitive)
      .replace(
        "в середине/в конце (в зависимости от первой буквы слова названия подарка – Н, Л, Ф)",
        context.parcel === "camera" ? "в конце" : "в середине",
      );
  return branches.map(({ id, label, results, scoreId, score }) => ({
    id,
    label: resolve(label),
    result: results.map(resolve),
    score: { ...score },
    sourceIds: [label, ...results, scoreId],
  }));
}

export const inventoryScene: SceneDefinition = {
  id: "inventory",
  number: 3,
  title: source("p325"),
  product: source("p326"),
  intro: () => [source("p354")],
  options: inventoryOptions,
  Art: InventoryArt,
};
