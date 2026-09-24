import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneContext } from "../types";
import { craneScene } from "./index";

const context: SceneContext = {
  parcel: "camera",
  recipient: "alva",
  profile: "student",
};
const cases = [
  ["rush", "p440", ["p444"], "p446", [-4, -3, 3]],
  ["wait", "p452", ["p454", "p456"], "p458", [0, 3, -4]],
  ["petr", "p465", ["p467", "p469"], "p473", [-2, 4, -3]],
  [
    "remote",
    "p475",
    ["p477", "p479", "p481", "p485", "p487"],
    "p491",
    [4, 4, 5],
  ],
] as const;

describe("craneScene source contract", () => {
  it("preserves all four intro paragraphs, including duplicate facts", () => {
    expect(craneScene.intro(context)).toEqual(
      ["p429", "p431", "p433", "p435"].map((id) =>
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
                .replace("(персонажу)", recipientNames[recipient].dative),
            ),
          );
        });
        expect(craneScene.intro({ ...context, parcel, recipient })[0]).toBe(
          source("p429").replace(
            "(название сюрприза)",
            parcelNames[parcel].nominative,
          ),
        );
      });
    }
  }
  it("renders the quay without duplicating the shell's choice controls", () => {
    const html = renderToStaticMarkup(
      <craneScene.Art
        context={context}
        showResult={false}
        selectedId="remote"
        onSelect={() => {}}
      />,
    );
    expect(html).not.toContain("<button");
    expect(html).toContain("/scene-art/crane.png");
    expect(html).toContain('data-selected="remote"');
    expect(html).toContain('data-gift="camera"');
    expect(html).toContain("<img");
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
