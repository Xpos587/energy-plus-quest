import { scenarioParagraph } from "../../game/scenarioDocument";
import styles from "./CraneDecisionContext.module.css";

const source = scenarioParagraph("62451EC9");
const decisionContext = source.slice(source.indexOf(". ") + 2);

export function CraneDecisionContext() {
  return (
    <div className={styles.context} data-crane-decision-context>
      <p>{decisionContext}</p>
      <p>{scenarioParagraph("6F7BE91B")}</p>
      <p>Пётр — {scenarioParagraph("0C6EC2FC").split(" — ")[1]}</p>
    </div>
  );
}
