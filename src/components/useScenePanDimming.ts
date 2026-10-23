import { useEffect, useState } from "react";

type Gesture = {
  pointerId: number;
  viewport: HTMLElement;
  startX: number;
  startY: number;
};

/** Emphasize the artwork throughout a pan, including a held touch at rest. */
export function useScenePanDimming<T extends HTMLElement>() {
  const [root, setRoot] = useState<T | null>(null);

  useEffect(() => {
    if (!root) return;

    let gesture: Gesture | undefined;
    let touchViewport: HTMLElement | undefined;
    let intendedViewport: HTMLElement | undefined;
    let activeViewport: HTMLElement | undefined;
    let intentUntil = 0;
    let clearTimer = 0;
    const previousScroll = new WeakMap<HTMLElement, number>();

    const viewportFrom = (target: EventTarget | null) =>
      target instanceof Element
        ? target.closest<HTMLElement>("[data-pan-viewport]")
        : null;
    const movable = (viewport: HTMLElement) =>
      viewport.scrollWidth - viewport.clientWidth > 1;
    const setActive = (viewport: HTMLElement) => {
      window.clearTimeout(clearTimer);
      activeViewport = viewport;
      root.dataset.scenePanning = "true";
      viewport.dispatchEvent(new Event("scene-pan-start"));
    };
    const clearLater = () => {
      window.clearTimeout(clearTimer);
      if (gesture || touchViewport) return;
      clearTimer = window.setTimeout(() => {
        activeViewport = undefined;
        root.removeAttribute("data-scene-panning");
      }, 220);
    };
    const onPointerDown = (event: PointerEvent) => {
      const viewport = viewportFrom(event.target);
      if (!viewport || !movable(viewport)) return;
      if (
        event.pointerType === "mouse" &&
        (event.button !== 0 || (event.target as Element).closest("button"))
      )
        return;
      window.clearTimeout(clearTimer);
      gesture = {
        pointerId: event.pointerId,
        viewport,
        startX: event.clientX,
        startY: event.clientY,
      };
      previousScroll.set(viewport, viewport.scrollLeft);
    };
    const onPointerMove = (event: PointerEvent) => {
      if (!gesture || event.pointerId !== gesture.pointerId) return;
      const deltaX = event.clientX - gesture.startX;
      const deltaY = event.clientY - gesture.startY;
      if (Math.abs(deltaX) > 8 && Math.abs(deltaX) > Math.abs(deltaY) * 1.15)
        setActive(gesture.viewport);
    };
    const onPointerEnd = (event: PointerEvent) => {
      if (!gesture || event.pointerId !== gesture.pointerId) return;
      intendedViewport = gesture.viewport;
      intentUntil = performance.now() + 350;
      gesture = undefined;
      if (activeViewport) clearLater();
    };
    const onTouchStart = (event: TouchEvent) => {
      const viewport = viewportFrom(event.target);
      if (!viewport || !movable(viewport)) return;
      touchViewport = viewport;
      window.clearTimeout(clearTimer);
    };
    const onTouchEnd = (event: TouchEvent) => {
      if (event.touches.length || !touchViewport) return;
      intendedViewport = touchViewport;
      intentUntil = performance.now() + 350;
      touchViewport = undefined;
      if (activeViewport) clearLater();
    };
    const onWheel = (event: WheelEvent) => {
      const viewport = viewportFrom(event.target);
      if (!viewport || !movable(viewport)) return;
      if (
        Math.abs(event.deltaX) < 2 ||
        Math.abs(event.deltaX) < Math.abs(event.deltaY) * 0.65
      )
        return;
      intendedViewport = viewport;
      intentUntil = performance.now() + 300;
      previousScroll.set(viewport, viewport.scrollLeft);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      const viewport = viewportFrom(event.target);
      if (!viewport || !movable(viewport)) return;
      intendedViewport = viewport;
      intentUntil = performance.now() + 300;
      previousScroll.set(viewport, viewport.scrollLeft);
    };
    const onScroll = (event: Event) => {
      const viewport = event.target;
      if (
        !(viewport instanceof HTMLElement) ||
        !viewport.matches("[data-pan-viewport]")
      )
        return;
      const previous = previousScroll.get(viewport);
      const changed =
        previous === undefined ||
        Math.abs(viewport.scrollLeft - previous) > 0.5;
      previousScroll.set(viewport, viewport.scrollLeft);
      if (!changed) return;
      if (
        gesture?.viewport === viewport ||
        touchViewport === viewport ||
        activeViewport === viewport ||
        (intendedViewport === viewport && performance.now() < intentUntil)
      ) {
        setActive(viewport);
        if (!gesture) clearLater();
      }
    };
    const onMapStart = (event: Event) => {
      if (event.target instanceof HTMLElement) setActive(event.target);
    };
    const onMapEnd = () => clearLater();
    const onBlur = () => {
      gesture = undefined;
      touchViewport = undefined;
      intendedViewport = undefined;
      window.clearTimeout(clearTimer);
      activeViewport = undefined;
      root.removeAttribute("data-scene-panning");
    };

    root.addEventListener("pointerdown", onPointerDown, true);
    root.addEventListener("scene-map-gesture-start", onMapStart);
    root.addEventListener("scene-map-gesture-end", onMapEnd);
    root.addEventListener("touchstart", onTouchStart, {
      capture: true,
      passive: true,
    });
    window.addEventListener("touchend", onTouchEnd, true);
    window.addEventListener("touchcancel", onTouchEnd, true);
    root.addEventListener("pointermove", onPointerMove, true);
    root.addEventListener("wheel", onWheel, { capture: true, passive: true });
    root.addEventListener("keydown", onKeyDown, true);
    root.addEventListener("scroll", onScroll, true);
    window.addEventListener("pointerup", onPointerEnd, true);
    window.addEventListener("pointercancel", onPointerEnd, true);
    window.addEventListener("blur", onBlur);
    return () => {
      onBlur();
      root.removeEventListener("pointerdown", onPointerDown, true);
      root.removeEventListener("scene-map-gesture-start", onMapStart);
      root.removeEventListener("scene-map-gesture-end", onMapEnd);
      root.removeEventListener("touchstart", onTouchStart, true);
      window.removeEventListener("touchend", onTouchEnd, true);
      window.removeEventListener("touchcancel", onTouchEnd, true);
      root.removeEventListener("pointermove", onPointerMove, true);
      root.removeEventListener("wheel", onWheel, true);
      root.removeEventListener("keydown", onKeyDown, true);
      root.removeEventListener("scroll", onScroll, true);
      window.removeEventListener("pointerup", onPointerEnd, true);
      window.removeEventListener("pointercancel", onPointerEnd, true);
      window.removeEventListener("blur", onBlur);
    };
  }, [root]);

  return setRoot;
}
