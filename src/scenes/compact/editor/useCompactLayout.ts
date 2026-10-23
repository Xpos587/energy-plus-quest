import { useEffect, useLayoutEffect, useState } from "react";
import {
  defaultLayout,
  draftStorageKey,
  parseLayout,
  readLayout,
  type CompactLayout,
} from "../layout";
export function useCompactLayout() {
  const preview =
    typeof window !== "undefined" &&
    new URLSearchParams(window.location.search).get("compactEditor") === "1";
  const [layout, setLayout] = useState<CompactLayout>(() =>
    typeof window === "undefined"
      ? defaultLayout
      : readLayout(window.localStorage, preview ? draftStorageKey : undefined),
  );
  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (
        !preview ||
        event.origin !== window.location.origin ||
        event.source !== window.parent ||
        event.data?.type !== "compact-layout-preview"
      )
        return;
      try {
        setLayout(parseLayout(JSON.stringify(event.data.layout)));
      } catch {
        /* Ignore invalid preview messages. */
      }
    };
    window.addEventListener("message", receive);
    return () => window.removeEventListener("message", receive);
  }, [preview]);
  useLayoutEffect(() => {
    const originals = new Map<
      HTMLElement,
      { translate: string; scale: string; origin: string }
    >();
    const update = () => {
      const profile = window.innerWidth <= 900 ? "mobile" : "desktop";
      for (const [id, alt] of [
        ["energy", "Энергия+"],
        ["company", "Газпром нефть — Газпромнефть-Снабжение"],
      ] as const) {
        for (const node of document.querySelectorAll<HTMLElement>(
          `[data-scene="compact"] img[alt="${alt}"]`,
        )) {
          if (!originals.has(node))
            originals.set(node, {
              translate: node.style.translate,
              scale: node.style.scale,
              origin: node.style.transformOrigin,
            });
          const value = layout.logos[profile][id];
          node.style.translate = `${value.dx}px ${value.dy}px`;
          node.style.scale = String(value.scale);
          node.style.transformOrigin = "center";
        }
      }
    };
    update();
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("resize", update);
      for (const [node, original] of originals) {
        node.style.translate = original.translate;
        node.style.scale = original.scale;
        node.style.transformOrigin = original.origin;
      }
    };
  }, [layout]);
  return layout;
}
