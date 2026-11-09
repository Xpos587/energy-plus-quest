import { useEffect, useRef, useState } from "react";
import { SoftGlow } from "../SoftGlow";
import type { SceneContext } from "../types";
import styles from "./WarehouseZones.module.css";
import { warehouseChoices } from "./warehouseZones";
import { warehouseContour, warehouseDrawing, type WarehouseComposition } from "./callouts";

type WarehouseZonesProps = {
  context: SceneContext;
  selectedId?: string;
  onSelect?: (id: string) => void;
  focusedId?: string;
  onFocusChange?: (id: string | undefined) => void;
  composition?: WarehouseComposition;
};

/**
 * Pointing at a choice (mouse, finger or keyboard) lights a soft glow around its shape; the rest
 * of the hall is never darkened (Teo 03.11: highlight the choice, don't hide the others).
 * Contours are the hit regions; the numbered pins are WorldArt's markers.
 */
export function WarehouseZones({ context, selectedId, onSelect, focusedId, onFocusChange, composition = "wide" }: WarehouseZonesProps) {
  const contours = warehouseDrawing(composition);
  const root = useRef<HTMLDivElement>(null);
  const [keyboardId, setKeyboardId] = useState<string>();
  // Keyboard focus on a pin lights the same glow as pointing at the object.
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
  const lit = onSelect ? (selectedId ?? keyboardId ?? focusedId) as typeof warehouseChoices[number] | undefined : undefined;
  const litPath = lit && warehouseChoices.includes(lit) ? warehouseContour(lit, context.parcel, composition).path : undefined;
  return (
    <div ref={root} className={styles.overlay} data-warehouse-annotations data-warehouse-lit={onSelect ? lit ?? "all" : undefined} aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${contours.width} ${contours.height}`} focusable="false" aria-hidden="true">
        {litPath && <SoftGlow className={styles.glow} data-warehouse-glow={lit} d={litPath} />}
        {warehouseChoices.map(id => {
          const contour = warehouseContour(id, context.parcel, composition);
          const interactive = !!onSelect && (!selectedId || selectedId === id);
          return (
            <path
                key={id}
                className={styles.zone}
                data-warehouse-zone={id}
                data-warehouse-contour={contour.key}
                data-warehouse-hitarea
                data-active={selectedId === id}
                data-focused={focusedId === id || undefined}
                data-interactive={interactive}
                onClick={interactive ? () => onSelect?.(id) : undefined}
                onPointerEnter={onFocusChange && (() => onFocusChange(id))}
                onPointerLeave={onFocusChange && (() => onFocusChange(undefined))}
                d={contour.path}
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />
          );
        })}
      </svg>
    </div>
  );
}
