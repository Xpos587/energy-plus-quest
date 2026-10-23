import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ScenarioLink, separateScenarioLink } from "./ScenarioLink";

it("separates only the three explicit scenario actions, keeping their labels", () => {
  for (const label of [
    "Узнать больше об Express",
    "Узнать больше о WMS Inventory.",
    "Узнать больше",
  ]) {
    expect(separateScenarioLink(["Сценарный текст.", label])).toEqual({
      text: "Сценарный текст.",
      label,
    });
  }
  expect(separateScenarioLink(["Система Compact выбрала место."])).toEqual({
    text: "Система Compact выбрала место.",
    label: undefined,
  });
});

it("explains an unavailable material without offering an action that cannot work", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  const url = window.location.href;
  try {
    await act(async () =>
      root.render(<ScenarioLink label="Узнать больше об Express" />),
    );
    expect(host.querySelector("a")).toBeNull();
    expect(host.querySelector("button")).toBeNull();
    expect(host.textContent).toContain("Узнать больше об Express");
    expect(host.textContent).toContain("Материал пока недоступен.");
    expect(window.location.href).toBe(url);
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
