import { MapPin } from "lucide-react";
import { imageAsset } from "../game/imageAssets";
import styles from "./StageIndicator.module.css";

/* Real artwork of every stage: the intro route sheet and the header progress
 * show the same five stops, so the player recognises where they are. */
export const routeArt = {
  carrier: imageAsset("opening/route-v1/carrier.webp"),
  loading: imageAsset("opening/route-v1/loading.webp"),
  warehouse: imageAsset("opening/route-v1/warehouse.webp"),
  barge: imageAsset("opening/route-v1/barge.webp"),
  "last-mile": imageAsset("opening/route-v1/lastmile.webp"),
} as const;
const stops = Object.values(routeArt);

/** Header progress (meeting 29.10, call 02.11): the intro route in miniature —
 * passed stops dimmed and ticked, the current one large, the rest ahead, then
 * the destination. The text stays for screen readers and narrow screens. */
export function StageIndicator({ step, total, label }: { step: number; total: number; label: string }) {
  return (
    <span className={styles.indicator} data-scene-progress aria-label={`Этап ${step} из ${total}: ${label}`}>
      <span className={styles.route} aria-hidden="true">
        {stops.slice(0, total).map((src, index) => (
          <i key={src} data-leg={index < step - 1 ? "done" : index === step - 1 ? "current" : undefined}>
            <img src={src} alt="" />
          </i>
        ))}
        <MapPin className={styles.goal} size={16} strokeWidth={2.4} />
      </span>
      <span className={styles.count} data-progress-count>Этап {step}/{total}</span>
    </span>
  );
}
