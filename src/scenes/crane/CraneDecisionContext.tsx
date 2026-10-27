import { MapPin, Timer } from "lucide-react";
import { craneFacts } from "./artwork";
import styles from "./CraneDecisionContext.module.css";

/** The situation in one line; the quay picture shows who is where. */
export const craneSituation = "Баржа вот-вот уйдёт, а ближний кран свободен только через 3 часа";

export function CraneDecisionContext() {
  return <p className={styles.context} data-crane-decision-context>{craneSituation}</p>;
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
            <dt>{label}</dt>
            <dd><Icon aria-hidden="true" />{value}</dd>
          </div>
        ))}
      </dl>
      <p className={styles.note}>{fact.note}</p>
    </div>
  );
}
