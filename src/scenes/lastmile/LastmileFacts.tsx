import { Mountain, UserRound } from "lucide-react";
import styles from "../crane/CraneDecisionContext.module.css";

/** The situation in one line; the map shows the swamps and the river. */
export const lastmileSituation = "Зимник ещё не работает: впереди болота и речка с первым льдом";

/** Card copy: what the vehicle is for, then what it gets through and who drives it. */
export const lastmileFacts = {
  helicopter: { about: "Ми-8 перелетит лес, болота и реку за один рейс. До четырёх тонн груза берёт в салон или на подвес. Садится только на вертолётную площадку.", passes: "Любые преграды, по воздуху", driver: "Экипаж" },
  rover: { about: "На шинах сверхнизкого давления держится на болоте, а на воде плывёт. Такими вездеходами «Снабжение» возит срочные грузы в межсезонье, когда грузовики не проходят.", passes: "Болота и реки", driver: "Водитель" },
  robot: { about: "На складе «Снабжения» роботы уже сами собирают и выдают экипировку. Эта тележка тоже ездит без водителя.", passes: "Ровные площадки", driver: "Автопилот" },
  "pipe-carrier": { about: "Полноприводный грузовик с длинной площадкой под трубы. Заберёт с баржи и подарок, и трубы одним рейсом.", passes: "Только по суше", driver: "Водитель" },
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
          [Mountain, "Пройдёт", fact.passes],
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
