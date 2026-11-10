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
  it.each(["place-3", "auto"])("keeps the socks result badge clear of the box for %s without moving its hit zone", selectedId => {
    const draw = (parcel: "socks" | "camera", showResult: boolean) => {
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(<CompactArt context={{ ...context, parcel }} selectedId={selectedId} showResult={showResult} onSelect={() => {}} />);
      return host;
    };
    const result = draw("socks", true);
    const camera = draw("camera", true);
    const badge = (host: HTMLElement) => host.querySelector<HTMLElement>('[data-layout-badge="place-3"]')!;
    expect(badge(result).style.transform).toBe("translateX(calc(-100% - 8px))");
    expect(badge(draw("socks", false)).style.transform).toBe("");
    expect(badge(camera).style.transform).toBe("");
    expect(result.querySelector('[data-hotspot="place-3"]')?.getAttribute("style"))
      .toBe(camera.querySelector('[data-hotspot="place-3"]')?.getAttribute("style"));
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
