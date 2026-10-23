import styles from "./ScenarioLink.module.css";

const labels = [
  "Узнать больше об Express",
  "Узнать больше о WMS Inventory.",
  "Узнать больше",
];

/** Preserve explicit scenario labels without inventing a destination. */
export function separateScenarioLink(paragraphs: string[]) {
  const text = paragraphs.join("\n\n");
  const label = labels.find((candidate) => text.trimEnd().endsWith(candidate));
  return label
    ? { text: text.slice(0, text.lastIndexOf(label)).trimEnd(), label }
    : { text, label: undefined };
}

export function ScenarioLink({ label }: { label: string }) {
  return (
    <div className={styles.unavailable}>
      <span>{label.replace(/\.$/u, "")}</span>
      <small>Материал пока недоступен.</small>
    </div>
  );
}
