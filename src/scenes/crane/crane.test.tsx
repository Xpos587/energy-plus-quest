import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph as source } from "../../game/scenarioDocument";
import type { SceneArtProps, SceneContext } from "../types";
import { craneScene } from "./index";
import { craneArtwork, craneCaptions, craneWorld } from "./artwork";
import { craneBeat, craneDuration } from "./consequence";
import { camera } from "./CraneArt";

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
  it("makes the three actors the tap targets, each with a numbered pin naming Ivan and Petr", () => {
    const html = renderToStaticMarkup(
      <craneScene.Art context={context} showResult={false} onSelect={() => {}} />,
    );
    expect(html.match(/data-hotspot=/g)).toHaveLength(3);
    expect(html).not.toContain("data-barge-label");
    // Owner 19.11: who is Ivan, who is Petr, where to tap — a pin inside each tap target.
    expect(html.match(/data-quay-pin=/g)).toHaveLength(3);
    // Call 21.11: numbers only on the map, as the warehouse; names wait for the card.
    expect(html).toMatch(/data-hotspot="remote"[^>]*>.*?data-quay-pin="remote".*?>1</);
    expect(html).toMatch(/data-hotspot="rush"[^>]*>.*?data-quay-pin="rush".*?>2</);
    expect(html).toMatch(/data-hotspot="petr"[^>]*>.*?data-quay-pin="petr".*?>3</);
    for (const word of ["С пульта<", "Пешком<", "Пётр<"]) expect(html).not.toContain(word);
    expect(html).not.toContain("·");
    // Owner 20.11: the cut-out ladder read as macaroni; the plate's painted ladder stays alone.
    expect(html).not.toContain('data-layer="ladder"');
    for (const id of ["remote", "rush", "petr"])
      expect(html).toContain(`data-hotspot="${id}"`);
    expect(html).toMatch(/scene-art\/barge-v7\/desk\/plate\.webp/);
    for (const caption of Object.values(craneCaptions)) expect(html).toContain(`aria-label="${caption}:`);
    expect(html).not.toContain("Баржа готова к отходу");
    expect(html).not.toContain(">Подарок<");
    expect(html.match(/data-barge-ripple=/g)).toHaveLength(3);
    // Grisha 09.11: the pulse is one ring size, drawn on the actor the finger actually hits.
    const format = html.match(/barge-v7\/(desk)\/plate/)![1] as keyof typeof craneArtwork;
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
  it("draws the selection rings only while a choice is clickable", () => {
    const rings = (props: Partial<SceneArtProps>) =>
      renderToStaticMarkup(<craneScene.Art context={context} showResult={false} {...props} />).match(/data-barge-ripple=/g)?.length ?? 0;
    expect(rings({ onSelect: () => {} })).toBe(3);
    expect(rings({})).toBe(0);
    expect(rings({ onSelect: () => {}, showResult: true, selectedId: "rush" })).toBe(0);
    expect(rings({ onSelect: () => {}, playing: "rush" })).toBe(0);
    expect(rings({ onSelect: () => {}, selectedId: "rush" })).toBe(0);
  });
  it("anchors reaction bubbles over Ivan at the office or over the loading crane cab", () => {
    expect(craneBeat("rush", craneDuration("rush")).emote).toEqual({ kind: "tired", at: "cab" });
    expect(craneBeat("petr", craneDuration("petr")).emote).toEqual({ kind: "sad", at: "cab" });
    for (const [name, art] of Object.entries(craneArtwork)) {
      const [x, y] = art.emote.office;
      const ivan = art.sprites.ivan;
      expect(x, name).toBeGreaterThanOrEqual(ivan.x);
      expect(x, name).toBeLessThanOrEqual(ivan.x + ivan.w);
      expect(Math.abs(y - ivan.y), name).toBeLessThanOrEqual(4);
      const [cx, cy] = art.emote.cab;
      expect(Math.abs(cx - art.anchors.nearCabin[0]), name).toBeLessThan(1);
      expect(cy, name).toBeLessThan(art.anchors.nearCabin[1]);
    }
  });
  it.each([["rush", "ivan"], ["petr", "far"]] as const)("%s: the walker goes to the ladder, climbs and sits in the cab", (id, walker) => {
    expect(craneBeat(id, 0)).toMatchObject({ walker, walk: 0 });
    const walkMs = id === "rush" ? 2600 : 1500;
    expect(craneBeat(id, walkMs / 2).walk).toBeCloseTo(0.5, 1);
    expect(craneBeat(id, walkMs + 550)).toMatchObject({ walker, walk: 1, lifted: false });
    expect(craneBeat(id, walkMs + 550).climb).toBeCloseTo(0.5, 1);
    expect(craneBeat(id, craneDuration(id))).toMatchObject({ walker, walk: 1, climb: 1 });
  });
  it("remote: Ivan walks into the ПРУ door, then the radio link comes up; no bubble over the empty office", () => {
    expect(craneBeat("remote", 0)).toMatchObject({ walker: "ivan", route: "office", walk: 0, office: "empty" });
    expect(craneBeat("remote", 999).signal).toBeUndefined();
    expect(craneBeat("remote", 1200)).toMatchObject({ signal: true, office: "empty" });
    expect(craneBeat("remote", 1200).walker).toBeUndefined();
    for (let ms = 0; ms <= craneDuration("remote"); ms += 50) expect(craneBeat("remote", ms).emote).toBeUndefined();
  });
  it.each(["remote", "rush", "petr"])("%s: the cable hangs plumb under the boom tip of the drawn slew frame", (id) => {
    for (let ms = 0; ms <= craneDuration(id); ms += 20) {
      const { hook, frame } = craneBeat(id, ms);
      if (!hook) continue;
      const tip = craneWorld.tips[frame];
      expect(Math.hypot(hook[0] - tip[0], hook[1] - tip[1]), `${id} @${ms}ms`).toBeLessThan(1e-9);
    }
  });
  it("paints Petr out of the plate and draws his step cycle with one lane mask while he walks", () => {
    const html = renderToStaticMarkup(<craneScene.Art context={context} showResult={false} playing="petr" />);
    expect(html).toMatch(/data-layer="post".*data-layer="far"[^>]*data-walking.*walkPetrEast\.webp.*data-layer="walkOccluderPetr"/);
    expect(html.match(/data-layer="(walkOccluder\w*|turnOccluder\w+|climbOccluder)"/g)).toHaveLength(1);
  });
  it("camera always covers the stage, never exposing the background", () => {
    for (let width = 320; width <= 2560; width += 10)
      for (let height = 400; height <= 1600; height += 10) {
        const view = camera({ width, height });
        expect(view.left, `${width}x${height}`).toBeLessThanOrEqual(1e-6);
        expect(view.top, `${width}x${height}`).toBeLessThanOrEqual(1e-6);
        expect(view.left + view.width, `${width}x${height}`).toBeGreaterThanOrEqual(width - 1e-6);
        expect(view.top + view.height, `${width}x${height}`).toBeGreaterThanOrEqual(height - 1e-6);
      }
  });
  it("pin 2 (rush) marks the barge crane cab, not its ladder", () => {
    for (const [name, art] of Object.entries(craneArtwork)) {
      const t = art.targets.rush;
      const [cx, cy] = art.anchors.nearCabin;
      expect(Math.abs(t.x + t.w / 2 - cx), name).toBeLessThan(1);
      expect(Math.abs(t.y + t.h / 2 - cy), name).toBeLessThan(1);
      // The ladder foot stays outside the box: the pin no longer points into the ladder and legs.
      expect(t.y + t.h, name).toBeLessThan(art.anchors.ladderFoot[1]);
    }
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
