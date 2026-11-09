import { ChartLine, Heart, Zap } from "lucide-react";
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
import type { ParcelId, Scores } from "../game/types";
import { sceneChoiceImage } from "./artwork";
import { deliveryLine, parcelNames, recipientNames } from "./names";
import { choiceLabel } from "./choiceLabel";
import { compactScene } from "./compact";
import { CompactCard } from "./compact/CompactCard";
import { craneScene } from "./crane";
import { craneCaptions, craneFacts } from "./crane/artwork";
import { CraneDecisionContext, CraneFacts } from "./crane/CraneDecisionContext";
import { inventoryScene } from "./inventory";
import { inventoryAlphabet } from "./inventory/alphabet";
import { JourneyEnding } from "./JourneyEnding";
import { lastmileScene } from "./lastmile";
import { LastmileDecisionContext, lastmileHeadings } from "./lastmile/LastmileFacts";
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
type SceneBrief = {
  eyebrow: string;
  route: (context: SceneContext) => string;
  goals: [energy: string, empathy: string, efficiency: string];
  places: (context: SceneContext) => Record<string, [name: string, detail: string]>;
};
const sceneBriefs: Partial<Record<SceneId, SceneBrief>> = {
  compact: {
    eyebrow: "Наряд на погрузку",
    route: () => "Фура до склада в Лабытнанги",
    goals: ["Погрузить быстро", "Довезти целым", "Не занять лишнее"],
    // The highlighted square names the place; no captions that hint at the outcome.
    places: () => ({
      "place-1": ["Место 1", ""],
      "place-2": ["Место 2", ""],
      "place-3": ["Место 3", ""],
      "place-4": ["Место 4", ""],
      auto: ["Подобрать автоматически", ""],
    }),
  },
  inventory: {
    eyebrow: "Карточка хранения",
    route: () => "Склад в Лабытнанги, пару дней до баржи",
    goals: ["Без лишнего крюка", "Не потерять подарок", "Ближе к отгрузке"],
    places: ({ parcel }) => ({
      entrance: ["У приёмки", "Свободные ячейки у входа"],
      alphabet: [`Стеллаж «${inventoryAlphabet[parcel].letter}»`, "По первой букве названия"],
      keeper: ["Кладовщик", "Спросить опытного коллегу"],
      wms: ["Автоподбор места", "Система Inventory сама подберёт ячейку"],
    }),
  },
  crane: {
    eyebrow: "Погрузка на баржу",
    route: () => "С причала на баржу до Нового Порта",
    goals: ["Беречь силы", "Позаботиться о людях", "Успеть к барже"],
    places: () => Object.fromEntries(
      Object.entries(craneFacts).map(([id, fact]) => [id, [optionTitles[id], fact.note]]),
    ),
  },
  lastmile: {
    eyebrow: "Последняя миля",
    route: ({ recipient }) => `От причала в Новом Порту до ${recipientNames[recipient].genitive}`,
    goals: ["Без лишних трат", "Довезти лично", "Пройти болота"],
    places: () => ({
      helicopter: ["Вертолёт", "По воздуху"],
      rover: ["Снегоболотоход", "Вездеход-амфибия"],
      robot: ["Роботизированная тележка", "Складской робот"],
      "pipe-carrier": ["Трубовоз", "Грузовик для труб"],
    }),
  },
};
// One hint for scenes 2–5: what to tap, then the hovered name and what the tap does.
const tapHintIdle: Partial<Record<SceneId, string>> = {
  compact: "Нажмите на место в кузове",
  inventory: "Нажмите на подсвеченное место на складе",
  crane: "Нажмите на человека или кран",
  lastmile: "Нажмите на транспорт",
};
const tapHintText = (id: SceneId, focused?: string) =>
  focused ? `${focused} · нажмите, чтобы ${id === "lastmile" ? "выбрать" : "узнать подробнее"}` : tapHintIdle[id];
