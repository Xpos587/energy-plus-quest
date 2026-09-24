import type { ReactNode } from "react";
import styles from "../App.module.css";
import { choiceArtwork } from "../game/artwork";
import { findParcel, findProfile, findRecipient } from "../game/content";
import type { GameState } from "../game/types";

type DeliverySelection = Pick<GameState, "profile" | "recipient" | "parcel">;

const progressSteps = [
  { id: "carrier", label: "Перевозчик" },
  { id: "loading", label: "Загрузка" },
  { id: "warehouse", label: "Склад" },
  { id: "barge", label: "Баржа" },
  { id: "last-mile", label: "Последняя миля" },
] as const;
const companyLogoUrl = `${import.meta.env.BASE_URL}brand/gpn-snabzhenie.svg`;
const energyLogoUrl = `${import.meta.env.BASE_URL}brand/energy-plus-logo.svg`;

export function QuestHeader({
  state,
  currentStep = 0,
}: {
  state: DeliverySelection;
  currentStep?: number;
}) {
  return (
    <header className={styles.header}>
      <div className={styles.brandCluster}>
        <div className={styles.energyMark}>
          <img alt="Энергия+" src={energyLogoUrl} />
        </div>
        <div className={styles.projectMark}>
          <img
            alt="Газпром нефть — Газпромнефть-Снабжение"
            className={styles.companyLogo}
            src={companyLogoUrl}
          />
        </div>
      </div>
      <nav className={styles.routeProgress} aria-label="Этапы доставки">
        <span
          className={styles.progressCaption}
          data-progress-caption
          aria-hidden="true"
        >
          {progressSteps[currentStep].label}
        </span>
        <div className={styles.progressTrack}>
          {progressSteps.map((step, index) => (
            <div
              aria-current={index === currentStep ? "step" : undefined}
              className={styles.progressItem}
              data-active={index === currentStep}
              data-current={index === currentStep}
              data-progress-step={step.id}
              key={step.id}
            >
              <i aria-hidden="true">
                <span>{index + 1}</span>
              </i>
              <span>{step.label}</span>
            </div>
          ))}
        </div>
        <span
          className={styles.progressCount}
          data-progress-count
          aria-hidden="true"
        >
          {currentStep + 1} / {progressSteps.length}
        </span>
      </nav>
      <SelectionSummary state={state} />
    </header>
  );
}

function SelectionSummary({ state }: { state: DeliverySelection }) {
  const selections = [
    { key: "profile", item: findProfile(state.profile) },
    { key: "recipient", item: findRecipient(state.recipient) },
    { key: "parcel", item: findParcel(state.parcel) },
  ] as const;

  if (!selections.some(({ item }) => item)) {
    return null;
  }

  return (
    <fieldset
      className={styles.selectionSummary}
      aria-label="Выбрано для доставки"
    >
      {selections.map(({ key, item }, index) =>
        item ? (
          <span data-selection-context={key} key={key}>
            {index > 0 && <i aria-hidden="true" />}
            <img alt={`Выбрано: ${item.title}`} src={choiceArtwork[item.id]} />
          </span>
        ) : null,
      )}
    </fieldset>
  );
}

export function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button className={styles.backButton} onClick={onClick} type="button">
      <span aria-hidden="true">←</span>
      Назад
    </button>
  );
}

export function MissionPanel({
  title,
  onBack,
  children,
  className = "",
  expanded,
  result = false,
}: {
  title: string;
  onBack?: () => void;
  children: ReactNode;
  className?: string;
  expanded?: boolean;
  result?: boolean;
}) {
  return (
    <div
      className={`${styles.missionBar} ${className}`}
      data-sheet-panel
      data-expanded={expanded}
      data-result={result || undefined}
    >
      <div className={styles.missionHeading}>
        {onBack && <BackButton onClick={onBack} />}
        <h2 tabIndex={-1}>{title}</h2>
      </div>
      {children}
    </div>
  );
}
