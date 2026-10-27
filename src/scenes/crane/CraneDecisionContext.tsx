import { Clock3, HardHat, MapPin, Ship, Timer, UserRound } from "lucide-react";
import { craneFacts } from "./artwork";
import styles from "./CraneDecisionContext.module.css";

/** The situation as four facts, each with the icon of what the quay shows. */
export const craneDecisionContext = [
  [Ship, "Баржа загружена и вот-вот уйдёт в Новый Порт"],
  [Clock3, "Ближний кран по графику свободен только через 3 часа"],
  [HardHat, "Крановщик Иван ждёт распоряжений в офисе"],
  [UserRound, "Пётр сидит в дальнем кране, у него скоро своя погрузка"],
] as const;

export function CraneDecisionContext() {
  return (
    <ul className={styles.context} data-crane-decision-context>
      {craneDecisionContext.map(([Icon, text]) => (
        <li key={text}><Icon aria-hidden="true" size={18} strokeWidth={2.2} />{text}</li>
      ))}
    </ul>
  );
}

/** Card body, like the truck card's readouts: who runs the crane, from where, when. */
export function CraneFacts({ id }: { id: keyof typeof craneFacts }) {
  const fact = craneFacts[id];
  return (
    <div className={styles.card} data-crane-facts={id}>
      <dl className={styles.facts}>
        {([
          [UserRound, "Кто", fact.who],
          [MapPin, "Откуда управляет", fact.where],
          [Timer, "Когда начнёт", fact.when],
        ] as const).map(([Icon, label, value]) => (
          <div key={label}>
            <dt><Icon aria-hidden="true" size={14} strokeWidth={2.2} />{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      {"note" in fact && <p className={styles.note}>{fact.note}</p>}
    </div>
  );
}
