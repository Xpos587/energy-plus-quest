import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { scenarioParagraph } from "../../game/scenarioDocument";
import { SceneOutcomeArt } from "../SceneOutcomeArt";
import { warehouseCallouts } from "./callouts";
import { inventoryScene } from "./index";

const expectations = [
  ["camera", "Ф", "в конце"],
  ["socks", "Н", "в середине"],
  ["boat", "Л", "в середине"],
] as const;

describe("warehouse alphabet follows gift names and starts at dispatch", () => {
  for (const [parcel, letter, position] of expectations) {
    it(`${parcel}: matching location, result text and consequence illustration`, () => {
      const context = {
        parcel,
        recipient: "alva",
        profile: "student",
      } as const;
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(
        <inventoryScene.Art
          context={context}
          showResult={false}
          onSelect={() => {}}
        />,
      );
      const marker = host.querySelector<HTMLElement>(
        '[data-hotspot="alphabet"]',
      )!;
      expect(parseFloat(marker.style.left)).toBeCloseTo(warehouseCallouts(parcel).alphabet.x * 100);
      expect(parseFloat(marker.style.top)).toBeCloseTo(warehouseCallouts(parcel).alphabet.y * 100);
      expect(marker.textContent).toBe("2");
      expect(marker.getAttribute("aria-label")).toContain("по алфавиту");
      expect(marker.getAttribute("aria-label")).toContain("по алфавиту");
      for (const [id, point] of Object.entries(warehouseCallouts(parcel)).filter(([id]) => id !== "alphabet")) {
        const unchanged = host.querySelector<HTMLElement>(
          `[data-hotspot="${id}"]`,
        )!;
        expect(parseFloat(unchanged.style.left)).toBeCloseTo(point.x * 100);
        expect(parseFloat(unchanged.style.top)).toBeCloseTo(point.y * 100);
      }
      const option = inventoryScene
        .options(context)
        .find((option) => option.id === "alphabet")!;
      expect(option.result).toEqual([scenarioParagraph("01E19BE1")]);
      expect(option.score).toEqual({ energy: -3, empathy: 0, efficiency: -1 });
      host.innerHTML = renderToStaticMarkup(
        <SceneOutcomeArt
          scene="inventory"
          selectedId="alphabet"
          context={context}
        />,
      );
      expect(host.querySelector("img")?.getAttribute("src")).toBe(
        "/scene-art/warehouse-polish-2026-10-17/alphabet.webp",
      );
      expect(host.querySelector("img")?.alt).toContain("закрытой коробке");
      expect(host.querySelector("img")?.alt).not.toContain(`буквой ${letter}`);
    });
  }
});
