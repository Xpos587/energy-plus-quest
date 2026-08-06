import type { CSSProperties } from "react";
import styles from "../App.module.css";
import type { Scores } from "../game/types";

const scoreItems: Array<{
  key: keyof Scores;
  short: string;
  label: string;
}> = [
  { key: "energy", short: "ЭН", label: "Энергия" },
  { key: "empathy", short: "ЭМ", label: "Эмпатия" },
  { key: "efficiency", short: "ЭФ", label: "Эффективность" },
];

export function ScoreBoard({ scores }: { scores: Scores }) {
  return (
    <fieldset className={styles.scoreBoard} aria-label="Показатели игрока">
      {scoreItems.map((item) => (
        <div
          className={styles.scoreItem}
          data-tone={scoreTone(scores[item.key])}
          key={item.key}
          title={item.label}
        >
          <span>
            <b className={styles.scoreShort}>{item.short}</b>
            <em className={styles.scoreLong}>{item.label}</em>
          </span>
          <strong>{formatScore(scores[item.key])}</strong>
          <i aria-hidden="true" className={styles.scoreGauge}>
            <b
              className={styles.scoreGaugeFill}
              style={
                {
                  "--score-fill": `${String(scoreFill(scores[item.key]))}%`,
                } as CSSProperties
              }
            />
          </i>
        </div>
      ))}
    </fieldset>
  );
}

export function ScoreDelta({ scores }: { scores: Scores }) {
  return (
    <fieldset className={styles.scoreDelta} aria-label="Изменение показателей">
      {scoreItems.map((item) => (
        <div data-direction={deltaDirection(scores[item.key])} key={item.key}>
          <span>{item.label}</span>
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

function scoreFill(value: number) {
  return Math.max(8, Math.min(100, ((value + 5) / 10) * 100));
}

function deltaFill(value: number) {
  return Math.min(50, (Math.abs(value) / 5) * 50);
}

function scoreTone(value: number) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}

function deltaDirection(value: number) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "neutral";
}
