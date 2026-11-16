import { act, useRef } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { ChoiceInspection } from "./ChoiceInspection";

it("focuses the selected artwork before inspection and restores the explicit choice", async () => {
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const artFocus = vi.fn();
  function Screen({ inspect }: { inspect: boolean }) {
    const trigger = useRef<HTMLButtonElement>(null);
    return <div>
      <button ref={trigger} data-scene-choice="keeper" style={{ visibility: inspect ? "hidden" : "visible" }}>Keeper</button>
      <button data-choice-id="keeper" data-callout-target aria-pressed="true">Label</button>
      <button data-choice-id="keeper" aria-pressed="true" onFocus={artFocus}>Artwork</button>
      {inspect && <ChoiceInspection selectionKey="inventory:keeper" title="Keeper" returnFocus={trigger.current} onCancel={() => {}} onConfirm={() => {}} />}
    </div>;
  }
  try {
    await act(async () => root.render(<Screen inspect={false} />));
    const trigger = host.querySelector<HTMLButtonElement>("[data-scene-choice]")!;
    trigger.focus();
    await act(async () => root.render(<Screen inspect />));
    expect(artFocus).toHaveBeenCalledOnce();
    expect(document.activeElement?.tagName).toBe("H3");
    expect(trigger.hasAttribute("data-inspection-occluded")).toBe(false);
    await act(async () => root.render(<Screen inspect={false} />));
    await vi.waitFor(() => expect(document.activeElement).toBe(trigger));
  } finally {
    await act(async () => root.unmount());
    host.remove();
  }
});

it.each([
  { moved: false, late: false }, { moved: true, late: false },
  { moved: false, late: true }, { moved: true, late: true },
])("restores hidden artwork without stealing focus (moved=$moved late=$late)", async ({ moved, late }) => {
  const host = document.createElement("div");
  const plane = document.createElement("div");
  const trigger = document.createElement("button");
  const other = document.createElement("button");
  plane.style.visibility = late ? "visible" : "hidden";
  plane.append(trigger);
  document.body.append(host, plane, other);
  const root = createRoot(host);
  const focus = trigger.focus.bind(trigger);
  // JSDOM does not implement the browser's hidden-element focus restriction.
  const spy = vi.spyOn(trigger, "focus").mockImplementation(options => {
    if (getComputedStyle(trigger).visibility !== "hidden") focus(options);
  });
  try {
    await act(async () => root.render(<ChoiceInspection selectionKey="crane:remote" title="Remote" returnFocus={trigger} onCancel={() => {}} onConfirm={() => {}} />));
    await act(async () => root.render(null));
    await vi.waitFor(() => expect(spy).toHaveBeenCalled());
    if (late) await act(async () => { plane.style.visibility = "hidden"; trigger.blur(); });
    expect(document.activeElement).not.toBe(trigger);
    if (moved) other.focus();
    await act(async () => { plane.style.visibility = "visible"; });
    expect(document.activeElement).toBe(moved ? other : trigger);
  } finally {
    await act(async () => root.unmount());
    host.remove(); plane.remove(); other.remove();
    spy.mockRestore();
  }
});
