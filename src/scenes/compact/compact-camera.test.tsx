import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { CompactArt } from "./CompactArt";
const context = { parcel: "boat", recipient: "alva", profile: "student" } as const;
const render = (selectedId?: string, choosing = false) => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<CompactArt context={context} selectedId={selectedId} showResult={false} onSelect={choosing ? () => {} : undefined} />);
  return host;
};
describe("loading camera context", () => {
  it.each(["boat", "camera", "socks"] as const)("previews Compact for %s on the whole truck without revealing its pick", parcel => {
    const element = document.createElement("div");
    element.innerHTML = renderToStaticMarkup(<CompactArt context={{ ...context, parcel }} selectedId="auto" showResult={false} onSelect={() => {}} />);
    const auto = element.querySelector<HTMLElement>("figure")!;
    expect(auto.hasAttribute("data-inspection-camera")).toBe(true);
    expect(auto.style.getPropertyValue("--inspection-scale")).toBe("");
    expect(auto.dataset.placement).toBe("waiting");
    expect(element.querySelector('[aria-pressed="true"]')?.getAttribute("data-hotspot")).toBe("auto");
  });
  it.each([
    ["socks", "place-3", "place-3"], ["socks", "auto", "place-3"],
    ["camera", "place-3", "place-3"], ["camera", "auto", "place-3"],
    ["boat", "place-4", "place-4"], ["boat", "auto", "place-4"],
  ] as const)("keeps the %s/%s result badge clear without moving its hit zone", (parcel, selectedId, badgeId) => {
    const draw = (showResult: boolean, gift: typeof context.parcel | "camera" | "socks" = parcel) => {
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(<CompactArt context={{ ...context, parcel: gift }} selectedId={selectedId} showResult={showResult} onSelect={() => {}} />);
      return host;
    };
    const result = draw(true);
    const choice = draw(false);
    const badge = (host: HTMLElement) => host.querySelector<HTMLElement>(`[data-layout-badge="${badgeId}"]`)!;
    expect(badge(result).style.transform).toBe("translateX(calc(-100% - 8px))");
    expect(badge(choice).style.transform).toBe("");
    expect(result.querySelector('[data-layout-badge="place-2"]')?.getAttribute("style"))
      .toBe(choice.querySelector('[data-layout-badge="place-2"]')?.getAttribute("style"));
    const unchangedResult = draw(true, badgeId === "place-4" ? "camera" : "socks");
    expect(result.querySelector(`[data-hotspot="${badgeId}"]`)?.getAttribute("style"))
      .toBe(unchangedResult.querySelector(`[data-hotspot="${badgeId}"]`)?.getAttribute("style"));
    expect(result.querySelectorAll("[data-loading-zone]")).toHaveLength(0);
  });
  it("does not expose numbered choices before choosing is available", () => {
    expect(render().querySelectorAll("button[data-hotspot]")).toHaveLength(0);
    expect(render(undefined, true).querySelectorAll('button[data-hotspot^="place-"]')).toHaveLength(4);
  });
  it.each(["place-1", "place-2", "place-3", "place-4"])("keeps the overview artwork and coordinate canvas while inspecting %s", id => {
    const overview = render(undefined, true);
    const inspection = render(id, true);
    expect(inspection.querySelector("image")?.getAttribute("href")).toBe(overview.querySelector("image")?.getAttribute("href"));
    expect(inspection.querySelector("svg")?.getAttribute("viewBox")).toBe(overview.querySelector("svg")?.getAttribute("viewBox"));
    const stage = inspection.querySelector<HTMLElement>("figure")!;
    expect(stage.hasAttribute("data-inspection-camera")).toBe(true);
    // No zoom: the whole truck, cab included, stays in view.
    expect(stage.style.getPropertyValue("--inspection-scale")).toBe("");
  });
});
