import styles from "./StageIndicator.module.css";

export function StageIndicator({ step, total, label }: { step: number; total: number; label: string }) {
  return (
    <span className={styles.indicator} data-scene-progress aria-label={`Этап ${step} из ${total}: ${label}`}>
      <span data-progress-count>Этап {step}/{total}</span>
      <span className={styles.bar} aria-hidden="true">
        {Array.from({ length: total }, (_, index) => (
          <i key={index} data-leg={index < step - 1 ? "done" : index === step - 1 ? "current" : undefined} />
        ))}
      </span>
    </span>
  );
}
