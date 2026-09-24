import {
  type ReactNode,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
} from "react";
import styles from "../App.module.css";

export function DescriptionSheet({
  expanded,
  onExpandedChange,
  children,
  result = false,
  collapsedLabel,
}: {
  expanded: boolean;
  onExpandedChange: (expanded: boolean) => void;
  children: ReactNode;
  result?: boolean;
  collapsedLabel?: string;
}) {
  const id = useId();
  const toggle = useRef<HTMLButtonElement>(null);
  const gesture = useRef<{ y: number; pointer: number } | null>(null);
  const swiped = useRef(false);
  const previousTop = useRef<number | null>(null);
  const animation = useRef<Animation | null>(null);
  const changeExpanded = (next: boolean) => {
    const panel = toggle.current?.closest<HTMLElement>("[data-sheet-panel]");
    animation.current?.cancel();
    previousTop.current = panel?.getBoundingClientRect().top ?? null;
    onExpandedChange(next);
  };
  useLayoutEffect(() => {
    const panel = toggle.current?.closest<HTMLElement>("[data-sheet-panel]");
    if (
      panel &&
      !window.matchMedia?.("(prefers-reduced-motion: reduce)").matches
    ) {
      const entering = previousTop.current === null;
      const offset = entering
        ? (expanded ? Math.min(panel.getBoundingClientRect().height, 240) : 0)
        : previousTop.current! - panel.getBoundingClientRect().top;
      if (offset && panel.animate)
        animation.current = panel.animate(
          [
            { transform: `translateY(${offset}px)` },
            { transform: "translateY(0)" },
          ],
          { duration: entering ? 420 : 240, easing: "cubic-bezier(.22,1,.36,1)" },
        );
    }
    previousTop.current = null;
  }, [expanded]);
  useEffect(() => {
    if (!expanded) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      changeExpanded(false);
      toggle.current?.focus();
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [expanded, onExpandedChange]);
  return (
    <section
      aria-label={result ? "Описание результата" : "Описание задания"}
      className={styles.descriptionSheet}
    >
      <button
        className={styles.sheetToggle}
        type="button"
        ref={toggle}
        aria-expanded={expanded}
        aria-controls={id}
        onPointerDown={(event) => {
          if (gesture.current || event.button !== 0) return;
          gesture.current = { y: event.clientY, pointer: event.pointerId };
          swiped.current = false;
          event.currentTarget.setPointerCapture?.(event.pointerId);
        }}
        onPointerUp={(event) => {
          if (gesture.current?.pointer !== event.pointerId) return;
          const delta = event.clientY - gesture.current.y;
          gesture.current = null;
          if (Math.abs(delta) > 28) {
            swiped.current = true;
            changeExpanded(delta < 0);
          }
        }}
        onPointerCancel={() => {
          gesture.current = null;
        }}
        onClick={() => {
          if (swiped.current) {
            swiped.current = false;
            return;
          }
          changeExpanded(!expanded);
        }}
      >
        <span className={styles.sheetHandle} aria-hidden="true" />
        <span>
          {expanded
            ? "Скрыть подробности"
            : (collapsedLabel ??
              (result ? "Читать результат" : "Подробнее о задании"))}
        </span>
        <svg
          className={styles.sheetChevron}
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      <div
        className={styles.sheetCopy}
        id={id}
        hidden={!expanded}
        tabIndex={expanded ? 0 : undefined}
      >
        {children}
      </div>
    </section>
  );
}
