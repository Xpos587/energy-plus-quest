import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { CraneConcept } from "./crane/CraneConcept";
import { InventoryConcept } from "./inventory/InventoryConcept";
import { LastmileConcept } from "./lastmile/LastmileConcept";
import type { SceneContext } from "./types";

const base: SceneContext = {
  parcel: "camera",
  recipient: "alva",
  profile: "student",
};
function fragment(markup: string) {
  const template = document.createElement("template");
  template.innerHTML = markup;
  return template.content;
}
for (const format of ["desktop", "mobile"] as const) {
  describe(`scenario illustration contract: ${format}`, () => {
    it("keeper and WMS share the correct dispatch position but not the handover", () => {
      const variants = ["keeper", "wms"].map((selectedId) =>
        fragment(
          renderToStaticMarkup(
            <InventoryConcept
              context={base}
              format={format}
              selectedId={selectedId}
              showResult
            />,
          ),
        ),
      );
      const gifts = variants.map((node) =>
        node.querySelector("[data-warehouse-gift]")!.getAttribute("transform"),
      );
      expect(gifts[0]).toBe(gifts[1]);
      variants.forEach((node) =>
        expect(node.querySelector("svg")?.getAttribute("data-gift-zone")).toBe(
          "dispatch",
        ),
      );
      expect(
        variants[0].querySelector(
          '[data-warehouse-address="missing-handover"]',
        ),
      ).not.toBeNull();
      expect(
        variants[1].querySelector('[data-warehouse-address="recorded"]'),
      ).not.toBeNull();
    });
    for (const selectedId of ["rush", "wait", "petr", "remote"]) {
      it(`barge ${selectedId}: two cranes, one of each operator and the actual gift`, () => {
        const node = fragment(
          renderToStaticMarkup(
            <CraneConcept
              context={base}
              format={format}
              selectedId={selectedId}
              showResult
            />,
          ),
        );
        expect(node.querySelectorAll("[data-crane]")).toHaveLength(2);
        expect(node.querySelectorAll('[data-operator="Иван"]')).toHaveLength(1);
        expect(node.querySelectorAll('[data-operator="Пётр"]')).toHaveLength(1);
        const gift = node.querySelector('[data-gift-type="camera"]');
        expect(gift?.getAttribute("data-gift-location")).toBe(
          selectedId === "wait" ? "quay" : "barge",
        );
        expect(
          gift?.querySelectorAll("path,rect,circle").length,
        ).toBeGreaterThan(0);
        expect(node.querySelectorAll("[data-pipes=aboard]")).toHaveLength(1);
        expect(node.querySelectorAll("[data-delayed-cargo]")).toHaveLength(
          selectedId === "petr" ? 1 : 0,
        );
        expect(node.querySelectorAll("[data-remote-console]")).toHaveLength(
          selectedId === "remote" ? 1 : 0,
        );
      });
    }
    it("the robot stops in the bog and the rover crosses at the river", () => {
      const robot = fragment(
        renderToStaticMarkup(
          <LastmileConcept context={base} format={format} outcome="robot" />,
        ),
      );
      const rover = fragment(
        renderToStaticMarkup(
          <LastmileConcept context={base} format={format} outcome="rover" />,
        ),
      );
      expect(robot.querySelector('[data-vehicle="robot"]')).not.toBeNull();
      expect(rover.querySelector('[data-vehicle="rover"]')).not.toBeNull();
      const bogTransform = robot
        .querySelector('[data-obstacle="bog"]')!
        .getAttribute("transform")!;
      expect(
        robot
          .querySelector('[data-vehicle="robot"]')!
          .getAttribute("transform")!
          .startsWith(bogTransform),
      ).toBe(true);
      expect(
        robot.querySelector('[data-event="stuck-in-ground"] path'),
      ).not.toBeNull();
      expect(
        rover.querySelector('[data-event="swimming"] path'),
      ).not.toBeNull();
      for (const node of [robot, rover]) {
        expect(node.querySelectorAll("[data-obstacle]")).toHaveLength(2);
        expect(node.querySelectorAll("[data-parcel]")).toHaveLength(1);
      }
    });
    for (const parcel of ["boat", "camera", "socks"] as const) {
      it(`pipe carrier requires the correct rescue for ${parcel}`, () => {
        const node = fragment(
          renderToStaticMarkup(
            <LastmileConcept
              context={{ ...base, parcel }}
              format={format}
              outcome="pipe-carrier"
            />,
          ),
        );
        expect(node.querySelector("svg")?.getAttribute("data-rescue")).toBe(
          parcel === "boat" ? "rover" : "drone",
        );
        expect(
          node.querySelector('[data-vehicle="pipe-carrier"]'),
        ).not.toBeNull();
        expect(
          node.querySelector('[data-location="quay"] [data-cargo="pipes"]'),
        ).not.toBeNull();
      });
    }
    for (const recipient of ["alva", "khor", "arseniy"] as const) {
      it(`helicopter last leg for ${recipient}`, () => {
        const node = fragment(
          renderToStaticMarkup(
            <LastmileConcept
              context={{ ...base, recipient }}
              format={format}
              outcome="helicopter"
            />,
          ),
        );
        expect(
          node.querySelector(
            '[data-event="air-delivery"] [data-vehicle="rover"]',
          ) !== null,
        ).toBe(recipient !== "arseniy");
        expect(node.textContent?.includes("10 км")).toBe(
          recipient !== "arseniy",
        );
      });
    }
  });
}
