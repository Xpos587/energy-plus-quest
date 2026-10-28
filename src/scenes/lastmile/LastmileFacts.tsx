import { Mountain, UserRound } from "lucide-react";
import styles from "../crane/CraneDecisionContext.module.css";

/** The situation in one line; the map shows the swamps and the river. */
export const lastmileSituation = "Зимник ещё не работает: впереди болота и речка с первым льдом";

export const lastmileFacts = {
  helicopter: { passes: "Любые, по воздуху", driver: "Пилот", note: "Садится только на вертолётной площадке" },
  rover: { passes: "Болота и реки", driver: "Водитель", note: "Шины сверхнизкого давления" },
  robot: { passes: "Небольшие препятствия", driver: "Автопилот", note: "Дадим водителям отдохнуть" },
  "pipe-carrier": { passes: "Болота", driver: "Водитель", note: "Заберёт с баржи и подарок, и трубы" },
} as const;

export function LastmileDecisionContext() {
  return <p className={styles.context} data-lastmile-decision-context>{lastmileSituation}</p>;
}

/** Card body, like the crane card: what the vehicle gets through and who drives it. */
export function LastmileFacts({ id }: { id: keyof typeof lastmileFacts }) {
  const fact = lastmileFacts[id];
  return (
    <div className={styles.card} data-lastmile-facts={id}>
      <dl className={styles.facts}>
        {([
          [Mountain, "Преодолеет", fact.passes],
          [UserRound, "Управляет", fact.driver],
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
