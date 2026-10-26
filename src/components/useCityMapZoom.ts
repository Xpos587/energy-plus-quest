import {
  type CSSProperties,
  type RefObject,
  useLayoutEffect,
  useRef,
  useState,
} from "react";


export type MapView = { scale: number; x: number; y: number };
export type MapBounds = {
  width: number;
  height: number;
  areaWidth: number;
  areaHeight: number;
  cx: number;
  cy: number;
  controlsBottom: number;
};
type Point = { x: number; y: number };
export const MAP_OVERVIEW: MapView = { scale: 1, x: 0, y: 0 };
export const MAX_MAP_ZOOM = 4;

export function constrainMap(view: MapView, bounds: MapBounds): MapView {
  const scale = Math.max(1, Math.min(MAX_MAP_ZOOM, view.scale));
  const xLimit = Math.max(0, (bounds.width * scale - bounds.areaWidth) / 2);
  const yLimit = Math.max(0, (bounds.height * scale - bounds.areaHeight) / 2);
  return {
    scale,
    x: xLimit ? Math.max(-xLimit, Math.min(xLimit, view.x)) : 0,
    y: yLimit ? Math.max(-yLimit, Math.min(yLimit, view.y)) : 0,
  };
}

/** Keep the city point under the gesture midpoint stationary while zooming. */
export function zoomMapAt(
  view: MapView,
  bounds: MapBounds,
  scale: number,
  from: Point,
  to = from,
): MapView {
  const next = Math.max(1, Math.min(MAX_MAP_ZOOM, scale));
  const ratio = next / view.scale;
  return constrainMap(
    {
      scale: next,
      x: to.x - bounds.cx - (from.x - bounds.cx - view.x) * ratio,
      y: to.y - bounds.cy - (from.y - bounds.cy - view.y) * ratio,
    },
    bounds,
  );
}

const emptyBounds: MapBounds = {
  width: 1,
  height: 1 / 1.44,
  areaWidth: 1,
  areaHeight: 1,
  cx: 0,
  cy: 0,
  controlsBottom: 130,
};

