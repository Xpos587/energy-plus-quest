import { act, type ReactNode, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { GameProvider, useGame } from "./GameContext";
import { restoreGame, SAVE_KEY, useStoredState } from "./persistence";

let root: ReturnType<typeof createRoot> | undefined;
let container: HTMLDivElement;
beforeEach(() => {
  localStorage.clear();
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  container = document.createElement("div");
  document.body.append(container);
});
afterEach(() => {
  act(() => root?.unmount());
  root = undefined;
  container.remove();
  vi.unstubAllGlobals();
});
function render(node: ReactNode) {
  root = createRoot(container);
  act(() => root!.render(node));
  return {
    unmount() {
      act(() => root!.unmount());
      root = undefined;
    },
    rerender(node: ReactNode) {
      act(() => root!.render(node));
    },
  };
}
const screen = {
  getByRole(_role: string) {
    return container.querySelector("output")!;
  },
  getByText(text: string) {
    return [...container.querySelectorAll("button")].find(
      (node) => node.textContent === text,
    )!;
  },
};
const fireEvent = {
  click(node: HTMLElement) {
    act(() => node.click());
  },
};
function Probe() {
  const { state, dispatch } = useGame();
  return (
    <>
      <output>
        {state.step}:{state.scores.energy}
      </output>
      <button
        type="button"
        onClick={() => {
          dispatch({ type: "CHOOSE_PROFILE", value: "student" });
          dispatch({ type: "CHOOSE_RECIPIENT", value: "khor" });
          dispatch({ type: "CHOOSE_PARCEL", value: "socks" });
          dispatch({ type: "CHOOSE_CARRIER", value: "express" });
        }}
      >
        Choose
      </button>
      <button type="button" onClick={() => dispatch({ type: "RESET" })}>
        Reset
      </button>
    </>
  );
}
describe("durable progress", () => {
  it("restores a confirmed result without adding its score again and resets durably", () => {
    const first = render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    fireEvent.click(screen.getByText("Choose"));
    const result = screen.getByRole("status").textContent;
    first.unmount();
    const second = render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    expect(screen.getByRole("status").textContent).toBe(result);
    expect(result).toMatch(/^outcome:/);
    fireEvent.click(screen.getByText("Reset"));
    second.unmount();
    render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    expect(screen.getByRole("status").textContent).toBe("profile:0");
  });
  it("ignores corrupted and incompatible storage", () => {
    expect(restoreGame({ version: 9, scope: "x", state: {} })).toBeUndefined();
    expect(
      restoreGame({
        version: 1,
        scope: "x",
        state: { step: "outcome", carrier: "express" },
      }),
    ).toBeUndefined();
    localStorage.setItem(SAVE_KEY, "bad json");
    render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    expect(screen.getByRole("status").textContent).toBe("profile:0");
  });
  it("isolates the default provider from existing saves", () => {
    const first = render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    fireEvent.click(screen.getByText("Choose"));
    first.unmount();
    render(
      <GameProvider>
        <Probe />
      </GameProvider>,
    );
    expect(screen.getByRole("status").textContent).toBe("profile:0");
  });
  it("restores pending UI state and changes namespace without reusing old state", () => {
    function Ui({ scope }: { scope: string }) {
      const [pending, setPending] = useStoredState<string>(
        scope,
        "none",
        (v): v is string => typeof v === "string",
      );
      return (
        <button type="button" onClick={() => setPending("auto")}>
          {pending}
        </button>
      );
    }
    const first = render(<Ui scope="one" />);
    fireEvent.click(screen.getByText("none"));
    first.unmount();
    const next = render(<Ui scope="one" />);
    expect(screen.getByText("auto")).toBeTruthy();
    next.rerender(<Ui scope="two" />);
    expect(screen.getByText("none")).toBeTruthy();
  });
});

it("restores a direct scene result, then forgets the answer after revision", async () => {
  vi.stubGlobal("matchMedia", () => ({ matches: true }));
  const { ScenesGame } = await import("../scenes/ScenesGame");
  const context = {
    parcel: "camera",
    recipient: "alva",
    profile: "student",
  } as const;
  const node = <ScenesGame context={context} persistenceKey="scene-test" />;
  let mounted = render(node);
  for (let page = 0; page < 30; page++) {
    const condition = container.querySelector('[aria-label="Условие задания"]');
    if (!condition) break;
    const next = [...condition.querySelectorAll("button")].find((button) =>
      /^(Далее|К выбору)$/.test(button.textContent ?? ""),
    );
    if (!next) throw new Error("Missing condition navigation");
    fireEvent.click(next);
  }
  fireEvent.click(
    container.querySelector<HTMLButtonElement>('[data-scene-choice="auto"]')!,
  );
  expect(container.querySelector("[data-choice-inspection]")).toBeNull();
  expect(container.querySelector("[data-result]")).not.toBeNull();
  mounted.unmount();
  mounted = render(node);
  const result = container.querySelector("[data-result]")?.textContent;
  expect(result).toBeTruthy();
  mounted.unmount();
  mounted = render(node);
  expect(container.querySelector("[data-result]")?.textContent).toBe(result);
  fireEvent.click(screen.getByText("Изменить выбор"));
  mounted.unmount();
  render(node);
  expect(container.querySelector("[data-result]")).toBeNull();
  expect(
    JSON.parse(localStorage.getItem("scene-test")!).progress.answers,
  ).toEqual({});
});

it("keeps the game usable when browser storage is blocked", () => {
  const get = vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
    throw new Error("blocked");
  });
  const set = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
    throw new Error("blocked");
  });
  try {
    render(
      <GameProvider persist>
        <Probe />
      </GameProvider>,
    );
    fireEvent.click(screen.getByText("Choose"));
    expect(screen.getByRole("status").textContent).toMatch(/^outcome:/);
  } finally {
    get.mockRestore();
    set.mockRestore();
  }
});

it("commits one StrictMode delivery scope and cleans only its old keys on reset", () => {
  render(
    <StrictMode>
      <GameProvider persist>
        <Probe />
      </GameProvider>
    </StrictMode>,
  );
  const firstScope = JSON.parse(localStorage.getItem(SAVE_KEY)!).scope;
  localStorage.setItem(`${firstScope}:remaining`, "true");
  const readingKey = `quest-reading-v1:${JSON.stringify([firstScope, "story"])}`;
  localStorage.setItem(readingKey, "2");
  localStorage.setItem("unrelated", "keep");
  localStorage.setItem('quest-reading-v1:["another-delivery","story"]', "1");
  fireEvent.click(screen.getByText("Choose"));
  const current = JSON.parse(localStorage.getItem(SAVE_KEY)!);
  expect(current.state.step).toBe("outcome");
  expect(current.scope).not.toBe(firstScope);
  expect(localStorage.getItem(`${firstScope}:remaining`)).toBeNull();
  expect(localStorage.getItem(readingKey)).toBeNull();
  expect(localStorage.getItem("unrelated")).toBe("keep");
  expect(
    localStorage.getItem('quest-reading-v1:["another-delivery","story"]'),
  ).toBe("1");
  localStorage.setItem(`${current.scope}:scenes`, "{}");
  fireEvent.click(screen.getByText("Reset"));
  expect(localStorage.getItem(`${current.scope}:scenes`)).toBeNull();
});
