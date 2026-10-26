import { type ReactNode, useId, useLayoutEffect, useRef } from "react";
import { ArrowLeft, Check } from "lucide-react";
import { PagedDescription } from "./PagedDescription";
import { useInspectionPlacement } from "./useInspectionPlacement";
import styles from "./SceneInteraction.module.css";

/** A preview only: the caller commits the answer in onConfirm. */
export function ChoiceInspection({
  selectionKey,
  title,
  children,
  paragraphs,
  media = false,
  continuous = false,
  onConfirm,
  onCancel,
  returnFocus,
  confirming = false,
  cancelLabel = "К вариантам",
}: {
  selectionKey: string;
  title: string;
  children?: ReactNode;
  paragraphs?: string[];
  media?: boolean;
  continuous?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  returnFocus?: HTMLElement | null;
  confirming?: boolean;
  /** Says where Cancel leads in the scene's own words. */
  cancelLabel?: string;
}) {
  const id = useId();
  const heading = useRef<HTMLHeadingElement>(null);
  useInspectionPlacement(heading, selectionKey, returnFocus);
  // biome-ignore lint/correctness/useExhaustiveDependencies: each inspected option must receive focus and restore its own trigger.
  useLayoutEffect(() => {
    const trigger = returnFocus ?? document.activeElement;
    const dialog = heading.current?.closest("[data-choice-inspection]");
    heading.current?.focus({ preventScroll: true });
    return () => {
      const restore =
        dialog?.contains(document.activeElement) ||
        document.activeElement === document.body;
      // Wait until the parent restores the mobile choice row before focusing it.
      queueMicrotask(() => {
        if (
          restore &&
          !heading.current?.isConnected &&
          trigger instanceof HTMLElement &&
          trigger.isConnected
        ) {
          trigger.focus({ preventScroll: true });
        }
      });
    };
  }, [selectionKey, returnFocus]);

  return (
    <section
      role="dialog"
      aria-labelledby={id}
      className={styles.inspection}
      data-choice-inspection={selectionKey}
      data-choice-media={media || undefined}
      data-continuous-description={continuous || undefined}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          event.preventDefault();
          event.stopPropagation();
          onCancel();
        }
      }}
    >
      <div className={styles.inspectionHeading}>
        <h3 id={id} ref={heading} tabIndex={-1}>
          {title}
        </h3>
      </div>
      {(children != null || (paragraphs?.length ?? 0) > 0) && (
        <section
          className={styles.inspectionCopy}
          aria-label="Описание варианта"
        >
          {paragraphs && continuous ? (
            paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)
          ) : paragraphs ? (
            <PagedDescription key={selectionKey} paragraphs={paragraphs} />
          ) : (
            children
          )}
        </section>
      )}
      <div className={styles.actions}>
        <button
          type="button"
          className={styles.secondary}
          data-choice-cancel
          onClick={onCancel}
        >
          <ArrowLeft size={18} aria-hidden="true" />
          {cancelLabel}
        </button>
        <button
          type="button"
          className={styles.primary}
          data-choice-confirm
          disabled={confirming}
          aria-busy={confirming || undefined}
          onClick={onConfirm}
        >
          <Check size={18} aria-hidden="true" />
          Подтвердить выбор
        </button>
      </div>
    </section>
  );
}
