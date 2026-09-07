import type { CSSProperties } from "react";
import styles from "./App.module.css";
import { CityMap } from "./components/CityMap";
import { ScoreDelta } from "./components/ScoreBoard";
import { choiceArtwork, outcomeArtwork } from "./game/artwork";
import {
  findCarrier,
  findParcel,
  findProfile,
  findRecipient,
  parcels,
  profiles,
  recipients,
} from "./game/content";
import { GameProvider, useGame } from "./game/GameContext";
import { interpolateOutcome } from "./game/outcomeText";
import type {
  CarrierId,
  ChoiceItem,
  GameAction,
  GameState,
} from "./game/types";

const progressSteps = [
  { id: "carrier", label: "Перевозчик" },
  { id: "loading", label: "Загрузка" },
  { id: "warehouse", label: "Склад" },
  { id: "barge", label: "Баржа" },
  { id: "last-mile", label: "Последняя миля" },
] as const;
const companyLogoUrl = `${import.meta.env.BASE_URL}brand/gpn-snabzhenie.svg`;
const energyLogoUrl = `${import.meta.env.BASE_URL}brand/energy-plus-logo.svg`;

export function App() {
  return (
    <GameProvider>
      <Game />
    </GameProvider>
  );
}

function Game() {
  const { state, dispatch } = useGame();
  const navigate = (action: GameAction) => {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    dispatch(action);
  };

  return (
    <div className={styles.app} data-step={state.step}>
      <header className={styles.header}>
        <div className={styles.brandCluster}>
          <div className={styles.projectMark}>
            <img
              alt="Газпром нефть — Газпромнефть-Снабжение"
              className={styles.companyLogo}
              src={companyLogoUrl}
            />
          </div>
          <div className={styles.energyMark}>
            <img alt="Энергия+" src={energyLogoUrl} />
          </div>
        </div>
        <nav className={styles.routeProgress} aria-label="Этапы доставки">
          {progressSteps.map((step, index) => (
            <div
              aria-current={index === 0 ? "step" : undefined}
              className={styles.progressItem}
              data-active={index === 0}
              data-current={index === 0}
              data-progress-step={step.id}
              key={step.id}
            >
              <i aria-hidden="true">{index + 1}</i>
              <span>{step.label}</span>
            </div>
          ))}
        </nav>
        <SelectionSummary state={state} />
      </header>

      <main className={styles.main} id="quest-main">
        <div className={styles.screen} key={state.step}>
          {state.step === "profile" && (
            <ChoiceScreen
              items={profiles}
              onSelect={(value) => navigate({ type: "CHOOSE_PROFILE", value })}
              title="Кто отправится в путь?"
            />
          )}
          {state.step === "recipient" && (
            <ChoiceScreen
              items={recipients}
              onBack={() => navigate({ type: "BACK" })}
              onSelect={(value) =>
                navigate({ type: "CHOOSE_RECIPIENT", value })
              }
              title="Выберите получателя"
            />
          )}
          {state.step === "parcel" && (
            <ChoiceScreen
              items={parcels}
              onBack={() => navigate({ type: "BACK" })}
              onSelect={(value) => navigate({ type: "CHOOSE_PARCEL", value })}
              title="Что будет в посылке?"
            />
          )}
          {state.step === "carrier" && (
            <CarrierScreen
              onBack={() => navigate({ type: "BACK" })}
              onSelect={(value) => navigate({ type: "CHOOSE_CARRIER", value })}
            />
          )}
          {state.step === "outcome" && (
            <Outcome onBack={() => navigate({ type: "BACK" })} />
          )}
        </div>
      </main>
    </div>
  );
}

