import { useId } from "react";
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
 * The busy hall is softly dimmed except the four choices; pointing at one leaves only
 * that one lit. Contours are the hit regions; the numbered pins are WorldArt's markers.
 */
export function WarehouseZones({ context, selectedId, onSelect, focusedId, onFocusChange, composition = "wide" }: WarehouseZonesProps) {
  const contours = warehouseDrawing(composition);
  const hole = `warehouse-hole-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const lit = selectedId ?? focusedId;
  const spotlight = !!onSelect;
  const holes = lit ? [lit] : warehouseChoices;
  return (
    <div className={styles.overlay} data-warehouse-annotations data-warehouse-lit={spotlight ? lit ?? "all" : undefined} aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${contours.width} ${contours.height}`} focusable="false" aria-hidden="true">
        {spotlight && (
          <>
            <defs>
              <filter id={`${hole}f`} x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14" /></filter>
              <mask id={hole} maskUnits="userSpaceOnUse" x="0" y="0" width={contours.width} height={contours.height}>
                <rect width={contours.width} height={contours.height} fill="white" />
                {holes.map(id => (
                  <path key={id} d={warehouseContour(id as typeof warehouseChoices[number], context.parcel, composition).path} fill="black" stroke="black" strokeWidth="40" strokeLinejoin="round" filter={`url(#${hole}f)`} />
                ))}
              </mask>
            </defs>
            <rect className={styles.scrim} data-lit={!!lit} width={contours.width} height={contours.height} mask={`url(#${hole})`} />
          </>
        )}
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
