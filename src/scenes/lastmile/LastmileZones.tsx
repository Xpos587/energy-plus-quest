import contours from "./segmentedContours.json";
import styles from "./LastmileZones.module.css";

type Props = {
  composition: "wide" | "tall";
  selectedId?: string;
  onSelect?: (id: string) => void;
};
const ids = ["helicopter", "rover", "robot", "pipe-carrier"] as const;

/** Full-art coordinates keep masks aligned across the two map compositions. */
export function LastmileZones({ composition, selectedId, onSelect }: Props) {
  const drawing = contours[composition];
  return (
    <div className={styles.overlay} data-lastmile-annotations data-lastmile-selection={selectedId} aria-hidden="true">
      <svg className={styles.drawing} viewBox={`0 0 ${drawing.width} ${drawing.height}`} focusable="false">
        {ids.map(id => (
          <g key={id} data-lastmile-object={id} data-active={selectedId === id}>
            <path className={styles.understroke} d={drawing.regions[id].path} vectorEffect="non-scaling-stroke" />
            <path
              className={styles.zone}
              data-lastmile-zone={id}
              data-interactive={!!onSelect && (!selectedId || selectedId === id)}
              onClick={onSelect && (!selectedId || selectedId === id) ? () => onSelect(id) : undefined}
              d={drawing.regions[id].path}
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />
          </g>
        ))}
      </svg>
    </div>
  );
}
