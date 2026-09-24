import { act, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ScenesGame } from "./ScenesGame";
import { compactScene } from "./compact";

it.each([
  [
    { energy: 2, empathy: 2, efficiency: 2 },
    { energy: 1, empathy: 13, efficiency: 14 },
  ],
  [
    { energy: -1, empathy: 5, efficiency: 5 },
    { energy: -2, empathy: 16, efficiency: 17 },
  ],
  [
    { energy: 0, empathy: 0, efficiency: 0 },
    { energy: -1, empathy: 11, efficiency: 12 },
  ],
])(
  "hands off original context, all answers and seeded totals exactly once (%j)",
  async (initialScores, expectedScores) => {
    vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
    vi.stubGlobal("matchMedia", () => ({ matches: false }));
    const container = document.createElement("div");
    document.body.append(container);
    const root = createRoot(container);
    const onComplete = vi.fn();
    const context = {
      parcel: "boat",
      recipient: "alva",
      profile: "professional",
    } as const;
    const originalScores = { ...initialScores };
    const click = async (button: HTMLButtonElement | null | undefined) => {
      if (!button) throw new Error("Missing journey button");
      await act(async () => button.click());
    };
    try {
      await act(async () =>
        root.render(
          <StrictMode>
            <ScenesGame
              context={context}
              initialScores={initialScores}
              onComplete={onComplete}
            />
          </StrictMode>,
        ),
      );
      expect(container.querySelector("dl")).toBeNull();
      for (const [id, values] of [
        ["auto", ["-4", "+3", "+5"]],
        ["wms", ["+4", "+4", "+5"]],
        ["remote", ["+4", "+4", "+5"]],
        ["pipe-carrier", ["-5", "0", "-3"]],
      ] as const) {
        await click(
          container.querySelector<HTMLButtonElement>(
            `[data-choice-id="${id}"]`,
          ),
        );
        expect(container.querySelector("dl")).toBeNull();
        expect(
          container.querySelectorAll(
            'fieldset[aria-label="Изменение показателей"]',
          ),
        ).toHaveLength(1);
        expect(
          [...container.querySelectorAll("[data-score-key] strong")].map(
            (node) => node.textContent,
          ),
        ).toEqual(values);
        await click(
          [...container.querySelectorAll("button")].find((button) =>
            /^(Продолжить|Завершить)/.test(button.textContent ?? ""),
          ),
        );
      }
      expect(onComplete).toHaveBeenCalledTimes(1);
      expect(onComplete).toHaveBeenLastCalledWith({
        context,
        answers: {
          compact: "auto",
          inventory: "wms",
          crane: "remote",
          lastmile: "pipe-carrier",
        },
        scores: expectedScores,
      });
      await click(
        [...container.querySelectorAll("button")].find((button) =>
          button.textContent?.startsWith("Завершено"),
        ),
      );
      expect(onComplete).toHaveBeenCalledTimes(1);
      expect(initialScores).toEqual(originalScores);
    } finally {
      await act(async () => root.unmount());
      container.remove();
      vi.unstubAllGlobals();
    }
  },
);

it("compact opens the canonical task while preserving the shared header and accessible disclosure", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  try {
    await act(async () =>
      root.render(
        <ScenesGame
          context={{
            parcel: "camera",
            recipient: "alva",
            profile: "professional",
          }}
        />,
      ),
    );
    expect(container.querySelectorAll("[data-progress-step]")).toHaveLength(5);
    expect(container.querySelectorAll("[data-selection-context]")).toHaveLength(
      3,
    );
    const toggle =
      container.querySelector<HTMLButtonElement>("[aria-expanded]")!;
    expect(toggle.getAttribute("aria-expanded")).toBe("true");
    expect(
      container.querySelector('[data-choice-id="place-1"]')?.textContent,
    ).toBe("№1");
    expect(
      container
        .querySelector('[data-testid="scene-intro"]')
        ?.closest("[hidden]"),
    ).toBeNull();
    expect(container.querySelector("[data-choice-description]")).toBeNull();
    expect(
      container.querySelector('[data-testid="scene-question"]')?.textContent,
    ).toBe(
      compactScene.intro({
        parcel: "camera",
        recipient: "alva",
        profile: "professional",
      })[1],
    );
    await act(async () =>
      toggle.dispatchEvent(
        new KeyboardEvent("keydown", { key: "Escape", bubbles: true }),
      ),
    );
    expect(toggle.getAttribute("aria-expanded")).toBe("false");
    expect(document.activeElement).toBe(toggle);
    await act(async () =>
      root.render(
        <ScenesGame
          startAt="inventory"
          context={{
            parcel: "camera",
            recipient: "alva",
            profile: "professional",
          }}
        />,
      ),
    );
    expect(
      container.querySelector("[aria-expanded]")?.getAttribute("aria-expanded"),
    ).toBe("true");
  } finally {
    await act(async () => root.unmount());
    container.remove();
    vi.unstubAllGlobals();
  }
});
