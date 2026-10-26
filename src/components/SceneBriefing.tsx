import { clearReadingState, useReadingState } from "./useReadingState";
import { PageText } from "./PageText";
import { StageIndicator } from "./StageIndicator";
import { ArrowLeft, ArrowRight, Info } from "lucide-react";
import {
  type ReactNode,
  useEffect,
  useLayoutEffect,
  useId,
  useRef,
  useState,
} from "react";
import { QuestBrand, progressSteps } from "./QuestShell";
import { useTextPages } from "./useTextPages";
import styles from "./SceneInteraction.module.css";

function briefingReadingKeys(title: string, paragraphs: string[]) {
  const text = paragraphs.join("\n\n");
  return [
    "briefing:open:" + title + text,
    "SceneBriefing:page:" + text,
  ] as const;
}

export function resetBriefingReadingState(
  scope: string | undefined,
  title: string,
  paragraphs: string[],
) {
  clearReadingState(scope, [
    ...briefingReadingKeys(title, paragraphs),
    "map-navigation:" + title,
  ]);
}

export function SceneBriefing({
  title,
  currentStep = 0,
  paragraphs,
  question,
  context,
  hint,
  navigation = "pan",
  action,
  decisionContext,
  onBack,
  onOpen,
  onReadingChange,
  onConditionComplete,
  inspecting = false,
  keepParagraphs = false,
  initiallyOpen = false,
  keepPanHint = false,
  showLeadOnChoice = true,
  conditionLabel = "О задаче",
}: {
  title: string;
  currentStep?: number;
  paragraphs: string[];
  question: string;
  context?: string;
  hint?: string;
  navigation?: "pan" | "zoom" | "fixed";
  action?: ReactNode;
  decisionContext?: ReactNode;
  onBack?: () => void;
  onOpen?: () => void;
  onReadingChange?: (reading: boolean) => void;
  onConditionComplete?: () => void;
  inspecting?: boolean;
  keepParagraphs?: boolean;
  initiallyOpen?: boolean;
  keepPanHint?: boolean;
  showLeadOnChoice?: boolean;
  combineCondition?: boolean;
  /** Names what the hidden condition holds, e.g. «Куда везём?». */
  conditionLabel?: string;
}) {
  // A separate first-entry condition and optional rereading share the same pages.
  const inlineCondition = false;
  const [openKey, pageKey] = briefingReadingKeys(title, paragraphs);
  const [open, setOpen] = useReadingState<boolean>(openKey, initiallyOpen);
  // biome-ignore lint/correctness/useExhaustiveDependencies: persist the entry mode once for this exact condition; later reopening stays user-controlled.
  useLayoutEffect(() => {
    setOpen(initiallyOpen);
  }, [initiallyOpen, openKey]);
  const [page, setPage] = useReadingState<number>(pageKey, 0);
  const [canPan, setCanPan] = useState(false);
  const [panDone, setPanDone] = useState(!initiallyOpen);
  const [choiceDone, setChoiceDone] = useState(false);
  const [zoomDone, setZoomDone] = useReadingState<boolean>(
    "map-navigation:" + title,
    false,
  );
  const showPanHint =
    navigation === "pan" && canPan && (!panDone || keepPanHint);
  const showChoiceHint =
    navigation !== "fixed" &&
    !!hint &&
    !choiceDone &&
    !(navigation === "zoom" && zoomDone);
  const toggle = useRef<HTMLButtonElement>(null);
  const focusAfterClose = useRef(false);
  const briefing = useRef<HTMLElement>(null);
  const id = useId();
  const visible =
    open && !inlineCondition && !inspecting && paragraphs.length > 0;
  useLayoutEffect(() => {
    onReadingChange?.(visible);
  }, [visible, onReadingChange]);
  const leadLength = 0;
  const { body, pages } = useTextPages(
    paragraphs,
    visible,
    true,
    keepParagraphs,
    false,
    false,
    keepParagraphs,
    leadLength,
  );
  const current = Math.min(page, Math.max(0, pages.length - 1));
  useLayoutEffect(() => {
    if (visible) body.current?.focus({ preventScroll: true });
  }, [visible, current]);
  const backLabel =
    currentStep === 0
      ? "К выбору подарка"
      : `К этапу «${progressSteps[currentStep - 1].label}»`;
  useLayoutEffect(() => {
    if (!visible && focusAfterClose.current) {
      focusAfterClose.current = false;
      toggle.current?.focus({ preventScroll: true });
    }
  }, [visible]);
  useLayoutEffect(() => {
    if (!visible) return;
    const region = briefing.current;
    const frame = region?.closest('[data-interaction="inspect-confirm"]');
    if (!frame || !region) return;
    const siblings = [...frame.children].filter(
      (node): node is HTMLElement =>
        node instanceof HTMLElement && !node.contains(region),
    );
    const previous = siblings.map((node) => node.inert);
    siblings.forEach((node) => {
      node.inert = true;
    });
    const blockChoice = (event: Event) => {
      if (event.target instanceof Node && !region.contains(event.target)) {
        event.preventDefault();
        event.stopPropagation();
      }
    };
    frame.addEventListener("click", blockChoice, true);
    return () => {
      siblings.forEach((node, index) => {
        node.inert = previous[index];
      });
      frame.removeEventListener("click", blockChoice, true);
    };
  }, [visible]);
  useEffect(() => {
    if (inspecting) {
      setOpen(false);
      setPanDone(true);
      setChoiceDone(true);
      if (navigation === "zoom") setZoomDone(true);
    }
  }, [inspecting, navigation]);
  useEffect(() => {
    if (navigation !== "zoom" || visible || inspecting || zoomDone) return;
    const frame = briefing.current?.closest(
      '[data-interaction="inspect-confirm"]',
    );
    if (!frame) return;
    const dismiss = () => setZoomDone(true);
    frame.addEventListener("scene-map-gesture-start", dismiss);
    return () => frame.removeEventListener("scene-map-gesture-start", dismiss);
  }, [navigation, visible, inspecting, zoomDone, setZoomDone]);
  useLayoutEffect(() => {
    if (navigation !== "pan") return;
    const viewport = briefing.current
      ?.closest('[data-interaction="inspect-confirm"]')
      ?.querySelector<HTMLElement>("[data-pan-viewport]");
    if (!viewport) return;
    const measure = () => {
      setCanPan(viewport.scrollWidth - viewport.clientWidth > 8);
    };
    measure();
    const observer =
      typeof ResizeObserver === "undefined"
        ? undefined
        : new ResizeObserver(measure);
    observer?.observe(viewport);
    if (viewport.firstElementChild)
      observer?.observe(viewport.firstElementChild);
    window.addEventListener("resize", measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, [navigation, visible]);
  useEffect(() => {
    if (!showPanHint || visible || inspecting || panDone) return;
    const viewport = briefing.current
      ?.closest('[data-interaction="inspect-confirm"]')
      ?.querySelector<HTMLElement>("[data-pan-viewport]");
    if (!viewport) return;
    const maxScroll = viewport.scrollWidth - viewport.clientWidth;
    const startScroll = viewport.scrollLeft;
    const distance = Math.min(40, maxScroll / 2);
    if (maxScroll <= 8) return;
    let animation = 0;
    let held = false;
    let touching = false;
    let elapsed = 0;
    let previousTime: number | undefined;
    const dismiss = () => setPanDone(true);
    const pause = () => {
      held = true;
    };
    const resume = () => {
      held = false;
    };
    const touchStart = () => {
      touching = true;
    };
    const touchEnd = (event: TouchEvent) => {
      touching = event.touches.length > 0;
    };
    if (!window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) {
      const animate = (time: number) => {
        if (!held && !touching)
          elapsed += previousTime === undefined ? 0 : time - previousTime;
        previousTime = time;
        const cycle = hint ? 6000 : 3600;
        const progress = hint
          ? Math.min((elapsed % cycle) / 2400, 1)
          : (elapsed % cycle) / cycle;
        const eased = progress * progress * (3 - 2 * progress);
        const inward = (distance * (1 - Math.cos(progress * Math.PI * 2))) / 2;
        const offset =
          startScroll < distance
            ? inward
            : maxScroll - startScroll < distance
              ? -inward
              : distance * Math.sin(eased * Math.PI * 2);
        if (!held && !touching)
          viewport.scrollLeft = Math.max(
            0,
            Math.min(maxScroll, startScroll + offset),
          );
        animation = requestAnimationFrame(animate);
      };
      animation = requestAnimationFrame(animate);
    }
    viewport.addEventListener("scene-pan-start", dismiss);
    viewport.addEventListener("pointerdown", pause);
    viewport.addEventListener("touchstart", touchStart, { passive: true });
    window.addEventListener("pointerup", resume);
    window.addEventListener("pointercancel", resume);
    window.addEventListener("touchend", touchEnd);
    window.addEventListener("touchcancel", touchEnd);
    return () => {
      cancelAnimationFrame(animation);
      viewport.removeEventListener("scene-pan-start", dismiss);
      viewport.removeEventListener("pointerdown", pause);
      viewport.removeEventListener("touchstart", touchStart);
      window.removeEventListener("pointerup", resume);
      window.removeEventListener("pointercancel", resume);
      window.removeEventListener("touchend", touchEnd);
      window.removeEventListener("touchcancel", touchEnd);
    };
  }, [showPanHint, visible, inspecting, hint, panDone]);
  const close = () => {
    focusAfterClose.current = true;
    setOpen(false);
    onConditionComplete?.();
  };
  return (
    <section
      className={styles.briefing}
      aria-label="Задание сцены"
      data-scene-briefing
      data-reading={visible}
      data-combined-condition={inlineCondition || undefined}
      data-briefing-inline={inlineCondition}
      data-briefing-longform={keepParagraphs || undefined}
      ref={briefing}
    >
      <div className={styles.headerCard}>
        <QuestBrand />
        <div className={styles.briefingHeading}>
          <div className={styles.sceneIdentity}>
            <h2 tabIndex={-1}>{title}</h2>
            <StageIndicator
              step={currentStep + 1}
              total={progressSteps.length}
              label={progressSteps[currentStep].label}
            />
          </div>
        </div>
      </div>
      <div
        className={styles.question}
        data-testid="scene-question"
        inert={visible}
      >
        {!visible && showLeadOnChoice && paragraphs[0] && (
          <p className={styles.questionLead}>{paragraphs[0]}</p>
        )}
        {inlineCondition && (
          <div className={styles.inlineCondition} data-testid="scene-intro">
            {paragraphs.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>
        )}
        <div className={styles.questionTop} data-choice-prompt>
          <p className={styles.questionPrompt}>{question}</p>
        </div>

        {decisionContext}
        {action && (
          <div className={styles.questionAction} data-choice-actions>
            {action}
          </div>
        )}
        {context && <span className={styles.questionContext}>{context}</span>}
        {showPanHint && !showChoiceHint && !visible && !inspecting && (
          <span
            className={styles.questionHint}
            role="status"
            data-scene-hint="pan"
            data-persistent={keepPanHint || undefined}
          >
            <span aria-hidden="true">↔ </span>
            {keepPanHint ? "Ещё варианты — листайте сцену" : "Листайте сцену"}
          </span>
        )}
        {(onBack || (paragraphs.length > 0 && !inlineCondition)) && (
          <div className={styles.questionNavigation} data-choice-navigation>
            {onBack && (
              <button
                className={styles.secondary}
                type="button"
                onClick={onBack}
              >
                <ArrowLeft size={18} aria-hidden="true" />
                {backLabel}
              </button>
            )}
            {paragraphs.length > 0 && !inlineCondition && (
              <button
                ref={toggle}
                className={`${styles.condition} ${styles.questionTask}`}
                type="button"
                aria-controls={id}
                aria-expanded={visible}
                disabled={visible}
                onClick={() => {
                  if (!visible) onOpen?.();
                  setPage(0);
                  setOpen(!visible);
                }}
              >
                <Info size={18} aria-hidden="true" />
                {conditionLabel}
              </button>
            )}
          </div>
        )}
      </div>
      {showChoiceHint && !visible && !inspecting && (
        <div
          className={`${styles.panHint} ${showChoiceHint ? styles.carrierTutorial : ""}`}
          role="status"
          data-scene-hint={showChoiceHint ? "carrier" : "pan"}
          data-can-pan={canPan}
          data-navigation={navigation}
        >
          <svg aria-hidden="true" viewBox="0 0 116 72">
            {navigation === "zoom" && (
              <g className={styles.tutorialPinch}>
                <path
                  className={styles.pinchArrows}
                  d="m20 17-8-8m0 7V9h7m19 29 8 8m-7 0h7v-7"
                />
                <g className={styles.pinchFingerFirst}>
                  <circle cx="0" cy="0" r="6" />
                  <path d="M-3 15V1a3 3 0 0 1 6 0v10l7 2a4 4 0 0 1 3 4l-2 10H0l-6-10a2 2 0 0 1 3-3l3 3" />
                </g>
                <g className={styles.pinchFingerSecond}>
                  <circle cx="0" cy="0" r="6" />
                  <path d="M-3 15V1a3 3 0 0 1 6 0v10l7 2a4 4 0 0 1 3 4l-2 10H0l-6-10a2 2 0 0 1 3-3l3 3" />
                </g>
              </g>
            )}
            {canPan && (
              <path
                className={styles.tutorialSwipe}
                d="m17 17-7 6 7 6m23-12 7 6-7 6M11 23h35"
              />
            )}
            <g className={styles.tutorialTruck}>
              <path d="M59 13h31v22H59zM90 20h12l8 9v6H90M96 23h5l5 6H96z" />
              <circle cx="68" cy="37" r="4" />
              <circle cx="101" cy="37" r="4" />
            </g>
            <circle className={styles.tutorialTap} cx="85" cy="24" r="10" />
            <g className={styles.tutorialHand}>
              <path d="M0 13V2a2 2 0 0 1 4 0v8l9 2a3 3 0 0 1 2 3l-1 8H3l-7-9a2 2 0 0 1 3-3l3 3" />
            </g>
          </svg>
          <span>
            {navigation === "zoom" ? (
              <>
                Приблизьте карту
                <br />и нажмите на фуру
              </>
            ) : (
              <>
                {canPan && (
                  <>
                    Листайте сцену
                    <br />и{" "}
                  </>
                )}
                {canPan ? "нажмите на фуру" : hint}
              </>
            )}
          </span>
        </div>
      )}
      {visible && (
        <section
          id={id}
          className={styles.briefingCard}
          aria-label="Условие задания"
        >
          <section
            ref={body}
            aria-label="Текст условия"
            tabIndex={-1}
            className={styles.briefingCopy}
            data-testid="scene-intro"
            aria-live="polite"
          >
            <p>
              <PageText
                text={pages[current]}
                leadLength={current === 0 ? leadLength : 0}
              />
            </p>
          </section>
          <div className={styles.dialogueActions}>
            {(current > 0 || onBack) && (
              <button
                type="button"
                className={styles.dialoguePrevious}
                onClick={() =>
                  current > 0 ? setPage(current - 1) : onBack?.()
                }
              >
                <ArrowLeft size={18} aria-hidden="true" />
                {current > 0 ? "Предыдущая страница" : backLabel}
              </button>
            )}
            <button
              type="button"
              className={styles.dialogueNext}
              onClick={() =>
                current < pages.length - 1 ? setPage(current + 1) : close()
              }
            >
              {current < pages.length - 1 ? "Далее" : "К выбору"}
              <ArrowRight size={18} aria-hidden="true" />
            </button>
          </div>
        </section>
      )}
    </section>
  );
}
