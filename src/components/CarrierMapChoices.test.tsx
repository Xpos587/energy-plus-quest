import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { IllustratedCityMap } from "./IllustratedCityMap";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";

describe("map choices stay available without video playback", () => {
  it("offers all four illustrated trucks with accessible names and selected state", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <IllustratedCityMap onSelect={() => {}} selectedId="crew" />,
    );
    const choices = host.querySelectorAll<HTMLButtonElement>(
      "[data-carrier-choice]",
    );
    expect(choices).toHaveLength(4);
    expect(
      [...choices].map((button) => button.getAttribute("aria-label")),
    ).toEqual(mapCarrierIds.map((id) => `Рассмотреть: ${carrierFacts[id].label}`));
    expect(
      host
        .querySelector('[data-carrier-choice="crew"]')
        ?.getAttribute("aria-pressed"),
    ).toBe("true");
    expect(
      [...choices].every((button) => button.style.left && button.style.top),
    ).toBe(true);
    expect(host.querySelector("[data-map-controls]")).toBeNull();
    expect([...choices].every((button) => button.textContent === "")).toBe(
      true,
    );
  });
});
