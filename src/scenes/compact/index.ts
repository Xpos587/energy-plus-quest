import type { ParcelId } from "../../game/types";
import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph } from "../../game/scenarioDocument";
import type { SceneDefinition } from "../types";
import { CompactArt } from "./CompactArt";

// Canonical block IDs preserve the document's role boundaries and provenance.
const outcomes: Record<ParcelId, readonly (readonly [readonly string[], readonly string[], readonly [number, number, number]])[]> = {
  socks: [
    [["16DAA849"], ["2FB0A4C8", "26AE4BE6", "07A275B9"], [0, -4, -1]],
    [["0366EE7A"], ["1ED770F9", "4A15D234", "422DF540"], [3, 3, 1]],
    [["5763185A"], ["5BAC2CE4", "77431D49", "64C78063"], [2, 2, 4]],
    [["576D051B"], ["0C69C3EA", "508D9916", "6336B9DB"], [-3, -3, -3]],
    [["1902BCFF"], ["7C0CBD33", "0FC34C29", "524D7378"], [2, 3, 4]],
  ],
  camera: [
    [["439C34AA"], ["5AEF4B53", "29298F70", "3A707ED3"], [-1, 0, -3]],
    [["41C1FFD6"], ["4A808C42", "40919FCF", "2DACAE41"], [2, 0, 1]],
    [["4A2E0642"], ["62B2FDA6", "07B9A3D2", "77CE72F2"], [2, 1, 3]],
    [["56E43720"], ["0C2399CD", "4CCFF269", "60939509"], [-3, -1, -3]],
    [["638A81E0"], ["53ACFC62", "2E5B1179", "76BA0893"], [1, 1, 4]],
  ],
  boat: [
    [["1A23B1CD"], ["5D1E5655", "6FE2E3A0", "6E436EC7"], [-2, 4, -5]],
    [["4E1FC015"], ["3318C9E2", "5905BE4A", "4C61F8E5"], [-3, -3, -4]],
    [["5570254C"], ["08525834", "5A0E68A7", "75D1BD7C"], [-4, -5, -5]],
    [["6083A47F"], ["354A961F", "096DF204", "59EA3342"], [-3, 3, 4]],
    [["0982F968"], ["720FF093", "688D2818", "0A4801C1"], [-4, 3, 5]],
  ],
};
const labels = ["31D20510", "046AB51D", "50E6D7F5", "490391EF", "381A07B3"];
const accessibleDescriptions = [
  "Над тяжёлыми ящиками у задних дверей, над колёсами. Свободное место без креплений.",
  "Над ящиком с хрупкой посудой, укрытым мягким материалом. Есть красные стропы.",
  "Небольшая ниша между посылками, за тремя коробками. Есть короткая стропа.",
  "Высокое место у передней стенки, за остальным грузом. Рядом подушки, на стенке красные стропы.",
  "Compact подберёт место для подарка с учётом размеров груза и свободного пространства в кузове.",
];

export const compactScene: SceneDefinition = {
  id: "compact",
  number: 2,
  title: scenarioParagraph("1599ECBA", "structure").replace("Сцена 2. ", ""),
  product: scenarioParagraph("4D1B5677", "structure").replace("Целевой продукт: ", ""),
  intro: ({ parcel }) => {
    const gift = parcelNames[parcel];
    return [
      scenarioParagraph("543B4FB4"),
      scenarioParagraph("4027C712")
        .replace("(название подарка)", gift.accusative)
        .replace("он(а)", gift.pronoun)
        .replace("доехал(а)", gift.arrived),
    ];
  },
  options: ({ parcel, recipient }) =>
    outcomes[parcel].map(
      ([paragraphs, scores, [energy, empathy, efficiency]], index) => ({
        id: index === 4 ? "auto" : `place-${index + 1}`,
        label: scenarioParagraph(labels[index], "structure"),
        accessibleDescription: accessibleDescriptions[index],
        result: paragraphs.map((id) =>
          scenarioParagraph(id).replace(
            "(персонаж)",
            recipientNames[recipient].nominative,
          ),
        ),
        score: { energy, empathy, efficiency },
        sourceIds: [labels[index], ...paragraphs, ...scores],
      }),
    ),
  Art: CompactArt,
};
