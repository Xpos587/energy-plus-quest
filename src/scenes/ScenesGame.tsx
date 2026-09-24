import { useEffect, useReducer, useRef, useState } from "react";
import shared from "../App.module.css";
import { DescriptionSheet } from "../components/DescriptionSheet";
import { MissionPanel, QuestHeader } from "../components/QuestShell";
import { ScoreDelta } from "../components/ScoreBoard";
import type { Scores } from "../game/types";
import { compactScene } from "./compact";
import { CompactOutcome } from "./compact/CompactOutcome";
import { craneScene } from "./crane";
import { inventoryScene } from "./inventory";
import { lastmileScene } from "./lastmile";
import { initialProgress, progressReducer, totalScores } from "./progress";
import styles from "./ScenesGame.module.css";
import type { SceneContext, SceneId } from "./types";

export const remainingScenes = [
  compactScene,
  inventoryScene,
  craneScene,
  lastmileScene,
];
const zeroScores: Scores = { energy: 0, empathy: 0, efficiency: 0 };

export type ScenesCompletion = {
  context: SceneContext;
  answers: Record<string, string>;
  scores: Scores;
};
export type ScenesGameProps = {
  context: SceneContext;
  initialScores?: Scores;
  startAt?: SceneId;
  onComplete?: (result: ScenesCompletion) => void;
  onBackToCarrier?: () => void;
};

export function ScenesGame(props: ScenesGameProps) {
  const { context, startAt = "compact" } = props;
  return (
    <ScenesSession
      key={`${context.parcel}-${context.recipient}-${context.profile}-${startAt}`}
      {...props}
    />
  );
}

