import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames } from "../names";
import { source } from "../source";
import type { SceneContext } from "../types";
import { inventoryScene } from "./index";

const branches = [
  ["entrance", "p355", ["p356"], "p359", [-2, -1, 0]],
  ["alphabet", "p361", ["p363"], "p365", [-3, 0, -1]],
  ["keeper", "p367", ["p369", "p371"], "p373", [1, 4, -3]],
  ["wms", "p375", ["p377", "p379"], "p381", [4, 4, 5]],
] as const;
describe("inventoryScene", () => {
  for (const parcel of ["camera", "socks", "boat"] as const) {
    const context: SceneContext = {
      parcel,
      recipient: "alva",
      profile: "student",
    };
    const names = parcelNames[parcel];
    const resolve = (text: string) =>
      text
        .replaceAll("(сюрприза)", names.genitive)
        .replaceAll("(сюрприз)", names.accusative)
        .replaceAll("(подарок)", names.accusative)
        .replaceAll("(подарке)", names.prepositional)
        .replaceAll("(подарка)", names.genitive)
        .replace(
          "в середине/в конце (в зависимости от первой буквы слова названия подарка – Н, Л, Ф)",
          parcel === "camera" ? "в конце" : "в середине",
        );
    it(`${parcel}: exact introduction`, () =>
      expect(inventoryScene.intro(context)).toEqual([source("p354")]));
    for (const [id, label, results, scoreId, scores] of branches) {
      it(`${parcel}: ${id} exact copy, provenance, score and art`, () => {
        const option = inventoryScene.options(context).find((o) => o.id === id);
        if (!option) throw new Error(`Missing warehouse option: ${id}`);
        expect(option.label).toBe(resolve(source(label)));
        expect(option.result).toEqual(results.map((p) => resolve(source(p))));
        expect(option.sourceIds).toEqual([label, ...results, scoreId]);
        expect(option.score).toEqual({
          energy: scores[0],
          empathy: scores[1],
          efficiency: scores[2],
        });
        expect(JSON.stringify(option)).not.toMatch(
          /\(сюрприз|\(подар|в зависимости/,
        );
        const markup = renderToStaticMarkup(
          <inventoryScene.Art context={context} selectedId={id} showResult />,
        );
        expect(markup).toContain(`data-outcome="${id}"`);
        expect(markup).toContain('aria-pressed="true"');
        expect(markup).toContain("/scene-art/inventory.png");
        expect(markup).not.toContain("href=");
        expect(markup).not.toContain("data-warehouse-motion");
      });
    }
    it(`${parcel}: no answer exposed before result`, () => {
      const markup = renderToStaticMarkup(
        <inventoryScene.Art
          context={context}
          showResult={false}
          onSelect={() => {}}
        />,
      );
      expect(markup.match(/<button/g)).toHaveLength(4);
      expect(markup).not.toContain("data-route");
      expect(markup).not.toContain("data-outcome");
      expect(markup).toContain("<img");
    });
  }
});

it("native spatial buttons select every strategy and lock after result", async () => {
  const { createRoot } = await import("react-dom/client");
  const { act } = await import("react");
  const element = document.createElement("div");
  const root = createRoot(element);
  const selections: string[] = [];
  const context: SceneContext = {
    parcel: "boat",
    recipient: "alva",
    profile: "student",
  };
  (
    globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
  ).IS_REACT_ACT_ENVIRONMENT = true;
  try {
    await act(async () =>
      root.render(
        <inventoryScene.Art
          context={context}
          showResult={false}
          selectedId="alphabet"
          onSelect={(id) => selections.push(id)}
        />,
      ),
    );
    const buttons = element.querySelectorAll("button");
    expect(buttons[1].getAttribute("aria-pressed")).toBe("true");
    for (const button of buttons) {
      expect(button.getAttribute("aria-label")).toBeTruthy();
      await act(async () => button.click());
    }
    expect(selections).toEqual(["entrance", "alphabet", "keeper", "wms"]);
    await act(async () =>
      root.render(
        <inventoryScene.Art
          context={context}
          showResult
          selectedId="keeper"
          onSelect={(id) => selections.push(id)}
        />,
      ),
    );
    expect(element.querySelectorAll("button:disabled")).toHaveLength(4);
    expect(
      element
        .querySelector('[aria-pressed="true"]')
        ?.getAttribute("data-hotspot"),
    ).toBe("keeper");
  } finally {
    await act(async () => root.unmount());
    (
      globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
    ).IS_REACT_ACT_ENVIRONMENT = false;
  }
});

it("keeps strategy numbers tied to choice IDs, not projection order", async () => {
  const manifest = (await import("../worldManifest.json")).default;
  const view = manifest.scenes.inventory.desktop;
  const original = view.hotspots;
  try {
    view.hotspots = [...original].reverse();
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <inventoryScene.Art
        context={{ parcel: "camera", recipient: "alva", profile: "student" }}
        selectedId="keeper"
        showResult={false}
      />,
    );
    branches.forEach(([id], index) => {
      const marker = host.querySelector(`[data-hotspot="${id}"]`);
      expect(marker?.textContent).toBe(String(index + 1));
      const point = view.hotspots.find((point) => point.id === id);
      expect(marker?.getAttribute("style")).toContain(
        `left:${(point?.x ?? 0) * 100}%`,
      );
    });
  } finally {
    view.hotspots = original;
  }
});
