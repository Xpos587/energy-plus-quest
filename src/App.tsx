import { type CSSProperties, useState } from "react";
import arrowDiscArtwork from "../design/scene-01/assets/ui/arrow-disc-blue.png";
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
  { id: "profile", label: "Профиль" },
  { id: "recipient", label: "Получатель" },
  { id: "parcel", label: "Подарок" },
  { id: "carrier", label: "Перевозчик" },
] as const;
const companyLogoUrl = `${import.meta.env.BASE_URL}brand/gpn-snabzhenie.svg`;
const energyLogoUrl = `${import.meta.env.BASE_URL}brand/energy-plus-logo.svg`;

const progressByStep = {
  intro: -1,
  profile: 0,
  recipient: 1,
  parcel: 2,
  carrier: 3,
  outcome: 3,
} as const;

export function App() {
  return (
    <GameProvider>
      <Game />
    </GameProvider>
  );
}

function Game() {
  const { state, dispatch } = useGame();
  const showChrome = state.step !== "intro";

  const navigate = (action: GameAction) => {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    dispatch(action);
  };

  return (
    <div className={styles.app} data-step={state.step}>
      {showChrome && (
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
          <nav className={styles.routeProgress} aria-label="Прогресс сцены">
            {progressSteps.map((step, index) => (
              <div
                aria-current={
                  index === progressByStep[state.step] ? "step" : undefined
                }
                className={styles.progressItem}
                data-active={index <= progressByStep[state.step]}
                data-current={index === progressByStep[state.step]}
                data-progress-step={step.id}
                key={step.id}
              >
                <i aria-hidden="true" />
                <span className={styles.visuallyHidden}>{step.label}</span>
              </div>
            ))}
          </nav>
          <SelectionSummary state={state} />
        </header>
      )}

      <main className={styles.main} id="quest-main">
        <div className={styles.screen} key={state.step}>
          {state.step === "intro" && (
            <Intro onStart={() => navigate({ type: "START" })} />
          )}
          {state.step === "profile" && (
            <ChoiceScreen
              items={profiles}
              onBack={() => navigate({ type: "BACK" })}
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
    { key: "parcel", item: findParcel(state.parcel) },
    { key: "recipient", item: findRecipient(state.recipient) },
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

function Intro({ onStart }: { onStart: () => void }) {
  return (
    <section className={styles.sceneStage} data-layout="intro">
      <CityMap mode="soft" />
      <div className={styles.mapVeil} aria-hidden="true" />
      <div className={styles.openingPanel}>
        <div className={styles.introBrandLockup}>
          <img
            alt="Газпром нефть — Газпромнефть-Снабжение"
            className={styles.introCompanyLogo}
            src={companyLogoUrl}
          />
          <span className={styles.introEnergyMark}>
            <img alt="Энергия+" src={energyLogoUrl} />
          </span>
        </div>
        <p className={styles.gameStart}>Начало игры</p>
        <h1>
          Доставляем <span>радость</span>
        </h1>
        <p>
          У логистов есть профессиональное правило: не бывает неважных грузов.
          Для кого-то это многотонная турбина, а для кого-то — одна маленькая
          коробка, одна большая радость.
        </p>
        <p>
          Сегодня вам предстоит провести такой груз на Крайний Север — быстро,
          легко и с любовью к людям.
        </p>
        <button
          className={styles.primaryButton}
          onClick={onStart}
          type="button"
        >
          <span>Начать игру</span>
          <ActionArrow />
        </button>
      </div>
    </section>
  );
}

type ChoiceScreenProps<T extends string> = {
  eyebrow?: string;
  title: string;
  description?: string;
  items: ChoiceItem<T>[];
  onBack: () => void;
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
        <BackButton onClick={onBack} />
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
                  data-art-version={
                    item.id === "professional"
                      ? "feedback-v12"
                      : item.id === "alva"
                        ? "feedback-v6"
                        : "feedback-v4"
                  }
                  src={choiceArtwork[item.id]}
                />
                <b>{item.symbol}</b>
              </span>
              <span className={styles.choiceText}>
                {item.eyebrow && (
                  <small data-role-part="label">{item.eyebrow}</small>
                )}
                <strong data-role-part="title">{item.title}</strong>
                {item.description && <p>{item.description}</p>}
              </span>
              <span className={styles.choiceArrow} data-role-part="action">
                <img alt="" aria-hidden="true" src={arrowDiscArtwork} />
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function CarrierScreen({
  onBack,
  onSelect,
}: {
  onBack: () => void;
  onSelect: (value: CarrierId) => void;
}) {
  return (
    <section className={styles.carrierScene}>
      <CityMap mode="live" onSelect={onSelect} />
      <div className={styles.missionBar}>
        <BackButton onClick={onBack} />
        <div className={styles.missionHeading}>
          <h2>Выберите транспорт для подарка</h2>
          <p>
            Выберите номер грузовика, который лучше всего справится с задачей.
          </p>
        </div>
        <div className={styles.carrierChoices}>
          <button
            data-carrier-choice="old"
            onClick={() => onSelect("old")}
            type="button"
          >
            №1 или №4
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
        </div>
        <button
          className={styles.expressButton}
          data-express-control="true"
          onClick={() => onSelect("express")}
          type="button"
        >
          Автоподбор Express
        </button>
      </div>
    </section>
  );
}

function Outcome({ onBack }: { onBack: () => void }) {
  const { state } = useGame();
  const [continued, setContinued] = useState(false);
  const carrier = findCarrier(state.carrier);
  const profile = findProfile(state.profile);
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
    >
      <picture>
        <source
          height="1688"
          media="(max-width: 760px)"
          srcSet={outcomeArtwork[carrier.id].mobile}
          type="image/webp"
          width="780"
        />
        <img
          alt=""
          aria-hidden="true"
          className={styles.outcomeBackdrop}
          data-art-version="feedback-v12"
          data-outcome-art={carrier.id}
          fetchPriority="high"
          height="1800"
          loading="eager"
          src={outcomeArtwork[carrier.id].desktop}
          width="2880"
        />
      </picture>
      <div aria-hidden="true" className={styles.outcomeVeil} />
      <div className={styles.resultPanel} data-carrier={carrier.id}>
        <fieldset
          className={styles.outcomeTokens}
          aria-label="Выбрано для доставки"
        >
          {[
            ["profile", profile],
            ["parcel", parcel],
            ["recipient", recipient],
          ].map(([key, item]) =>
            typeof item === "object" && item ? (
              <span
                className={styles.outcomeTokenThumb}
                data-selection-context={key as string}
                key={key as string}
              >
                <img
                  alt={`Выбрано: ${item.title}`}
                  src={choiceArtwork[item.id]}
                />
              </span>
            ) : null,
          )}
        </fieldset>
        <div className={styles.outcomeCopy}>
          <p className={styles.eyebrow}>Вот что произошло</p>
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
            <button
              className={styles.primaryButton}
              onClick={() => setContinued(true)}
              type="button"
            >
              <span>Едем дальше</span>
            </button>
          </div>
          {continued && (
            <p
              aria-live="polite"
              className={styles.continuationStatus}
              role="status"
            >
              Продолжение маршрута появится в следующей версии
            </p>
          )}
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

function ActionArrow() {
  return (
    <span className={styles.actionArrow}>
      <img alt="" aria-hidden="true" src={arrowDiscArtwork} />
    </span>
  );
}
