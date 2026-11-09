import { Fragment } from "react";
import { imageAsset } from "../game/imageAssets";
import styles from "./StageIndicator.module.css";

/* Real artwork of every stage: the intro route sheet and the header progress
 * show the same stops, so the player recognises where they are. */
export const routeArt = {
  carrier: imageAsset("opening/route-v1/carrier.webp"),
  loading: imageAsset("opening/route-v1/loading.webp"),
  warehouse: imageAsset("opening/route-v1/warehouse.webp"),
  barge: imageAsset("opening/route-v1/barge.webp"),
  "last-mile": imageAsset("opening/route-v1/lastmile.webp"),
} as const;
/* Header-only icons (Teo, 03.11): one big object per stage, so it still
 * reads at 26 px on a phone where the route pictures turn into noise. */
const stops = ["carrier", "loading", "warehouse", "barge", "lastmile"].map((key) =>
  imageAsset(`opening/stage-icons-v1/${key}.webp`),
);

/** Header progress (meeting 29.10, call 02.11): the intro route in miniature.
 * Every stop shows its stage object: passed ones ticked, the current one
 * large, the ones ahead pale. No caption: the
 * route itself says how far is left; the stage is named for screen readers. */
export function StageIndicator({ step, total, label }: { step: number; total: number; label: string }) {
  return (
    <span className={styles.indicator} data-scene-progress role="img" aria-label={`Этап ${step} из ${total}: ${label}`}>
      {stops.slice(0, total).map((src, index) => {
        const leg = index < step - 1 ? "done" : index === step - 1 ? "current" : "ahead";
        return (
          <Fragment key={src}>
            {index > 0 && <b data-leg={index < step ? "done" : "ahead"} />}
            <i data-leg={leg}><img src={src} alt="" /></i>
          </Fragment>
        );
      })}
    </span>
  );
}
