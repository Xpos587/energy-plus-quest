import type { ReactNode } from "react";
import { ChevronLeft, UserRound } from "lucide-react";
import styles from "../App.module.css";
import { choiceArtwork } from "../game/artwork";
import { thumbnailAsset } from "../game/imageAssets";
import { findParcel, findProfile, findRecipient } from "../game/content";
import type { GameState } from "../game/types";
import chrome from "./QuestChrome.module.css";
import { StageIndicator } from "./StageIndicator";
import { BrandLockup } from "./BrandLockup";

type DeliverySelection = Pick<GameState, "profile" | "recipient" | "parcel">;

export const progressSteps = [
  { id: "carrier", label: "Перевозчик" },
  { id: "loading", label: "Загрузка" },
  { id: "warehouse", label: "Склад" },
  { id: "barge", label: "Баржа" },
  { id: "last-mile", label: "Последняя миля" },
] as const;

export function QuestBrand() {
  return (
    <div className={chrome.brandCluster} style={{ padding: 0 }}>
      <BrandLockup />
    </div>
  );
}

export function HeaderBackButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      aria-label="Назад"
      className={chrome.selectionBack}
      onClick={onClick}
      type="button"
    >
      <ChevronLeft aria-hidden="true" size={24} />
    </button>
  );
}

export function QuestHeader({
  state,
  currentStep = 0,
  selectionTitle,
  onSelectionBack,
  result = false,
}: {
  state: DeliverySelection;
  currentStep?: number;
  selectionTitle?: string;
  selectionStep?: number;
  onSelectionBack?: () => void;
  result?: boolean;
}) {
  const activeStep = selectionTitle ? -1 : currentStep;
  const progressLabel = selectionTitle
    ? "Подготовка"
    : progressSteps[currentStep].label;
  return (
    <header className={chrome.header} data-header-result={result || undefined}>
      <div
        className={
          selectionTitle
            ? chrome.selectionHeaderCard
            : result
              ? chrome.resultHeaderCard
              : undefined
        }
        data-quest-brand
      >
        <QuestBrand />
        {selectionTitle && (
          <div className={chrome.selectionHeading}>
            {onSelectionBack ? (
              <HeaderBackButton onClick={onSelectionBack} />
            ) : (
              <span className={chrome.selectionIcon} aria-hidden="true">
                <UserRound size={24} />
              </span>
            )}
            <h1>{selectionTitle}</h1>
          </div>
        )}
      </div>
      {!selectionTitle && result && (
        <section className={chrome.routeProgress} aria-label="Этапы доставки">
          <StageIndicator step={currentStep + 1} total={progressSteps.length} label={progressLabel} />
        </section>
      )}
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
      className={chrome.selectionSummary}
      aria-label="Выбрано для доставки"
    >
      {selections.map(({ key, item }, index) =>
        item ? (
          <span data-selection-context={key} key={key}>
            {index > 0 && <i aria-hidden="true" />}
            <img
              alt={`Выбрано: ${item.title}`}
              src={thumbnailAsset(choiceArtwork[item.id])}
            />
          </span>
        ) : null,
      )}
    </fieldset>
  );
}

export function BackButton({ onClick }: { onClick: () => void }) {
  return <HeaderBackButton onClick={onClick} />;
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
