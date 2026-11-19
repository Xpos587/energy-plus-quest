import { useEffect, useRef, useState } from "react";
import { SoftGlow } from "../SoftGlow";
import contours from "./segmentedContours.json";
import styles from "./LastmileZones.module.css";

type Props = {
  composition: "wide" | "tall";
  selectedId?: string;
  onSelect?: (id: string) => void;
  focusedId?: string;
  onFocusChange?: (id: string | undefined) => void;
};
const ids = ["helicopter", "rover", "robot", "pipe-carrier"] as const;

/** Centre and radius of a contour (paths are absolute M/L/Z polygons). */
function bounds(path: string) {
  const n = path.match(/-?\d+(\.\d+)?/g)!.map(Number);
  const xs = n.filter((_, i) => i % 2 === 0), ys = n.filter((_, i) => i % 2 === 1);
  const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, r: Math.max(x1 - x0, y1 - y0) / 2 };
}
// Preferred ring floor in plate px; nearby vehicles can cap it without shrinking tap targets.
const ringMin = 82;

/**
 * The vehicles themselves are the tap targets, without name tags. Untried vehicles
 * breathe with a soft ring; pointing at one (mouse or keyboard) lights it with a glow around its
 * shape — the rest of the map is never darkened (03.11: highlight the choice, don't hide the others).
 * Full-art coordinates keep masks aligned across the two map compositions.
 */
export function LastmileZones({ composition, selectedId, onSelect, focusedId, onFocusChange }: Props) {
  const drawing = contours[composition];
  const centres = ids.map(id => bounds(drawing.regions[id].path));
  const root = useRef<HTMLDivElement>(null);
  const [seen, setSeen] = useState<string[]>([]);
  const [keyboardId, setKeyboardId] = useState<string>();
  useEffect(() => { if (selectedId) setSeen(s => s.includes(selectedId) ? s : [...s, selectedId]); }, [selectedId]);
  // The marker buttons stay invisible; keyboard focus shows as the same vehicle highlight.
  useEffect(() => {
    const stage = root.current?.closest("figure");
    if (!stage) return;
    const on = (e: FocusEvent) => {
      const el = e.target as HTMLElement;
      setKeyboardId(el.matches?.("[data-hotspot]:focus-visible") ? el.dataset.hotspot : undefined);
    };
    const off = () => setKeyboardId(undefined);
    stage.addEventListener("focusin", on);
    stage.addEventListener("focusout", off);
    return () => { stage.removeEventListener("focusin", on); stage.removeEventListener("focusout", off); };
  }, []);
  const lit = selectedId ?? keyboardId ?? focusedId;
  return (
    <div ref={root} className={styles.overlay} data-lastmile-annotations data-lastmile-selection={selectedId} data-lastmile-lit={lit} aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${drawing.width} ${drawing.height}`} focusable="false">
        {lit && <SoftGlow className={styles.glow} data-lastmile-glow={lit} d={drawing.regions[lit as typeof ids[number]].path} />}
        {ids.map((id, i) => {
          const b = centres[i];
          const nearest = Math.min(...centres.filter(other => other !== b)
            .map(other => Math.hypot(b.cx - other.cx, b.cy - other.cy)));
          // Reserve a gap at breathe's 1.15x peak, for either artwork composition.
          const radius = Math.min(Math.max(b.r * .8, ringMin), nearest * .48 / 1.15);
          const idle = !lit && !selectedId && !seen.includes(id);
          return (
            <g key={id} data-lastmile-object={id} data-active={selectedId === id} data-focused={focusedId === id || undefined}>
              {idle && <circle className={styles.ripple} data-lastmile-ripple={id} cx={b.cx} cy={b.cy} r={radius} style={{ animationDelay: `${i * .7}s` }} />}
              <path
                className={styles.zone}
                data-lastmile-zone={id}
                data-interactive={!!onSelect}
                onClick={onSelect ? () => onSelect(id) : undefined}
                onPointerEnter={onFocusChange && (() => onFocusChange(id))}
                onPointerLeave={onFocusChange && (() => onFocusChange(undefined))}
                d={drawing.regions[id].path}
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
