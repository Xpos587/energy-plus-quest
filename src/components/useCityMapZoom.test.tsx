import { act, useRef } from "react";
import { createRoot } from "react-dom/client";
import { expect, it, vi } from "vitest";
import {
  constrainMap,
  MAP_OVERVIEW,
  type MapBounds,
  useCityMapZoom,
  zoomMapAt,
} from "./useCityMapZoom";

const bounds: MapBounds = {
  width: 360,
  height: 250,
  areaWidth: 360,
  areaHeight: 360,
  cx: 180,
  cy: 320,
  controlsBottom: 100,
};

it("eases inspection, decoded-frame following and return on the display clock", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.stubGlobal("matchMedia", () => ({ matches: false }));
  let now = 0;
  vi.spyOn(performance, "now").mockImplementation(() => now);
  const callbacks = new Map<number, FrameRequestCallback>();
  let serial = 0;
  vi.stubGlobal("requestAnimationFrame", (fn: FrameRequestCallback) => { callbacks.set(++serial, fn); return serial; });
  vi.stubGlobal("cancelAnimationFrame", (id: number) => callbacks.delete(id));
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width: 720, height: 500, left: 0, top: 0 } as DOMRect);
  let camera: ReturnType<typeof useCityMapZoom>;
  let renders = 0;
  function Harness() {
    const ref = useRef<HTMLDivElement>(null);
    camera = useCityMapZoom(ref);
    renders++;
    return <div ref={ref}><div data-map-surface style={camera.style} /></div>;
  }
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  const tick = async (ms = 16) => {
    now += ms;
    const batch = [...callbacks.values()];
    callbacks.clear();
    await act(async () => batch.forEach(fn => fn(now)));
  };
  try {
    await act(async () => root.render(<Harness />));
    const surface = host.querySelector("[data-map-surface]") as HTMLElement;
    const original = surface.style.transform;
    await act(async () => camera.inspect("crew", { x: .6, y: .5 }));
    expect(surface.style.transform).toBe(original);
    await tick();
    const first = surface.style.transform;
    expect(first).not.toBe(original);
    const count = renders;
    await tick();
    expect(surface.style.transform).not.toBe(first);
    expect(renders).toBe(count);
    for (let i = 0; i < 50; i++) await tick();
    const settled = surface.style.transform;
    camera!.track({ x: .65, y: .5 });
    expect(surface.style.transform).toBe(settled);
    await tick();
    const following = surface.style.transform;
    await tick();
    expect(surface.style.transform).not.toBe(following);
    await act(async () => camera.inspect(undefined));
    expect(surface.style.transform).not.toBe(original);
    for (let i = 0; i < 70; i++) await tick();
    expect(surface.style.transform).toBe(original);
    expect(callbacks.size).toBe(0);
    await act(async () => camera.inspect("near", { x: .4, y: .5 }));
    await tick();
    await act(async () => camera.zoomIn());
    const gesture = surface.style.transform;
    await tick();
    expect(surface.style.transform).toBe(gesture);
    expect(callbacks.size).toBe(0);
    await act(async () => camera.inspect(undefined));
    expect(callbacks.size).toBeGreaterThan(0);
  } finally {
    await act(async () => root.unmount());
    expect(callbacks.size).toBe(0);
    host.remove(); vi.restoreAllMocks(); vi.unstubAllGlobals();
  }
});

