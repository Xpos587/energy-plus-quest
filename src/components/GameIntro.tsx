import {
  ArrowLeft,
  ArrowRight,
  ChartLine,
  Heart,
  MapPin,
  Zap,
} from "lucide-react";
import { type CSSProperties, useRef, useState } from "react";
import { scenarioParagraph } from "../game/scenarioDocument";
import { sceneChoiceImage } from "../scenes/artwork";
import { BrandLockup } from "./BrandLockup";
import styles from "./GameIntro.module.css";
import { progressSteps } from "./QuestShell";
import { routeArt, stageIcons } from "./StageIndicator";

/* One line instead of the two canonical paragraphs (R19, 09.11): the five
   stages below are the screen's subject, the story only sets them up. */
const parcelStory = [scenarioParagraph("24D093EF"), scenarioParagraph("42DF6085")].join(
  " ",
);
/* The letter's own words (R19): one rule, no «Тогда вперёд!» and no second
   restatement of the destination already printed above it. */
const invitation = scenarioParagraph("38763B42");
const explanation = scenarioParagraph("4C9AA992");
const metricParts = explanation.match(
  /^(.*?) (В пути вы будете получать баллы за то, что) (.*?) \(Энергия\), (.*?) \(Эмпатия\) и (.*?) \(Эффективность\)\. (.*)$/,
);
if (!metricParts)
  throw new Error("Canonical introduction metrics structure changed");
const [, mission, , energy, empathy, efficiency, preparation] =
  metricParts;
const metricLead = "В пути вы будете получать баллы:";

/* Same icons as the in-game score delta, so the player recognises them later.
   `hint` is our plain-language gloss of the scenario phrase, drawn from the
   scene goals the metric rewards. */
const metrics = [
  {
    key: "energy",
    title: "Энергия",
    text: energy,
    hint: "Время, силы, топливо и деньги.",
    Icon: Zap,
  },
  {
    key: "empathy",
    title: "Эмпатия",
    text: empathy,
    hint: "О подарке, получателе и людях рядом.",
    Icon: Heart,
  },
  {
    key: "efficiency",
    title: "Эффективность",
    text: efficiency,
    hint: "Вовремя и самым подходящим способом.",
    Icon: ChartLine,
  },
];

const introWorld = sceneChoiceImage("lastmile");

export function GameIntro({
  onStart,
  initialPage = -1,
}: {
  onStart: () => void;
  initialPage?: number;
}) {
  const introWorldUrl = new URL(introWorld, document.baseURI).href;
  const [page, setPage] = useState(initialPage);
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
                    <p className={styles.lead}>{parcelStory}</p>
                    <ol
                      className={styles.route}
                      aria-label="Этапы доставки в игре"
                    >
                      {progressSteps.map((step, index) => (
                        <li className={styles.stop} key={step.id}>
                          <span className={styles.stopArt}>
                            <img src={stageIcons[step.id]} alt="" />
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
                    <article
                      className={styles.letter}
                      aria-label="Маршрутный лист"
                    >
                      <header className={styles.letterHead}>
                        <div>
                          <h1 id="intro-title">Маршрутный лист</h1>
                          <p className={styles.address}>
                            <span className={styles.fieldName}>
                              Пункт назначения
                            </span>{" "}
                            <strong className={styles.destination}>
                              Крайний Север
                            </strong>
                          </p>
                        </div>
                        <span className={styles.stamp} aria-hidden="true">
                          <img src={routeArt["last-mile"]} alt="" />
                        </span>
                      </header>
                      <p className={styles.invitation}>{invitation}</p>
                      <div className={styles.scoring}>
                        <p className={styles.metricLead}>{metricLead}</p>
                        <ul className={styles.metrics} aria-label="Показатели">
                          {metrics.map(({ key, title, text, hint, Icon }) => (
                            <li key={key} data-metric={key}>
                              <strong>
                                <Icon
                                  className={styles.metricIcon}
                                  aria-hidden="true"
                                  size={26}
                                  strokeWidth={2.2}
                                />
                                {title}
                              </strong>{" "}
                              <span>За то, что {text}.</span>{" "}
                              <small>{hint}</small>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <p className={styles.preparation}>{preparation}</p>
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
                  <span>Назад</span>
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
                    К маршрутному листу <ArrowRight size={24} aria-hidden="true" />
                  </button>
                ) : (
                  <button
                    className={styles.primary}
                    data-intro-start
                    type="button"
                    onClick={onStart}
                  >
                    Собрать посылку <ArrowRight size={24} aria-hidden="true" />
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
