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
    const open = async (id: string) => act(async () => host.querySelector<HTMLButtonElement>(`[data-hotspot="${id}"]`)!.click());
    const card = () => host.querySelector<HTMLElement>("[data-choice-inspection]");
    expect(host.querySelector("[data-scene-choice]")).toBeNull();
    for (let i = 1; i <= 4; i++) {
      await open(`place-${i}`);
      // The highlighted square explains the place; the card only confirms it.
      expect(card()?.querySelector("[data-choice-eyebrow]")).toBeNull();
      expect(card()?.querySelector("h3")?.textContent).toBe(`Место ${i}`);
      expect(card()?.querySelector('[aria-label="Описание варианта"]')).toBeNull();
      await act(async () => card()!.querySelector<HTMLButtonElement>("[data-choice-cancel]")!.click());
      expect(card()).toBeNull();
    }
    expect(host.querySelector('[data-hotspot="place-3"]')?.getAttribute("aria-label")).toContain("ниша над коробками");
    await open("place-3");
    expect(host.querySelector("[data-result]")).toBeNull();
    await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")!.click());
    expect(card()).toBeNull();
    expect(host.querySelector('[data-verdict] small')).toBeNull();
    expect(host.querySelector("[data-result-heading] > span")?.textContent).toBe("Лодка не поместилась в нишу");
    await act(async () => host.querySelector<HTMLButtonElement>('[data-result-reader] button[aria-label="Изменить выбор"]')!.click());
    expect(card()).toBeNull();
    await open("auto");
    expect(host.querySelector('[data-hotspot="auto"]')?.textContent).not.toContain("Compact");
    expect(card()?.querySelector("h3")?.textContent).toBe("Подобрать автоматически");
    expect(card()?.textContent).toContain("Compact Logotech");
    expect(card()?.textContent).toContain("компактно");
    await act(async () => host.querySelector<HTMLButtonElement>("[data-choice-confirm]")!.click());
    expect(host.querySelector('[data-result]')).not.toBeNull();
    expect(host.querySelector("[data-result-heading] > span")?.textContent).toBe("Compact выбрал место 4");
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});