it("follows a truck without rendering every frame and restores the original manually zoomed view", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width: 720, height: 500, left: 0, top: 0 } as DOMRect);
  let camera: ReturnType<typeof useCityMapZoom>;
  let renders = 0;
  function Harness() {
    const ref = useRef<HTMLDivElement>(null);
    camera = useCityMapZoom(ref);
    renders++;
    return <div ref={ref}><div data-map-surface style={camera.style} /><button data-carrier-choice="crew">Truck</button></div>;
  }
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Harness />));
    await act(async () => { camera.zoomIn(); camera.zoomIn(); camera.zoomIn(); });
    const surface = host.querySelector("[data-map-surface]") as HTMLElement;
    const original = surface.style.transform;
    const scale = camera!.scale;
    await act(async () => camera.inspect("crew", { x: .6, y: .5 }));
    expect(camera!.scale).toBeCloseTo(scale);
    const before = surface.style.transform;
    const renderCount = renders;
    camera!.track({ x: .65, y: .55 });
    expect(surface.style.transform).not.toBe(before);
    expect(renders).toBe(renderCount);
    await act(async () => camera.zoomOut());
    expect(camera!.scale).toBeLessThan(scale);
    const zoomed = surface.style.transform;
    camera!.track({ x: .7, y: .6 });
    expect(surface.style.transform).not.toBe(zoomed);
    const viewport = host.firstElementChild as HTMLElement;
    viewport.setPointerCapture = vi.fn();
    viewport.hasPointerCapture = () => false;
    for (const [type, x] of [["pointerdown", 300], ["pointermove", 350], ["pointerup", 350]] as const) {
      await act(async () => {
        const event = new Event(type, { bubbles: true });
        Object.assign(event, { pointerId: 1, pointerType: "mouse", button: 0, clientX: x, clientY: 250 });
        viewport.dispatchEvent(event);
      });
    }
    const dragged = surface.style.transform;
    camera!.track({ x: .4, y: .4 });
    expect(surface.style.transform).toBe(dragged);
    await act(async () => camera.inspect("near", { x: .4, y: .5 }));
    expect(camera!.scale).toBeGreaterThanOrEqual(2.4);
    camera!.track({ x: .45, y: .5 });
    expect(surface.style.transform).not.toBe(dragged);
    // Manual drag becomes the new view to restore after inspecting another truck.
    vi.stubGlobal("matchMedia", () => ({ matches: true }));
    await act(async () => camera.inspect(undefined));
    expect(surface.style.transform).toBe(dragged);
    const truck = host.querySelector("button")!;
    truck.getBoundingClientRect = () => ({ left: 0, top: 0, width: 44, height: 44 }) as DOMRect;
    await act(async () => truck.dispatchEvent(new FocusEvent("focusin", { bubbles: true })));
    expect(surface.style.transform).toBe(dragged);
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});

it("keeps the chosen city point under the fingers while their midpoint moves", () => {
  const start = { scale: 2, x: -30, y: 20 };
  const from = { x: 210, y: 290 };
  const to = { x: 230, y: 300 };
  const next = zoomMapAt(start, bounds, 3, from, to);
  expect((from.x - bounds.cx - start.x) / start.scale).toBeCloseTo(
    (to.x - bounds.cx - next.x) / next.scale,
  );
  expect((from.y - bounds.cy - start.y) / start.scale).toBeCloseTo(
    (to.y - bounds.cy - next.y) / next.scale,
  );
});

it("returns to a centered complete overview and never pans beyond city edges", () => {
  expect(constrainMap({ scale: 0.5, x: 900, y: -900 }, bounds)).toEqual(
    MAP_OVERVIEW,
  );
  expect(constrainMap({ scale: 8, x: 900, y: -900 }, bounds)).toEqual({
    scale: 4,
    x: 540,
    y: -320,
  });
});

