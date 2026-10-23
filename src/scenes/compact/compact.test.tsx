import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { ParcelId } from "../../game/types";
import { parcelNames, recipientNames } from "../names";
import { scenarioParagraph } from "../../game/scenarioDocument";
import type { SceneContext } from "../types";
import { compactScene } from "./index";

const labels = ["31D20510", "046AB51D", "50E6D7F5", "490391EF", "381A07B3"];
const ids = ["place-1", "place-2", "place-3", "place-4", "auto"];
const cases = {
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
} as const;
const context = (parcel: ParcelId): SceneContext => ({
  parcel,
  recipient: "alva",
  profile: "student",
});

describe("compactScene source contract", () => {
  it("exports the scene metadata from source, without staging prefixes", () => {
    expect(compactScene.id).toBe("compact");
    expect(compactScene.number).toBe(2);
    expect(compactScene.title).toBe(scenarioParagraph("1599ECBA", "structure").replace("Сцена 2. ", ""));
    expect(compactScene.product).toBe(
      scenarioParagraph("4D1B5677", "structure").replace("Целевой продукт: ", ""),
    );
  });
  for (const parcel of Object.keys(cases) as ParcelId[]) {
    it(`${parcel}: preserves full intro and inflects only explicit placeholders`, () => {
      const name = parcelNames[parcel];
      expect(compactScene.intro(context(parcel))).toEqual([
        scenarioParagraph("543B4FB4"),
        scenarioParagraph("4027C712")
          .replace("(название подарка)", name.accusative)
          .replace("он(а)", name.pronoun)
          .replace("доехал(а)", name.arrived),
      ]);
    });
    cases[parcel].forEach(([paragraphs, scores, values], index) => {
      it(`${parcel} / ${ids[index]}: exact paragraphs, score and provenance`, () => {
        const option = compactScene.options(context(parcel))[index];
        expect(option.id).toBe(ids[index]);
        expect(option.label).toBe(scenarioParagraph(labels[index], "structure"));
        expect(option.result).toEqual(
          paragraphs.map((p) => scenarioParagraph(p).replace("(персонаж)", "Майма")),
        );
        expect(option.score).toEqual({
          energy: values[0],
          empathy: values[1],
          efficiency: values[2],
        });
        expect(
          scores.map((p) => Number(scenarioParagraph(p, "scores").match(/[+-]?\d+/)?.[0])),
        ).toEqual(values);
        expect(option.sourceIds).toEqual(
          [labels[index], ...paragraphs, ...scores],
        );
      });
    });
  }
  it("resolves every recipient in nominative and does not branch on profile", () => {
    for (const recipient of ["alva", "khor", "arseniy"] as const) {
      const ctx = { ...context("socks"), recipient };
      expect(compactScene.options(ctx)[2].result).toEqual([
        scenarioParagraph("5763185A").replace(
          "(персонаж)",
          recipientNames[recipient].nominative,
        ),
      ]);
      expect(compactScene.options({ ...ctx, profile: "professional" })).toEqual(
        compactScene.options(ctx),
      );
    }
  });
});

describe("Compact flat sector artwork", () => {
  const Art = compactScene.Art;
  it("uses a side-on cargo bay with four sectors and no synthetic gifts", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <Art
        context={context("camera")}
        showResult={false}
        onSelect={() => {}}
      />,
    );
    expect(host.querySelector('[data-cargo-view="side-2d"]')).not.toBeNull();
    expect(host.querySelectorAll("[data-loading-zone]")).toHaveLength(4);
    expect(host.querySelector("[data-placed-parcel]")).toBeNull();
    expect(host.querySelector('[aria-pressed="true"]')).toBeNull();
  });
  for (const parcel of ["camera", "socks", "boat"] as const) {
    it(`${parcel}: preserves automatic result and locks sectors`, () => {
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(
        <Art context={context(parcel)} selectedId="auto" showResult />,
      );
      expect(
        host
          .querySelector('[aria-pressed="true"]')
          ?.getAttribute("data-hotspot"),
      ).toBe(parcel === "boat" ? "place-4" : "place-3");
      expect(host.querySelectorAll('[aria-disabled="true"]')).toHaveLength(4);
    });
  }
  it("selects by sector without committing hover, and prevents result changes", async () => {
    const host = document.createElement("div");
    const root = createRoot(host);
    const selected: string[] = [];
    Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
    const render = async (showResult = false) =>
      act(async () =>
        root.render(
          <Art
            context={context("camera")}
            showResult={showResult}
            onSelect={(id) => selected.push(id)}
          />,
        ),
      );
    await render();
    const sector = () =>
      host.querySelector<HTMLButtonElement>('[data-hotspot="place-1"]')!;
    await act(async () =>
      sector().dispatchEvent(new MouseEvent("mouseover", { bubbles: true })),
    );
    expect(selected).toEqual([]);
    await act(async () => sector().click());
    expect(selected).toEqual(["place-1"]);
    await render(true);
    await act(async () => sector().click());
    expect(selected).toEqual(["place-1"]);
    await act(async () => root.unmount());
  });
});

