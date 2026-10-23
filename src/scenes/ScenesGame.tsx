import { useEffect, useRef, useState } from "react";
import { QuestHeader } from "../components/QuestShell";
import { ResultCopy } from "../components/ResultCopy";
import {
  resetBriefingReadingState,
  SceneBriefing,
} from "../components/SceneBriefing";
import { SceneChoices } from "../components/SceneChoices";
import flow from "../components/SceneInteraction.module.css";
import { clearReadingState } from "../components/useReadingState";
import { useOptionalSaveScope } from "../game/GameContext";
import { prefetchImage } from "../game/imageAssets";
import { useStoredState } from "../game/persistence";
import type { Scores } from "../game/types";
import { sceneChoiceImage } from "./artwork";
import { choiceLabel } from "./choiceLabel";
import { compactScene } from "./compact";
import { craneScene } from "./crane";
import { CraneDecisionContext } from "./crane/CraneDecisionContext";
import { inventoryScene } from "./inventory";
import { inventoryAlphabet } from "./inventory/alphabet";
import { JourneyEnding } from "./JourneyEnding";
import { lastmileScene } from "./lastmile";
import { initialProgress, progressReducer, totalScores } from "./progress";
import { SceneOutcomeArt } from "./SceneOutcomeArt";
import type { SceneContext, SceneId } from "./types";

export const remainingScenes = [
  compactScene,
  inventoryScene,
  craneScene,
  lastmileScene,
];
function briefingParagraphs(scene: SceneId, intro: string[]) {
  return scene === "compact" || scene === "lastmile"
    ? intro.slice(0, -1)
    : intro;
}

/** Explicit forward navigation starts the target condition; reloads retain their reading state. */
export function restartSceneCondition(
  id: SceneId,
  context: SceneContext,
  scope: string | undefined,
) {
  const scene = remainingScenes.find((scene) => scene.id === id);
  if (!scene) return;
  resetBriefingReadingState(
    scope,
    scene.title.replace(/^Сцена \d+\.\s*/, ""),
    briefingParagraphs(id, scene.intro(context)),
  );
}
const optionTitles: Record<string, string> = {
  "place-1": "Место 1",
  "place-2": "Место 2",
  "place-3": "Место 3",
  "place-4": "Место 4",
  entrance: "У приёмки",
  keeper: "Кладовщик",
  alphabet: "По алфавиту",
  wms: "Система WMS",
  rush: "Отправить Ивана на кран",
  wait: "Дождаться работы крана",
  petr: "Попросить Петра помочь",
  remote: "Иван управляет краном из офиса",
  helicopter: "Вертолёт",
  rover: "Снегоболотоход",
  robot: "Роботизированная тележка",
  "pipe-carrier": "Трубовоз",
};
const zeroScores: Scores = { energy: 0, empathy: 0, efficiency: 0 };
export type ScenesCompletion = {
  context: SceneContext;
  answers: Record<string, string>;
  scores: Scores;
};
export type ScenesGameProps = {
  persistenceKey?: string;
  context: SceneContext;
  initialScores?: Scores;
  startAt?: SceneId;
  onComplete?: (result: ScenesCompletion) => void;
  onBackToCarrier?: () => void;
  onRestart?: () => void;
  onHome?: () => void;
};