it("pinches and drags from a truck without selecting it, then accepts a deliberate tap", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({
    x: 0,
    y: 0,
    left: 0,
    top: 0,
    right: 375,
    bottom: 667,
    width: 375,
    height: 667,
    toJSON() {},
  });
  const select = vi.fn();
  function Harness() {
    const ref = useRef<HTMLDivElement>(null);
    const map = useCityMapZoom(ref, select);
    return (
      <div ref={ref} data-scale={map.scale}>
        <button data-carrier-choice="crew">Фура</button>
        <button onClick={map.reset}>Весь город</button>
      </div>
    );
  }
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Harness />));
    const viewport = host.firstElementChild as HTMLElement;
    viewport.setPointerCapture = vi.fn();
    viewport.hasPointerCapture = () => false;
    const truck = viewport.querySelector("button")!;
    const pointer = async (
      type: string,
      id: number,
      x: number,
      y: number,
      target: Element = viewport,
    ) => {
      await act(async () => {
        const event = new Event(type, { bubbles: true });
        Object.assign(event, {
          pointerId: id,
          pointerType: "touch",
          button: 0,
          clientX: x,
          clientY: y,
        });
        target.dispatchEvent(event);
      });
    };
    await pointer("pointerdown", 1, 140, 310, truck);
    await pointer("pointerdown", 2, 220, 310);
    await pointer("pointermove", 1, 100, 310);
    await pointer("pointermove", 2, 260, 310);
    expect(Number(viewport.dataset.scale)).toBeCloseTo(2);
    await pointer("pointerup", 2, 260, 310);
    await pointer("pointermove", 1, 70, 350);
    await pointer("pointerup", 1, 70, 350);
    truck.dispatchEvent(new MouseEvent("click", { bubbles: true, detail: 1 }));
    expect(select).not.toHaveBeenCalled();
    await act(async () =>
      (viewport.lastElementChild as HTMLButtonElement).click(),
    );
    expect(viewport.dataset.scale).toBe("1");
    await pointer("pointerdown", 3, 140, 310, truck);
    await pointer("pointerup", 3, 140, 310);
    expect(select).toHaveBeenCalledExactlyOnceWith("crew");
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  }
});

it("covers other scene aspect ratios and accepts their choice buttons", async () => {
  vi.stubGlobal("IS_REACT_ACT_ENVIRONMENT", true);
  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockReturnValue({ width: 400, height: 600, left: 0, top: 0 } as DOMRect);
  const select = vi.fn();
  const retry = vi.fn();
  function Harness() {
    const ref = useRef<HTMLDivElement>(null);
    const map = useCityMapZoom(ref, select, { aspectRatio: 2 });
    return <div ref={ref}><div style={map.style} data-surface /><button data-choice-id="place-1">Place</button><button data-choice-id="place-2" disabled>Disabled</button><button data-retry onClick={retry}>Retry</button></div>;
  }
  const host = document.createElement("div");
  document.body.append(host);
  const root = createRoot(host);
  try {
    await act(async () => root.render(<Harness />));
    expect((host.querySelector("[data-surface]") as HTMLElement).style.width).toBe("1200px");
    const viewport = host.firstElementChild as HTMLElement;
    viewport.setPointerCapture = vi.fn();
    viewport.hasPointerCapture = () => false;
    const button = host.querySelector("button")!;
    for (const type of ["pointerdown", "pointerup"]) await act(async () => {
      const event = new Event(type, { bubbles: true });
      Object.assign(event, { pointerId: 1, pointerType: "touch", button: 0, clientX: 200, clientY: 300 });
      button.dispatchEvent(event);
    });
    expect(select).toHaveBeenCalledWith("place-1");
    (host.querySelector("[data-retry]") as HTMLElement).dispatchEvent(new MouseEvent("click", { bubbles: true, detail: 1 }));
    expect(retry).toHaveBeenCalledOnce();
    for (const type of ["pointerdown", "pointerup"]) await act(async () => {
      const event = new Event(type, { bubbles: true });
      Object.assign(event, { pointerId: 2, pointerType: "touch", button: 0, clientX: 200, clientY: 300 });
      host.querySelector("[disabled]")!.dispatchEvent(event);
    });
    expect(select).toHaveBeenCalledTimes(1);
    const surface = host.querySelector("[data-surface]") as HTMLElement;
    const beforeFocus = surface.style.transform;
    button.getBoundingClientRect = () => ({ left: 800, top: 280, width: 40, height: 40 }) as DOMRect;
    await act(async () => button.dispatchEvent(new FocusEvent("focusin", { bubbles: true })));
    expect(surface.style.transform).not.toBe(beforeFocus);
  } finally {
    await act(async () => root.unmount());
    host.remove();
    vi.restoreAllMocks();
  }
});
