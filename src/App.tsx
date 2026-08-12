import { type CSSProperties, useEffect } from "react";
import carrierCrewArtwork from "../design/scene-01/assets/carriers-cutout/crew.png";
import carrierExpressArtwork from "../design/scene-01/assets/carriers-cutout/express.png";
import carrierNearArtwork from "../design/scene-01/assets/carriers-cutout/near.png";
import carrierOldArtwork from "../design/scene-01/assets/carriers-cutout/old.png";
import alvaArtwork from "../design/scene-01/assets/choices-v2/alva.webp";
import arseniyArtwork from "../design/scene-01/assets/choices-v2/arseniy.webp";
import boatArtwork from "../design/scene-01/assets/choices-v2/boat.webp";
import cameraArtwork from "../design/scene-01/assets/choices-v2/camera.webp";
import khorArtwork from "../design/scene-01/assets/choices-v2/khor.webp";
import professionalArtwork from "../design/scene-01/assets/choices-v2/professional.webp";
import socksArtwork from "../design/scene-01/assets/choices-v2/socks.webp";
import studentArtwork from "../design/scene-01/assets/choices-v2/student.webp";
import arrowDiscArtwork from "../design/scene-01/assets/ui/arrow-disc-blue.png";
import routeTokenArtwork from "../design/scene-01/assets/ui/route-token.png";
import styles from "./App.module.css";
import { CityMap } from "./components/CityMap";
import { ScoreBoard, ScoreDelta } from "./components/ScoreBoard";
import {
  carriers,
  findCarrier,
  findParcel,
  findProfile,
  findRecipient,
  parcels,
  profiles,
  recipients,
} from "./game/content";
import { GameProvider, useGame } from "./game/GameContext";
import type { CarrierId, ChoiceItem } from "./game/types";

const progressSteps = ["Профиль", "Получатель", "Груз", "Перевозчик"];
const brandIconUrl = `${import.meta.env.BASE_URL}brand/icon-192.png`;

const progressByStep = {
  intro: -1,
  profile: 0,
  recipient: 1,
  parcel: 2,
  briefing: 2,
  carrier: 3,
  outcome: 3,
  express: 3,
  complete: 3,
} as const;

const choiceArtwork: Record<string, string> = {
  student: studentArtwork,
  professional: professionalArtwork,
  alva: alvaArtwork,
  khor: khorArtwork,
  arseniy: arseniyArtwork,
  camera: cameraArtwork,
  socks: socksArtwork,
  boat: boatArtwork,
};

