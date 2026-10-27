import { ChartLine, CircleAlert, CircleCheck, CircleX, Heart, Zap } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { QuestHeader } from "../components/QuestShell";
import { ResultCopy } from "../components/ResultCopy";
import {
  resetBriefingReadingState,
  SceneBriefing,
} from "../components/SceneBriefing";
import { CarrierTapHint } from "../components/CarrierTapHint";
import { ChoiceInspection } from "../components/ChoiceInspection";
import { SceneChoices } from "../components/SceneChoices";
import flow from "../components/SceneInteraction.module.css";
import { clearReadingState } from "../components/useReadingState";
import { useOptionalSaveScope } from "../game/GameContext";
import { choiceArtwork } from "../game/artwork";
import { prefetchImage, thumbnailAsset } from "../game/imageAssets";
import { useStoredState } from "../game/persistence";
import type { Scores } from "../game/types";
import { sceneChoiceImage } from "./artwork";
import { parcelNames, recipientNames } from "./names";
import { choiceLabel } from "./choiceLabel";
import { compactScene } from "./compact";
import { craneScene } from "./crane";
import { craneCaptions, craneFacts } from "./crane/artwork";
import { CraneDecisionContext, CraneFacts } from "./crane/CraneDecisionContext";
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
// Names and hints repeat what the artwork shows; the result stays unspoiled.
const scorePoints = [
  { key: "energy", icon: Zap, score: "Энергия" },
  { key: "empathy", icon: Heart, score: "Эмпатия" },
  { key: "efficiency", icon: ChartLine, score: "Эффективность" },
] as const;
type Tone = "best" | "fair" | "bad";
type SceneBrief = {
  eyebrow: string;
  route: (context: SceneContext) => string;
  goals: [energy: string, empathy: string, efficiency: string];
  places: (context: SceneContext) => Record<string, [name: string, detail: string]>;
  verdicts: Record<Tone, string>;
  picked: (id: string, name: string) => string;
};
const sceneBriefs: Partial<Record<SceneId, SceneBrief>> = {
  compact: {
    eyebrow: "Наряд на погрузку",
    route: () => "Фура до склада в Лабытнанги",
    goals: ["Погрузить быстро", "Довезти целым", "Не занять лишнее"],
    places: () => ({
      "place-1": ["У задних дверей", "Над гирями, без креплений"],
      "place-2": ["Над посудой", "Есть красные стропы"],
      "place-3": ["Ниша за коробками", "Есть короткая стропа"],
      "place-4": ["У передней стенки", "Высоко, рядом подушки"],
      auto: ["Доверить Compact", "Подберёт место по размеру"],
    }),
    verdicts: { best: "Отличная погрузка", fair: "Можно лучше", bad: "Неудачная погрузка" },
    picked: (id, name) => id === "auto" ? "Место выбрал Compact" : `${optionTitles[id]} · ${name}`,
  },
  inventory: {
    eyebrow: "Карточка хранения",
    route: () => "Склад в Лабытнанги, пару дней до баржи",
    goals: ["Без лишнего крюка", "Не потерять подарок", "Ближе к отгрузке"],
    places: ({ parcel }) => ({
      entrance: ["У приёмки", "Свободные ячейки у входа"],
      alphabet: [`Стеллаж «${inventoryAlphabet[parcel].letter}»`, "По первой букве названия"],
      keeper: ["Кладовщик", "Спросить опытного коллегу"],
      wms: ["Система WMS", "Место подскажет Inventory"],
    }),
    verdicts: { best: "Отличное место", fair: "Можно лучше", bad: "Неудачное место" },
    picked: (_id, name) => `Ваш выбор · ${name}`,
  },
  crane: {
    eyebrow: "Погрузка на баржу",
    route: () => "С причала на баржу до Нового Порта",
    goals: ["Беречь силы", "Позаботиться о людях", "Успеть к барже"],
    places: () => Object.fromEntries(
      Object.entries(craneFacts).map(([id, fact]) => [id, [optionTitles[id], fact.where]]),
    ),
    verdicts: { best: "Отличная погрузка", fair: "Можно лучше", bad: "Неудачная погрузка" },
    picked: (_id, name) => `Ваш выбор · ${name}`,
  },
  lastmile: {
    eyebrow: "Последняя миля",
    route: ({ recipient }) => `От причала в Новом Порту до ${recipientNames[recipient].genitive}`,
    goals: ["Без лишних трат", "Довезти лично", "Пройти болота"],
    places: () => ({
      helicopter: ["Вертолёт", "Перелетит любые преграды"],
      rover: ["Снегоболотоход", "Создан для таких мест"],
      robot: ["Роботизированная тележка", "Возит багаж в аэропортах"],
      "pipe-carrier": ["Трубовоз", "Возьмёт груз вместе с трубами"],
    }),
    verdicts: { best: "Лучший транспорт", fair: "Можно лучше", bad: "Неудачный выбор" },
    picked: (_id, name) => `Ваш выбор · ${name}`,
  },
};
export function SceneGoals({ goals }: { goals: SceneBrief["goals"] }) {
  return (
    <ul className={flow.compactGoals} aria-label="Что важно" data-compact-goals>
      {scorePoints.map(({ key, icon: Icon, score }, index) => (
        <li key={key} data-goal-key={key} data-metric={key}><Icon aria-hidden="true" size={16} strokeWidth={2.2} /><span>{goals[index]}</span><small>{score}</small></li>
      ))}
    </ul>
  );
}
const sum = ({ energy, empathy, efficiency }: Scores) => energy + empathy + efficiency;
/** Ranks the choice against the best one available in this context. */
export function rankChoice(score: Scores, all: Scores[]): Tone {
  const value = sum(score);
  if (value >= Math.max(...all.map(sum)) - 1) return "best";
  return value > 0 ? "fair" : "bad";
}
const verdictIcons = { best: CircleCheck, fair: CircleAlert, bad: CircleX } as const;

