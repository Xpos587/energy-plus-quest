import { useLayoutEffect, useSyncExternalStore } from "react";

const legacyPauseKey = "energy-quest-motion-paused";
const preference = () => window.matchMedia?.("(prefers-reduced-motion: reduce)");
const getReduced = () => preference()?.matches ?? false;
const subscribeReduced = (notify: () => void) => {
  const media = preference();
  media?.addEventListener?.("change", notify);
  return () => media?.removeEventListener?.("change", notify);
};

export function useAmbientMotion() {
  const reduced = useSyncExternalStore(subscribeReduced, getReduced, () => false);
  useLayoutEffect(() => {
    try {
      localStorage.removeItem(legacyPauseKey);
    } catch {
      // Storage can be unavailable.
    }
    document.documentElement.style.setProperty("--ambient-motion", reduced ? "paused" : "running");
  }, [reduced]);
  return { reduced, stopped: reduced };
}
