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
  it.each(["boat", "camera", "socks"] as const)("previews the automatic placement for %s with the same camera as its manual place", parcel => {
    const host = (id: string) => {
      const element = document.createElement("div");
      element.innerHTML = renderToStaticMarkup(<CompactArt context={{ ...context, parcel }} selectedId={id} showResult={false} onSelect={() => {}} />);
      return element.querySelector<HTMLElement>("figure")!;
    };
    const auto = host("auto");
    const manual = host(parcel === "boat" ? "place-4" : "place-3");
    expect(auto.hasAttribute("data-inspection-camera")).toBe(true);
    expect(auto.style.getPropertyValue("--inspection-scale")).toBe(manual.style.getPropertyValue("--inspection-scale"));
    expect(auto.style.getPropertyValue("--inspection-center")).toBe(manual.style.getPropertyValue("--inspection-center"));
  });
  it("does not expose numbered choices before choosing is available", () => {
    expect(render().querySelectorAll("button[data-hotspot]")).toHaveLength(0);
    expect(render(undefined, true).querySelectorAll("button[data-hotspot]")).toHaveLength(4);
  });
  it.each(["place-1", "place-2", "place-3", "place-4"])("keeps the overview artwork and coordinate canvas while inspecting %s", id => {
    const overview = render(undefined, true);
    const inspection = render(id, true);
    expect(inspection.querySelector("image")?.getAttribute("href")).toBe(overview.querySelector("image")?.getAttribute("href"));
    expect(inspection.querySelector("svg")?.getAttribute("viewBox")).toBe(overview.querySelector("svg")?.getAttribute("viewBox"));
    const stage = inspection.querySelector<HTMLElement>("figure")!;
    expect(stage.hasAttribute("data-inspection-camera")).toBe(true);
    const scale = Number(stage.style.getPropertyValue("--inspection-scale"));
    const center = Number(stage.style.getPropertyValue("--inspection-center"));
    const left = center - 520 / scale;
    const right = center + 520 / scale;
    expect(right).toBeGreaterThanOrEqual(1040);
    expect(left).toBeLessThanOrEqual(Number(inspection.querySelector(`[data-loading-zone="${id}"]`)?.getAttribute("x")));
  });
});
