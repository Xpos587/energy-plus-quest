import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneContext, SceneDefinition, SceneOption } from "../types";
import { LastmileArt } from "./LastmileArt";

export function lastmileOptions({
  recipient,
  parcel,
}: SceneContext): SceneOption[] {
  const remote = recipient !== "arseniy";
  return [
    {
      id: "helicopter",
      label: source("p556"),
      result: [
        source("p558"),
        ...(remote
          ? [
              source("p560").replace(
                "чума/ мест, где обитает Хор",
                recipient === "alva" ? "чума" : "мест, где обитает Хор",
              ),
            ]
          : []),
      ],
      score: { energy: -4, empathy: remote ? -2 : 0, efficiency: 4 },
      sourceIds: ["p556", "p558", ...(remote ? ["p560"] : []), "p563"],
    },
    {
      id: "rover",
      label: source("p565"),
      result: [source("p567")],
      score: { energy: 4, empathy: 3, efficiency: 5 },
      sourceIds: ["p565", "p567", "p569"],
    },
    {
      id: "robot",
      label: source("p572"),
      result: [source("p574"), source("p576")],
      score: { energy: -4, empathy: 3, efficiency: -5 },
      sourceIds: ["p572", "p574", "p576", "p578"],
    },
    {
      id: "pipe-carrier",
      label: source("p580"),
      result: [
        source("p582"),
        source("p584"),
        source("p585").replace(
          "беспилотник (для подарка «лодка» – снегоболотоход)",
          parcel === "boat" ? "снегоболотоход" : "беспилотник",
        ),
      ],
      score: { energy: -5, empathy: 0, efficiency: -3 },
      sourceIds: ["p580", "p582", "p584", "p585", "p587"],
    },
  ];
}

export const lastmileScene: SceneDefinition = {
  id: "lastmile",
  number: 5,
  title: source("p495").replace("Сцена 5. ", ""),
  product: source("p496").replace("Целевой продукт: ", ""),
  intro: ({ recipient, parcel }) => [
    source("p549").replace("(имя персонажа)", recipientNames[recipient].dative),
    source("p551"),
    source("p552"),
    source("p554")
      .replace("(название подарка)", parcelNames[parcel].genitive)
      .replace("(имени персонажа)", recipientNames[recipient].dative),
  ],
  options: lastmileOptions,
  Art: LastmileArt,
};
