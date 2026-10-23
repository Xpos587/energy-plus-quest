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

it("lets the player choose from the visible warehouse scene and shows the consequence in one action", async () => {
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
  const choice = host.querySelector<HTMLButtonElement>('[data-scene-choice="wms"]');
  expect(choice).not.toBeNull();
  expect(choice?.textContent).toContain("Система WMS");

  await act(async () => choice?.click());

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