function ScenesSession({
  context,
  initialScores = zeroScores,
  startAt = "compact",
  onComplete,
  onBackToCarrier,
}: ScenesGameProps) {
  const [state, dispatch] = useReducer(
    (
      state: typeof initialProgress,
      action: Parameters<typeof progressReducer>[1],
    ) => progressReducer(state, action, remainingScenes, context),
    {
      ...initialProgress,
      sceneIndex: Math.max(
        0,
        remainingScenes.findIndex(({ id }) => id === startAt),
      ),
    },
  );
  const [expanded, setExpanded] = useState(true);
  const stage = useRef<HTMLDivElement>(null);
  const completionSent = useRef(false);
  const previousScreen = useRef<string | null>(null);
  const scene = remainingScenes[state.sceneIndex];
  const options = scene.options(context);
  const intro = scene.intro(context);
  const selected = options.find(({ id }) => id === state.answers[scene.id]);
  const score = totalScores(state, remainingScenes, context, initialScores);
  const { Art } = scene;
  const resultVisible = state.phase === "result" && selected !== undefined;

  const choose = (id: string) => {
    setExpanded(true);
    dispatch({ type: "CHOOSE", id });
  };

  useEffect(() => {
    const screen = `${state.sceneIndex}:${state.phase}`;
    if (previousScreen.current === screen) return;
    previousScreen.current = screen;
    setExpanded(true);
    stage.current
      ?.querySelector<HTMLHeadingElement>("h2")
      ?.focus({ preventScroll: true });
  }, [state.sceneIndex, state.phase, scene.id]);

  useEffect(() => {
    if (state.finished && !completionSent.current) {
      completionSent.current = true;
      onComplete?.({ context, answers: { ...state.answers }, scores: score });
    }
    if (!state.finished) completionSent.current = false;
  }, [state.finished, state.answers, context, score, onComplete]);

  const title = scene.title.replace(/^Сцена \d+\.\s*/, "");
  const back =
    state.phase === "result" ||
    (state.sceneIndex > 0 && Object.keys(state.answers).length > 0)
      ? () => dispatch({ type: "BACK" })
      : onBackToCarrier;

  return (
    <div className={shared.app} data-scene={scene.id}>
      <QuestHeader state={context} currentStep={scene.number - 1} />
      <main className={shared.main} id="quest-main">
        <div
          className={`${shared.carrierScene} ${styles.stage}`}
          ref={stage}
          data-compact-hall={scene.id === "compact" || undefined}
          data-score-result={resultVisible || undefined}
          data-compact-result={
            (resultVisible && scene.id === "compact") || undefined
          }
          data-art-result={
            (resultVisible &&
              (scene.id === "compact" ||
                scene.id === "inventory" ||
                scene.id === "crane" ||
                scene.id === "lastmile")) ||
            undefined
          }
        >
          <section
            className={styles.visual}
            aria-label={`Иллюстрация: ${title}`}
          >
            <Art
              context={context}
              selectedId={selected?.id}
              showResult={resultVisible}
              onSelect={state.phase === "choice" ? choose : undefined}
            />
          </section>
          <MissionPanel
            title={title}
            onBack={!resultVisible ? back : undefined}
            expanded={expanded}
            result={resultVisible}
            className={`${styles.panel} ${resultVisible ? shared.resultPanel : ""}`}
          >
            <DescriptionSheet
              key={`${scene.id}:${state.phase}`}
              expanded={expanded}
              onExpandedChange={setExpanded}
              result={resultVisible}
            >
              {resultVisible ? (
                <>
                  {scene.id === "compact" && (
                    <CompactOutcome
                      parcel={context.parcel}
                      selectedId={selected.id}
                    />
                  )}
                  <div data-testid="result-copy">
                    {selected.result.map((paragraph) => (
                      <p key={paragraph}>{paragraph.replace(
                        /^\s*Результат:\s*(.)?/iu,
                        (_prefix, first: string = "") => first.toLocaleUpperCase("ru-RU"),
                      )}</p>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div data-testid="scene-intro">
                    {(scene.id === "compact" ? intro.slice(0, -1) : intro).map(
                      (paragraph) => (
                        <p key={paragraph}>{paragraph}</p>
                      ),
                    )}
                  </div>
                  {scene.id !== "compact" && (
                    <ol className={styles.descriptions}>
                      {options.map((option) => (
                        <li
                          key={option.id}
                          data-choice-description
                        >
                          {option.label.replace(
                            /^\s*(?:(?:Место|Вариант)\s*№?\s*\d+|№\s*\d+|\d+[.)])(?:[.):]\s*|\s+)*/u,
                            "",
                          )}
                        </li>
                      ))}
                    </ol>
                  )}
                </>
              )}
            </DescriptionSheet>
            {!resultVisible && scene.id === "compact" && (
              <p className={styles.question} data-testid="scene-question">
                {intro.at(-1)}
              </p>
            )}
            {resultVisible ? (
              <>
                <ScoreDelta scores={selected.score} />
                <div className={shared.resultActions}>
                  <button
                    className={shared.textButton}
                    type="button"
                    onClick={() =>
                      dispatch({ type: state.finished ? "RESET" : "BACK" })
                    }
                  >
                    {state.finished ? "Пройти сцены заново" : "Изменить выбор"}
                  </button>
                  <button
                    className={shared.nextButton}
                    type="button"
                    disabled={state.finished}
                    onClick={() => dispatch({ type: "NEXT" })}
                  >
                    {state.finished
                      ? "Завершено"
                      : scene.number === 5
                        ? "Завершить"
                        : "Продолжить"}
                  </button>
                </div>
              </>
            ) : (
              <div
                className={shared.carrierChoices}
                data-count={options.length}
              >
                {options.map((option, index) => (
                  <button
                    key={option.id}
                    type="button"
                    data-choice-id={option.id}
                    aria-label={[option.label, option.accessibleDescription]
                      .filter(Boolean)
                      .join(". ")}
                    onClick={() => choose(option.id)}
                  >
                    {option.id === "auto" ? option.label : `№${index + 1}`}
                  </button>
                ))}
              </div>
            )}
          </MissionPanel>
        </div>
      </main>
    </div>
  );
}
