import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { parcelNames } from "../names";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { sceneChoiceImage } from "../artwork";
import type { SceneContext } from "../types";
import { inventoryAlphabet } from "./alphabet";
import { warehouseCallouts } from "./callouts";
import { inventoryScene } from "./index";

const branches = [
  ["entrance", "4FCD4F75", ["126E10DA"], "24A59A28", [-2, -1, 0]],
  ["alphabet", "26CAA917", ["01E19BE1"], "0DDE5C3A", [-3, 0, -1]],
  ["keeper", "50B1777D", ["4341C888-text", "7CABB462"], "3B214E47", [1, 4, -3]],
  ["wms", "277603D2", ["7DC9A705", "757D6707"], "385D8024", [4, 4, 5]],
] as const;
describe("inventoryScene", () => {
  it("uses the canonical structure blocks for the scene and product names", () => {
    expect(inventoryScene.title).toBe(scenarioParagraph("4A260F2F", "structure").replace("Сцена 3. ", ""));
    expect(inventoryScene.product).toBe(scenarioParagraph("312158D0", "structure").replace("Целевой продукт: ", ""));
  });
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
      expect(inventoryScene.intro(context)).toEqual([scenarioParagraph("769F13F3")]));
    for (const [id, label, results, scoreId, scores] of branches) {
      it(`${parcel}: ${id} exact copy, provenance, score and art`, () => {
        const option = inventoryScene.options(context).find((o) => o.id === id);
        if (!option) throw new Error(`Missing warehouse option: ${id}`);
        expect(option.label).toBe(resolve(scenarioParagraph(label)));
        expect(option.result).toEqual(results.map((p) => resolve(scenarioParagraph(p))));
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
        expect(markup).not.toContain('data-hotspot=');
        expect(markup).toContain(sceneChoiceImage("inventory"));
        expect(markup).not.toContain("<a ");
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
      expect(markup.match(/data-hotspot=/g)).toHaveLength(4);
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
          onSelect={(id) => selections.push(id)}
        />,
      ),
    );
    const buttons = element.querySelectorAll<HTMLButtonElement>(
      "button[data-hotspot]",
    );
    expect(buttons[1].getAttribute("aria-pressed")).toBe("false");
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
    expect(element.querySelectorAll("button[data-hotspot]")).toHaveLength(0);
    expect(element.querySelector("[data-warehouse-leader]")).toBeNull();
  } finally {
    await act(async () => root.unmount());
    (
      globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }
    ).IS_REACT_ACT_ENVIRONMENT = false;
  }
});

it("keeps numbered object markers tied to choice IDs, not projection order", async () => {
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
        onSelect={() => {}}
      />,
    );
    expect(host.querySelector('[data-navigation="fixed"]')).not.toBeNull();
    expect(host.querySelector('[data-map-viewport], [data-callout-target]')).toBeNull();
    expect(host.querySelector('[data-warehouse-leader], polyline')).toBeNull();
    branches.forEach(([id], index) => {
      const marker = host.querySelector<HTMLButtonElement>(`[data-hotspot="${id}"]`)!;
      expect(marker.textContent).toBe(String(index + 1));
      expect(marker.getAttribute("data-choice-id")).toBe(id);
      expect(marker.getAttribute("aria-label")).toContain(`Вариант ${index + 1}`);
      const point = warehouseCallouts("camera")[id];
      expect(parseFloat(marker.style.left)).toBeCloseTo(point.x * 100);
      expect(parseFloat(marker.style.top)).toBeCloseTo(point.y * 100);
    });
  } finally {
    view.hotspots = original;
  }
});
