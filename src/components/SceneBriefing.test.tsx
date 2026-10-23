import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { SceneBriefing } from "./SceneBriefing";

it("marks long-form briefings so narrow layouts can reserve more reading room", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const element = document.createElement("div");
  const root = createRoot(element);
  try {
    await act(async () =>
      root.render(
        <SceneBriefing
          title="Баржа"
          paragraphs={["Первый абзац.", "Второй абзац."]}
          question="Как отправить груз?"
          keepParagraphs
        />,
      ),
    );
    expect(
      element.querySelector("[data-scene-briefing]")?.getAttribute(
        "data-briefing-longform",
      ),
    ).toBe("true");
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("shows a single-paragraph task without a redundant reading step", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const element = document.createElement("div");
  const root = createRoot(element);
  try {
    await act(async () =>
      root.render(
        <SceneBriefing
          title="Склад"
          paragraphs={["Груз прибыл."]}
          question="Куда поставить груз?"
        />,
      ),
    );
    expect(element.querySelector('[aria-label^="Фрагмент"]')).toBeNull();
    expect(element.querySelector("i[data-current]")).toBeNull();
    expect(element.textContent).toContain("Груз прибыл.");
    expect(element.querySelector('[aria-label="Условие задания"]')).toBeNull();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});

it("pages every paragraph, keeps the question visible and allows rereading", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const element = document.createElement("div");
  document.body.append(element);
  const root = createRoot(element);
  const click = async (label: string) => {
    const button = [...element.querySelectorAll("button")].find(
      (b) => b.textContent === label,
    );
    expect(button).toBeDefined();
    if (!button) throw new Error(`Missing button ${label}`);
    await act(async () => button.click());
  };
  try {
    await act(async () =>
      root.render(
        <SceneBriefing
          title="Баржа"
          paragraphs={["Груз прибыл.", "Кран занят.", "Есть другой путь."]}
          question="Как отправить груз?"
          initiallyOpen
        />,
      ),
    );
    expect(
      element.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).toContain("Груз прибыл.");
    expect(
      element.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).not.toContain("Кран занят.");
    expect(element.querySelector('[aria-label="Закрыть условие"]')).toBeNull();
    await click("Далее");
    expect(
      element.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).toContain("Кран занят.");
    await click("Далее");
    expect(
      element.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).toContain("Есть другой путь.");
    await click("К выбору");
    expect(element.querySelector('[data-testid="scene-intro"]')).toBeNull();
    expect(
      element.querySelector('[data-testid="scene-question"]')?.textContent,
    ).toContain("Как отправить груз?");
    await click("О задаче");
    expect(
      element.querySelector('[data-testid="scene-intro"]')?.textContent,
    ).toContain("Груз прибыл.");
  } finally {
    await act(async () => root.unmount());
    element.remove();
    vi.unstubAllGlobals();
  }
});
