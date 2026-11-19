import { MapPin, Timer } from "lucide-react";
import { craneFacts } from "./artwork";
import styles from "./CraneDecisionContext.module.css";

/** The scene story on the choice screen itself: no separate briefing step before the quay. */
export function CraneDecisionContext({ paragraphs }: { paragraphs: readonly string[] }) {
  return (
    <div className={styles.story} data-crane-decision-context>
      {paragraphs.map((text) => <p key={text} className={styles.context}>{text}</p>)}
    </div>
  );
}

/** Card body, like the truck card's readouts: from where and when the crane starts. */
export function CraneFacts({ id }: { id: keyof typeof craneFacts }) {
  const fact = craneFacts[id];
  return (
    <div className={styles.card} data-crane-facts={id}>
      <dl className={styles.facts}>
        {([
          [MapPin, "Откуда управляет", fact.where],
          [Timer, "Когда начнёт", fact.when],
        ] as const).map(([Icon, label, value]) => (
          <div key={label}>
            <dt><Icon aria-hidden="true" />{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      <p className={styles.note}>{fact.note}</p>
    </div>
  );
}
