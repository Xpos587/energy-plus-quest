import { Package } from "lucide-react";
import styles from "./StageIndicator.module.css";

export function StageIndicator({ step, total, label }: { step: number; total: number; label: string }) {
  return (
    <span className={styles.indicator} data-scene-progress aria-label={`Этап ${step} из ${total}: ${label}`}>
      <span data-progress-count>Этап {step}/{total}</span>
      <Package aria-hidden="true" size={20} />
    </span>
  );
}
