import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph as source } from "../../game/scenarioDocument";
import type { SceneContext } from "../types";
import { craneScene } from "./index";
import { craneArtwork, craneCaptions } from "./artwork";

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
  it("makes the three actors the tap targets, with no numbers, captions or chips", () => {
    const html = renderToStaticMarkup(
      <craneScene.Art context={context} showResult={false} onSelect={() => {}} />,
    );
    expect(html.match(/data-hotspot=/g)).toHaveLength(3);
    for (const id of ["remote", "rush", "petr"])
      expect(html).toContain(`data-hotspot="${id}"`);
    expect(html).toMatch(/scene-art\/barge-v4\/(mid|desk|wide|tall)\/plate\.webp/);
    for (const caption of Object.values(craneCaptions)) expect(html).toContain(`aria-label="${caption}:`);
    expect(html).not.toContain("Баржа готова к отходу");
    expect(html).not.toContain(">Подарок<");
    expect(html.match(/data-barge-ripple=/g)).toHaveLength(3);
    // Grisha 09.11: the pulse is one ring size, drawn on the actor the finger actually hits.
    const format = html.match(/barge-v4\/(mid|desk|wide|tall)\/plate/)![1] as keyof typeof craneArtwork;
    const art = craneArtwork[format];
    const radii = new Set<number>();
    for (const id of ["remote", "rush", "petr"]) {
      const ring = html.match(new RegExp(`data-barge-ripple="${id}" cx="([\\d.]+)" cy="([\\d.]+)" r="([\\d.]+)"`))!;
      expect(ring, id).not.toBeNull();
      const target = art.targets[id];
      expect(Math.abs(Number(ring[1]) - (target.x + target.w / 2))).toBeLessThan(1);
      expect(Math.abs(Number(ring[2]) - (target.y + target.h / 2))).toBeLessThan(1);
      radii.add(Math.round(Number(ring[3]) * 100));
    }
    expect(radii.size).toBe(1);
    expect(html).not.toContain("disabled");
  });
  it("locks the pins once a result is shown", () => {
    const html = renderToStaticMarkup(
      <craneScene.Art context={context} selectedId="petr" showResult />,
    );
    expect(html).toContain('data-selected="petr"');
    expect(html.match(/disabled=""/g)).toHaveLength(3);
  });
  it("keeps every tap target inside its drawing", () => {
    for (const art of Object.values(craneArtwork))
      for (const t of Object.values(art.targets)) {
        expect(t.x).toBeGreaterThanOrEqual(0);
        expect(t.x + t.w).toBeLessThanOrEqual(art.width);
        expect(t.y).toBeGreaterThanOrEqual(-1);
        expect(t.y + t.h).toBeLessThanOrEqual(art.height);
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
