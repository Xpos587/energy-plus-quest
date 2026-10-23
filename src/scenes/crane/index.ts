import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph as source } from "../../game/scenarioDocument";
import type { SceneContext, SceneDefinition } from "../types";
import { CraneArt } from "./CraneArt";

export const craneIntroSourceIds = ["53B56B9E", "62451EC9", "6F7BE91B"] as const;
const choices = [
  {
    id: "remote",
    label: "5EDD1701",
    result: ["77362BA7", "5A05E1F5", "44E790DE"],
    scoreId: "47D92404",
    score: { energy: 4, empathy: 4, efficiency: 5 },
  },
  {
    id: "rush",
    label: "0023E31A",
    result: ["27629778"],
    scoreId: "639F545D",
    score: { energy: -4, empathy: -3, efficiency: 3 },
  },
  {
    id: "wait",
    label: "553650B7",
    result: ["14753450"],
    scoreId: "6F64992E",
    score: { energy: 0, empathy: 3, efficiency: -4 },
  },
  {
    id: "petr",
    label: "0C6EC2FC",
    result: ["42344E38", "64BD7433"],
    scoreId: "2B2A52A6",
    score: { energy: -2, empathy: 4, efficiency: -3 },
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
        .replace("(персонажу)", recipient.dative)
        .replace(
          "Теперь он придет",
          `Теперь ${gift.pronoun} ${context.parcel === "socks" ? "придут" : "придет"}`,
        ),
    ),
    score: { ...choice.score },
    sourceIds: [choice.label, ...choice.result, choice.scoreId],
  }));
}

export const craneScene: SceneDefinition = {
  id: "crane",
  number: 4,
  title: source("726CB289", "structure").replace("Сцена 4. ", ""),
  product: source("4F0A1B91", "structure").replace("Целевой продукт: ", ""),
  intro: (context) =>
    craneIntroSourceIds.map((id) =>
      source(id)
        .replace("(название сюрприза)", parcelNames[context.parcel].nominative)
        .replace(
          /^Ваш /,
          context.parcel === "boat"
            ? "Ваша "
            : context.parcel === "socks"
              ? "Ваши "
              : "Ваш ",
        )
        .replace(
          "— его вместе",
          `— ${context.parcel === "boat" ? "её" : context.parcel === "socks" ? "их" : "его"} вместе`,
        ),
    ),
  options: craneOptions,
  Art: CraneArt,
};
