import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";
import { IllustratedCityMap } from "./IllustratedCityMap";

describe("the city map is the only way to choose", () => {
  it("offers four rigs and the Express call with accessible names", () => {
    const host = document.createElement("div");
    host.innerHTML = renderToStaticMarkup(
      <IllustratedCityMap onSelect={() => {}} selectedId="crew" />,
    );
    const rigs = host.querySelectorAll<HTMLButtonElement>(
      "[data-carrier-choice]:not([data-map-autopick])",
    );
    expect(
      [...rigs].map((button) => button.getAttribute("aria-label")),
    ).toEqual(
      mapCarrierIds.map((id) => `Рассмотреть: ${carrierFacts[id].label}`),
    );
    expect(
      host
        .querySelector('[data-carrier-choice="crew"]')
        ?.getAttribute("aria-pressed"),
    ).toBe("true");
    expect([...rigs].every((b) => b.style.left && b.style.top)).toBe(true);
    // No numbers or labels on the rigs: the canvas draws the pins.
    expect([...rigs].every((b) => b.textContent === "")).toBe(true);
    const express = host.querySelector<HTMLButtonElement>(
      "[data-map-autopick]",
    );
    expect(express?.dataset.carrierChoice).toBe("express");
    expect(express?.getAttribute("aria-label")).toBe("Express: подобрать фуру");
    expect(host.querySelector("video")).toBeNull();
    expect(host.querySelector("[data-city-plate]")).not.toBeNull();
  });
});
