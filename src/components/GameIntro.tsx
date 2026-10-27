import {
  ArrowLeft,
  ArrowRight,
  ChartLine,
  Heart,
  MapPin,
  Zap,
} from "lucide-react";
import { type CSSProperties, useRef, useState } from "react";
import { imageAsset } from "../game/imageAssets";
import { scenarioParagraph } from "../game/scenarioDocument";
import { sceneChoiceImage } from "../scenes/artwork";
import { BrandLockup } from "./BrandLockup";
import styles from "./GameIntro.module.css";
import { progressSteps } from "./QuestShell";

const [parcelStory, logisticsStory] = [
  scenarioParagraph("24D093EF"),
  scenarioParagraph("42DF6085"),
];
const invitation = scenarioParagraph("38763B42");
const explanation = scenarioParagraph("4C9AA992");
const metricParts = explanation.match(
  /^(.*?) (В пути вы будете получать баллы за то, что) (.*?) \(Энергия\), (.*?) \(Эмпатия\) и (.*?) \(Эффективность\)\. (.*)$/,
);
if (!metricParts)
  throw new Error("Canonical introduction metrics structure changed");
const [, mission, metricLead, energy, empathy, efficiency, preparation] =
  metricParts;

/* Same icons as the in-game score delta, so the player recognises them later. */
const metrics = [
  { key: "energy", title: "Энергия", text: energy, Icon: Zap },
  { key: "empathy", title: "Эмпатия", text: empathy, Icon: Heart },
  {
    key: "efficiency",
    title: "Эффективность",
    text: efficiency,
    Icon: ChartLine,
  },
];

/* Real artwork of every stage: the briefing previews the actual journey. */
const routeArt: Record<(typeof progressSteps)[number]["id"], string> = {
  carrier: imageAsset("opening/route-v1/carrier.webp"),
  loading: imageAsset("opening/route-v1/loading.webp"),
  warehouse: imageAsset("opening/route-v1/warehouse.webp"),
  barge: imageAsset("opening/route-v1/barge.webp"),
  "last-mile": imageAsset("opening/route-v1/lastmile.webp"),
};
const waybillFields = ["Отправитель", "Получатель", "Груз"];
const introWorld = sceneChoiceImage("lastmile");

export function GameIntro({ onStart }: { onStart: () => void }) {
  const introWorldUrl = new URL(introWorld, document.baseURI).href;
  const [page, setPage] = useState(-1);
  const copy = useRef<HTMLDivElement>(null);
  function turnPage(next: number) {
    setPage(next);
    requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: "instant" });
      copy.current?.focus({ preventScroll: true });
    });
  }
  return (
    <div
      className={styles.intro}
      data-intro-page={page < 0 ? "cover" : page}
      style={{ "--intro-world": `url("${introWorldUrl}")` } as CSSProperties}
    >
      <header className={styles.brand}>
        <BrandLockup large />
      </header>
      <main className={styles.main} id="quest-main">
        {page < 0 ? (
          <section className={styles.cover} aria-labelledby="intro-title">
            <img className={styles.coverArt} src={introWorld} alt="" />
            <div className={styles.copy}>
              <h1 id="intro-title">
                Доставляем <br />
                радость
              </h1>
              <p className={styles.promise}>{mission}</p>
              <button
                className={styles.primary}
                data-intro-enter
                type="button"
                onClick={() => turnPage(0)}
              >
                Далее <ArrowRight aria-hidden="true" size={25} />
              </button>
            </div>
          </section>
        ) : (
          <section
            className={styles.lesson}
            aria-labelledby="intro-title"
            data-page={page}
          >
            <div className={styles.lessonInner}>
              <div ref={copy} tabIndex={-1} className={styles.page} key={page}>
                {page === 0 ? (
                  <>
                    <h1 id="intro-title">Путь одной посылки</h1>
                    <div className={styles.story}>
                      <p className={styles.lead}>{parcelStory}</p>
                      <p>{logisticsStory}</p>
                    </div>
                    <ol
                      className={styles.route}
                      aria-label="Этапы доставки в игре"
                    >
                      {progressSteps.map((step, index) => (
                        <li className={styles.stop} key={step.id}>
                          <span className={styles.stopArt}>
                            <img src={routeArt[step.id]} alt="" />
                            <b aria-hidden="true">{index + 1}</b>
                          </span>
                          <span className={styles.stopLabel}>{step.label}</span>
                        </li>
                      ))}
                      <li className={styles.goal}>
                        <MapPin
                          aria-hidden="true"
                          size={22}
                          strokeWidth={2.2}
                        />
                        <span>Крайний Север</span>
                      </li>
                    </ol>
                  </>
                ) : (
                  <>
                    <h1 id="intro-title">Маршрутный лист</h1>
                    <p className={styles.invitation}>
                      {invitation} <strong>{mission}</strong>
                    </p>
                    <article
                      className={styles.waybill}
                      aria-label="Маршрутный лист"
                    >
                      <div className={styles.trip}>
                        <img
                          className={styles.tripArt}
                          src={routeArt["last-mile"]}
                          alt=""
                        />
                        <div>
                          <span className={styles.fieldName}>
                            Пункт назначения
                          </span>
                          <strong className={styles.destination}>
                            Крайний Север
                          </strong>
                        </div>
                      </div>
                      <div className={styles.fields}>
                        {waybillFields.map((name) => (
                          <span className={styles.field} key={name}>
                            <span className={styles.fieldName}>{name}</span>
                            <span className={styles.blank} aria-hidden="true" />
                          </span>
                        ))}
                        <p className={styles.preparation}>{preparation}</p>
                      </div>
                      <div className={styles.scoring}>
                        <p className={styles.metricLead}>{metricLead}</p>
                        <ul className={styles.metrics} aria-label="Показатели">
                          {metrics.map(({ key, title, text, Icon }) => (
                            <li key={key} data-metric={key}>
                              <Icon
                                className={styles.metricIcon}
                                aria-hidden="true"
                                size={26}
                                strokeWidth={2}
                              />
                              <div>
                                <span>{text}</span> <strong><i aria-hidden="true">(</i>{title}<i aria-hidden="true">)</i></strong>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </article>
                  </>
                )}
              </div>
              <nav className={styles.lessonActions} aria-label="Вступление">
                <button
                  className={styles.secondary}
                  type="button"
                  onClick={() => turnPage(page - 1)}
                >
                  <ArrowLeft size={24} aria-hidden="true" />
                  Назад
                </button>
                <span
                  className={styles.steps}
                  role="img"
                  aria-label={`Шаг ${page + 1} из 2`}
                >
                  {[0, 1].map((step) => (
                    <i key={step} data-active={step === page} />
                  ))}
                </span>
                {page === 0 ? (
                  <button
                    className={styles.primary}
                    data-intro-next
                    type="button"
                    onClick={() => turnPage(1)}
                  >
                    Далее <ArrowRight size={24} aria-hidden="true" />
                  </button>
                ) : (
                  <button
                    className={styles.primary}
                    data-intro-start
                    type="button"
                    onClick={onStart}
                  >
                    Начать <ArrowRight size={24} aria-hidden="true" />
                  </button>
                )}
              </nav>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
