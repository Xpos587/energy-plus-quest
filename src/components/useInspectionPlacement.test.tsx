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
    expect(document.activeElement).toBe(trigger);
  } finally {
    await act(async () => root.unmount());
    host.remove();
  }
});
