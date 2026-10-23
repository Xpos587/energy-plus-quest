import { type PointerEvent, useLayoutEffect, useRef } from "react";

/** Fullscreen results are inspected in place; keep the initial crop centered. */
export function usePanoramicResult<T extends HTMLElement = HTMLElement>() {
  const ref = useRef<T>(null);
  useLayoutEffect(() => {
    const viewport = ref.current;
    if (!viewport) return;
    let previousMax = -1;
    const position = () => {
      const max = Math.max(0, viewport.scrollWidth - viewport.clientWidth);
      if (max === previousMax) return;
      const progress =
        previousMax > 0 ? viewport.scrollLeft / previousMax : 0.5;
      viewport.scrollLeft = max * progress;
      previousMax = max;
    };
    position();
    const observer =
      typeof ResizeObserver === "undefined"
        ? undefined
        : new ResizeObserver(position);
    observer?.observe(viewport);
    const image = viewport.querySelector("img");
    if (image) observer?.observe(image);
    viewport.addEventListener("load", position, true);
    return () => {
      observer?.disconnect();
      viewport.removeEventListener("load", position, true);
    };
  }, []);
  return {
    ref,
    tabIndex: 0,
    "data-pan-viewport": true,
    onPointerDown(event: PointerEvent<HTMLElement>) {
      if (
        event.pointerType !== "mouse" ||
        event.button !== 0 ||
        (event.target as Element).closest("button")
      )
        return;
      event.currentTarget.setPointerCapture(event.pointerId);
      event.currentTarget.focus({ preventScroll: true });
    },
    onPointerMove(event: PointerEvent<HTMLElement>) {
      if (
        event.pointerType === "mouse" &&
        event.currentTarget.hasPointerCapture(event.pointerId)
      )
        event.currentTarget.scrollBy(-event.movementX, 0);
    },
    onPointerUp(event: PointerEvent<HTMLElement>) {
      if (event.currentTarget.hasPointerCapture(event.pointerId))
        event.currentTarget.releasePointerCapture(event.pointerId);
    },
  };
}
