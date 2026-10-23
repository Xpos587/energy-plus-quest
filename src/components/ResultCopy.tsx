import { type ReactNode, useLayoutEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Check, RotateCcw } from "lucide-react";
import type { Scores } from "../game/types";
import styles from "./ResultCopy.module.css";
import { ScenarioLink, separateScenarioLink } from "./ScenarioLink";
import { ScoreDelta } from "./ScoreBoard";
import { splitReadingParagraphs, useTextPages } from "./useTextPages";

export { splitTextPages as splitResultNarrative } from "./useTextPages";

type ResultNavigation = {
  scores: Scores;
  onBack: () => void;
  onNext?: () => void;
  backLabel: string;
  nextLabel: string;
};

export function ResultCopy({ paragraphs, title, titleTabIndex, children, navigation, fillSpace = false, continuous = false, onDisplayedBeatChange }: {
  paragraphs: string[];
  title?: ReactNode;
  titleTabIndex?: number;
  children?: ReactNode;
  artworkMode?: "page" | "alongside";
  navigation?: ResultNavigation;
  fillSpace?: boolean;
  continuous?: boolean;
  onDisplayedBeatChange?: (beat: number) => void;
}) {
  const narrative = separateScenarioLink(paragraphs);
  const authoredBeats = onDisplayedBeatChange
    ? paragraphs
        .map((paragraph) =>
          narrative.label && paragraph.trimEnd().endsWith(narrative.label)
            ? paragraph.slice(0, paragraph.lastIndexOf(narrative.label)).trimEnd()
            : paragraph,
        )
        .filter(Boolean)
    : [narrative.text];
  const { body, pages } = useTextPages(
    authoredBeats,
    !continuous,
    false,
    Boolean(onDisplayedBeatChange),
    false,
    false,
  );
  const [page, setPage] = useState(0);
  const activePage = Math.min(page, Math.max(0, pages.length - 1));
  let pageOffset = 0;
  let beatIndex = 0;
  let beatEnd = authoredBeats[0]?.length ?? 0;
  const pageBeats = pages.map((part) => {
    while (pageOffset >= beatEnd && beatIndex < authoredBeats.length - 1) {
      beatIndex += 1;
      beatEnd += authoredBeats[beatIndex].length;
    }
    const displayedBeat = beatIndex;
    pageOffset += part.length;
    return displayedBeat;
  });
  const displayedBeat = pageBeats[activePage] ?? 0;
  const density = !continuous && pages.length > 1 ? "paged" : "compact";
  useLayoutEffect(() => {
    onDisplayedBeatChange?.(displayedBeat);
  }, [displayedBeat, onDisplayedBeatChange]);
  const atEnd = continuous || activePage >= pages.length - 1;
  const advance = () => {
    if (!atEnd) setPage(activePage + 1);
    else navigation?.onNext?.();
  };
  return (
    <section className={styles.reader} aria-label="Рассказ о результате" data-result-reader data-result-density={density} data-continuous={continuous || undefined}>
      <div className={styles.narrativeRow} data-result-narrative>
        {title != null && <h2 tabIndex={titleTabIndex}>{title}</h2>}
        {children && <div className={styles.consequence}>{children}</div>}
        <div ref={body} className={styles.reading} data-result-reading aria-label="Текст результата" tabIndex={navigation ? undefined : 0} aria-live="polite">
          <p data-testid="result-copy">
            {splitReadingParagraphs(continuous || !navigation ? narrative.text : pages[activePage]?.trim() ?? "").map((part, index) =>
              index % 2
                ? <span key={index} hidden aria-hidden="true">{part}</span>
                : <span key={index} className={styles.paragraph}>{part}</span>,
            )}
          </p>
        </div>
      </div>
      {narrative.label && <div data-result-link data-visible><ScenarioLink label={narrative.label} /></div>}
      {navigation && (
        <>
          {!navigation.onNext && <span className={styles.completion} role="status">Завершено</span>}
          <footer className={styles.footer}>
            <button className={styles.back} type="button" aria-label={navigation.backLabel} title={navigation.backLabel} onClick={navigation.onBack}>
              <span>{navigation.backLabel === "Пройти сцены заново" ? "Заново" : navigation.backLabel === "Назад к машинам" ? "К машинам" : navigation.backLabel}</span>
              {navigation.backLabel === "Пройти сцены заново"
                ? <RotateCcw aria-hidden="true" size={24} />
                : <ArrowLeft aria-hidden="true" size={24} />}
            </button>
            <div className={styles.resultFeedback} data-result-feedback>
              <ScoreDelta scores={navigation.scores} />
            </div>
            {!atEnd || navigation.onNext ? (
              <button className={styles.next} type="button" aria-label={atEnd ? navigation.nextLabel : "Читать дальше"} title={atEnd ? navigation.nextLabel : "Читать дальше"} onClick={advance}>
                <span>{atEnd ? navigation.nextLabel : "Читать дальше"}</span>
                <ArrowRight aria-hidden="true" size={24} />
              </button>
            ) : <span className={styles.done} aria-hidden="true"><Check size={24} /></span>}
          </footer>
        </>
      )}
    </section>
  );
}
