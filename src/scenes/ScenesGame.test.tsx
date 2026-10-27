import { act, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { compactScene } from "./compact";
import { ScenesGame } from "./ScenesGame";

it("preserves the compact plane while switching between choice and result artwork", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  const click = async (button: HTMLButtonElement | null | undefined) => {
    if (!button) throw new Error("Missing compact transition button");
    await act(async () => button.click());
  };
  const plane = () =>
    container.querySelector('[data-world-scene="compact"] [data-world-plane]');
  try {
    await act(async () =>
      root.render(
        <ScenesGame
          context={{
            parcel: "boat",
            recipient: "khor",
            profile: "professional",
          }}
        />,
      ),
    );
    for (let beat = 0; beat < 30; beat++) {
      const condition = container.querySelector(
        '[aria-label="Условие задания"]',
      );
      if (!condition) break;
      await click(
        [...condition.querySelectorAll("button")].find((button) =>
          /^(Далее|К выбору)$/.test(button.textContent ?? ""),
        ),
      );
    }
    const overviewPlane = plane();
    expect(overviewPlane).not.toBeNull();
    await click(
      container.querySelector<HTMLButtonElement>(
        '[data-scene-choice="place-4"]',
      ),
    );
    const resultPlane = plane();
    expect(resultPlane).not.toBeNull();
    expect(resultPlane).toBe(overviewPlane);
    expect(resultPlane?.hasAttribute("data-map-surface")).toBe(false);
    expect(
      container
        .querySelector('[data-world-scene="compact"]')
        ?.getAttribute("data-selected"),
    ).toBe("place-4");
    await click(
      container.querySelector<HTMLButtonElement>(
        '[data-result-reader] button[aria-label="Изменить выбор"]',
      ),
    );
    const returnedPlane = plane();
    expect(returnedPlane).not.toBeNull();
    expect(returnedPlane).toBe(resultPlane);
    expect(returnedPlane?.hasAttribute("data-map-surface")).toBe(true);
    expect(
      container
        .querySelector('[data-world-scene="compact"]')
        ?.hasAttribute("data-inspection-camera"),
    ).toBe(false);
  } finally {
    await act(async () => root.unmount());
    container.remove();
    vi.unstubAllGlobals();
  }
});

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
    vi.stubGlobal("matchMedia", () => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
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
        for (let beat = 0; beat < 30; beat++) {
          const condition = container.querySelector(
            '[aria-label="Условие задания"]',
          );
          if (!condition) break;
          await click(
            [...condition.querySelectorAll("button")].find((button) =>
              /^(Далее|К выбору)$/.test(button.textContent ?? ""),
            ),
          );
        }
        if (id === "remote") {
          // Barge: the pin opens a card; only the card commits the choice.
          await click(container.querySelector<HTMLButtonElement>(`[data-hotspot="${id}"]`));
          expect(container.querySelector("[data-result]")).toBeNull();
          await click(container.querySelector<HTMLButtonElement>("[data-choice-confirm]"));
        } else
          await click(
            container.querySelector<HTMLButtonElement>(
              `[data-scene-choice="${id}"]`,
            ),
          );
        expect(container.querySelector("dl")).toBeNull();
        expect(container.querySelector("[data-choice-inspection]")).toBeNull();
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
        for (let page = 0; page < 30; page++) {
          const nextPage = container.querySelector<HTMLButtonElement>(
            '[data-result-reader] button[aria-label="Читать дальше"]',
          );
          if (!nextPage) break;
          await click(nextPage);
        }
        await click(
          [
            ...container.querySelectorAll<HTMLButtonElement>(
              "[data-result-reader] button",
            ),
          ].find(
            (button) => button.getAttribute("aria-label") !== "Изменить выбор",
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
      expect(container.querySelector("[data-journey-ending]")).not.toBeNull();
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
      expect(onComplete).toHaveBeenCalledTimes(1);
      expect(initialScores).toEqual(originalScores);
    } finally {
      await act(async () => root.unmount());
      container.remove();
      vi.unstubAllGlobals();
    }
  },
);

it("compact separates its condition and keeps the selected gift visible in the header", async () => {
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
    expect(container.querySelectorAll("[data-progress-step]")).toHaveLength(0);
    expect(container.querySelectorAll("[data-selection-context]")).toHaveLength(
      3,
    );
    expect(
      container.querySelector("[data-scene-briefing] [aria-expanded]"),
    ).not.toBeNull();
    expect(
      container.querySelector('[data-choice-id="place-1"]')?.textContent,
    ).toBe("1");
    expect(
      container.querySelector('[data-testid="scene-question"]')?.textContent,
    ).not.toContain(
      compactScene.intro({
        parcel: "camera",
        recipient: "alva",
        profile: "professional",
      })[0],
    );
    expect(container.querySelector("[data-choice-description]")).toBeNull();
    expect(
      container.querySelector('[data-testid="scene-question"]')?.textContent,
    ).toContain(
      compactScene.intro({
        parcel: "camera",
        recipient: "alva",
        profile: "professional",
      })[1],
    );
    expect(
      container.querySelector('[data-scene-choice="place-1"]'),
    ).not.toBeNull();
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
    expect(container.querySelector('[data-testid="scene-question"]')?.textContent).toContain("Давайте решим, где его разместить.");
  } finally {
    await act(async () => root.unmount());
    container.remove();
    vi.unstubAllGlobals();
  }
});
