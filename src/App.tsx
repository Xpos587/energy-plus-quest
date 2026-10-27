import { type CSSProperties, useEffect, useRef, useState } from "react";
import styles from "./App.module.css";
import { CarrierInspection } from "./components/CarrierInspection";
import { CarrierTapHint } from "./components/CarrierTapHint";
import { ChoiceInspection } from "./components/ChoiceInspection";
import { GameIntro } from "./components/GameIntro";
import { GiftPreparation } from "./components/GiftPreparation";
import { IllustratedCityMap } from "./components/IllustratedCityMap";
import { ImageSources } from "./components/ImageSources";
import { QuestHeader } from "./components/QuestShell";
import { ResultCopy } from "./components/ResultCopy";
import { SceneBriefing } from "./components/SceneBriefing";
import { SceneChoices } from "./components/SceneChoices";
import flow from "./components/SceneInteraction.module.css";
import { outcomeArtwork } from "./game/artwork";
import { carrierFacts } from "./game/carrierFacts";
import {
  carrierBriefing,
  carrierQuestion,
  carriers,
  findCarrier,
  findParcel,
  findRecipient,
} from "./game/content";
import {
  GameProvider,
  useGame,
  useOptionalSaveScope,
} from "./game/GameContext";
import { detailImageAsset, prefetchImage } from "./game/imageAssets";
import { interpolateOutcome } from "./game/outcomeText";
import { useStoredState } from "./game/persistence";
import type { CarrierId, GameAction } from "./game/types";
import { sceneChoiceImage } from "./scenes/artwork";
import { outcomeFocus } from "./scenes/outcomeFraming";
import { ChoiceVerdict, restartSceneCondition, SceneGoals, ScenesGame } from "./scenes/ScenesGame";

export function App() {
  return (
    <GameProvider persist>
      <Game />
    </GameProvider>
  );
}

function Game() {
  const { state, dispatch } = useGame();
  const scope = useOptionalSaveScope();
  const [remaining, setRemaining] = useStoredState(
    scope && `${scope}:remaining`,
    false,
    (v): v is boolean => typeof v === "boolean",
  );
  const [introSeen, setIntroSeen] = useStoredState(
    scope && `${scope}:intro-seen`,
    false,
    (v): v is boolean => typeof v === "boolean",
  );
  const [introOpen, setIntroOpen] = useState(false);
  const [carrierToFocus, setCarrierToFocus] = useState<CarrierId>();
  const navigate = (action: GameAction) => {
    setCarrierToFocus(
      action.type === "BACK" && state.step === "outcome"
        ? state.carrier
        : undefined,
    );
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    dispatch(action);
  };

  if (introOpen || (state.step === "profile" && !state.profile && !introSeen)) {
    return (
      <GameIntro
        onStart={() => {
          setIntroSeen(true);
          setIntroOpen(false);
        }}
      />
    );
  }

  if (remaining && state.profile && state.recipient && state.parcel) {
    return (
      <ScenesGame
        persistenceKey={scope && `${scope}:scenes`}
        context={{
          profile: state.profile,
          recipient: state.recipient,
          parcel: state.parcel,
          carrier: state.carrier,
        }}
        initialScores={state.scores}
        onRestart={() => {
          setRemaining(false);
          setIntroSeen(false);
          setIntroOpen(true);
          navigate({ type: "RESET" });
        }}
        onHome={() => {
          setRemaining(false);
          setIntroSeen(false);
          setIntroOpen(true);
          navigate({ type: "RESET" });
        }}
        onBackToCarrier={() => {
          setRemaining(false);
        }}
      />
    );
  }

  return (
    <div
      className={
        state.step === "carrier" || state.step === "outcome"
          ? flow.app
          : styles.app
      }
      data-step={state.step}
      data-scene="carrier"
    >
      <QuestHeader
        state={state}
        result={state.step === "outcome"}
        selectionStep={
          state.step === "profile"
            ? 1
            : state.step === "recipient"
              ? 2
              : state.step === "parcel"
                ? 3
                : undefined
        }
      />

      <main
        className={
          state.step === "carrier" || state.step === "outcome"
            ? flow.main
            : styles.main
        }
        id="quest-main"
      >
        <div
          className={
            state.step === "carrier" || state.step === "outcome"
              ? flow.screen
              : styles.screen
          }
          key={
            state.step === "profile" ||
            state.step === "recipient" ||
            state.step === "parcel"
              ? "preparation"
              : state.step
          }
        >
          {(state.step === "profile" ||
            state.step === "recipient" ||
            state.step === "parcel") && (
            <GiftPreparation
              state={state}
              onAction={navigate}
              onBackToIntro={() => setIntroOpen(true)}
            />
          )}
          {state.step === "carrier" && (
            <CarrierScreen
              focusCarrier={carrierToFocus}
              onBack={() => navigate({ type: "BACK" })}
              onSelect={(value) => navigate({ type: "CHOOSE_CARRIER", value })}
            />
          )}
          {state.step === "outcome" && (
            <Outcome
              onBack={() => navigate({ type: "BACK" })}
              onNext={() => {
                if (state.profile && state.recipient && state.parcel) {
                  restartSceneCondition(
                    "compact",
                    {
                      profile: state.profile,
                      recipient: state.recipient,
                      parcel: state.parcel,
                    },
                    scope,
                  );
                }
                setRemaining(true);
              }}
            />
          )}
        </div>
      </main>
    </div>
  );
}

