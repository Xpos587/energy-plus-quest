import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph as source } from "../../game/scenarioDocument";
import type { SceneContext } from "../types";
import { craneScene } from "./index";

const context: SceneContext = {
  parcel: "camera",
  recipient: "alva",
  profile: "student",
};
const cases = [
  [
    "remote",
    "5EDD1701",
    ["77362BA7", "5A05E1F5", "44E790DE"],
    "47D92404",
    [4, 4, 5],
  ],
  ["rush", "0023E31A", ["27629778"], "639F545D", [-4, -3, 3]],
  ["wait", "553650B7", ["14753450"], "6F64992E", [0, 3, -4]],
  ["petr", "0C6EC2FC", ["42344E38", "64BD7433"], "2B2A52A6", [-2, 4, -3]],

] as const;

describe("craneScene source contract", () => {
  it("uses the three canonical intro paragraphs with Ivan awaiting player orders", () => {
    expect(craneScene.intro(context)).toEqual(
      ["53B56B9E", "62451EC9", "6F7BE91B"].map((id) =>
        source(id).replace("(название сюрприза)", "фотоаппарат"),
      ),
    );
  });
  for (const parcel of Object.keys(
    parcelNames,
  ) as (keyof typeof parcelNames)[]) {
    for (const recipient of Object.keys(
      recipientNames,
    ) as (keyof typeof recipientNames)[]) {
      it(`preserves all options, scores and paragraphs for ${parcel}/${recipient}`, () => {
        const options = craneScene.options({ ...context, parcel, recipient });
        expect(options.map((o) => o.id)).toEqual(cases.map((c) => c[0]));
        cases.forEach(([id, label, paragraphs, scoreId, score], index) => {
          const option = options[index];
          expect(option.id).toBe(id);
          expect(option.label).toBe(source(label));
          expect(option.sourceIds).toEqual([label, ...paragraphs, scoreId]);
          expect(option.score).toEqual({
            energy: score[0],
            empathy: score[1],
            efficiency: score[2],
          });
          expect(option.result).toEqual(
            paragraphs.map((p) =>
              source(p)
                .replace("(название сюрприза)", parcelNames[parcel].genitive)
                .replace("(имя персонажа)", recipientNames[recipient].genitive)
                .replaceAll("(подарок)", parcelNames[parcel].accusative)
                .replace("(персонажу)", recipientNames[recipient].dative)
                .replace(
                  "Теперь он придет",
                  `Теперь ${parcelNames[parcel].pronoun} ${parcel === "socks" ? "придут" : "придет"}`,
                ),
            ),
          );
        });
        expect(craneScene.intro({ ...context, parcel, recipient })[0]).toBe(
          source("53B56B9E")
            .replace("(название сюрприза)", parcelNames[parcel].nominative)
            .replace(
              /^Ваш /,
              parcel === "boat"
                ? "Ваша "
                : parcel === "socks"
                  ? "Ваши "
                  : "Ваш ",
            )
            .replace(
              "— его вместе",
              `— ${parcel === "boat" ? "её" : parcel === "socks" ? "их" : "его"} вместе`,
            ),
        );
      });
    }
  }
  it("renders four direct choices on the quay", () => {
    const html = renderToStaticMarkup(
      <craneScene.Art
        context={context}
        showResult={false}
        selectedId="remote"
        onSelect={() => {}}
      />,
    );
    expect(html.match(/data-hotspot=/g)).toHaveLength(4);
    expect(html).toContain("/scene-art/barge-family-v1/choice-neutral-tall-v7.webp");
    expect(html).toContain('data-selected="remote"');
    expect(html).toContain('data-gift="camera"');
    expect(html).toContain("<img");
    for (const label of [
      "Отправить Ивана на кран",
      "Ждать 3 часа",
      "Попросить Петра",
      "Управлять из офиса",
    ])
      expect(html).toContain(label);
    expect(html).not.toContain("<a ");
  });
  for (const [id] of cases)
    it(`renders the distinct ${id} result`, () => {
      const html = renderToStaticMarkup(
        <craneScene.Art context={context} selectedId={id} showResult />,
      );
      expect(html).toContain(`data-outcome="${id}"`);
      expect(html).toContain(
        `data-gift-location="${id === "wait" ? "quay" : "barge"}"`,
      );
      expect(html).toContain("Иллюстрация");
      expect(html).toContain(`data-outcome="${id}"`);
      expect(html).not.toContain("data-world-annotation");
      expect(html).not.toContain("Результат выбора:");
      expect(html).toContain("data-selected-marker");
      expect(html).not.toContain("<button");
    });
  it("renders each gift in both quay and barge states", () => {
    for (const parcel of Object.keys(
      parcelNames,
    ) as (keyof typeof parcelNames)[]) {
      for (const showResult of [false, true]) {
        expect(
          renderToStaticMarkup(
            <craneScene.Art
              context={{ ...context, parcel }}
              selectedId="remote"
              showResult
            />,
          ),
        ).toContain(`data-gift="${parcel}"`);
        expect(
          renderToStaticMarkup(
            <craneScene.Art
              context={{ ...context, parcel }}
              selectedId="remote"
              showResult={showResult}
            />,
          ),
        ).toContain(`data-gift-location="${showResult ? "barge" : "quay"}"`);
      }
    }
  });
});

it.each([
  ["socks", "Ваши вязаные носки", "Теперь они придут", "— их вместе"],
  ["boat", "Ваша лодка", "Теперь она придет", "— её вместе"],
  ["camera", "Ваш фотоаппарат", "Теперь он придет", "— его вместе"],
] as const)(
  "agrees the parcel gender and number for %s",
  (parcel, opening, arrival, transport) => {
    const selection = { ...context, parcel };
    expect(craneScene.intro(selection)[0]).toContain(opening);
    expect(craneScene.intro(selection)[0]).toContain(transport);
    expect(
      craneScene.options(selection).find(({ id }) => id === "petr")?.result[0],
    ).toContain(arrival);
  },
);