type SceneSession = { progress: typeof initialProgress; briefed?: SceneId[] };

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
  onRestart,
  onHome,
  persistenceKey,
}: ScenesGameProps) {
  const saveScope = useOptionalSaveScope();
  const fallback = {
    ...initialProgress,
    sceneIndex: Math.max(
      0,
      remainingScenes.findIndex(({ id }) => id === startAt),
    ),
  };
  const [session, setSession] = useStoredState(
    persistenceKey,
    { progress: fallback } as SceneSession,
    (value): value is SceneSession => {
      if (!value || typeof value !== "object") return false;
      const briefed = (value as SceneSession).briefed;
      if (briefed !== undefined && (!Array.isArray(briefed) || briefed.some(id => !remainingScenes.some(scene => scene.id === id)))) return false;
      const { progress: p } = value as {
        progress?: typeof initialProgress;
      };
      if (
        !p ||
        !Number.isInteger(p.sceneIndex) ||
        p.sceneIndex < 0 ||
        p.sceneIndex >= remainingScenes.length ||
        !["choice", "result"].includes(p.phase) ||
        typeof p.finished !== "boolean" ||
        !p.answers ||
        typeof p.answers !== "object"
      )
        return false;
      if (
        Object.entries(p.answers).some(
          ([id, answer]) =>
            !remainingScenes
              .find((scene) => scene.id === id)
              ?.options(context)
              .some((option) => option.id === answer),
        )
      )
        return false;
      if (
        remainingScenes
          .slice(0, p.sceneIndex)
          .some((scene) => !p.answers[scene.id])
      )
        return false;
      if (p.phase === "result" && !p.answers[remainingScenes[p.sceneIndex].id])
        return false;
      if (
        p.finished &&
        (p.sceneIndex !== remainingScenes.length - 1 || p.phase !== "result")
      )
        return false;
      return true;
    },
  );
  const state = session.progress;
  const dispatch = (action: Parameters<typeof progressReducer>[1]) => {
    if (action.type === "RESET") clearReadingState(saveScope);
    if (action.type === "NEXT" && session.progress.phase === "result") {
      const next = remainingScenes[session.progress.sceneIndex + 1];
      if (next && !session.briefed?.includes(next.id)) restartSceneCondition(next.id, context, saveScope);
    }
    setSession((current) => ({
      ...current,
      ...(action.type === "RESET" ? { briefed: [] } : {}),
      progress: progressReducer(
        current.progress,
        action,
        remainingScenes,
        context,
      ),
    }));
  };
  const stage = useRef<HTMLDivElement>(null);
  const choicePan = useRef<Partial<Record<SceneId, number>>>({});
  const lastChoice = useRef<Partial<Record<SceneId, string>>>({});
  const completionSent = useRef(false);
  const previousScreen = useRef(`${state.sceneIndex}:${state.phase}`);
  const scene = remainingScenes[state.sceneIndex];
  const options = scene.options(context);
  const intro = scene.intro(context);
  const selected = options.find(({ id }) => id === state.answers[scene.id]);
  const [resultBeat, setResultBeat] = useState(0);
  const score = totalScores(state, remainingScenes, context, initialScores);
  const { Art } = scene;
  const resultVisible = state.phase === "result" && selected !== undefined;
  useEffect(() => {
    if (resultVisible) {
      const next = remainingScenes[state.sceneIndex + 1];
      // These maps choose their format from the mounted stage geometry.
      // A guessed wide image wastes a request before the actual tall/context map.
      if (next && next.id !== "crane" && next.id !== "lastmile")
        return prefetchImage(sceneChoiceImage(next.id, context));
    }
  }, [resultVisible, state.sceneIndex, context]);
  const choose = (id: string) => {
    if (
      state.phase === "choice" &&
      options.some((option) => option.id === id)
    ) {
      lastChoice.current[scene.id] = id;
      dispatch({ type: "CHOOSE", id });
    }
  };

  useEffect(() => {
    const screen = `${state.sceneIndex}:${state.phase}`;
    if (previousScreen.current === screen) return;
    previousScreen.current = screen;
    const destination = stage.current?.querySelector<HTMLElement>(
      '[data-reading="true"] [data-testid="scene-intro"]',
    ) ?? (state.phase === "choice"
      ? stage.current?.querySelector<HTMLButtonElement>(`[data-scene-choice="${lastChoice.current[remainingScenes[state.sceneIndex].id] ?? ""}"]`)
        ?? stage.current?.querySelector<HTMLButtonElement>("[data-scene-choice]")
      : stage.current?.querySelector<HTMLHeadingElement>("h2"));
    destination?.focus({ preventScroll: true });
  }, [state.sceneIndex, state.phase]);

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
  const hasSeparateQuestion = scene.id === "compact" || scene.id === "lastmile";
  const question = hasSeparateQuestion
    ? (intro.at(-1) ?? title)
    : scene.id === "inventory"
      ? (intro[0].split(/(?<=\.)\s+/u).at(-1) ?? title)
      : "Как погрузить подарок на баржу?";
  const resultParagraphs =
    selected?.result.map((paragraph) =>
      scene.id === "inventory"
        ? paragraph
        : paragraph.replace(
            /^\s*Результат:\s*«?(.)?/iu,
            (_prefix, first: string = "") => first.toLocaleUpperCase("ru-RU"),
          ),
    ) ?? [];
  const synchronizedHelicopterResult =
    scene.id === "lastmile" &&
    selected?.id === "helicopter" &&
    context.recipient !== "arseniy";

  if (state.finished) {
    return (
      <JourneyEnding
        context={context}
        scores={score}
        onRestart={() => {
          if (onRestart) onRestart();
          else dispatch({ type: "RESET" });
        }}
        onHome={onHome}
      />
    );
  }

  return (
    <div className={flow.app} data-scene={scene.id}>
      <QuestHeader
        state={context}
        currentStep={scene.number - 1}
        result={resultVisible}
      />
      <main className={flow.main} id="quest-main">
        <div
          className={flow.frame}
          ref={stage}
          data-interaction={!resultVisible ? "inspect-confirm" : undefined}
          data-inspecting={false}
          data-compact-hall={scene.id === "compact" || undefined}
          data-score-result={resultVisible || undefined}
          data-compact-result={
            (resultVisible && scene.id === "compact") || undefined
          }
          data-art-result={resultVisible || undefined}
          data-layout={resultVisible ? "result" : undefined}
        >
          {!resultVisible && (
            <SceneBriefing
              currentStep={scene.number - 1}
              key={scene.id}
              title={title}
              paragraphs={briefingParagraphs(scene.id, intro)}
              initiallyOpen={!session.briefed?.includes(scene.id)}
              showLeadOnChoice={false}
              onConditionComplete={() => setSession(current => ({
                ...current,
                briefed: [...new Set([...(current.briefed ?? []), scene.id])],
              }))}
              navigation="fixed"
              question={question}
              keepParagraphs={scene.id === "crane"}
              decisionContext={
                scene.id === "crane" ? <CraneDecisionContext /> : undefined
              }
              onBack={back}
              action={
                <SceneChoices
                  variant="scene"
                  options={options.map((option) => ({
                    id: option.id,
                    showBadge: option.id !== "auto",
                    accessibleLabel:
                      scene.id === "compact" && option.id !== "auto"
                        ? optionTitles[option.id]
                        : undefined,
                    label:
                      scene.id === "compact" && option.id !== "auto"
                        ? "Место"
                        : option.id === "auto"
                          ? "Поручить размещение Compact"
                          : scene.id === "inventory" && option.id === "alphabet"
                            ? `Стеллаж «${inventoryAlphabet[context.parcel].letter}»`
                            : scene.id === "crane" && (option.id === "rush" || option.id === "wait")
                              ? choiceLabel(option.label)
                              : optionTitles[option.id] ?? choiceLabel(option.label),
                  }))}
                  onInspect={choose}
                  badgeShape={
                    scene.id === "compact" || scene.id === "crane"
                      ? "square"
                      : "circle"
                  }
                />
              }
            />
          )}
          <section
            className={flow.carrierMap}
            aria-label={`Иллюстрация: ${title}`}
          >
            {resultVisible && scene.id !== "compact" ? (
              <SceneOutcomeArt
                scene={scene.id}
                selectedId={selected.id}
                context={context}
                displayedBeat={
                  synchronizedHelicopterResult ? resultBeat : undefined
                }
              />
            ) : (
              <Art
                context={context}
                initialPan={choicePan.current[scene.id]}
                onPanChange={(position) => {
                  choicePan.current[scene.id] = position;
                }}
                selectedId={resultVisible ? selected?.id : undefined}
                showResult={resultVisible}
                onSelect={state.phase === "choice" ? choose : undefined}
              />
            )}
          </section>
          {resultVisible ? (
            <section
              className={flow.result}
              aria-label="Результат выбора"
              data-sheet-panel
              data-result
            >
              <div className={flow.resultStory}>
                <ResultCopy
                  key={`${scene.id}:${selected.id}`}
                  title={title}
                  titleTabIndex={-1}
                  paragraphs={resultParagraphs}
                  fillSpace
                  continuous={
                    (scene.id === "lastmile" && selected.id === "pipe-carrier") ||
                    (scene.id === "crane" && selected.id === "petr")
                  }
                  onDisplayedBeatChange={
                    synchronizedHelicopterResult ? setResultBeat : undefined
                  }
                  navigation={{
                    scores: selected.score,
                    onBack: () => {
                      lastChoice.current[scene.id] = selected.id;
                      if (state.finished && onRestart) onRestart();
                      else
                        dispatch({ type: state.finished ? "RESET" : "BACK" });
                    },
                    onNext: state.finished
                      ? undefined
                      : () => dispatch({ type: "NEXT" }),
                    backLabel: state.finished
                      ? "Пройти сцены заново"
                      : "Изменить выбор",
                    nextLabel: state.finished
                      ? "Завершено"
                      : scene.number === 5
                        ? "К вручению подарка"
                        : "Продолжить",
                  }}
                />
              </div>
            </section>
          ) : null}
        </div>
      </main>
    </div>
  );
}
