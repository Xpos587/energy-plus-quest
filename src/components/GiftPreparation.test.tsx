import { act, useReducer } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, it, vi } from "vitest";
import { GiftPreparation } from "./GiftPreparation";
import { gameReducer, initialGameState } from "../game/gameReducer";
import { App } from "../App";
const cleanups: (() => void)[] = [];
afterEach(async () => {
  for (const cleanup of cleanups.splice(0)) await act(cleanup);
  localStorage.clear();
  vi.unstubAllGlobals();
});
async function render(element: React.ReactNode) {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addEventListener() {},
    removeEventListener() {},
  }));
  window.scrollTo = vi.fn();
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  cleanups.push(() => {
    root.unmount();
    host.remove();
  });
  await act(async () => root.render(element));
  return host;
}
async function click(host: HTMLElement, selector: string) {
  await act(async () =>
    host.querySelector<HTMLButtonElement>(selector)!.click(),
  );
}
function Setup() {
  const [state, dispatch] = useReducer(gameReducer, initialGameState);
  return (
    <>
      <GiftPreparation state={state} onAction={dispatch} />
      <output>{JSON.stringify(state)}</output>
    </>
  );
}
it("carries a chosen sender and recipient through preparation, with no extra confirmation", async () => {
  const host = await render(<Setup />);
  await click(host, '[data-choice="professional"]');
  expect(host.querySelector("h1")?.textContent).toBe("Кому отправим подарок?");
  expect(host.textContent).toContain("Профессионал");
  await click(host, '[data-choice="alva"]');
  expect(host.querySelector("h1")?.textContent).toBe("Что отправим Майме?");
  expect(host.querySelector("figure img")).not.toBeNull();
  await click(host, '[data-choice="boat"]');
  expect(JSON.parse(host.querySelector("output")!.textContent!)).toMatchObject({
    step: "carrier",
    profile: "professional",
    recipient: "alva",
    parcel: "boat",
  });
});
it("backs out to change the recipient and updates the gift destination", async () => {
  const host = await render(<Setup />);
  await click(host, '[data-choice="student"]');
  await click(host, '[data-choice="khor"]');
  await click(host, "button:not([data-choice])");
  expect(host.querySelector("h1")?.textContent).toBe("Кому отправим подарок?");
  await click(host, '[data-choice="arseniy"]');
  expect(host.querySelector("h1")?.textContent).toBe("Что отправим Арсению?");
  expect(host.querySelector("figcaption")?.textContent).toBe("Арсений");
  expect(document.activeElement).toBe(host.querySelector("h1"));
});
it("restores preparation at the selected recipient after a page reload", async () => {
  const first = await render(<App />);
  await click(first, "[data-intro-enter]");
  await click(first, "[data-intro-next]");
  await click(first, "[data-intro-start]");
  await click(first, '[data-choice="student"]');
  await click(first, '[data-choice="alva"]');
  const next = await render(<App />);
  expect(next.querySelector("h1")?.textContent).toBe("Что отправим Майме?");
  expect(next.querySelector('[data-choice="socks"]')).not.toBeNull();
  expect(next.querySelector("[data-intro-start]")).toBeNull();
});
