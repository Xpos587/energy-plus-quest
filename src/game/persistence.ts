import { useEffect, useState, type SetStateAction } from "react";
import { findCarrier } from "./content";
import { initialGameState } from "./gameReducer";
import type { GameState } from "./types";

export const SAVE_KEY = "energy-quest-save-v1";
export function readStored(key: string): unknown {
  try {
    return JSON.parse(localStorage.getItem(key) ?? "null");
  } catch {
    return null;
  }
}
export function writeStored(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* Storage can be unavailable or full. */
  }
}
export function newSaveScope() {
  return `quest-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
export function restoreGame(
  value: unknown,
): { state: GameState; scope: string } | undefined {
  if (!value || typeof value !== "object") return;
  const saved = value as {
    version?: unknown;
    state?: GameState;
    scope?: unknown;
  };
  const state = saved.state;
  if (
    saved.version !== 1 ||
    typeof saved.scope !== "string" ||
    !/^quest-[a-zA-Z0-9-]+$/.test(saved.scope) ||
    !state
  )
    return;
  const steps = ["profile", "recipient", "parcel", "carrier", "outcome"];
  const index = steps.indexOf(state.step);
  if (
    index < 0 ||
    (index > 0 && !["student", "professional"].includes(state.profile ?? "")) ||
    (index > 1 &&
      !["alva", "khor", "arseniy"].includes(state.recipient ?? "")) ||
    (index > 2 && !["camera", "socks", "boat"].includes(state.parcel ?? "")) ||
    (index > 3 && !findCarrier(state.carrier!))
  )
    return;
  return {
    scope: saved.scope,
    state: {
      ...initialGameState,
      step: state.step,
      ...(index > 0 ? { profile: state.profile } : {}),
      ...(index > 1 ? { recipient: state.recipient } : {}),
      ...(index > 2 ? { parcel: state.parcel } : {}),
      ...(index > 3
        ? { carrier: state.carrier, scores: findCarrier(state.carrier!)!.score }
        : {}),
    },
  };
}

export function useStoredState<T>(
  key: string | undefined,
  initial: T,
  valid: (value: unknown) => value is T,
) {
  const load = () => {
    const value = key ? readStored(key) : null;
    return valid(value) ? value : initial;
  };
  const [entry, setEntry] = useState(() => ({ key, value: load() }));
  let value = entry.value;
  if (entry.key !== key) {
    value = load();
    setEntry({ key, value });
  }
  const setValue = (update: SetStateAction<T>) => {
    setEntry((current) => {
      const next =
        typeof update === "function"
          ? (update as (value: T) => T)(current.value)
          : update;
      return { key, value: next };
    });
  };
  useEffect(() => {
    if (entry.key && entry.key === key) writeStored(entry.key, entry.value);
  }, [entry, key]);
  return [value, setValue] as const;
}

/** Remove only this delivery's own saves, never unrelated browser storage. */
export function clearSaveScope(scope: string) {
  try {
    const keys = Array.from({ length: localStorage.length }, (_, index) =>
      localStorage.key(index),
    );
    for (const key of keys) {
      if (!key) continue;
      let owned = key.startsWith(`${scope}:`);
      if (key.startsWith("quest-reading-v1:")) {
        try {
          const identity: unknown = JSON.parse(
            key.slice("quest-reading-v1:".length),
          );
          owned = Array.isArray(identity) && identity[0] === scope;
        } catch {
          /* Not a recognized reading key. */
        }
      }
      if (owned) localStorage.removeItem(key);
    }
  } catch {
    /* Clearing optional saves must not prevent a new game. */
  }
}
