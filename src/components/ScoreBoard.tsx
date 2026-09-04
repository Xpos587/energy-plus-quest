import type { CSSProperties } from "react";
import efficiencyIconUrl from "../../design/scene-01/assets/feedback-v5/production/metrics/efficiency.webp";
import empathyIconUrl from "../../design/scene-01/assets/feedback-v5/production/metrics/empathy-no-border.webp";
import energyIconUrl from "../../design/scene-01/assets/feedback-v5/production/metrics/energy.webp";
import styles from "../App.module.css";
import type { Scores } from "../game/types";

const scoreItems: Array<{
  key: keyof Scores;
  iconUrl: string;
  label: string;
}> = [
  { key: "energy", iconUrl: energyIconUrl, label: "Энергия" },
  { key: "empathy", iconUrl: empathyIconUrl, label: "Эмпатия" },
  {
    key: "efficiency",
    iconUrl: efficiencyIconUrl,
    label: "Эффективность",
  },
];

export function ScoreDelta({ scores }: { scores: Scores }) {
  return (
    <fieldset className={styles.scoreDelta} aria-label="Изменение показателей">
      {scoreItems.map((item) => (
        <div
          data-score-key={item.key}
          data-direction={deltaDirection(scores[item.key])}
          key={item.key}
        >
          <span>
            <img
              alt=""
              aria-hidden="true"
              className={styles.deltaIcon}
              data-score-art="feedback-v5"
              src={item.iconUrl}
            />
            <em className={styles.deltaLabel}>{item.label}</em>
          </span>
          <strong data-positive={scores[item.key] > 0}>
            {formatScore(scores[item.key])}
          </strong>
          <i aria-hidden="true" className={styles.deltaTrack}>
            <b
              className={styles.deltaFill}
              style={
                {
                  "--delta-fill": `${String(deltaFill(scores[item.key]))}%`,
                } as CSSProperties
              }
            />
          </i>
        </div>
      ))}
    </fieldset>
  );
}

function formatScore(value: number) {
  return value > 0 ? `+${value}` : String(value);
}

function deltaFill(value: number) {
  return Math.min(50, (Math.abs(value) / 5) * 50);
}

function deltaDirection(value: number) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}
