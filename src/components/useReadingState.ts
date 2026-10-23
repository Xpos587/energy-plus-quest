import { type SetStateAction, useMemo, useState } from "react";
import { useOptionalSaveScope } from "../game/GameContext";

export function clearReadingState(scope: string | undefined, keys?: readonly string[]) {
  if (!scope) return;
  try {
    const prefix = `quest-reading-v1:[${JSON.stringify(scope)},`;
    const selected = keys?.map(key => `quest-reading-v1:${JSON.stringify([scope, key])}`);
    for (const key of Object.keys(localStorage)) {
      if (selected ? selected.includes(key) : key.startsWith(prefix)) localStorage.removeItem(key);
    }
  } catch {
    /* A fresh run still works when storage is unavailable. */
  }
}

/** Save only reading controls, scoped to the current delivery and exact text. */
export function useReadingState<T extends number | boolean>(
  key: string,
  initial: T,
) {
  const scope = useOptionalSaveScope();
  const storageKey = scope
    ? `quest-reading-v1:${JSON.stringify([scope, key])}`
    : undefined;
  const restored = useMemo(() => {
    if (storageKey) {
      try {
        const saved: unknown = JSON.parse(
          localStorage.getItem(storageKey) ?? "null",
        );
        if (
          typeof saved === typeof initial &&
          (typeof saved !== "number" ||
            (Number.isSafeInteger(saved) && saved >= 0))
        )
          return saved as T;
      } catch {
        /* Storage may be disabled or contain an old value. */
      }
    }
    return initial;
  }, [storageKey, initial]);
  const [state, setState] = useState({ storageKey, value: restored });
  const value = state.storageKey === storageKey ? state.value : restored;
  const setValue = (next: SetStateAction<T>) => {
    const updated = typeof next === "function" ? next(value) : next;
    if (storageKey) {
      try {
        localStorage.setItem(storageKey, JSON.stringify(updated));
      } catch {
        /* Keep playing without storage. */
      }
    }
    setState({ storageKey, value: updated });
  };
  return [value, setValue] as const;
}
