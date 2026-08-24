import type { CSSProperties } from "react";
import arrowDiscArtwork from "../design/scene-01/assets/ui/arrow-disc-blue.png";
import styles from "./App.module.css";
import { CityMap } from "./components/CityMap";
import { ScoreBoard, ScoreDelta } from "./components/ScoreBoard";
import { choiceArtwork, outcomeArtwork } from "./game/artwork";
import {
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

const progressSteps = ["Профиль", "Получатель", "Подарок", "Перевозчик"];
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
            {progressSteps.map((label, index) => (
              <div
                aria-current={
                  index === progressByStep[state.step] ? "step" : undefined
                }
                className={styles.progressItem}
                data-active={index <= progressByStep[state.step]}
                data-current={index === progressByStep[state.step]}
                key={label}
              >
                <i>{index + 1}</i>
                <span>{label}</span>
              </div>
            ))}
          </nav>
          <ScoreBoard scores={state.scores} />
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
            <Outcome
              onBack={() => navigate({ type: "BACK" })}
              onReset={() => navigate({ type: "RESET" })}
            />
          )}
        </div>
      </main>
    </div>
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
                      ? "feedback-v5"
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
          <div>
            <p className={styles.eyebrow}>Первый участок пути</p>
            <h2>Выберите транспорт для подарка</h2>
          </div>
        </div>
        <p>Нажмите на машину и сразу узнайте, чем закончится ваш выбор.</p>
      </div>
    </section>
  );
}

function Outcome({
  onBack,
  onReset,
}: {
  onBack: () => void;
  onReset: () => void;
}) {
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
    >
      <picture>
        <source
          media="(max-width: 760px)"
          srcSet={outcomeArtwork[carrier.id].mobile}
        />
        <img
          alt=""
          aria-hidden="true"
          className={styles.outcomeBackdrop}
          data-art-version={
            carrier.id === "crew" ? "feedback-v4" : "feedback-v5"
          }
          data-outcome-art={carrier.id}
          src={outcomeArtwork[carrier.id].desktop}
        />
      </picture>
      <div aria-hidden="true" className={styles.outcomeVeil} />
      <div className={styles.resultPanel} data-carrier={carrier.id}>
        <div className={styles.outcomeTokens}>
          {recipient && (
            <span className={styles.outcomeTokenThumb}>
              <img alt={recipient.title} src={choiceArtwork[recipient.id]} />
            </span>
          )}
          <span aria-hidden="true">+</span>
          {parcel && (
            <span className={styles.outcomeTokenThumb}>
              <img alt={parcel.title} src={choiceArtwork[parcel.id]} />
            </span>
          )}
        </div>
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
          <p className={styles.outcomeTiming}>
            <span>Изменение срока</span>
            <strong>{carrier.delivery}</strong>
          </p>
          <ScoreDelta scores={carrier.score} />
          <p className={styles.nextBeat}>
            Теперь нам нужно погрузить подарок...
          </p>
          <div className={styles.resultActions}>
            <button
              className={styles.textButton}
              data-control-style="secondary"
              onClick={onBack}
              type="button"
            >
              Назад к машинам
            </button>
            <button className={styles.primaryButton} disabled type="button">
              <span>Дальше · скоро</span>
            </button>
            <button
              className={styles.textButton}
              data-control-style="secondary"
              onClick={onReset}
              type="button"
            >
              Начать заново
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

function ActionArrow() {
  return (
    <span className={styles.actionArrow}>
      <img alt="" aria-hidden="true" src={arrowDiscArtwork} />
    </span>
  );
}