export function useCityMapZoom<Choice extends string = string>(
  viewport: RefObject<HTMLElement | null>,
  onSelect?: (id: Choice) => void,
  { aspectRatio = 1.44, enabled = true, fit = "cover" }: { aspectRatio?: number; enabled?: boolean; fit?: "cover" | "contain" } = {},
) {
  const [view, setView] = useState<MapView>(MAP_OVERVIEW);
  const [isZoomed, setIsZoomed] = useState(false);
  const zoomed = useRef(false);
  const [bounds, setBounds] = useState(emptyBounds);
  const liveView = useRef(view);
  const liveBounds = useRef(bounds);
  const inspection = useRef<{ id: Choice; saved: MapView; point: Point; suspended: boolean } | null>(null);
  const restoringFocus = useRef(false);
  const focusFrame = useRef(0);
  const motion = useRef<{ target: MapView; frame: number; time: number } | null>(null);
  const select = useRef(onSelect);
  select.current = onSelect;
  const transform = (next: MapView, area: MapBounds) =>
    `translate(${area.cx - (area.width * next.scale) / 2 + next.x}px, ${area.cy - (area.height * next.scale) / 2 + next.y}px) scale(${next.scale})`;
  const commit = (next: MapView, render = true, frame = false) => {
    if (!frame && motion.current) {
      cancelAnimationFrame(motion.current.frame);
      motion.current = null;
    }
    liveView.current = next;
    const changedScale = Math.abs(next.scale - 1) > .001;
    if (zoomed.current !== changedScale) {
      zoomed.current = changedScale;
      setIsZoomed(changedScale);
    }
    // Decoded video frames update only the transform; React stays out of the
    // frame loop. Subsequent renders read liveView so they cannot rewind it.
    const surface = viewport.current?.querySelector<HTMLElement>("[data-map-surface]");
    if (surface) {
      surface.style.transform = transform(next, liveBounds.current);
      surface.style.setProperty("--map-zoom", String(next.scale));
    }
    viewport.current?.setAttribute("data-map-scale", String(next.scale));
    if (render) setView(next);
  };
  const animateTo = (next: MapView) => {
    const current = liveView.current;
    if (!motion.current && next.scale === current.scale && next.x === current.x && next.y === current.y) return;
    if (typeof matchMedia !== "function" || matchMedia("(prefers-reduced-motion: reduce)").matches) {
      commit(next);
      return;
    }
    if (motion.current) {
      motion.current.target = next;
      return;
    }
    const animation = { target: next, frame: 0, time: performance.now() };
    motion.current = animation;
    const step = (time: number) => {
      if (motion.current !== animation) return;
      const elapsed = Math.max(0, Math.min(64, time - animation.time));
      animation.time = time;
      const current = liveView.current;
      const target = animation.target;
      // Exponential damping is independent of refresh rate. The video supplies
      // roof targets at 24fps; the camera moves between them on every display frame.
      const amount = -Math.expm1(-elapsed / 70);
      const next = {
        scale: current.scale + (target.scale - current.scale) * amount,
        x: current.x + (target.x - current.x) * amount,
        y: current.y + (target.y - current.y) * amount,
      };
      const done = Math.abs(target.scale - next.scale) < .0001 &&
        Math.hypot(target.x - next.x, target.y - next.y) < .05;
      if (done) {
        motion.current = null;
        commit(target, true, true);
      } else {
        commit(next, false, true);
        animation.frame = requestAnimationFrame(step);
      }
    };
    animation.frame = requestAnimationFrame(step);
  };
  const centered = (next: MapView, point: Point) => constrainMap({
    ...next,
    x: (.5 - point.x) * liveBounds.current.width * next.scale,
    y: (.5 - point.y) * liveBounds.current.height * next.scale,
  }, liveBounds.current);
  const releaseInspection = () => {
    if (!inspection.current) return;
    inspection.current = null;
    viewport.current?.dispatchEvent(new Event("scene-map-inspection-release", { bubbles: true }));
  };
  const commitZoom = (next: MapView) => {
    const following = inspection.current;
    commit(following && !following.suspended ? centered(next, following.point) : next);
  };
  const track = (point: Point, snap = false) => {
    const following = inspection.current;
    if (!following) return;
    following.point = point;
    if (!following.suspended) {
      const next = centered(motion.current?.target ?? liveView.current, point);
      if (snap) commit(next);
      else animateTo(next);
    }
  };
  const inspect = (id: Choice | undefined, point?: Point, zoom = 2.4) => {
    const current = inspection.current;
    if (id === current?.id) return;
    if (id && point) {
      inspection.current = { id, point, saved: current?.saved ?? { ...liveView.current }, suspended: false };
      animateTo(centered({ ...liveView.current, scale: Math.max(zoom, liveView.current.scale) }, point));
    } else if (current) {
      inspection.current = null;
      restoringFocus.current = true;
      cancelAnimationFrame(focusFrame.current);
      focusFrame.current = requestAnimationFrame(() => { restoringFocus.current = false; });
      // The surrounding inspection panel may still be resizing. Preserve the
      // snapshot here; the observer constrains it against the restored layout.
      animateTo(current.saved);
    }
  };

  useLayoutEffect(() => {
    const element = viewport.current;
    if (!element) return;
    const measure = () => {
      const rect = element.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      // Maps fill their viewport; bounded diagrams can start with every zone visible.
      const areaWidth = rect.width;
      const areaHeight = rect.height;
      const width = fit === "contain"
        ? Math.min(areaWidth, areaHeight * aspectRatio)
        : Math.max(areaWidth, areaHeight * aspectRatio);
      const next: MapBounds = {
        width,
        height: width / aspectRatio,
        areaWidth,
        areaHeight,
        cx: rect.width / 2,
        cy: rect.height / 2,
        controlsBottom: 0,
      };
      liveBounds.current = next;
      setBounds(next);
      const following = inspection.current;
      if (following && !following.suspended) {
        animateTo(centered(motion.current?.target ?? liveView.current, following.point));
      } else if (motion.current) {
        motion.current.target = constrainMap(motion.current.target, next);
      } else commit(constrainMap(liveView.current, next));
    };
    measure();
    const observer =
      typeof ResizeObserver === "undefined"
        ? undefined
        : new ResizeObserver(measure);
    observer?.observe(element);
    window.addEventListener("resize", measure);
    if (!enabled) return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measure);
    };

    const pointers = new Map<number, Point>();
    let origin = MAP_OVERVIEW;
    let anchor: Point = { x: 0, y: 0 };
    let distance = 0;
    let dragged = false;
    let active = false;
    let candidate: Choice | undefined;
    let wheelTimer = 0;
    const point = (event: { clientX: number; clientY: number }): Point => {
      const rect = element.getBoundingClientRect();
      return { x: event.clientX - rect.left, y: event.clientY - rect.top };
    };
    const middle = () => {
      const [a, b] = [...pointers.values()];
      return b ? { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 } : a;
    };
    const separation = () => {
      const [a, b] = [...pointers.values()];
      return b ? Math.hypot(a.x - b.x, a.y - b.y) : 0;
    };
    const start = () => {
      if (active) return;
      active = true;
      element.dispatchEvent(
        new Event("scene-map-gesture-start", { bubbles: true }),
      );
    };
    const end = () => {
      if (!active) return;
      active = false;
      element.dispatchEvent(
        new Event("scene-map-gesture-end", { bubbles: true }),
      );
    };
    const rebase = () => {
      origin = liveView.current;
      anchor = middle();
      distance = separation();
    };
    const down = (event: PointerEvent) => {
      if (event.pointerType === "mouse" && event.button !== 0) return;
      if ((event.target as Element).closest("button:not([data-carrier-choice]):not([data-choice-id])")) return;
      window.clearTimeout(wheelTimer);
      pointers.set(event.pointerId, point(event));
      if (pointers.size === 1) {
        dragged = false;
        const target = (event.target as Element).closest<HTMLButtonElement>("[data-carrier-choice], [data-choice-id]");
        candidate = target && !target.disabled ? (target.dataset.carrierChoice ?? target.dataset.choiceId) as Choice : undefined;
      } else {
        dragged = true;
        candidate = undefined;
        start();
      }
      rebase();
      element.setPointerCapture(event.pointerId);
    };
    const move = (event: PointerEvent) => {
      if (!pointers.has(event.pointerId)) return;
      pointers.set(event.pointerId, point(event));
      const current = middle();
      if (pointers.size >= 2 && distance > 0) {
        commitZoom(
          zoomMapAt(
            origin,
            liveBounds.current,
            (origin.scale * separation()) / distance,
            anchor,
            current,
          ),
        );
      } else if (
        dragged ||
        Math.hypot(current.x - anchor.x, current.y - anchor.y) > 6
      ) {
        dragged = true;
        candidate = undefined;
        start();
        releaseInspection();
        commit(
          constrainMap(
            {
              ...origin,
              x: origin.x + current.x - anchor.x,
              y: origin.y + current.y - anchor.y,
            },
            liveBounds.current,
          ),
        );
      }
    };
    const up = (event: PointerEvent) => {
      if (!pointers.has(event.pointerId)) return;
      const chosen =
        !dragged && pointers.size === 1 && event.type === "pointerup"
          ? candidate
          : undefined;
      pointers.delete(event.pointerId);
      if (element.hasPointerCapture(event.pointerId))
        element.releasePointerCapture(event.pointerId);
      if (pointers.size) rebase();
      else {
        candidate = undefined;
        end();
      }
      if (chosen) select.current?.(chosen);
    };
    // Pointer selection is handled above, so a swipe can never click a truck.
    // Keyboard/screen-reader activation still uses the button's ordinary click.
    const click = (event: MouseEvent) => {
      if (event.detail > 0 && (event.target as Element).closest("[data-carrier-choice], [data-choice-id]")) {
        event.preventDefault();
        event.stopPropagation();
      }
    };
    const wheel = (event: WheelEvent) => {
      event.preventDefault();
      start();
      const delta =
        event.deltaY *
        (event.deltaMode === 1
          ? 16
          : event.deltaMode === 2
            ? element.clientHeight
            : 1);
      commitZoom(
        zoomMapAt(
          liveView.current,
          liveBounds.current,
          liveView.current.scale * Math.exp(-delta * 0.003),
          point(event),
        ),
      );
      window.clearTimeout(wheelTimer);
      wheelTimer = window.setTimeout(end, 220);
    };
    const key = (event: KeyboardEvent) => {
      if (event.target !== element) return;
      const current = liveView.current;
      const area = liveBounds.current;
      if (
        [
          "+",
          "=",
          "-",
          "0",
          "Home",
          "ArrowLeft",
          "ArrowRight",
          "ArrowUp",
          "ArrowDown",
        ].includes(event.key)
      )
        event.preventDefault();
      if (event.key === "+" || event.key === "=")
        commitZoom(
          zoomMapAt(current, area, current.scale * 1.4, {
            x: area.cx,
            y: area.cy,
          }),
        );
      else if (event.key === "-")
        commitZoom(
          zoomMapAt(current, area, current.scale / 1.4, {
            x: area.cx,
            y: area.cy,
          }),
        );
      else if (event.key === "0" || event.key === "Home") {
        releaseInspection();
        commit(MAP_OVERVIEW);
      } else if (event.key.startsWith("Arrow")) {
        releaseInspection();
        commit(
          constrainMap(
            {
              ...current,
              x:
                current.x +
                (event.key === "ArrowLeft"
                  ? 60
                  : event.key === "ArrowRight"
                    ? -60
                    : 0),
              y:
                current.y +
                (event.key === "ArrowUp"
                  ? 60
                  : event.key === "ArrowDown"
                    ? -60
                    : 0),
            },
            area,
          ),
        );
      }
    };
    const focus = (event: FocusEvent) => {
      if (pointers.size || inspection.current || restoringFocus.current || motion.current || !(event.target instanceof Element)) return;
      const target = event.target.closest<HTMLElement>("[data-carrier-choice], [data-choice-id]");
      if (!target) return;
      const rect = target.getBoundingClientRect();
      const viewportRect = element.getBoundingClientRect();
      const area = liveBounds.current;
      const current = liveView.current;
      commit(constrainMap({
        ...current,
        x: current.x + area.cx - (rect.left - viewportRect.left + rect.width / 2),
        y: current.y + area.cy - (rect.top - viewportRect.top + rect.height / 2),
      }, area));
    };
    const cancel = () => {
      pointers.clear();
      candidate = undefined;
      dragged = true;
      window.clearTimeout(wheelTimer);
      end();
    };
    element.addEventListener("pointerdown", down);
    element.addEventListener("pointermove", move);
    element.addEventListener("pointerup", up);
    element.addEventListener("pointercancel", up);
    element.addEventListener("lostpointercapture", up);
    element.addEventListener("click", click, true);
    element.addEventListener("wheel", wheel, { passive: false });
    element.addEventListener("keydown", key);
    element.addEventListener("focusin", focus);
    window.addEventListener("blur", cancel);
    return () => {
      cancel();
      cancelAnimationFrame(focusFrame.current);
      if (motion.current) cancelAnimationFrame(motion.current.frame);
      motion.current = null;
      observer?.disconnect();
      window.removeEventListener("resize", measure);
      element.removeEventListener("pointerdown", down);
      element.removeEventListener("pointermove", move);
      element.removeEventListener("pointerup", up);
      element.removeEventListener("pointercancel", up);
      element.removeEventListener("lostpointercapture", up);
      element.removeEventListener("click", click, true);
      element.removeEventListener("wheel", wheel);
      element.removeEventListener("keydown", key);
      element.removeEventListener("focusin", focus);
      window.removeEventListener("blur", cancel);
    };
  }, [viewport, aspectRatio, enabled, fit]);

  const zoom = (factor: number) => {
    const area = liveBounds.current;
    commitZoom(
      zoomMapAt(liveView.current, area, liveView.current.scale * factor, {
        x: area.cx,
        y: area.cy,
      }),
    );
  };
  return {
    scale: view.scale,
    isZoomed,
    isOverview: view.scale === 1 && view.x === 0 && view.y === 0,
    bounds,
    inspect,
    track,
    zoomIn: () => zoom(1.4),
    zoomOut: () => zoom(1 / 1.4),
    reset: () => {
      releaseInspection();
      commit(MAP_OVERVIEW);
    },
    style: {
      width: `${bounds.width}px`,
      height: `${bounds.height}px`,
      transform: transform(liveView.current, bounds),
      "--map-zoom": liveView.current.scale,
    } as CSSProperties,
  };
}
