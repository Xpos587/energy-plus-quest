import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ScenesGame } from "./ScenesGame";

it("names each numbered place and lets the player revise a direct choice", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }));
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<ScenesGame context={{ parcel: "boat", recipient: "alva", profile: "professional" }} startAt="compact" />));
    for (let i = 0; i < 30 && host.querySelector('[aria-label="Условие задания"]'); i++) {
      const button = [...host.querySelectorAll<HTMLButtonElement>('[aria-label="Условие задания"] button')].find(b => /^(Далее|К выбору)$/.test(b.textContent ?? ""));
      expect(button).toBeDefined();
      await act(async () => button!.click());
    }
    const names = ["У задних дверей", "Над посудой", "Ниша за коробками", "У передней стенки"];
    for (let i = 1; i <= 4; i++) {
      const choice = host.querySelector<HTMLButtonElement>(`[data-scene-choice="place-${i}"]`)!;
      expect(choice.querySelector(":scope > span:last-child")?.firstChild?.textContent).toBe(names[i - 1]);
      expect(choice.querySelector("[data-choice-detail]")?.textContent).toBeTruthy();
      expect(choice.querySelector('[aria-hidden="true"]')?.textContent).toBe(String(i));
      expect(choice.getAttribute("aria-label")).toBe(`Место ${i}: ${names[i - 1]}`);
    }
    const hotspot = host.querySelector<HTMLButtonElement>('[data-hotspot="place-3"]')!;
    expect(hotspot.getAttribute("aria-label")).toContain("за тремя коробками");
    await act(async () => hotspot.click());
    expect(host.querySelector('[data-choice-inspection]')).toBeNull();
    expect(host.querySelector('[data-result]')).not.toBeNull();
    expect(host.querySelector('[data-verdict]')?.textContent).toContain("Ниша за коробками");
    await act(async () => host.querySelector<HTMLButtonElement>('[data-result-reader] button[aria-label="Изменить выбор"]')!.click());
    expect(host.querySelector('[data-choice-inspection]')).toBeNull();
    await act(async () => host.querySelector<HTMLButtonElement>('[data-scene-choice="auto"]')!.click());
    expect(host.querySelector('[data-result]')).not.toBeNull();
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});
