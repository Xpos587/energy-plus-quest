import styles from "../App.module.css";
import { ChartLine, Heart, Zap } from "lucide-react";
import type { Scores } from "../game/types";

const scoreItems = [
  { key: "energy", label: "Энергия", icon: Zap },
  {
    key: "empathy",
    label: "Эмпатия",
    icon: Heart,
  },
  {
    key: "efficiency",
    label: "Эффективность",
    icon: ChartLine,
  },
] as const;

export function ScoreDelta({ scores }: { scores: Scores }) {
  return (
    <fieldset className={styles.scoreDelta} data-score-delta aria-label="Изменение показателей">
      {scoreItems.map((item) => (
        <div data-score-key={item.key} key={item.key}>
          <span>
            <item.icon
              aria-hidden="true"
              className={styles.deltaIcon}
              size={24}
              strokeWidth={2}
            />
            <strong
              data-positive={scores[item.key] > 0}
              data-neutral={scores[item.key] === 0}
            >
              {scores[item.key] > 0
                ? `+${scores[item.key]}`
                : String(scores[item.key])}
            </strong>
          </span>
          <em className={styles.deltaLabel}>{item.label}</em>
        </div>
      ))}
    </fieldset>
  );
}
