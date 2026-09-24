import { act } from "react";
import { createRoot } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import type { ParcelId } from "../../game/types";
import { parcelNames, recipientNames } from "../names";
import { source } from "../source";
import type { SceneContext } from "../types";
import { compactScene } from "./index";

const labels = [206, 229, 252, 277, 300];
const ids = ["place-1", "place-2", "place-3", "place-4", "auto"];
const cases = {
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
    expect(compactScene.title).toBe(source("p160").replace("Сцена 2. ", ""));
    expect(compactScene.product).toBe(
      source("p161").replace("Целевой продукт: ", ""),
    );
  });
  for (const parcel of Object.keys(cases) as ParcelId[]) {
    it(`${parcel}: preserves full intro and inflects only explicit placeholders`, () => {
      const name = parcelNames[parcel];
      expect(compactScene.intro(context(parcel))).toEqual([
        source("p175"),
        source("p177")
          .replace("(название подарка)", name.accusative)
          .replace("он(а)", name.pronoun)
          .replace("доехал(а)", name.arrived),
      ]);
    });
    cases[parcel].forEach(([paragraphs, scores, values], index) => {
      it(`${parcel} / ${ids[index]}: exact paragraphs, score and provenance`, () => {
        const option = compactScene.options(context(parcel))[index];
        expect(option.id).toBe(ids[index]);
        expect(option.label).toBe(source(`p${labels[index]}`));
        expect(option.result).toEqual(
          paragraphs.map((p) => source(`p${p}`).replace("(персонаж)", "Альва")),
        );
        expect(option.score).toEqual({
          energy: values[0],
          empathy: values[1],
          efficiency: values[2],
        });
        expect(
          scores.map((p) => Number(source(`p${p}`).match(/[+-]?\d+/)?.[0])),
        ).toEqual(values);
        expect(option.sourceIds).toEqual(
          [labels[index], ...paragraphs, ...scores].map((p) => `p${p}`),
        );
      });
    });
  }
  it("resolves every recipient in nominative and does not branch on profile", () => {
    for (const recipient of ["alva", "khor", "arseniy"] as const) {
      const ctx = { ...context("socks"), recipient };
      expect(compactScene.options(ctx)[2].result).toEqual([
        source("p257").replace(
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

describe("Compact approved sector artwork", () => {
  const Art = compactScene.Art;
  it("uses the approved illustration with four sectors and no synthetic gifts", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <Art
        context={context("camera")}
        showResult={false}
        onSelect={() => {}}
      />,
    );
    expect(host.querySelector("image")?.getAttribute("href")).toContain(
      "compact-art/loading-neutral-v2.png",
    );
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
          ?.getAttribute("data-loading-zone"),
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
    const sector = () => host.querySelector('[data-loading-zone="place-1"]')!;
    await act(async () =>
      sector().dispatchEvent(new MouseEvent("mouseover", { bubbles: true })),
    );
    expect(selected).toEqual([]);
    await act(async () =>
      sector().dispatchEvent(new MouseEvent("click", { bubbles: true })),
    );
    expect(selected).toEqual(["place-1"]);
    await render(true);
    await act(async () =>
      sector().dispatchEvent(new MouseEvent("click", { bubbles: true })),
    );
    expect(selected).toEqual(["place-1"]);
    await act(async () => root.unmount());
  });
});

it("shows source-backed consequence schematics only for Compact results, distinguishing automatic choices", async () => {
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
        root.render(<ScenesGame context={context(parcel)} />),
      );
      for (const [index, id] of ids.entries()) {
        expect(host.querySelector("[data-compact-consequence]")).toBeNull();
        await click(`[data-choice-id="${id}"]`);
        const figure = host.querySelector("[data-compact-consequence]");
        expect(figure?.getAttribute("data-compact-consequence")).toBe(
          `${parcel}-${id}`,
        );
        expect(figure?.querySelector("svg")?.getAttribute("data-diagram")).toBe(
          diagrams[parcel][index],
        );
        const caption = figure?.querySelector("figcaption")?.textContent;
        const sourceId = figure?.getAttribute("data-source-id");
        if (!caption || !sourceId)
          throw new Error("Missing consequence provenance");
        expect(caption.length).toBeGreaterThan(10);
        const option = compactScene.options(context(parcel))[index];
        expect(option.result.some((text) => text.includes(caption))).toBe(true);
        expect(option.sourceIds).toContain(sourceId);
        expect(source(sourceId)).toContain(caption);
        expect(
          host.querySelector('[data-testid="result-copy"]')?.textContent,
        ).toBe(option.result.join(""));
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
    await click('[data-choice-id="wms"]');
    expect(host.querySelector("[data-compact-consequence]")).toBeNull();
  } finally {
    await act(async () => root.unmount());
  }
});