/** Result headings (R18 draft for Teo): what happened, taken from the result text; no score verdict. */
const resultHeadings: Partial<Record<SceneId, Record<string, string>>> = {
  inventory: {
    entrance: "Лишний крюк до отгрузки",
    alphabet: "Подарок в середине алфавита, груз — в начале",
    keeper: "Место знал один кладовщик",
    wms: "Система выбрала место у отгрузки",
  },
  crane: {
    remote: "Кран из офиса, без подъёма",
    rush: "Подъём в кабину — много сил",
    wait: "Баржа ушла без подарка",
    petr: "Пётр выручил, свой груз отложил",
  },
  lastmile: lastmileHeadings,
};
/** Scene 1 result headings (R19, call 05.11): what happened to the parcel, no verdict. */
export const carrierHeadings: Record<string, string> = {
  old: "Сервис — подарок на неделю позже",
  old4: "Сервис — подарок на неделю позже",
  near: "Рядом, но на три дня позже",
  crew: "За рулём двое — на три дня раньше",
  express: "Платформа выбрала — на неделю раньше",
};
// The truck outcome depends on the parcel.
const compactHeadings: Record<ParcelId, Record<string, string>> = {
  socks: {
    "place-1": "Один носок здесь, другой там",
    "place-2": "Носки под крышей — больше ничего не влезет",
    "place-3": "Носки в нише, место осталось",
    "place-4": "Носки заняли место трёх ящиков",
    auto: "Compact выбрал место 3",
  },
  camera: {
    "place-1": "Фотоаппарат разбил посуду",
    "place-2": "Место над фотоаппаратом пустует",
    "place-3": "Фотоаппарат в нише — до него тянуться",
    "place-4": "К фотоаппарату долго пробирались",
    auto: "Compact выбрал место 3",
  },
  boat: {
    "place-1": "Перегруз сломал фуру",
    "place-2": "Лодка разбила посуду",
    "place-3": "Лодка не поместилась в нишу",
    "place-4": "Лодку закрепили стоя",
    auto: "Compact выбрал место 4",
  },
};
export const resultHeading = (scene: SceneId, id: string, parcel: ParcelId = "socks") =>
  (scene === "compact" ? compactHeadings[parcel] : resultHeadings[scene])?.[id];
