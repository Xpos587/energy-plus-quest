import { Route, Truck } from "lucide-react";
import type { CSSProperties } from "react";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";
import type { CarrierId } from "../game/types";
import layout from "./CarrierChoiceLayout.module.css";
import styles from "./CarrierChoices.module.css";

const colors = ["#c34436", "#117db7", "#34815e", "#d4a128"];
export function CarrierChoices({
  selectedId,
  onInspect,
}: {
  selectedId?: CarrierId;
  onInspect: (id: CarrierId) => void;
}) {
  return (
    <fieldset
      className={`${styles.controls} ${layout.layout}`}
      data-carrier-controls
      aria-label="Выбор перевозчика"
    >
      <div className={styles.trucks}>
        {mapCarrierIds.map((id, index) => (
          <button
            key={id}
            type="button"
            className={styles.truck}
            style={{ "--truck-color": colors[index] } as CSSProperties}
            data-scene-choice={id}
            aria-label={carrierFacts[id].label}
            aria-pressed={selectedId === id}
            onClick={() => onInspect(id)}
          >
            <Truck aria-hidden="true" />
          </button>
        ))}
      </div>
      <button
        type="button"
        className={styles.automatic}
        data-scene-choice="express"
        aria-pressed={selectedId === "express"}
        onClick={() => onInspect("express")}
      >
        <Route aria-hidden="true" />
        Подобрать автоматически
      </button>
    </fieldset>
  );
}
