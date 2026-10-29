import carrier from "../../components/CarrierInspection.module.css";

/** Card body for the automatic choice: here the player first meets Compact. */
export function CompactCard() {
  return (
    <div className={carrier.express} data-compact-card="auto">
      <p className={carrier.automatic}>
        Цифровая система Compact Logotech сама подберет место по размеру груза
        и учтет нагрузку на оси. Ваш груз разместится компактно и надежно.
      </p>
    </div>
  );
}
