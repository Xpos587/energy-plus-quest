import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ScenesGame } from "./ScenesGame";

let host: HTMLDivElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() }));
  host = document.createElement("div");
  document.body.append(host);
  root = createRoot(host);
});

afterEach(async () => {
  await act(async () => root.unmount());
  host.remove();
  vi.unstubAllGlobals();
});

it("lets the player pick a place on the warehouse art, check its card and confirm", async () => {
  await act(async () => root.render(<ScenesGame
    context={{ profile: "professional", recipient: "alva", parcel: "camera" }}
    startAt="inventory"
  />));

  expect(host.querySelector("[data-scene-briefing]")?.getAttribute("data-reading")).toBe("true");
  for (let page = 0; page < 30 && host.querySelector('[aria-label="Условие задания"]'); page++) {
    const next = [...host.querySelectorAll<HTMLButtonElement>('[aria-label="Условие задания"] button')]
      .find(button => /^(Далее|К выбору)$/.test(button.textContent ?? ""));
    expect(next).toBeDefined();
    await act(async () => next!.click());
  }
  expect(host.querySelector('[aria-label="Условие задания"]')).toBeNull();
  expect(host.querySelector("[data-scene-briefing]")?.getAttribute("data-reading")).toBe("false");
  expect(host.querySelector("[data-scene-choice]")).toBeNull();
  const place = host.querySelector<HTMLButtonElement>('[data-hotspot="wms"]');
  expect(place?.textContent).toContain("WMS");

  await act(async () => place?.click());
  const card = host.querySelector("[data-choice-inspection]");
  expect(card?.textContent).toContain("Система WMS");
  expect(card?.textContent).toContain("К складу");
  expect(host.querySelector('[data-testid="result-copy"]')).toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")?.click());

  expect(host.querySelector("[data-choice-inspection]")).toBeNull();
  expect(host.querySelector('[data-testid="result-copy"]')).not.toBeNull();
  expect(host.querySelector("[data-scene-consequence]")?.getAttribute("data-scene-consequence")).toBe("inventory-wms");
  expect(host.querySelector('[data-result-reader]')).not.toBeNull();
});

it("uses the unchanged warehouse question from the scenario", async () => {
  await act(async () => root.render(<ScenesGame
    context={{ profile: "professional", recipient: "alva", parcel: "boat" }}
    startAt="inventory"
  />));
  const prompt = host.querySelector('[data-testid="scene-question"] [class*="questionPrompt"]');
  expect(prompt?.textContent).toContain("Давайте решим, где его разместить.");
});
