import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ScenesGame } from "./ScenesGame";

let container: HTMLDivElement;
let root: ReturnType<typeof createRoot>;
const context = {
  parcel: "camera",
  recipient: "alva",
  profile: "professional",
} as const;

beforeEach(() => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({
    matches: true,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);
});
afterEach(async () => {
  await act(async () => root.unmount());
  container.remove();
  vi.unstubAllGlobals();
});

async function click(selector: string) {
  const button = container.querySelector<HTMLButtonElement>(selector);
  if (!button) throw new Error(`Missing ${selector}`);
  button.focus();
  await act(async () => button.click());
}

it("records a direct choice, then lets the player revise it without stale scores", async () => {
  await act(async () =>
    root.render(<ScenesGame context={context} startAt="inventory" />),
  );
  expect(container.querySelector("[data-score-key]")).toBeNull();
  await click('[data-scene-choice="entrance"]');
  expect(container.querySelector("[data-choice-inspection]")).toBeNull();
  expect(container.querySelector('[data-testid="result-copy"]')).not.toBeNull();
  expect(
    container
      .querySelector("[data-scene-consequence]")
      ?.getAttribute("data-scene-consequence"),
  ).toBe("inventory-entrance");
  expect(
    [...container.querySelectorAll("[data-score-key] strong")].map(
      (node) => node.textContent,
    ),
  ).toEqual(["-2", "-1", "0"]);
  await click('[data-result-reader] button[aria-label="Изменить выбор"]');
  expect(container.querySelector("[data-score-key]")).toBeNull();
  expect(
    container.querySelector('[data-scene-choice="entrance"]'),
  ).not.toBeNull();
  await click('[data-scene-choice="wms"]');
  expect(
    container
      .querySelector("[data-scene-consequence]")
      ?.getAttribute("data-scene-consequence"),
  ).toBe("inventory-wms");
  expect(
    [...container.querySelectorAll("[data-score-key] strong")].map(
      (node) => node.textContent,
    ),
  ).toEqual(["+4", "+4", "+5"]);
});

it("focuses the selected button and resets the result when the starting scene changes", async () => {
  await act(async () =>
    root.render(<ScenesGame context={context} startAt="inventory" />),
  );
  await click('[data-scene-choice="wms"]');
  expect(container.querySelector("[data-result]")).not.toBeNull();
  await act(async () =>
    root.render(<ScenesGame context={context} startAt="crane" />),
  );
  expect(container.querySelector('[data-scene="crane"]')).not.toBeNull();
  expect(container.querySelector("[data-result]")).toBeNull();
  expect(
    container.querySelector('[data-hotspot="remote"]'),
  ).not.toBeNull();
  expect(container.querySelector("[data-scene-choice]")).toBeNull();
});

it("shows a single-paragraph task alongside directly available choices", async () => {
  await act(async () =>
    root.render(<ScenesGame context={context} startAt="inventory" />),
  );
  expect(container.querySelector('[data-testid="scene-question"]')?.textContent).toContain("Давайте решим, где его разместить.");
  await click('[data-scene-choice="wms"]');
  expect(container.querySelector("[data-choice-inspection]")).toBeNull();
  expect(container.querySelector("[data-result]")).not.toBeNull();
});
