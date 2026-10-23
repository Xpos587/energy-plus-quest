import { act, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { remainingScenes, ScenesGame } from "./ScenesGame";

it("separates complete condition from choice and remembers reading across result/scene returns", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const context = {
    profile: "student",
    recipient: "khor",
    parcel: "boat",
  } as const;
  const find = (label: string) =>
    [...host.querySelectorAll("button")].find((b) => b.textContent === label);
  const click = async (b: HTMLButtonElement | undefined | null) => {
    expect(b).toBeDefined();
    if (!b) throw Error("missing button");
    await act(async () => b.click());
  };
  const condition = () => host.querySelector('[aria-label="Условие задания"]');
  async function read() {
    const seen: string[] = [];
    for (let i = 0; i < 40 && condition(); i++) {
      seen.push(
        host.querySelector('[data-testid="scene-intro"]')?.textContent ?? "",
      );
      await click(find("Далее") ?? find("К выбору"));
    }
    return seen.join(" ").replace(/\s+/g, " ").trim();
  }
  try {
    await act(async () =>
      root.render(
        <StrictMode>
          <ScenesGame context={context} />
        </StrictMode>,
      ),
    );
    expect(condition()).not.toBeNull();
    const readText = await read();
    const intro = remainingScenes[0]
      .intro(context)
      .slice(0, -1)
      .join(" ")
      .replace(/\s+/g, " ")
      .trim();
    expect(readText).toBe(intro);
    expect(
      host.querySelector('[data-testid="scene-question"]')?.textContent,
    ).not.toContain(remainingScenes[0].intro(context)[0]);
    await click(find("О задаче"));
    expect(condition()).not.toBeNull();
    await read();
    await click(host.querySelector('[data-scene-choice="place-1"]'));
    expect(host.querySelector("[data-result]")).not.toBeNull();
    await click(find("Изменить выбор"));
    expect(condition()).toBeNull();
    await click(host.querySelector('[data-scene-choice="place-1"]'));
    for (let i = 0; i < 40 && find("Читать дальше"); i++)
      await click(find("Читать дальше"));
    await click(find("Продолжить"));
    expect(host.querySelector("[data-scene]")?.getAttribute("data-scene")).toBe(
      "inventory",
    );
    expect(condition()).not.toBeNull();
    const warehouse = await read();
    expect(warehouse).toBe(
      remainingScenes[1].intro(context).join(" ").replace(/\s+/g, " ").trim(),
    );
    await click(find("К этапу «Загрузка»"));
    expect(host.querySelector("[data-result]")).not.toBeNull();
    await click(find("Продолжить"));
    expect(condition()).toBeNull();
    expect(find("О задаче")).toBeDefined();
    await click(find("О задаче"));
    expect(condition()).not.toBeNull();
    await read();
    expect(document.activeElement?.textContent).toBe("О задаче");
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.unstubAllGlobals();
  }
});

it("opens the new separate condition even when an older immediate-choice save stored it closed", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const { GameProvider } = await import("../game/GameContext");
  const context = {
    profile: "student",
    recipient: "khor",
    parcel: "boat",
  } as const;
  const intro = remainingScenes[0].intro(context).slice(0, -1);
  const key =
    "briefing:open:" +
    remainingScenes[0].title.replace(/^Сцена \d+\.\s*/, "") +
    intro.join("\n\n");
  localStorage.setItem(
    "energy-quest-save-v1",
    JSON.stringify({
      version: 1,
      scope: "quest-r2-migration",
      state: { step: "profile" },
    }),
  );
  localStorage.setItem(
    "quest-reading-v1:" + JSON.stringify(["quest-r2-migration", key]),
    "false",
  );
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () =>
      root.render(
        <GameProvider persist>
          <ScenesGame context={context} />
        </GameProvider>,
      ),
    );
    expect(host.querySelector('[aria-label="Условие задания"]')).not.toBeNull();
  } finally {
    await act(async () => root.unmount());
    host.remove();
    localStorage.clear();
    vi.unstubAllGlobals();
  }
});
