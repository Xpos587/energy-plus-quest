import { Link, Package, Ruler, Scale, ScanLine } from "lucide-react";
import carrier from "../../components/CarrierInspection.module.css";
import styles from "../crane/CraneDecisionContext.module.css";

/** What the picture shows around each place: no verdicts, the result stays unspoiled. */
export const compactFacts = {
  "place-1": { near: "Тяжёлые гири", straps: "Нет" },
  "place-2": { near: "Хрупкая посуда", straps: "Красные стропы" },
  "place-3": { near: "Три коробки", straps: "Короткая стропа" },
  "place-4": { near: "Мягкие подушки", straps: "Стропы на стенке" },
} as const;

/** Card body: the place's neighbours and straps, or what Compact does. */
export function CompactCard({ id }: { id: string }) {
  if (id === "auto")
    return (
      <div className={carrier.express} data-compact-card="auto">
        <p className={carrier.automatic}>Система Compact сама найдёт место груза в кузове.</p>
        <ul className={carrier.expressSteps}>
          <li><Ruler aria-hidden="true" />Сравнит размер груза со свободным местом</li>
          <li><Scale aria-hidden="true" />Распределит нагрузку на оси</li>
          <li><ScanLine aria-hidden="true" />Сразу покажет место в кузове</li>
        </ul>
      </div>
    );
  const fact = compactFacts[id as keyof typeof compactFacts];
  return (
    <div className={styles.card} data-compact-card={id}>
      <dl className={styles.facts}>
        {([
          [Package, "Рядом", fact.near],
          [Link, "Крепления", fact.straps],
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
