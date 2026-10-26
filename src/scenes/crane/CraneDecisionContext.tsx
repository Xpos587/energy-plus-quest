import styles from "./CraneDecisionContext.module.css";

/** Short restatement of the scenario's three constraints, shown next to the choices. */
export const craneDecisionContext = [
  "Баржа загружена и вот-вот уйдёт по Оби в Новый порт. Ближайший кран по графику свободен только через 3 часа.",
  "Крановщик Иван ждёт распоряжений в офисе, а оператор Пётр сидит в дальнем кране: у него скоро своя погрузка.",
];

export function CraneDecisionContext() {
  return (
    <div className={styles.context} data-crane-decision-context>
      {craneDecisionContext.map((text) => <p key={text}>{text}</p>)}
    </div>
  );
}
