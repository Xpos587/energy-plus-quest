import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { QuestHeader } from "./QuestShell";

it("shows delivery progress without an expandable route menu", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const container = document.createElement("div");
  const root = createRoot(container);
  try {
    await act(async () =>
      root.render(
        <QuestHeader
          state={{}}
          selectionTitle="Кто отправится в путь?"
          selectionStep={1}
        />,
      ),
    );
    expect(container.textContent).toContain("Кто отправится в путь?");
    expect(
      container.querySelector('[aria-controls="delivery-route"]'),
    ).toBeNull();
    expect(container.querySelectorAll("[data-progress-step]")).toHaveLength(0);
    expect(container.querySelector('[aria-label="Шаг 1 из 3"]')).toBeNull();
    await act(async () =>
      root.render(<QuestHeader state={{}} currentStep={2} result />),
    );
    expect(container.querySelector('[data-scene-progress]')?.getAttribute("aria-label")).toBe("Этап 3 из 5: Склад");
    expect(container.querySelector("#delivery-route")).toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
