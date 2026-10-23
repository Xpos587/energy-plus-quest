import { renderToStaticMarkup } from "react-dom/server";
import { expect, it } from "vitest";
import { WorldArt } from "../WorldArt";
import { InventoryArt } from "./InventoryArt";
import { inventoryScene } from "./index";
import { warehouseCallouts, warehouseContour } from "./callouts";

const context = { parcel: "boat", recipient: "alva", profile: "student" } as const;
it("keeps map numbering tied to the corresponding warehouse buttons", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(<WorldArt scene="inventory" title="Склад" options={inventoryScene.options(context)} context={context} markers onSelect={() => {}} showResult={false} />);
  inventoryScene.options(context).forEach((option, index) => {
    expect(host.querySelector(`[data-hotspot="${option.id}"]`)?.textContent).toBe(String(index + 1));
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

it("uses model silhouette paths as four choice targets with number-only badges", () => {
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
