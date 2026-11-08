import { scenarioParagraph } from "../../game/scenarioDocument";
import styles from "../crane/CraneDecisionContext.module.css";

/** The situation in the scenario's own words; the map shows the swamps and the river. */
export const lastmileSituation = scenarioParagraph("5214BC84");

/** Result headings: what happened, in plain words, no score verdict (Teo, 05.11). */
export const lastmileHeadings = {
  helicopter: "Дорогой рейс над болотами",
  rover: "И по болоту, и по реке",
  robot: "Тележка увязла в грунте",
  "pipe-carrier": "Эту реку не переплыть",
} as const;

export function LastmileDecisionContext() {
  return <p className={styles.context} data-lastmile-decision-context>{lastmileSituation}</p>;
}
