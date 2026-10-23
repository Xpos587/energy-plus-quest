import styles from "./SceneChoices.module.css";
import { Truck, Route, DoorOpen, LibraryBig, UserRound, Monitor, Helicopter, Navigation, Bot, ScanLine, Footprints, Clock3, UsersRound } from "lucide-react";

const optionIcons = {
  entrance: DoorOpen, alphabet: LibraryBig, keeper: UserRound, wms: Monitor,
  helicopter: Helicopter, rover: Navigation, robot: Bot, "pipe-carrier": Truck,
  auto: ScanLine,
  remote: Monitor, rush: Footprints, wait: Clock3, petr: UsersRound,
};

export function SceneChoices<Id extends string>({
  options,
  selectedId,
  onInspect,
  numbered = true,
  badgeShape = "circle",
  variant,
  opensDialog = false,
}: {
  options: readonly { id: Id; label: string; accessibleLabel?: string; showBadge?: boolean }[];
  selectedId?: Id;
  onInspect: (id: Id) => void;
  numbered?: boolean;
  badgeShape?: "circle" | "square";
  variant?: "carriers" | "scene";
  opensDialog?: boolean;
}) {
  return (
    <div className={styles.choices} data-choice-variant={variant} role="group" aria-label="Варианты выбора">
      {options.map(({ id, label, accessibleLabel, showBadge = true }, index) => {
        const Icon = variant === "carriers" ? (id === "express" ? Route : Truck)
          : variant === "scene" ? optionIcons[id as keyof typeof optionIcons] : undefined;
        return (
        <button
          key={id}
          className={styles.choice}
          type="button"
          data-scene-choice={id}
          aria-label={accessibleLabel}
          aria-haspopup={opensDialog ? "dialog" : undefined}
          aria-pressed={selectedId === id}
          onClick={() => onInspect(id)}
        >
          {Icon && (
            <span className={styles.vehicleIcon} data-choice-number={numbered && showBadge ? index + 1 : undefined} aria-hidden="true">
              <Icon />
            </span>
          )}
          {numbered && showBadge && !Icon && (
            <span
              className={styles.number}
              data-badge-shape={badgeShape}
              aria-hidden="true"
            >
              <span>{index + 1}</span>
            </span>
          )}
          <span>{label}</span>
        </button>
      ); })}
    </div>
  );
}
