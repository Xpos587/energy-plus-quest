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
  // Call 05.11: like the other scenes, the warehouse itself is the only choice — no button row.
  expect(host.querySelectorAll("[data-scene-choice]")).toHaveLength(0);
  const place = host.querySelector<HTMLButtonElement>('[data-hotspot="wms"]');
  expect(place?.getAttribute("aria-label")).toContain("Стол с компьютером");

  await act(async () => place?.click());
  const card = host.querySelector("[data-choice-inspection]");
  expect(card?.textContent).toContain("Автоподбор места");
  expect(card?.textContent).toContain("К складу");
  expect(host.querySelector('[data-testid="result-copy"]')).toBeNull();
  await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")?.click());

  expect(host.querySelector("[data-choice-inspection]")).toBeNull();
  expect(host.querySelector('[data-testid="result-copy"]')).not.toBeNull();
  expect(host.querySelector("[data-scene-consequence]")?.getAttribute("data-scene-consequence")).toBe("inventory-wms");
  expect(host.querySelector('[data-result-reader]')).not.toBeNull();
});

it.each(["helicopter", "rover", "robot", "pipe-carrier"])("last mile previews %s without committing, can cancel, and keeps the parcel through confirmation", async (id) => {
  await act(async () => root.render(<ScenesGame
    context={{ profile: "professional", recipient: "khor", parcel: "boat" }}
    startAt="lastmile"
  />));
  for (let page = 0; page < 30 && host.querySelector('[aria-label="Условие задания"]'); page++) {
    const next = [...host.querySelectorAll<HTMLButtonElement>('[aria-label="Условие задания"] button')]
      .find(button => /^(Далее|К выбору)$/.test(button.textContent ?? ""));
    await act(async () => next!.click());
  }
  const vehicle = host.querySelector<HTMLButtonElement>(`[data-hotspot="${id}"]`)!;
  await act(async () => vehicle.click());
  expect(host.querySelector('[data-testid="result-copy"]')).toBeNull();
  const card = host.querySelector('[data-choice-inspection]');
  expect(card).not.toBeNull();
  expect(card?.querySelector('[data-delivery-reminder]')?.textContent).toContain("Хабта");
  expect(card?.querySelector('[data-delivery-reminder] img')?.getAttribute('src')).toContain("boat");
  await act(async () => host.querySelector<HTMLButtonElement>('[data-choice-cancel]')!.click());
  expect(host.querySelector('[data-choice-inspection]')).toBeNull();
  expect(host.querySelector('[data-testid="result-copy"]')).toBeNull();
  await act(async () => vehicle.click());
  await act(async () => host.querySelector<HTMLButtonElement>('[data-choice-confirm]')!.click());
  expect(host.querySelector('[data-choice-inspection]')).toBeNull();
  expect(host.querySelector('[data-result-reader] [data-delivery-reminder]')?.textContent).toContain("Хабта");
  expect(host.querySelector('[data-testid="result-copy"]')).not.toBeNull();
  expect(host.querySelectorAll('fieldset[aria-label="Изменение показателей"]')).toHaveLength(1);
});

it("switches last-mile previews through markers and vehicle shapes without cancelling", async () => {
  await act(async () => root.render(<ScenesGame
    context={{ profile: "professional", recipient: "khor", parcel: "boat" }}
    startAt="lastmile"
  />));
  for (let page = 0; page < 30 && host.querySelector('[aria-label="Условие задания"]'); page++) {
    const next = [...host.querySelectorAll<HTMLButtonElement>('[aria-label="Условие задания"] button')]
      .find(button => /^(Далее|К выбору)$/.test(button.textContent ?? ""));
    await act(async () => next!.click());
  }
  for (const [kind, id] of [["hotspot", "helicopter"], ["hotspot", "rover"], ["lastmile-zone", "robot"], ["lastmile-zone", "pipe-carrier"]]) {
    const target = host.querySelector<HTMLElement>(`[data-${kind}="${id}"]`)!;
    if (kind === "hotspot") expect((target as HTMLButtonElement).disabled).toBe(false);
    else expect(target.getAttribute("data-interactive")).toBe("true");
    await act(async () => target.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    expect(host.querySelector('[data-choice-inspection]')?.getAttribute('data-choice-inspection')).toBe(id);
    expect(host.querySelector('[data-result-reader]')).toBeNull();
  }
  await act(async () => host.querySelector<HTMLButtonElement>('[data-choice-confirm]')!.click());
  expect(host.querySelector('[data-scene-consequence]')?.getAttribute('data-scene-consequence')).toBe('lastmile-pipe-carrier-boat');
});

it("uses the unchanged warehouse question from the scenario", async () => {
  await act(async () => root.render(<ScenesGame
    context={{ profile: "professional", recipient: "alva", parcel: "boat" }}
    startAt="inventory"
  />));
  const prompt = host.querySelector('[data-testid="scene-question"] [class*="questionPrompt"]');
  expect(prompt?.textContent).toContain("Давайте решим, где его разместить.");
});
