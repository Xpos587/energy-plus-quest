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
    const open = async (id: string) => act(async () => host.querySelector<HTMLButtonElement>(`[data-hotspot="${id}"]`)!.click());
    const card = () => host.querySelector<HTMLElement>("[data-choice-inspection]");
    expect(host.querySelector("[data-scene-choice]")).toBeNull();
    for (let i = 1; i <= 4; i++) {
      await open(`place-${i}`);
      expect(card()?.querySelector("[data-choice-eyebrow]")?.textContent).toBe(`Место ${i}`);
      expect(card()?.querySelector("h3")?.lastChild?.textContent).toBe(names[i - 1]);
      expect(card()?.querySelectorAll("dd")).toHaveLength(2);
      await act(async () => card()!.querySelector<HTMLButtonElement>("[data-choice-cancel]")!.click());
      expect(card()).toBeNull();
    }
    expect(host.querySelector('[data-hotspot="place-3"]')?.getAttribute("aria-label")).toContain("за тремя коробками");
    await open("place-3");
    expect(host.querySelector("[data-result]")).toBeNull();
    await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")!.click());
    expect(card()).toBeNull();
    expect(host.querySelector('[data-verdict]')?.textContent).toContain("Ниша за коробками");
    await act(async () => host.querySelector<HTMLButtonElement>('[data-result-reader] button[aria-label="Изменить выбор"]')!.click());
    expect(card()).toBeNull();
    await open("auto");
    expect(card()?.querySelector("h3")?.lastChild?.textContent).toBe("Compact подберёт место");
    await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")!.click());
    expect(host.querySelector('[data-result]')).not.toBeNull();
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});
