import { type RefObject, useEffect, useState } from "react";
import { RotateCcw } from "lucide-react";
import { createPortal } from "react-dom";
import styles from "./ArtworkLoading.module.css";
import type { ArtworkStatus } from "./useArtworkLoading";

export function ArtworkLoading({
  status,
  onRetry,
  inline = false,
  container,
}: {
  status: ArtworkStatus;
  onRetry: () => void;
  inline?: boolean;
  container?: RefObject<HTMLElement | null>;
}) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (status === "ready") return null;
  const feedback = (
    <div
      className={`${styles.status} ${inline ? styles.inline : ""}`}
      role="status"
      aria-live="polite"
      data-artwork-status={status}
    >
      <span>
        {status === "error"
          ? "Иллюстрация не загрузилась"
          : "Загружаем иллюстрацию…"}
      </span>
      {status === "error" && (
        <button type="button" onClick={onRetry}>
          <RotateCcw size={18} aria-hidden="true" />
          Повторить
        </button>
      )}
    </div>
  );
  return mounted && container?.current ? createPortal(feedback, container.current) : feedback;
}
