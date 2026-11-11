import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { WorldArt } from "../WorldArt";
import { InventoryArt } from "./InventoryArt";
import { inventoryScene } from "./index";
import { warehouseCallouts, warehouseContour, warehouseDrawing } from "./callouts";

const context = { parcel: "boat", recipient: "alva", profile: "student" } as const;
it("points 3 at the keeper's cap and 4 at the monitor, excluding the operator", () => {
  for (const [composition, cap, monitor, operatorLeft] of [
    ["wide", { left: 1332, right: 1358, top: 580, bottom: 588 }, { left: 1286, right: 1300, top: 687, bottom: 700 }, 1400],
    ["tall", { left: 918, right: 940, top: 905, bottom: 914 }, { left: 863, right: 880, top: 1050, bottom: 1062 }, 965],
  ] as const) {
    const drawing = warehouseDrawing(composition);
    const { keeper, wms } = drawing.regions;
    for (const [region, target] of [[keeper, cap], [wms, monitor]] as const) {
      expect(region.anchorPixel[0]).toBeGreaterThanOrEqual(target.left);
      expect(region.anchorPixel[0]).toBeLessThanOrEqual(target.right);
      expect(region.anchorPixel[1]).toBeGreaterThanOrEqual(target.top);
      expect(region.anchorPixel[1]).toBeLessThanOrEqual(target.bottom);
    }
    const x = wms.path.match(/-?\d+(?:\.\d+)?/g)!.map(Number).filter((_, index) => index % 2 === 0);
    expect(Math.max(...x)).toBeLessThan(operatorLeft);
    for (const region of [keeper, wms]) {
      expect(region.anchor.x * drawing.width).toBeCloseTo(region.anchorPixel[0], 2);
      expect(region.anchor.y * drawing.height).toBeCloseTo(region.anchorPixel[1], 2);
    }
  }
});
it("keeps map numbering tied to the corresponding warehouse buttons", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<WorldArt scene="inventory" title="Склад" options={inventoryScene.options(context)} context={context} markers onSelect={() => {}} showResult={false} />);
  inventoryScene.options(context).forEach((option, index) => {
    expect(host.querySelector(`[data-hotspot="${option.id}"]`)?.querySelector("span")?.textContent).toBe(String(index + 1));
  });
});
it("shows small anchor-based buttons without leader wires only while choice is actionable", () => {
  function markup(onSelect?: (id: string) => void, showResult = false) {
    return renderToStaticMarkup(<WorldArt scene="inventory" title="Склад" options={inventoryScene.options(context)} context={context} markers onSelect={onSelect} showResult={showResult} />);
  }
  const host = document.createElement("div");host.innerHTML = markup(() => {});
  expect(host.querySelector('[data-warehouse-leader], polyline')).toBeNull();
  expect(host.querySelector('[data-hotspot="keeper"]')?.getAttribute("style")).toContain(`left:${warehouseCallouts("boat").keeper.x * 100}%`);
  expect(markup()).not.toContain('data-hotspot=');
  expect(markup(() => {}, true)).not.toContain('data-warehouse-leader');
  expect(markup(() => {}, true)).not.toContain('data-hotspot=');
});

it("uses model silhouette paths as four choice targets without badges or captions", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<InventoryArt context={context} onSelect={() => {}} showResult={false} />);
  ["entrance", "alphabet", "keeper", "wms"].forEach(id => {
    const hit = host.querySelector(`[data-warehouse-zone="${id}"][data-interactive="true"]`);
    expect(hit).not.toBeNull();
    expect(hit?.tagName.toLowerCase()).toBe("path");
    expect(hit?.getAttribute("d")).toBe(warehouseContour(id as "entrance" | "alphabet" | "keeper" | "wms", context.parcel).path);
    expect(host.querySelector(`[data-hotspot="${id}"]`)?.getAttribute("data-zone-caption")).toBeNull();
  });
  for (const markup of [
    renderToStaticMarkup(<InventoryArt context={context} showResult={false} />),
    renderToStaticMarkup(<InventoryArt context={context} onSelect={() => {}} showResult selectedId="wms" />),
  ]) {
    expect(markup).not.toContain("data-warehouse-zone=");
    expect(markup).not.toContain("data-zone-caption=");
  }
});

it("uses the gift's segmented rack contour without selecting a target at idle", () => {
  for (const parcel of ["camera", "socks", "boat"] as const) {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(<InventoryArt context={{ ...context, parcel }} onSelect={() => {}} showResult={false} />);
    expect(host.querySelectorAll('[data-warehouse-contour]')).toHaveLength(4);
    expect(host.querySelector('[data-warehouse-zone="alphabet"]')?.getAttribute("data-warehouse-contour")).toBe(`alphabet-${parcel}`);
    expect(host.querySelectorAll('[data-warehouse-contour][data-active="true"]')).toHaveLength(0);
    host.innerHTML = renderToStaticMarkup(<InventoryArt context={{ ...context, parcel }} selectedId="keeper" onSelect={() => {}} showResult={false} />);
    expect(host.querySelectorAll('[data-warehouse-contour][data-active="true"]')).toHaveLength(1);
    expect(host.querySelector('[data-warehouse-zone="keeper"]')?.getAttribute("data-active")).toBe("true");
    host.innerHTML = renderToStaticMarkup(<InventoryArt context={{ ...context, parcel }} selectedId="keeper" showResult />);
    expect(host.querySelector('[data-warehouse-contour]')).toBeNull();
  }
});
