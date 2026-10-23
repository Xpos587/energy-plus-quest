import { useRef, useState, type CSSProperties } from "react";
import { ArrowLeft, ArrowRight, Zap, Heart, ChartNoAxesCombined } from "lucide-react";
import { imageAsset } from "../game/imageAssets";
import { scenarioParagraph } from "../game/scenarioDocument";
import { sceneChoiceImage } from "../scenes/artwork";
import styles from "./GameIntro.module.css";
import { BrandLockup } from "./BrandLockup";

const opening = [scenarioParagraph("24D093EF"), scenarioParagraph("42DF6085")];
const invitation = scenarioParagraph("38763B42");
const explanation = scenarioParagraph("4C9AA992");
const metricParts = explanation.match(/^(.*?) (В пути вы будете получать баллы за то, что) (.*?) \(Энергия\), (.*?) \(Эмпатия\) и (.*?) \(Эффективность\)\. (.*)$/);
if (!metricParts) throw new Error("Canonical introduction metrics structure changed");
const [, mission, metricLead, energy, empathy, efficiency, preparation] = metricParts;
const metrics = [
  { title: "Энергия", text: energy, Icon: Zap },
  { title: "Эмпатия", text: empathy, Icon: Heart },
  { title: "Эффективность", text: efficiency, Icon: ChartNoAxesCombined },
];
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
    <div className={styles.intro} data-intro-page={page < 0 ? "cover" : page}
      style={{ "--intro-world": `url("${introWorldUrl}")` } as CSSProperties}>
      <header className={styles.brand}>
        <BrandLockup large />
      </header>
      <main className={styles.main} id="quest-main">
        {page < 0 ? <section className={styles.cover} aria-labelledby="intro-title">
          <img className={styles.coverArt} src={introWorld} alt="" />
          <div className={styles.copy}>
            <h1 id="intro-title">Доставляем <br />радость</h1>
            <p className={styles.promise}>{mission}</p>
            <button className={styles.primary} data-intro-enter type="button" onClick={() => turnPage(0)}>Далее <ArrowRight aria-hidden="true" size={25} /></button>
          </div>
        </section> : <section className={styles.lesson} aria-labelledby="intro-title" data-page={page}>
          <div className={styles.lessonInner}>
            <h1 id="intro-title">Доставляем радость</h1>
            <div className={styles.briefing}>
              <div ref={copy} tabIndex={-1} className={styles.authored}>
                {page === 0 ? <>
                  {opening.map(text => <p key={text}>{text}</p>)}
                </> : <>
                  <p>{invitation}</p>
                  <p>{mission}</p>
                  <p className={styles.metricLead}>{metricLead}</p>
                  <ul className={styles.metrics} aria-label="Показатели">
                    {metrics.map(({ title, text, Icon }) => <li key={title}>
                      <Icon size={30} strokeWidth={1.8} aria-hidden="true" />
                      <div><span>{text}</span>{" "}<strong>({title})</strong></div>
                    </li>)}
                  </ul>
                  <p className={styles.preparation}>{preparation}</p>
                </>}
              </div>
              <img className={styles.parcelDrawing} src={imageAsset("opening/parcel-heart-v2.webp")} alt="" />
            </div>
            <nav className={styles.lessonActions} aria-label="Вступление">
              <button className={styles.secondary} type="button" onClick={() => turnPage(page - 1)}><ArrowLeft size={24} aria-hidden="true" />Назад</button>
              {page === 0
                ? <button className={styles.primary} data-intro-next type="button" onClick={() => turnPage(1)}>Далее <ArrowRight size={24} aria-hidden="true" /></button>
                : <button className={styles.primary} data-intro-start type="button" onClick={onStart}>Начать <ArrowRight size={24} aria-hidden="true" /></button>}
            </nav>
          </div>
        </section>}
      </main>
    </div>
  );
}