function CarrierScreen({
  onSelect,
  onBack,
  focusCarrier,
}: {
  onSelect: (value: CarrierId) => void;
  onBack: () => void;
  focusCarrier?: CarrierId;
}) {
  const { state } = useGame();
  const scope = useOptionalSaveScope();
  const [pendingId, setPendingId] = useStoredState<CarrierId | undefined>(
    scope && `${scope}:carrier-pending`,
    undefined,
    (v): v is CarrierId | undefined =>
      typeof v === "string" &&
      ["old", "old4", "near", "crew", "express"].includes(v),
  );
  const [mapReading, setMapReading] = useState(false);
  const taskSentences = carrierQuestion.split(/(?<=\.)\s+/);
  const taskQuestion = (taskSentences.at(-1) ?? carrierQuestion).replace(
    /:\s*$/,
    "",
  );
  const panel = useRef<HTMLElement>(null);
  const choiceTrigger = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!pendingId) return;
    const dismissOutside = (event: PointerEvent) => {
      const target = event.target;
      if (
        !(target instanceof Element) ||
        target.closest(
          "[data-choice-inspection], [data-carrier-choice], [data-scene-choice], [data-map-viewport], [data-map-controls]",
        )
      )
        return;
      setPendingId(undefined);
    };
    document.addEventListener("pointerdown", dismissOutside, true);
    return () =>
      document.removeEventListener("pointerdown", dismissOutside, true);
  }, [pendingId, setPendingId]);
  useEffect(() => {
    const element = panel.current;
    const release = () => setPendingId(undefined);
    element?.addEventListener("scene-map-inspection-release", release);
    return () =>
      element?.removeEventListener("scene-map-inspection-release", release);
  }, [setPendingId]);
  const inspect = (id: CarrierId) => {
    choiceTrigger.current =
      document.activeElement instanceof HTMLElement &&
      document.activeElement.matches(
        "[data-scene-choice], [data-carrier-choice]",
      )
        ? document.activeElement
        : (panel.current?.querySelector(`[data-scene-choice="${id}"]`) ?? null);
    setPendingId(id);
  };
  useEffect(() => {
    if (!pendingId) return;
    const format = matchMedia("(max-width: 600px)").matches
      ? "mobile"
      : "desktop";
    return prefetchImage(outcomeArtwork[pendingId][format]);
  }, [pendingId]);
  useEffect(() => {
    if (!focusCarrier) return;
    const selected = panel.current?.querySelector<HTMLButtonElement>(
      `[data-scene-choice="${focusCarrier}"], [data-carrier-choice="${focusCarrier}"]`,
    );
    selected?.focus({ preventScroll: true });
    selected?.scrollIntoView({ block: "nearest", inline: "nearest" });
  }, [focusCarrier]);
  return (
    <section
      className={flow.frame}
      ref={panel}
      data-interaction="inspect-confirm"
      data-carrier-layout
      id="carrier-choice-scene"
      data-inspecting={!!pendingId}
      data-camera-inspection={
        (!!pendingId && pendingId !== "express") || undefined
      }
    >
      <SceneBriefing
        currentStep={0}
        title="Выбор перевозчика"
        showLeadOnChoice={false}
        // The hidden text is the destination: name it, not "the task".
        conditionLabel="Куда везём?"
        initiallyOpen={false}
        question={taskQuestion}
        navigation="fixed"
        onReadingChange={setMapReading}
        paragraphs={[
          interpolateOutcome(
            carrierBriefing,
            undefined,
            findParcel(state.parcel)?.accusativeTitle,
          ),
          ...taskSentences.slice(0, -1),
        ]}
        onBack={onBack}
        inspecting={!!pendingId}
        onOpen={() => setPendingId(undefined)}
        // The rigs on the map are the only way to choose.
        action={<CarrierTapHint selectedId={pendingId} />}
        decisionContext={<SceneGoals goals={carrierGoals} />}
      />
      <div className={flow.carrierMap} data-carrier-map>
        <IllustratedCityMap
          interactive={!mapReading}
          onSelect={inspect}
          selectedId={pendingId}
        />
      </div>
      {pendingId && (
        <ChoiceInspection
          returnFocus={choiceTrigger.current}
          selectionKey={pendingId}
          media={pendingId !== "express"}
          eyebrow={
            // Crew already lists «Два водителя» in its facts; Express has its own title.
            pendingId === "express" || pendingId === "crew"
              ? undefined
              : findCarrier(pendingId)?.eyebrow
          }
          title={
            pendingId === "express"
              ? "Express подберёт фуру"
              : carrierFacts[pendingId].label
          }
          cancelLabel="Другая фура"
          onCancel={() => setPendingId(undefined)}
          onConfirm={() => onSelect(pendingId)}
        >
          <CarrierInspection carrierId={pendingId} showPreview={false} />
        </ChoiceInspection>
      )}
    </section>
  );
}

