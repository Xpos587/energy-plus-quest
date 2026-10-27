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

/** Native illustration contours keep highlighting and hit regions on the same objects. */
export function WarehouseZones({ context, selectedId, onSelect, focusedId, onFocusChange, composition = "wide" }: WarehouseZonesProps) {
  const contours = warehouseDrawing(composition);
  return (
    <div className={styles.overlay} data-warehouse-annotations aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${contours.width} ${contours.height}`} focusable="false" aria-hidden="true">
        {warehouseChoices.map(id => {
          const contour = warehouseContour(id, context.parcel, composition);
          const interactive = !!onSelect && (!selectedId || selectedId === id);
          return (
            <g key={id}>
              <path className={styles.understroke} d={contour.path} vectorEffect="non-scaling-stroke" />
              <path
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
            </g>
          );
        })}
      </svg>
    </div>
  );
}
