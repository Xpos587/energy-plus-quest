import { Pointer } from "lucide-react";
import type { CarrierId } from "../game/types";
import layout from "./CarrierChoiceLayout.module.css";
import styles from "./CarrierTapHint.module.css";

/** The map itself is the only choice; one line says how. */
export function CarrierTapHint({ selectedId }: { selectedId?: CarrierId }) {
  return (
    <p
      className={`${styles.tapHint} ${layout.layout}`}
      data-carrier-tap-hint
      data-active={selectedId ? "" : undefined}
    >
      <span className={styles.tapIcon} aria-hidden="true">
        <Pointer />
      </span>
      <span>Нажмите на фуру — или вызовите Express у склада</span>
    </p>
  );
}
