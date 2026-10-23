import { act } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import { SceneBriefing } from "./SceneBriefing";
import { useScenePanDimming } from "./useScenePanDimming";

function Harness() {
  const ref = useScenePanDimming<HTMLDivElement>();
  return (
    <div ref={ref} data-interaction="inspect-confirm">
      <div data-pan-viewport />
      <SceneBriefing title="Сцена" paragraphs={["Условие"]} question="Выбор" initiallyOpen />
    </div>
  );
}
async function setup() {
  vi.useFakeTimers();
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  await act(async () => root.render(<Harness />));
  const viewport = host.querySelector<HTMLElement>("[data-pan-viewport]")!;
  Object.defineProperties(viewport, {
    scrollWidth: { value: 1000 },
    clientWidth: { value: 320 },
  });
  viewport.scrollLeft = 340;
  const event = (type: string, props = {}) => {
    const event = new Event(type, { bubbles: true });
    Object.assign(event, props);
    viewport.dispatchEvent(event);
  };
  return {
    host,
    viewport,
    event,
    cleanup: async () => {
      await act(async () => root.unmount());
      host.remove();
      vi.useRealTimers();
      vi.unstubAllGlobals();
    },
  };
}
it("keeps hint and camera moving beyond the old timeout, ignores taps, ends on pan", async () => {
  const s = await setup();
  try {
    await act(async () =>
      [...s.host.querySelectorAll("button")]
        .find(button => button.textContent === "К выбору")!
        .click(),
    );
    await act(async () => vi.advanceTimersByTime(6000));
    expect(s.host.textContent).toContain("Листайте сцену");
    const position = s.viewport.scrollLeft;
    await act(async () => vi.advanceTimersByTime(400));
    expect(s.viewport.scrollLeft).not.toBe(position);
    await act(async () =>
      s.event("pointerdown", {
        pointerId: 1,
        pointerType: "mouse",
        button: 0,
        clientX: 100,
        clientY: 100,
      }),
    );
    await act(async () => vi.advanceTimersByTime(400));
    expect(s.host.textContent).toContain("Листайте сцену");
    await act(async () =>
      s.event("pointermove", { pointerId: 1, clientX: 140, clientY: 100 }),
    );
    expect(s.host.textContent).not.toContain("Листайте сцену");
  } finally {
    await s.cleanup();
  }
});
it("keeps scene dimmed after native touch scroll cancels pointer, until touch release", async () => {
  const s = await setup();
  try {
    s.event("pointerdown", {
      pointerId: 1,
      pointerType: "touch",
      clientX: 100,
      clientY: 100,
    });
    s.event("touchstart", { touches: [{ identifier: 1 }] });
    s.event("pointermove", { pointerId: 1, clientX: 140, clientY: 100 });
    s.event("pointercancel", { pointerId: 1, pointerType: "touch" });
    s.viewport.scrollLeft += 40;
    s.event("scroll");
    await act(async () => vi.advanceTimersByTime(1000));
    expect(s.host.firstElementChild?.getAttribute("data-scene-panning")).toBe(
      "true",
    );
    s.event("touchend", { touches: [] });
    await act(async () => vi.advanceTimersByTime(250));
    expect(s.host.firstElementChild?.hasAttribute("data-scene-panning")).toBe(
      false,
    );
  } finally {
    await s.cleanup();
  }
});

it("reattaches gesture detection when navigation replaces the scene root", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  const host = document.createElement("div");
  const root = createRoot(host);
  function Screen({ present }: { present: boolean }) {
    const ref = useScenePanDimming<HTMLDivElement>();
    return present ? <div ref={ref}><div data-pan-viewport /></div> : <section />;
  }
  try {
    await act(async () => root.render(<Screen present />));
    await act(async () => root.render(<Screen present={false} />));
    await act(async () => root.render(<Screen present />));
    const viewport = host.querySelector<HTMLElement>("[data-pan-viewport]")!;
    Object.defineProperties(viewport, {scrollWidth:{value:1000},clientWidth:{value:320}});
    const started = vi.fn();
    viewport.addEventListener("scene-pan-start", started);
    for (const [type,x] of [["pointerdown",100],["pointermove",50]] as const) {
      const event = new Event(type,{bubbles:true});
      Object.assign(event,{pointerType:"mouse",pointerId:1,button:0,clientX:x,clientY:100});
      viewport.dispatchEvent(event);
    }
    expect(started).toHaveBeenCalled();
  } finally {
    await act(async () => root.unmount());
    vi.unstubAllGlobals();
  }
});
