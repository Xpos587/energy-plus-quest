import styles from "../App.module.css";
import type { Scores } from "../game/types";

const scoreItems = [
  { key: "energy", label: "Энергия", path: "M13 2 4 14h7l-1 8 10-13h-8z" },
  {
    key: "empathy",
    label: "Эмпатия",
    path: "M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z",
  },
  { key: "efficiency", label: "Эффективность", path: "M4 20 20 4M7 4h13v13" },
] as const;

export function ScoreDelta({ scores }: { scores: Scores }) {
  return (
    <fieldset className={styles.scoreDelta} aria-label="Изменение показателей">
      {scoreItems.map((item) => (
        <div data-score-key={item.key} key={item.key}>
          <span>
            <svg
              aria-hidden="true"
              className={styles.deltaIcon}
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d={item.path} />
            </svg>
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
