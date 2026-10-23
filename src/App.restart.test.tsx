import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { App } from "./App";
import { SAVE_KEY } from "./game/persistence";

it("restarts the entire journey from a saved completed game and stays reset after reload", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: false }));
  vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  localStorage.clear();
  const scope = "quest-restart-test";
  localStorage.setItem(SAVE_KEY, JSON.stringify({ version: 1, scope, state: {
    step: "outcome", profile: "student", recipient: "alva", parcel: "socks",
    carrier: "express", scores: { energy: -1, empathy: 5, efficiency: 5 },
  }}));
  localStorage.setItem(`${scope}:remaining`, "true");
  localStorage.setItem(`${scope}:intro-seen`, "true");
  localStorage.setItem(`${scope}:scenes`, JSON.stringify({progress: {
    sceneIndex: 3, phase: "result", finished: true,
    answers: { compact: "auto", inventory: "wms", crane: "remote", lastmile: "pipe-carrier" },
  }}));
  const container = document.createElement("div");
  document.body.append(container);
  let root = createRoot(container);
  try {
    await act(async () => root.render(<App />));
    const profile = [...container.querySelectorAll("button")].find(b => b.textContent === "Узнать, какой вы логист");
    expect(profile).toBeDefined();
    await act(async () => profile!.click());
    const restart = container.querySelector<HTMLButtonElement>('button[aria-label="Пройти заново"]');
    expect(restart).not.toBeNull();
    await act(async () => restart!.click());
    expect(container.textContent).toContain("Доставляем радость");
    expect(container.querySelector('[data-intro-enter]')).not.toBeNull();
    expect(container.textContent).not.toContain("Представьте, что вы хотите");
    expect(JSON.parse(localStorage.getItem(SAVE_KEY)!).state.step).toBe("profile");
    expect(localStorage.getItem(`${scope}:scenes`)).toBeNull();
    await act(async () => root.unmount());
    root = createRoot(container);
    await act(async () => root.render(<App />));
    expect(container.textContent).toContain("Доставляем радость");
    expect(container.querySelector('[data-intro-enter]')).not.toBeNull();
  } finally {
    await act(async () => root.unmount());
    container.remove();
    localStorage.clear();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});
