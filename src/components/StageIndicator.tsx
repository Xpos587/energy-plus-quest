import { Fragment } from "react";
import { stageIcons } from "./stageProgress";
import styles from "./StageIndicator.module.css";

const stops = Object.values(stageIcons);

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
