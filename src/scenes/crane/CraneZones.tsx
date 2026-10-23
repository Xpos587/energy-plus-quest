import type { MouseEvent } from "react";
import styles from "./CraneZones.module.css";
import contours from "./segmentedContours.json";

type CraneZonesProps = {
  composition: "wide" | "tall";
  selectedId?: string;
  onSelect?: (id: string) => void;
};

const regionIds = ["crane", "petr", "remote"] as const;

/** Both numbered crane actions share one physical object and one silhouette. */
export function CraneZones({ composition, selectedId, onSelect }: CraneZonesProps) {
  const drawing = contours[composition];
  // The hit regions follow the revised illustration, without painting a route
  // or a silhouette over the ship and cranes.
  const offsets = composition === "wide"
    ? { crane: -190, petr: -210, remote: -20 }
    : { crane: -70, petr: 0, remote: 0 };
  const selectedRegion = selectedId === "rush" || selectedId === "wait" ? "crane" : selectedId;
  function focusCraneChoice(event: MouseEvent<SVGPathElement>) {
    const plane = event.currentTarget.closest("[data-world-plane]");
    const preferredAction = selectedId === "wait" ? "wait" : "rush";
    plane?.querySelector<HTMLButtonElement>(`button[data-hotspot="${preferredAction}"]`)?.focus();
  }
  return (
    <div className={styles.overlay} data-crane-annotations data-crane-selection={selectedId} aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${drawing.width} ${drawing.height}`} focusable="false" aria-hidden="true">
        {regionIds.map(id => {
          const interactive = !!onSelect && (!selectedRegion || selectedRegion === id);
          return (
            <g key={id} transform={`translate(${offsets[id]} 0)`}>
              <path
                className={styles.zone}
                data-crane-zone={id}
                data-active={selectedRegion === id}
                data-interactive={interactive}
                onClick={interactive ? id === "crane" ? focusCraneChoice : () => onSelect?.(id) : undefined}
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