const carrierGoals: [string, string, string] = ["Без лишних трат", "Порадовать раньше", "Надёжная фура"];
const carrierVerdicts = { best: "Отличный перевозчик", fair: "Можно лучше", bad: "Неудачный выбор" };

function Outcome({
  onBack,
  onNext,
}: {
  onBack: () => void;
  onNext: () => void;
}) {
  const { state } = useGame();
  const carrier = findCarrier(state.carrier);
  const recipient = findRecipient(state.recipient);
  const parcel = findParcel(state.parcel);
  useEffect(
    () =>
      prefetchImage(
        detailImageAsset(sceneChoiceImage("compact")),
        undefined,
        true,
      ),
    [],
  );
  // The scenario heading («Близко — не значит быстро!») stays as the opening
  // line; the verdict above it reads the same in every scene.
  const resultNarrative = carrier
    ? interpolateOutcome(
        [carrier.resultTitle, carrier.resultBody].filter(Boolean).join(" "),
        recipient?.title,
        parcel?.accusativeTitle,
      )
    : "";

  if (!carrier) {
    return null;
  }
  const portraitArtwork = outcomeArtwork[carrier.id].portrait;

  return (
    <section
      className={flow.frame}
      data-carrier={carrier.id}
      data-layout="result"
    >
      <div
        className={flow.outcomePicture}
        data-result-art
        style={
          {
            "--outcome-focus": outcomeFocus[`carrier-${carrier.id}`],
          } as CSSProperties
        }
      >
        <picture>
          {outcomeArtwork[carrier.id].wide && (
            <ImageSources
              media="(min-width: 901px) and (min-height: 501px)"
              src={outcomeArtwork[carrier.id].wide!}
            />
          )}
          {portraitArtwork && (
            <ImageSources
              media="(max-width: 600px) and (min-height: 700px) and (orientation: portrait)"
              src={portraitArtwork}
            />
          )}
          <ImageSources
            media="(max-width: 600px) and (orientation: landscape)"
            src={outcomeArtwork[carrier.id].mobile}
          />
          <ImageSources src={outcomeArtwork[carrier.id].desktop} />
          <img
            alt=""
            aria-hidden="true"
            className={flow.outcomeBackdrop}
            data-art-version="current"
            data-outcome-art={carrier.id}
            fetchPriority="high"
            loading="eager"
            decoding="async"
            src={outcomeArtwork[carrier.id].desktop}
          />
        </picture>
      </div>
      <div
        className={flow.result}
        data-sheet-panel
        data-carrier={carrier.id}
        data-carrier-outcome
      >
        <div className={flow.resultInner}>
          <div className={flow.resultStory}>
            <ResultCopy
              fillSpace
              key={carrier.id}
              titleTabIndex={-1}
              title={
                <ChoiceVerdict
                  picked={`Ваш выбор · ${carrier.id === "express" ? "Express" : carrierFacts[carrier.id].label}`}
                  verdicts={carrierVerdicts}
                  score={carrier.score}
                  all={carriers.map((item) => item.score)}
                />
              }
              paragraphs={[resultNarrative]}
              navigation={{
                scores: carrier.score,
                onBack,
                onNext,
                backLabel: "Назад к машинам",
                nextLabel: "Дальше: погрузка",
              }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