export function SceneGoals({ goals }: { goals: SceneBrief["goals"] }) {
  return (
    <ul className={flow.compactGoals} aria-label="Что важно" data-compact-goals>
      {scorePoints.map(({ key, icon: Icon, score }, index) => (
        <li key={key} data-goal-key={key} data-metric={key}><Icon aria-hidden="true" size={16} strokeWidth={2.2} /><span>{goals[index]}</span><small>{score}</small></li>
      ))}
    </ul>
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
  wms: "Автоподбор места",
  rush: "Иван идёт на кран и поднимается в кабину",
  wait: "Ждать кран по графику — 3 часа",
  petr: "Попросить Петра помочь",
  remote: "Иван управляет краном удалённо из офиса ПРУ",
  helicopter: "Вертолёт",
  rover: "Снегоболотоход",
  robot: "Роботизированная тележка",
  "pipe-carrier": "Трубовоз",
};
const zeroScores: Scores = { energy: 0, empathy: 0, efficiency: 0 };

export function ChoiceVerdict({ picked, heading }: { picked: string; heading: string }) {
  return (
    <span className={flow.compactVerdict} data-verdict="none">
      <small>{picked}</small>
      <span>{heading}</span>
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
  // Truck, barge and last mile: the places on the art are the only choice; a place opens a card, the card confirms.
  const [pendingId, setPendingId] = useState<string>();
  // Barge: after the card confirms, the quay plays the way out before the result.
  const [playingCrane, setPlayingCrane] = useState<string>();
  const inspectsOnArt = ["crane", "compact", "lastmile", "inventory"].includes(scene.id) && state.phase === "choice";
  const pending = inspectsOnArt ? options.find(({ id }) => id === pendingId) : undefined;
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
      setPendingId(undefined);
      setPlayingCrane(undefined);
      dispatch({ type: "CHOOSE", id });
    }
  };
  const playing = inspectsOnArt && scene.id === "crane" ? playingCrane : undefined;
  // A new screen starts clean: no stale hover/focus highlight carried over from the last pick (R19).
  useEffect(() => { setPlayingCrane(undefined); setFocusedChoice(undefined); }, [state.sceneIndex, state.phase]);

  useEffect(() => {
    const screen = `${state.sceneIndex}:${state.phase}`;
    if (previousScreen.current === screen) return;
    previousScreen.current = screen;
    const destination = stage.current?.querySelector<HTMLElement>(
      '[data-reading="true"] [data-testid="scene-intro"]',
    ) ?? (state.phase === "choice"
      ? stage.current?.querySelector<HTMLButtonElement>(`:is([data-scene-choice], [data-hotspot])[data-${["crane", "compact", "lastmile", "inventory"].includes(remainingScenes[state.sceneIndex].id) ? "hotspot" : "scene-choice"}="${lastChoice.current[remainingScenes[state.sceneIndex].id] ?? ""}"]`)
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
              // Scene 2 (Teo 05.11): condition and choice on one screen, no separate intro step.
              initiallyOpen={scene.id !== "compact" && !session.briefed?.includes(scene.id)}
              showLeadOnChoice={scene.id === "compact"}
              onConditionComplete={() => setSession(current => ({
                ...current,
                briefed: [...new Set([...(current.briefed ?? []), scene.id])],
              }))}
              navigation="fixed"
              question={question}
              keepParagraphs={scene.id === "crane"}
              decisionContext={
                scene.id === "crane" || scene.id === "lastmile" ? (
                  <>
                    {scene.id === "crane" ? <CraneDecisionContext /> : <LastmileDecisionContext />}
                    {/* Last scene, tired players (05.11): the task is plain text, no goal icons. */}
                    {scene.id === "crane" && <SceneGoals goals={brief!.goals} />}
                  </>
                ) : brief ? (
                  <SceneGoals goals={brief.goals} />
                ) : undefined
              }
              onBack={back}
              reminder={brief ? [deliveryLine(context.parcel, context.recipient), brief.route(context)] : undefined}
              lead={
                brief ? (
                  <div className={flow.briefingLead} data-briefing-lead>
                    <img src={thumbnailAsset(choiceArtwork[context.parcel])} alt="" />
                    <span>
                      <small>{brief.eyebrow}</small>
                      <strong>{parcelNames[context.parcel].nominative}</strong>
                      <em>{brief.route(context)}</em>
                    </span>
                    {scene.id !== "lastmile" && <SceneGoals goals={brief.goals} />}
                  </div>
                ) : undefined
              }
              inspecting={!!pending}
              onOpen={() => setPendingId(undefined)}
              action={inspectsOnArt ? undefined : (
                <SceneChoices
                  variant="scene"
                  options={options.map((option) => ({
                    id: option.id,
                    detail: places?.[option.id][1],
                    label: places ? places[option.id][0] : optionTitles[option.id] ?? choiceLabel(option.label),
                  }))}
                  {...syncFocus}
                  onInspect={choose}
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
                onSelect={state.phase === "choice" && !playing ? (inspectsOnArt && scene.id !== "lastmile" ? setPendingId : choose) : undefined}
                playing={playing}
                onPlayed={playing ? () => choose(playing) : undefined}
                {...syncFocus}
              />
            )}
            {/* Fetch the result picture while the quay plays, so the hand-off is not a loading flash. */}
            {playing && <div hidden><SceneOutcomeArt scene={scene.id} selectedId={playing} context={context} /></div>}
            {inspectsOnArt && !resultVisible && !playing && (
              <CarrierTapHint
                selectedId={pending?.id}
                text={tapHintText(scene.id, focusedChoice && (scene.id === "crane" ? craneCaptions[focusedChoice as keyof typeof craneCaptions] : places?.[focusedChoice]?.[0]))}
              />
            )}
          </section>
          {pending && (
            <ChoiceInspection
              selectionKey={pending.id}
              returnFocus={document.querySelector<HTMLElement>(`[data-hotspot="${pending.id}"]`)}
              title={scene.id === "compact" || scene.id === "inventory" ? places![pending.id][0] : optionTitles[pending.id]}
              cancelLabel={scene.id === "compact" ? "К кузову" : scene.id === "inventory" ? "К складу" : "К причалу"}
              paragraphs={scene.id === "inventory" ? [choiceLabel(pending.label)] : undefined}
              onCancel={() => setPendingId(undefined)}
              onConfirm={() => {
                setPendingId(undefined);
                if (scene.id === "crane") setPlayingCrane(pending.id);
                else choose(pending.id);
              }}
            >
              {scene.id === "compact"
                ? pending.id === "auto" ? <CompactCard /> : undefined
                : scene.id === "inventory" ? undefined
                : <CraneFacts id={pending.id as keyof typeof craneFacts} />}
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
                  title={brief && places ? (
                    // Teo 05.11: a plain line about what happened, no score verdict.
                    <span className={flow.compactVerdict} data-verdict="none" data-result-heading={selected.id}>
                      <span>{resultHeading(scene.id, selected.id, context.parcel)}</span>
                    </span>
                  ) : title}
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