function SelectionSummary({ state }: { state: GameState }) {
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

type ChoiceScreenProps<T extends string> = {
  eyebrow?: string;
  title: string;
  description?: string;
  items: ChoiceItem<T>[];
  onBack?: () => void;
  onSelect: (value: T) => void;
};

function ChoiceScreen<T extends string>({
  eyebrow,
  title,
  description,
  items,
  onBack,
  onSelect,
}: ChoiceScreenProps<T>) {
  return (
    <section className={styles.sceneStage} data-layout="dialog">
      <div className={styles.mapBackdrop}>
        <CityMap mode="soft" />
      </div>
      <div className={styles.dialogPanel}>
        {onBack && <BackButton onClick={onBack} />}
        <ScreenHeading
          description={description}
          eyebrow={eyebrow}
          title={title}
        />
        <div className={styles.choiceGrid} data-count={items.length}>
          {items.map((item, index) => (
            <button
              className={styles.choiceCard}
              data-choice={item.id}
              key={item.id}
              onClick={() => onSelect(item.id)}
              style={{ "--delay": `${String(index * 75)}ms` } as CSSProperties}
              type="button"
            >
              <span className={styles.choiceSymbol}>
                <img
                  alt=""
                  aria-hidden="true"
                  data-art-version="current"
                  src={choiceArtwork[item.id]}
                />
              </span>
              <span className={styles.choiceText}>
                {item.eyebrow && (
                  <small data-role-part="label">{item.eyebrow}</small>
                )}
                <strong data-role-part="title">{item.title}</strong>
                {item.description && <p>{item.description}</p>}
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function CarrierScreen({
  onSelect,
  onBack,
}: {
  onSelect: (value: CarrierId) => void;
  onBack: () => void;
}) {
  return (
    <section className={styles.carrierScene}>
      <CityMap mode="live" />
      <div className={styles.missionBar}>
        <BackButton onClick={onBack} />
        <div className={styles.missionHeading}>
          <h2>Выберите транспорт для подарка</h2>
        </div>
        <div className={styles.carrierChoices}>
          <button
            data-carrier-choice="old"
            onClick={() => onSelect("old")}
            type="button"
          >
            №1
          </button>
          <button
            data-carrier-choice="near"
            onClick={() => onSelect("near")}
            type="button"
          >
            №2
          </button>
          <button
            data-carrier-choice="crew"
            onClick={() => onSelect("crew")}
            type="button"
          >
            №3
          </button>
          <button
            data-carrier-choice="old"
            onClick={() => onSelect("old")}
            type="button"
          >
            №4
          </button>
          <button
            data-carrier-choice="express"
            data-express-control="true"
            onClick={() => onSelect("express")}
            type="button"
          >
            Подобрать автоматически
          </button>
        </div>
      </div>
    </section>
  );
}

function Outcome({ onBack }: { onBack: () => void }) {
  const { state } = useGame();
  const carrier = findCarrier(state.carrier);
  const recipient = findRecipient(state.recipient);
  const parcel = findParcel(state.parcel);

  if (!carrier) {
    return null;
  }

  return (
    <section
      className={styles.outcomeScene}
      data-carrier={carrier.id}
      data-layout="result"
      style={
        {
          "--scene-art": `url("${outcomeArtwork[carrier.id].desktop}")`,
          "--scene-mobile-art": `url("${outcomeArtwork[carrier.id].mobile}")`,
        } as CSSProperties
      }
    >
      <picture className={styles.outcomePicture}>
        <source
          media="(max-width: 900px) and (orientation: portrait)"
          srcSet={outcomeArtwork[carrier.id].mobile}
          type="image/webp"
        />
        <img
          alt=""
          aria-hidden="true"
          className={styles.outcomeBackdrop}
          data-art-version="current"
          data-outcome-art={carrier.id}
          fetchPriority="high"
          loading="eager"
          src={outcomeArtwork[carrier.id].desktop}
        />
      </picture>
      <div aria-hidden="true" className={styles.outcomeVeil} />
      <div className={styles.resultPanel} data-carrier={carrier.id}>
        <div className={styles.outcomeCopy}>
          <h2>{carrier.resultTitle}</h2>
          <p className={styles.panelLead}>
            {interpolateOutcome(
              carrier.resultBody,
              recipient?.title,
              parcel?.accusativeTitle,
            )}
          </p>
          <ScoreDelta scores={carrier.score} />
          <div className={styles.resultActions}>
            <button
              className={styles.textButton}
              data-control-style="secondary"
              onClick={onBack}
              type="button"
            >
              Назад к машинам
            </button>
            <button className={styles.nextButton} disabled type="button">
              К следующей сцене
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function BackButton({ onClick }: { onClick: () => void }) {
  return (
    <button className={styles.backButton} onClick={onClick} type="button">
      <span aria-hidden="true">←</span>
      Назад
    </button>
  );
}

function ScreenHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <div
      className={styles.screenHeading}
      data-compact={!eyebrow && !description ? "true" : undefined}
    >
      {eyebrow && <p className={styles.eyebrow}>{eyebrow}</p>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
}