it("shows full Compact result text without decorative consequence thumbnails", async () => {
  const { ScenesGame } = await import("../ScenesGame");
  const host = document.createElement("div");
  const root = createRoot(host);
  Object.assign(globalThis, { IS_REACT_ACT_ENVIRONMENT: true });
  const diagrams = {
    socks: ["scatter", "secured-space", "compact", "unused-space", "compact"],
    camera: [
      "dishes",
      "secured-space",
      "unload-three",
      "unused-space",
      "compact",
    ],
    boat: ["axle", "dishes", "no-fit", "reload-upright", "upright"],
  };
  const click = async (selector: string) => {
    const button = host.querySelector<HTMLButtonElement>(selector);
    if (!button) throw new Error(`Missing ${selector}`);
    await act(async () => button.click());
  };
  try {
    for (const parcel of Object.keys(diagrams) as ParcelId[]) {
      await act(async () =>
        root.render(<ScenesGame key={parcel} context={context(parcel)} />),
      );
      for (const [index, id] of ids.entries()) {
        expect(host.querySelector("[data-compact-consequence]")).toBeNull();
        const proceed = [...host.querySelectorAll("button")].find((b) => b.textContent === "К выбору");
        if (proceed) await act(async () => proceed.click());
        await click(`[data-scene-choice="${id}"]`);
        expect(host.querySelector("[data-compact-consequence]")).toBeNull();
        expect(host.querySelector("[data-choice-inspection]")).toBeNull();
        const option = compactScene.options(context(parcel))[index];
        const readPages: string[] = [];
        for (let page = 0; page < 30; page++) {
          readPages.push(host.querySelector('[data-testid="result-copy"]')?.textContent ?? "");
          const nextPage = host.querySelector<HTMLButtonElement>('[data-result-reader] button[aria-label="Читать дальше"]');
          if (!nextPage) break;
          await act(async () => nextPage.click());
        }
        expect(readPages.join(" ").replace(/\s+/g, " ").trim()).toBe(option.result.join(" ").replace(/\s+/g, " ").trim());
        expect(host.querySelector("[data-compact-consequence]")).toBeNull();
        for (let page = 0; page < 30; page++) {
          const previousPage = host.querySelector<HTMLButtonElement>('[data-result-reader] button[aria-label="Назад по рассказу"]');
          if (!previousPage) break;
          await act(async () => previousPage.click());
        }
        const revise = [...host.querySelectorAll("button")].find(
          (b) => b.textContent === "Изменить выбор",
        );
        if (!revise) throw new Error("Missing revision action");
        await act(async () => revise.click());
      }
    }
    await act(async () =>
      root.render(<ScenesGame startAt="inventory" context={context("boat")} />),
    );
    const proceed = [...host.querySelectorAll("button")].find((b) => b.textContent === "К выбору");
    if (proceed) await act(async () => proceed.click());
    await click('[data-scene-choice="wms"]');
    expect(host.querySelector("[data-choice-inspection]")).toBeNull();
    expect(host.querySelector("[data-compact-consequence]")).toBeNull();
  } finally {
    await act(async () => root.unmount());
  }
});
