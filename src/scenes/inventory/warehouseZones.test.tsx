import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { inventoryScene } from "./index";
import { warehouseShelfRanges, warehouseZone } from "./warehouseZones";
import { warehouseContour } from "./callouts";

const context = {
  parcel: "socks",
  recipient: "alva",
  profile: "student",
} as const;

describe("warehouse storage geography", () => {
  it("covers the Russian alphabet exactly once, from receiving left to dispatch right", () => {
    expect(warehouseShelfRanges.map((range) => range.letters).join("")).toBe(
      "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
    );
    warehouseShelfRanges.slice(1).forEach((range, index) => {
      expect(range.x).toBeGreaterThan(warehouseShelfRanges[index].x);
    });
  });

  for (const [parcel, range] of [
    ["camera", "Ф–Э"],
    ["socks", "Н–У"],
    ["boat", "Л–М"],
  ] as const) {
    it(`${parcel}: highlights the shelf containing the gift's letter`, () => {
      const zone = warehouseZone("alphabet", { ...context, parcel });
      expect(zone.label).toContain(range);
      expect(zone.description).toContain(range);
      const host = document.createElement("div");
      host.innerHTML = renderToStaticMarkup(
        <inventoryScene.Art
          context={{ ...context, parcel }}
          selectedId="alphabet"
          showResult={false}
          onSelect={() => {}}
        />,
      );
      expect(
        host
          .querySelector('[data-hotspot="alphabet"]')
          ?.getAttribute("aria-pressed"),
      ).toBe("true");
      expect(
        host.querySelectorAll('[data-warehouse-zone]'),
      ).toHaveLength(4);
      const selectedZone = host.querySelector('[data-warehouse-zone="alphabet"]');
      expect(selectedZone?.getAttribute("d")).toBe(warehouseContour("alphabet", parcel).path);
      expect(selectedZone?.getAttribute("data-active")).toBe("true");
      expect(host.querySelectorAll('[data-warehouse-zone][data-active="true"]')).toHaveLength(1);
      expect(host.querySelector('[data-warehouse-leader], polyline')).toBeNull();
      expect(
        host
          .querySelector('[data-hotspot="alphabet"]')
          ?.getAttribute("aria-label"),
      ).toContain(range);
    });
  }

  it("keeps four distinct choices with descriptions tied to visible objects", () => {
    const options = inventoryScene.options(context);
    expect(options.map((option) => option.id)).toEqual([
      "entrance",
      "alphabet",
      "keeper",
      "wms",
    ]);
    expect(
      options.every((option) => Boolean(option.accessibleDescription)),
    ).toBe(true);
    expect(warehouseZone("entrance", context).description).toContain("приёмки");
    expect(warehouseZone("keeper", context).description).toContain(
      "Опытный кладовщик",
    );
    expect(warehouseZone("wms", context).description).toContain("терминал");
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <inventoryScene.Art
        context={context}
        showResult={false}
        onSelect={() => {}}
      />,
    );
    expect(
      host.querySelectorAll('[data-warehouse-zone][data-active="true"]'),
    ).toHaveLength(0);
    expect(host.querySelectorAll("[data-hotspot]")).toHaveLength(4);
    expect(host.textContent).not.toMatch(/правильный|лучший|эффективность/i);
  });
});

it("uses the main warehouse canvas without a second inspection or floating labels", () => {
  const host = document.createElement("div");
  host.innerHTML = renderToStaticMarkup(
    <inventoryScene.Art
      context={context}
      showResult={false}
      onSelect={() => {}}
    />,
  );
  expect(host.querySelector("dialog")).toBeNull();
  expect(host.textContent).not.toContain("Рассмотреть склад");
  expect(host.querySelectorAll("[data-warehouse-label]")).toHaveLength(0);
  expect(host.querySelectorAll("[data-hotspot]")).toHaveLength(4);
  expect(
    host.querySelectorAll("[data-warehouse-annotations] text"),
  ).toHaveLength(0);
});

it("does not resolve the scenario's conflicting keeper names in added UI copy", () => {
  expect(warehouseZone("keeper", context).description).not.toMatch(
    /Павел|Арсений/,
  );
  expect(warehouseZone("keeper", context).description).toContain("кладовщик");
});
