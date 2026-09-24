import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneContext, SceneDefinition } from "../types";
import { CraneArt } from "./CraneArt";

export const craneIntroSourceIds = ["p429", "p431", "p433", "p435"] as const;
const choices = [
  {
    id: "rush",
    label: "p440",
    result: ["p444"],
    scoreId: "p446",
    score: { energy: -4, empathy: -3, efficiency: 3 },
  },
  {
    id: "wait",
    label: "p452",
    result: ["p454", "p456"],
    scoreId: "p458",
    score: { energy: 0, empathy: 3, efficiency: -4 },
  },
  {
    id: "petr",
    label: "p465",
    result: ["p467", "p469"],
    scoreId: "p473",
    score: { energy: -2, empathy: 4, efficiency: -3 },
  },
  {
    id: "remote",
    label: "p475",
    result: ["p477", "p479", "p481", "p485", "p487"],
    scoreId: "p491",
    score: { energy: 4, empathy: 4, efficiency: 5 },
  },
] as const;

export function craneOptions(context: SceneContext) {
  const gift = parcelNames[context.parcel];
  const recipient = recipientNames[context.recipient];
  return choices.map((choice) => ({
    id: choice.id,
    label: source(choice.label),
    result: choice.result.map((id) =>
      source(id)
        .replace("(название сюрприза)", gift.genitive)
        .replace("(имя персонажа)", recipient.genitive)
        .replaceAll("(подарок)", gift.accusative)
        .replace("(персонажу)", recipient.dative),
    ),
    score: { ...choice.score },
    sourceIds: [choice.label, ...choice.result, choice.scoreId],
  }));
}

export const craneScene: SceneDefinition = {
  id: "crane",
  number: 4,
  title: source("p384").replace("Сцена 4. ", ""),
  product: source("p385").replace("Целевой продукт: ", ""),
  intro: (context) =>
    craneIntroSourceIds.map((id) =>
      source(id).replace(
        "(название сюрприза)",
        parcelNames[context.parcel].nominative,
      ),
    ),
  options: craneOptions,
  Art: CraneArt,
};
