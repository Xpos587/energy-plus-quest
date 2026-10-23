import { type RefObject, useLayoutEffect } from "react";

/** Keep the preview clear of the selected labels and warehouse endpoints. */
export function useInspectionPlacement(
  heading: RefObject<HTMLHeadingElement | null>,
  selectionKey: string,
  trigger?: HTMLElement | null,
) {
  // biome-ignore lint/correctness/useExhaustiveDependencies: reset occlusion and placement for every newly inspected option.
  useLayoutEffect(() => {
    const card = heading.current?.closest<HTMLElement>(
      "[data-choice-inspection]",
    );
    const frame = card?.parentElement;
    if (!card || !frame) return;
    const selectedArtwork = () => [...frame.querySelectorAll<HTMLElement>(
      '[data-choice-id][aria-pressed="true"], [data-carrier-choice][aria-pressed="true"]',
    )];
    if (trigger?.hasAttribute("data-scene-choice")) {
      const targets = selectedArtwork();
      const artwork = targets.find(target => !target.hasAttribute("data-callout-target")) ?? targets[0];
      artwork?.focus({ preventScroll: true });
    }
    const place = () => {
      // The edge-to-edge shell reserves a grid cell for the preview.
      // Only floating layouts need position and occlusion calculations.
      if (getComputedStyle(frame).display === "grid") {
        card.style.removeProperty("left");
        card.style.removeProperty("top");
        card.style.removeProperty("right");
        card.style.removeProperty("bottom");
        card.style.removeProperty("max-height");
        return;
      }
      const bounds = frame.getBoundingClientRect();
      const gap = bounds.width <= 600 ? 12 : 24;
      const header = frame.querySelector("[data-scene-briefing] > div");
      const top = Math.max(
        124,
        (header?.getBoundingClientRect().bottom ?? 100) - bounds.top + 12,
      );
      card.style.maxHeight = `${Math.max(120, bounds.height - top - gap)}px`;
      const { width, height } = card.getBoundingClientRect();
      const candidatesForPlacement = selectedArtwork();
      if (trigger && !candidatesForPlacement.includes(trigger)) candidatesForPlacement.push(trigger);
      candidatesForPlacement.forEach(target => target.removeAttribute("data-inspection-occluded"));
      const targets = candidatesForPlacement.filter(el => {
        const style = getComputedStyle(el);
        return el.getClientRects().length && style.visibility !== "hidden" && style.visibility !== "collapse" && style.display !== "none";
      });
      const rects = targets.map((el) => el.getBoundingClientRect());
      const overlap = (x: number, y: number) =>
        rects.reduce(
          (sum, r) =>
            sum +
            Math.max(
              0,
              Math.min(x + width + 12, r.right - bounds.left) -
                Math.max(x - 12, r.left - bounds.left),
            ) *
              Math.max(
                0,
                Math.min(y + height + 12, r.bottom - bounds.top) -
                  Math.max(y - 12, r.top - bounds.top),
              ),
          0,
        );
      const bottom = Math.max(top, bounds.height - height - gap);
      const right = Math.max(gap, bounds.width - width - gap);
      const candidates = [
        [right, bottom],
        [gap, bottom],
        [right, top],
        [gap, top],
      ];
      candidates.sort((a, b) => overlap(a[0], a[1]) - overlap(b[0], b[1]));
      const [x, y] = candidates[0];
      card.style.left = `${x}px`;
      card.style.top = `${y}px`;
      card.style.right = "auto";
      card.style.bottom = "auto";
      // Very small screens may have no free corner. Never leave a clipped,
      // apparently usable label peeking out from behind the preview.
      targets.forEach((target) => {
        const r = target.getBoundingClientRect();
        const covered =
          r.right > bounds.left + x &&
          r.left < bounds.left + x + width &&
          r.bottom > bounds.top + y &&
          r.top < bounds.top + y + height;
        target.toggleAttribute("data-inspection-occluded", covered);
      });
    };
    place();
    const observer =
      typeof ResizeObserver === "undefined"
        ? undefined
        : new ResizeObserver(place);
    observer?.observe(card);
    observer?.observe(frame);
    frame.addEventListener("scroll", place, true);
    return () => {
      observer?.disconnect();
      frame.removeEventListener("scroll", place, true);
      frame.querySelectorAll("[data-inspection-occluded]").forEach((el) => {
        el.removeAttribute("data-inspection-occluded");
      });
    };
  }, [heading, selectionKey, trigger]);
}