const optionTitles: Record<string, string> = {
  "place-1": "Место 1",
  "place-2": "Место 2",
  "place-3": "Место 3",
  "place-4": "Место 4",
  entrance: "У приёмки",
  keeper: "Кладовщик",
  alphabet: "По алфавиту",
  wms: "Система WMS",
  rush: "Отправить Ивана в кабину крана",
  wait: "Ждать крана по графику — 3 часа",
  petr: "Попросить Петра помочь",
  remote: "Иван управляет краном из офиса",
  helicopter: "Вертолёт",
  rover: "Снегоболотоход",
  robot: "Роботизированная тележка",
  "pipe-carrier": "Трубовоз",
};
const zeroScores: Scores = { energy: 0, empathy: 0, efficiency: 0 };
export function ChoiceVerdict({ picked, verdicts, score, all }: { picked: string; verdicts: Record<Tone, string>; score: Scores; all: Scores[] }) {
  const tone = rankChoice(score, all);
  const Icon = verdictIcons[tone];
  return (
    <span className={flow.compactVerdict} data-verdict={tone}>
      <small>{picked}</small>
      <span><Icon aria-hidden="true" size={26} strokeWidth={2.2} />{verdicts[tone]}</span>
    </span>
  );
}
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
  const [focusedChoice, setFocusedChoice] = useState<string>();
  // Barge: the quay pins are the only choice; a pin opens a card, the card confirms.
  const [pendingCrane, setPendingCrane] = useState<string>();
  const inspectsOnArt = scene.id === "crane" && state.phase === "choice";
  const pending = inspectsOnArt ? options.find(({ id }) => id === pendingCrane) : undefined;
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
      setPendingCrane(undefined);
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
      ? stage.current?.querySelector<HTMLButtonElement>(`:is([data-scene-choice], [data-hotspot])[data-${remainingScenes[state.sceneIndex].id === "crane" ? "hotspot" : "scene-choice"}="${lastChoice.current[remainingScenes[state.sceneIndex].id] ?? ""}"]`)
        ?? stage.current?.querySelector<HTMLButtonElement>("[data-scene-choice], [data-hotspot]")
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
  const brief = sceneBriefs[scene.id];
  const places = brief?.places(context);
  const syncFocus = brief ? { focusedId: focusedChoice, onFocusChange: setFocusedChoice } : {};
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
          data-inspecting={!!pending}
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
                scene.id === "crane" ? (
                  <>
                    <CraneDecisionContext />
                    <SceneGoals goals={brief!.goals} />
                  </>
                ) : brief ? (
                  <>
                    <div className={flow.compactCargo} data-compact-cargo>
                      <img src={thumbnailAsset(choiceArtwork[context.parcel])} alt="" />
                      <span><small>Груз</small><strong>{parcelNames[context.parcel].nominative}</strong></span>
                    </div>
                    <SceneGoals goals={brief.goals} />
                  </>
                ) : undefined
              }
              onBack={back}
              lead={
                brief ? (
                  <div className={flow.briefingLead} data-briefing-lead>
                    <img src={thumbnailAsset(choiceArtwork[context.parcel])} alt="" />
                    <span>
                      <small>{brief.eyebrow}</small>
                      <strong>{parcelNames[context.parcel].nominative}</strong>
                      <em>{brief.route(context)}</em>
                    </span>
                    <SceneGoals goals={brief.goals} />
                  </div>
                ) : undefined
              }
              inspecting={!!pending}
              onOpen={() => setPendingCrane(undefined)}
              action={inspectsOnArt ? (
                <CarrierTapHint selectedId={pending?.id} text="Нажмите на номер на причале" />
              ) : (
                <SceneChoices
                  variant="scene"
                  options={options.map((option) => ({
                    id: option.id,
                    showBadge: option.id !== "auto",
                    detail: places?.[option.id][1],
                    accessibleLabel:
                      scene.id === "compact" && option.id !== "auto"
                        ? `${optionTitles[option.id]}: ${places![option.id][0]}`
                        : undefined,
                    label:
                      places
                        ? places[option.id][0]
                        : option.id === "auto"
                          ? "Поручить размещение Compact"
                          : scene.id === "inventory" && option.id === "alphabet"
                            ? `Стеллаж «${inventoryAlphabet[context.parcel].letter}»`
                            : optionTitles[option.id] ?? choiceLabel(option.label),
                  }))}
                  {...syncFocus}
                  onInspect={choose}
                  badgeShape={
                    scene.id === "compact" || scene.id === "crane"
                      ? "square"
                      : "circle"
                  }
                />
              )}
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
                selectedId={resultVisible ? selected?.id : pending?.id}
                showResult={resultVisible}
                onSelect={state.phase === "choice" ? (inspectsOnArt ? setPendingCrane : choose) : undefined}
                {...syncFocus}
              />
            )}
          </section>
          {pending && (
            <ChoiceInspection
              selectionKey={pending.id}
              returnFocus={document.querySelector<HTMLElement>(`[data-hotspot="${pending.id}"]`)}
              eyebrow={craneCaptions[pending.id as keyof typeof craneCaptions]}
              title={optionTitles[pending.id]}
              cancelLabel="К причалу"
              onCancel={() => setPendingCrane(undefined)}
              onConfirm={() => choose(pending.id)}
            >
              <CraneFacts id={pending.id as keyof typeof craneFacts} />
            </ChoiceInspection>
          )}
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
                  title={brief && places ? <ChoiceVerdict picked={brief.picked(selected.id, places[selected.id][0])} verdicts={brief.verdicts} score={selected.score} all={options.map(o => o.score)} /> : title}
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
