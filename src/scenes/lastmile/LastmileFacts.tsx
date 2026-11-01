import { Mountain, UserRound } from "lucide-react";
import styles from "../crane/CraneDecisionContext.module.css";

/** The situation in one line; the map shows the swamps and the river. */
export const lastmileSituation = "Зимник ещё не работает: впереди болота и речка с первым льдом";

/** Card copy: what the vehicle is for, then what it gets through and who drives it. */
export const lastmileFacts = {
  helicopter: { about: "Пролетит над лесом, болотами и рекой — преграды на земле ему не мешают. Садится только на вертолётную площадку.", passes: "Любые преграды", driver: "Пилот" },
  rover: { about: "Создан для тундры: на огромных мягких шинах идёт по болоту, а реку переплывает.", passes: "Болота и реки", driver: "Водитель" },
  robot: { about: "В аэропортах сама развозит багаж пассажиров. Пусть поработает и здесь, а водители отдохнут.", passes: "Небольшие препятствия", driver: "Автопилот" },
  "pipe-carrier": { about: "Возит трубы на месторождения. Заберёт с баржи и подарок, и трубы — одним рейсом.", passes: "Болота", driver: "Водитель" },
} as const;

export function LastmileDecisionContext() {
  return <p className={styles.context} data-lastmile-decision-context>{lastmileSituation}</p>;
}

/** Card body, like the crane card. */
export function LastmileFacts({ id }: { id: keyof typeof lastmileFacts }) {
  const fact = lastmileFacts[id];
  return (
    <div className={styles.card} data-lastmile-facts={id}>
      <p className={styles.context}>{fact.about}</p>
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
    </div>
  );
}
