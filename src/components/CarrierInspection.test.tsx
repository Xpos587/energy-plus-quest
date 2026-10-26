import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { CarrierInspection } from "./CarrierInspection";

const trucks = ["old", "near", "crew", "old4"] as const;
describe("carrier inspection before committing a choice", () => {
  it.each(trucks)(
    "%s shows the matching truck without outcome spoilers",
    (carrierId) => {
      const html = renderToStaticMarkup(
        <CarrierInspection carrierId={carrierId} />,
      );
      const host = document.createElement("div");
      host.innerHTML = html;
      expect(host.querySelector("img")?.getAttribute("src")).toContain(
        `/closer-${carrierId}.png`,
      );
      expect(host.querySelector("dl")).not.toBeNull();
      expect(host.textContent).not.toMatch(
        /дымят|потрепанные|передвигается рядом с офисом/i,
      );
      expect(host.textContent).not.toMatch(/на неделю|опоздал|на три дня|балл/);
      expect(host.querySelector("button")).toBeNull();
    },
  );
  it("states the crew size before revealing the consequence", () => {
    const html = renderToStaticMarkup(<CarrierInspection carrierId="crew" />);
    expect(html).toContain("Два водителя");
    expect(html).not.toContain("дорогой");
  });
  it("explains Express as a freight aggregator, without a truck photo", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <CarrierInspection carrierId="express" />,
    );
    expect(host.textContent).toContain("Как такси, только для грузов");
    expect(host.querySelectorAll("li")).toHaveLength(3);
    expect(host.querySelector("img")).toBeNull();
  });
});