const carrierArtwork: Record<CarrierId, string> = {
  old: carrierOldArtwork,
  near: carrierNearArtwork,
  crew: carrierCrewArtwork,
  express: carrierExpressArtwork,
};

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

  useEffect(() => {
    if (state.step !== "intro" || window.scrollY > 0) {
      window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    }
  }, [state.step]);

  return (
    <div className={styles.app} data-step={state.step}>
      {showChrome && (
        <header className={styles.header}>
          <div className={styles.projectMark}>
            <img
              alt="Энергия+"
              className={styles.brandIcon}
              height="192"
              src={brandIconUrl}
              width="192"
            />
            <div>
              <span>Доставляем радость</span>
              <small>Энергия+ · сцена 01</small>
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
            <Intro onStart={() => dispatch({ type: "START" })} />
          )}
          {state.step === "profile" && (
            <ChoiceScreen
              description="Выберите, от чьего имени проходите маршрут. Роль задаст тон финалу, а условия доставки останутся одинаковыми."
              eyebrow="Шаг 1 из 4 · роль"
              items={profiles}
              onSelect={(value) => dispatch({ type: "CHOOSE_PROFILE", value })}
              title="Кто сегодня управляет доставкой?"
            />
          )}
          {state.step === "recipient" && (
            <ChoiceScreen
              description="Выберите того, кто ждёт посылку в Лабытнанги. От этого зависит история доставки и финал сцены."
              eyebrow="Шаг 2 из 4 · получатель"
              items={recipients}
              onSelect={(value) =>
                dispatch({ type: "CHOOSE_RECIPIENT", value })
              }
              title="Кому доставим радость?"
            />
          )}
          {state.step === "parcel" && (
            <ChoiceScreen
              description="Выберите, что отправляем на Север. Груз войдёт в историю маршрута, а затем вы подберёте перевозчика."
              eyebrow="Шаг 3 из 4 · посылка"
              items={parcels}
              onSelect={(value) => dispatch({ type: "CHOOSE_PARCEL", value })}
              title="Что отправится на Север?"
            />
          )}
          {state.step === "briefing" && (
            <Briefing
              onContinue={() => dispatch({ type: "OPEN_CARRIER_MAP" })}
            />
          )}
          {state.step === "carrier" && (
            <CarrierScreen
              onSelect={(value) => dispatch({ type: "CHOOSE_CARRIER", value })}
            />
          )}
          {state.step === "outcome" && (
            <Outcome onContinue={() => dispatch({ type: "SHOW_EXPRESS" })} />
          )}
          {state.step === "express" && (
            <ExpressReveal
              onContinue={() => dispatch({ type: "COMPLETE_SCENE" })}
            />
          )}
          {state.step === "complete" && (
            <Complete onReset={() => dispatch({ type: "RESET" })} />
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
        <div className={styles.sceneMeta}>
          <span>СЦЕНА 01</span>
          <i />
          <span>МОСКВА → ЛАБЫТНАНГИ</span>
        </div>
        <h1>
          ДОСТАВЛЯЕМ
          <br />
          <span>РАДОСТЬ</span>
        </h1>
        <p>
          Соберите отправление и выберите машину на первый участок до
          Лабытнанги. Цена, срок и надёжность меняются после каждого решения.
        </p>
        <button
          className={styles.primaryButton}
          onClick={onStart}
          type="button"
        >
          <span>Начать маршрут</span>
          <ActionArrow />
        </button>
        <small>4 решения · 3 показателя · 1 маршрут</small>
      </div>
    </section>
  );
}

type ChoiceScreenProps<T extends string> = {
  eyebrow: string;
  title: string;
  description: string;
  items: ChoiceItem<T>[];
  onSelect: (value: T) => void;
};

function ChoiceScreen<T extends string>({
  eyebrow,
  title,
  description,
  items,
  onSelect,
}: ChoiceScreenProps<T>) {
  return (
    <section className={styles.sceneStage} data-layout="dialog">
      <div className={styles.mapBackdrop}>
        <CityMap mode="soft" />
      </div>
      <div className={styles.dialogPanel}>
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
                <img alt="" aria-hidden="true" src={choiceArtwork[item.id]} />
                <b>{item.symbol}</b>
              </span>
              <span className={styles.choiceText}>
                <small>{item.eyebrow}</small>
                <strong>{item.title}</strong>
                <p>{item.description}</p>
              </span>
              <span className={styles.choiceArrow}>
                <img alt="" aria-hidden="true" src={arrowDiscArtwork} />
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function Briefing({ onContinue }: { onContinue: () => void }) {
  const { state } = useGame();
  const profile = findProfile(state.profile);
  const recipient = findRecipient(state.recipient);
  const parcel = findParcel(state.parcel);

  return (
    <section className={styles.sceneStage} data-layout="briefing">
      <div className={styles.mapBackdrop}>
        <CityMap mode="soft" />
      </div>
      <div className={styles.briefingPanel}>
        <p className={styles.eyebrow}>Задание сформировано</p>
        <h2>Первый участок: Москва → Лабытнанги</h2>
        <p className={styles.panelLead}>
          Выберите перевозчика для первого участка. Смотрите не только на
          расстояние до центра: сравните технику, экипаж, цену и срок.
        </p>
        <dl className={styles.manifest}>
          <div>
            <dt>Логист</dt>
            <dd>{profile?.title}</dd>
          </div>
          <div>
            <dt>Получатель</dt>
            <dd>{recipient?.title}</dd>
          </div>
          <div>
            <dt>Груз</dt>
            <dd>{parcel?.title}</dd>
          </div>
          <div>
            <dt>Участок</dt>
            <dd>2 600+ км</dd>
          </div>
        </dl>
        <button
          className={styles.primaryButton}
          onClick={onContinue}
          type="button"
        >
          <span>Открыть карту машин</span>
          <ActionArrow />
        </button>
      </div>
      <div className={styles.routeTicket} aria-hidden="true">
        <img alt="" src={routeTokenArtwork} />
        <span>{parcel?.symbol}</span>
        <strong>{recipient?.symbol}</strong>
      </div>
    </section>
  );
}

function CarrierScreen({ onSelect }: { onSelect: (value: CarrierId) => void }) {
  return (
    <section className={styles.carrierScene}>
      <CityMap mode="live" onSelect={onSelect} />
      <div className={styles.missionBar}>
        <div className={styles.missionHeading}>
          <div>
            <p className={styles.eyebrow}>Сцена 1 · выбор перевозчика</p>
            <h2>Кому доверите первый участок?</h2>
          </div>
          <span className={styles.missionBadge}>4 варианта</span>
        </div>
        <p>
          Оцените четыре варианта и нажмите на машину или карточку. Сразу после
          выбора покажем последствие и сравним решение с Express.
        </p>
      </div>
      <div className={styles.carrierDock}>
        {carriers.map((carrier, index) => (
          <button
            className={styles.carrierRow}
            data-express={carrier.id === "express"}
            key={carrier.id}
            onClick={() => onSelect(carrier.id)}
            style={{ "--delay": `${String(index * 70)}ms` } as CSSProperties}
            type="button"
          >
            <span className={styles.carrierVehicle}>
              <img alt="" aria-hidden="true" src={carrierArtwork[carrier.id]} />
            </span>
            <div>
              <small>{carrier.eyebrow}</small>
              <strong>{carrier.title}</strong>
              <p>{carrier.description}</p>
            </div>
            <span className={styles.carrierArrow}>
              <img alt="" aria-hidden="true" src={arrowDiscArtwork} />
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}

function Outcome({ onContinue }: { onContinue: () => void }) {
  const { state } = useGame();
  const carrier = findCarrier(state.carrier);
  const recipient = findRecipient(state.recipient);
  const parcel = findParcel(state.parcel);

  if (!carrier) {
    return null;
  }

  return (
    <section className={styles.sceneStage} data-layout="result">
      <CityMap mode="result" selected={carrier.id} />
      <div className={styles.resultPanel} data-carrier={carrier.id}>
        <div className={styles.resultTopline}>
          <span>Сдвиг графика</span>
          <strong>{carrier.delivery}</strong>
        </div>
        <h2>{carrier.resultTitle}</h2>
        <p className={styles.panelLead}>
          {carrier.resultBody} {recipient?.title} получит{" "}
          {parcel?.title.toLowerCase()} по новому графику.
        </p>
        <div className={styles.carrierFacts}>
          <span>
            <small>Техника</small>
            <strong>{carrier.condition}</strong>
          </span>
          <span>
            <small>Экипаж</small>
            <strong>{carrier.crew}</strong>
          </span>
          <span>
            <small>Цена</small>
            <strong>{carrier.cost}</strong>
          </span>
        </div>
        <ScoreDelta scores={carrier.score} />
        <button
          className={styles.primaryButton}
          onClick={onContinue}
          type="button"
        >
          <span>
            {carrier.id === "express"
              ? "Разобрать подбор Express"
              : "Сравнить с Express"}
          </span>
          <ActionArrow />
        </button>
      </div>
    </section>
  );
}

function ExpressReveal({ onContinue }: { onContinue: () => void }) {
  const { state } = useGame();
  const selected = findCarrier(state.carrier);
  const express = findCarrier("express");

  if (!selected || !express) {
    return null;
  }

  return (
    <section className={styles.sceneStage} data-layout="express">
      <CityMap mode="express" selected="express" />
      <div className={styles.expressPanel}>
        <div className={styles.expressIntro}>
          <p className={styles.eyebrow}>Express · цифровой автоподбор</p>
          <h2>Не искать фуру. Найти лучшее решение.</h2>
          <p className={styles.panelLead}>
            За два часа сервис проверяет цену, рейтинг, состояние транспорта и
            график экипажа. На карте эти ограничения не видны одновременно.
          </p>
        </div>
        <div className={styles.scanResults}>
          <ComparisonRow
            label="Ваш выбор"
            muted={selected.id !== "express"}
            title={selected.title}
            value={selected.delivery}
          />
          <ComparisonRow
            label="Рекомендация Express"
            best
            title="Новая фура · 2 водителя"
            value="−7 дней"
          />
        </div>
        <div className={styles.expressMetrics}>
          <span>
            <small>Рейтинг</small>
            <strong>Высокий</strong>
          </span>
          <span>
            <small>Техника</small>
            <strong>Новая</strong>
          </span>
          <span>
            <small>Экипаж</small>
            <strong>2 водителя</strong>
          </span>
          <span>
            <small>Стоимость</small>
            <strong>Выгодная</strong>
          </span>
        </div>
        {selected.id !== "express" && (
          <div className={styles.learningNote}>
            <span>Что показало сравнение</span>
            <p>
              Ручной выбор опирался на заметный параметр. Express проверил все
              ограничения вместе. Полученные баллы остаются без изменений.
            </p>
          </div>
        )}
        <button
          className={styles.primaryButton}
          onClick={onContinue}
          type="button"
        >
          <span>Зафиксировать результат</span>
          <ActionArrow />
        </button>
      </div>
    </section>
  );
}

function ComparisonRow({
  label,
  title,
  value,
  muted = false,
  best = false,
}: {
  label: string;
  title: string;
  value: string;
  muted?: boolean;
  best?: boolean;
}) {
  return (
    <div
      className={styles.comparisonRow}
      data-best={best}
      data-muted={muted}
      style={
        {
          "--comparison-position": `${String(comparisonPosition(value))}%`,
        } as CSSProperties
      }
    >
      <span>{label}</span>
      <strong>{title}</strong>
      <i>{value}</i>
      <b aria-hidden="true" className={styles.comparisonTrack}>
        <span />
      </b>
    </div>
  );
}

function comparisonPosition(value: string) {
  const days = Number.parseInt(value.replace("−", "-"), 10);
  return Math.max(0, Math.min(100, ((days + 7) / 14) * 100));
}

function Complete({ onReset }: { onReset: () => void }) {
  const { state } = useGame();
  const recipient = findRecipient(state.recipient);
  const parcel = findParcel(state.parcel);
  const profile = findProfile(state.profile);

  return (
    <section className={styles.sceneStage} data-layout="complete">
      <CityMap mode="complete" selected="express" />
      <div className={styles.completePanel}>
        <div className={styles.completionMark} aria-hidden="true">
          <span>01</span>
          <i>✓</i>
        </div>
        <p className={styles.eyebrow}>Сцена 1 завершена</p>
        <h2>Первый участок пройден</h2>
        <p className={styles.panelLead}>
          {parcel?.title} уже в пути. Получатель — {recipient?.title}. Следующая
          задача — правильно разместить груз в фуре с помощью Compact.
        </p>
        <div className={styles.completeStats}>
          <div>
            <span>Профиль</span>
            <strong>{profile?.title}</strong>
          </div>
          <div>
            <span>Маршрут</span>
            <strong>Москва → Лабытнанги</strong>
          </div>
        </div>
        <ScoreDelta scores={state.scores} />
        <div className={styles.completeActions}>
          <button className={styles.primaryButton} disabled type="button">
            <span>Сцена 2 · скоро</span>
          </button>
          <button className={styles.textButton} onClick={onReset} type="button">
            Пройти сцену заново
          </button>
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
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className={styles.screenHeading}>
      <p className={styles.eyebrow}>{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
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
