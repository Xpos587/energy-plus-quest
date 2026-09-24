import type { ParcelId } from "../../game/types";
import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneDefinition } from "../types";
import { CompactArt } from "./CompactArt";

// Each row preserves result paragraphs, score paragraphs, then the score vector.
const outcomes: Record<
  ParcelId,
  readonly (readonly [
    readonly number[],
    readonly number[],
    readonly [number, number, number],
  ])[]
> = {
  socks: [
    [[208], [210, 211, 212], [0, -4, -1]],
    [
      [230, 231],
      [233, 234, 235],
      [3, 3, 1],
    ],
    [[257], [260, 261, 262], [2, 2, 4]],
    [[278], [280, 281, 282], [-3, -3, -3]],
    [[301], [304, 305, 306], [2, 3, 4]],
  ],
  camera: [
    [
      [215, 216],
      [218, 219, 220],
      [-1, 0, -3],
    ],
    [[240], [242, 243, 244], [2, 0, 1]],
    [[264], [266, 267, 268], [2, 1, 3]],
    [[284], [286, 287, 288], [-3, -1, -3]],
    [[308], [310, 311, 312], [1, 1, 4]],
  ],
  boat: [
    [[223], [225, 226, 227], [-2, 4, -5]],
    [[247], [249, 250, 251], [-3, -3, -4]],
    [[270], [272, 273, 274], [-4, -5, -5]],
    [[290], [292, 293, 294], [-3, 3, 4]],
    [
      [314, 316],
      [319, 320, 321],
      [-4, 3, 5],
    ],
  ],
};
const labels = [206, 229, 252, 277, 300];
const accessibleDescriptions = [
  "Над тяжёлыми ящиками у задних дверей, над колёсами. Свободное место без креплений.",
  "Над ящиком с хрупкой посудой, укрытым мягким материалом. Есть красные стропы.",
  "Небольшая ниша между посылками, за тремя коробками. Есть короткая стропа.",
  "Высокое место у передней стенки, за остальным грузом. Рядом подушки, на стенке красные стропы.",
];

export const compactScene: SceneDefinition = {
  id: "compact",
  number: 2,
  title: source("p160").replace("Сцена 2. ", ""),
  product: source("p161").replace("Целевой продукт: ", ""),
  intro: ({ parcel }) => {
    const gift = parcelNames[parcel];
    return [
      source("p175"),
      source("p177")
        .replace("(название подарка)", gift.accusative)
        .replace("он(а)", gift.pronoun)
        .replace("доехал(а)", gift.arrived),
    ];
  },
  options: ({ parcel, recipient }) =>
    outcomes[parcel].map(
      ([paragraphs, scores, [energy, empathy, efficiency]], index) => ({
        id: index === 4 ? "auto" : `place-${index + 1}`,
        label: source(`p${labels[index]}`),
        accessibleDescription: accessibleDescriptions[index],
        result: paragraphs.map((id) =>
          source(`p${id}`).replace(
            "(персонаж)",
            recipientNames[recipient].nominative,
          ),
        ),
        score: { energy, empathy, efficiency },
        sourceIds: [labels[index], ...paragraphs, ...scores].map(
          (id) => `p${id}`,
        ),
      }),
    ),
  Art: CompactArt,
};
