import { type CSSProperties, useEffect, useRef, useState } from "react";
import styles from "./App.module.css";
import { CityMap } from "./components/CityMap";
import { DescriptionSheet } from "./components/DescriptionSheet";
import mapStyles from "./components/IllustratedCityMap.module.css";
import { BackButton, QuestHeader } from "./components/QuestShell";
import { ScoreDelta } from "./components/ScoreBoard";
import { choiceArtwork, outcomeArtwork } from "./game/artwork";
import {
  carrierBriefing,
  carrierQuestion,
  findCarrier,
  findParcel,
  findRecipient,
  parcels,
  profiles,
  recipients,
} from "./game/content";
import { GameProvider, useGame } from "./game/GameContext";
import { interpolateOutcome } from "./game/outcomeText";
import type { CarrierId, ChoiceItem, GameAction } from "./game/types";
import { ScenesGame } from "./scenes/ScenesGame";

export function App() {
  return (
    <GameProvider>
      <Game />
    </GameProvider>
  );
}

function Game() {
  const { state, dispatch } = useGame();
  const [remaining, setRemaining] = useState(false);
  const [carrierToFocus, setCarrierToFocus] = useState<CarrierId>();
  const navigate = (action: GameAction) => {
    setCarrierToFocus(
      action.type === "BACK" && state.step === "outcome"
        ? state.carrier
        : undefined,
    );
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    dispatch(action);
  };

  if (remaining && state.profile && state.recipient && state.parcel) {
    return (
      <ScenesGame
        context={{
          profile: state.profile,
          recipient: state.recipient,
          parcel: state.parcel,
        }}
        initialScores={state.scores}
        onBackToCarrier={() => {
          setRemaining(false);
          navigate({ type: "BACK" });
        }}
      />
    );
  }

  return (
    <div className={styles.app} data-step={state.step}>
      <QuestHeader state={state} />

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
              focusCarrier={carrierToFocus}
              onBack={() => navigate({ type: "BACK" })}
              onSelect={(value) => navigate({ type: "CHOOSE_CARRIER", value })}
            />
          )}
          {state.step === "outcome" && (
            <Outcome
              onBack={() => navigate({ type: "BACK" })}
              onNext={() => setRemaining(true)}
            />
          )}
        </div>
      </main>
    </div>
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
  focusCarrier,
}: {
  onSelect: (value: CarrierId) => void;
  onBack: () => void;
  focusCarrier?: CarrierId;
}) {
  const { state } = useGame();
  const [expanded, setExpanded] = useState(false);
  const [mapOnly, setMapOnly] = useState(false);
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!focusCarrier) return;
    const selected = panel.current?.querySelector<HTMLButtonElement>(
      `[data-carrier-choice="${focusCarrier}"]`,
    );
    selected?.focus({ preventScroll: true });
    selected?.scrollIntoView({ block: "nearest", inline: "nearest" });
  }, [focusCarrier]);
  return (
    <section className={mapStyles.scene} data-map-only={mapOnly}>
      <CityMap mode="live" />
      <button
        type="button"
        className={mapStyles.mapToggle}
        aria-controls="carrier-selection"
        aria-expanded={!mapOnly}
        onClick={() => {
          setExpanded(false);
          setMapOnly(!mapOnly);
        }}
      >
        {mapOnly ? "Вернуться к выбору" : "Рассмотреть карту"}
      </button>
      <div
        id="carrier-selection"
        ref={panel}
        className={mapStyles.panel}
        data-carrier-panel
        data-sheet-panel
        data-expanded={expanded}
        hidden={mapOnly}
      >
        <div className={mapStyles.briefing}>
          <div className={mapStyles.navigation}>
            <BackButton onClick={onBack} />
            <DescriptionSheet
              expanded={expanded}
              onExpandedChange={setExpanded}
              collapsedLabel="Описание доставки"
            >
              <p data-carrier-briefing>
                {interpolateOutcome(
                  carrierBriefing,
                  undefined,
                  findParcel(state.parcel)?.accusativeTitle,
                )}
              </p>
            </DescriptionSheet>
          </div>
          <h2 id="carrier-question">
            {carrierQuestion.split(/(?<=\.) /).map((sentence, index) => (
              <span key={sentence}>
                {index > 0 && " "}
                {sentence}
              </span>
            ))}
          </h2>
        </div>
        <fieldset
          className={mapStyles.choices}
          aria-labelledby="carrier-question"
        >
          {(["old", "near", "crew", "old4"] as const).map((id, index) => (
            <button
              data-carrier-choice={id}
              aria-label={`№${index + 1}`}
              key={id}
              onClick={() => onSelect(id)}
              type="button"
            >
              <span>№{index + 1}</span>
            </button>
          ))}
          <button
            data-carrier-choice="express"
            data-express-control="true"
            onClick={() => onSelect("express")}
            type="button"
          >
            Подобрать автоматически
          </button>
        </fieldset>
      </div>
    </section>
  );
}

function Outcome({
  onBack,
  onNext,
}: {
  onBack: () => void;
  onNext: () => void;
}) {
  const { state } = useGame();
  const [expanded, setExpanded] = useState(true);
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
    >
      <div className={styles.outcomePicture}>
        {(["mobile", "desktop"] as const).map((format) => (
          <img
            alt=""
            aria-hidden="true"
            className={styles.outcomeBackdrop}
            data-art-version="current"
            data-outcome-art={carrier.id}
            data-format={format}
            fetchPriority="high"
            loading="eager"
            key={format}
            src={outcomeArtwork[carrier.id][format]}
          />
        ))}
      </div>
      <div aria-hidden="true" className={styles.outcomeVeil} />
      <div
        className={styles.resultPanel}
        data-sheet-panel
        data-expanded={expanded}
        data-carrier={carrier.id}
      >
        <div className={styles.outcomeCopy}>
          <h2>{carrier.resultTitle}</h2>
          <DescriptionSheet
            expanded={expanded}
            onExpandedChange={setExpanded}
            result
          >
            <p className={styles.panelLead}>
              {interpolateOutcome(
                carrier.resultBody,
                recipient?.title,
                parcel?.accusativeTitle,
              )}
            </p>
          </DescriptionSheet>
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
              className={styles.nextButton}
              onClick={onNext}
              type="button"
            >
              К следующей сцене
            </button>
          </div>
        </div>
      </div>
    </section>
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
