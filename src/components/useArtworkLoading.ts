import { useLayoutEffect, useRef, useState } from "react";

export type ArtworkStatus = "loading" | "ready" | "error";

export function useArtworkLoading<
  T extends HTMLImageElement | SVGImageElement = HTMLImageElement,
>(source: string, fallbackSource?: string) {
  const ref = useRef<T>(null);
  const [failedDetail, setFailedDetail] = useState<string>();
  const activeSource = failedDetail === source && fallbackSource ? fallbackSource : source;
  const [attempt, setAttempt] = useState({ source, count: 0 });
  const count = attempt.source === activeSource ? attempt.count : 0;
  const src = count
    ? `${activeSource}${activeSource.includes("?") ? "&" : "?"}artwork-retry=${count}`
    : activeSource;
  const [readiness, setReadiness] = useState<{
    src: string;
    status: ArtworkStatus;
  }>({ src, status: "loading" });
  const status = readiness.src === src ? readiness.status : "loading";
  const onLoad = () => setReadiness({ src, status: "ready" });
  const onError = () => {
    if (fallbackSource && activeSource !== fallbackSource) setFailedDetail(source);
    else setReadiness({ src, status: "error" });
  };

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) return;
    if (element instanceof HTMLImageElement) {
      if (element.complete && element.naturalWidth > 0)
        setReadiness({ src, status: "ready" });
      return;
    }
    // SVG images have no complete/naturalWidth; the cache probe also catches an
    // SVG load event that fired before the component's effect was attached.
    const probe = new Image();
    probe.onload = () => setReadiness({ src, status: "ready" });
    probe.onerror = onError;
    probe.src = src;
    if (probe.complete && probe.naturalWidth > 0)
      setReadiness({ src, status: "ready" });
    return () => {
      probe.onload = null;
      probe.onerror = null;
    };
  }, [src]);

  const retry = () => {
    if (status !== "error") return;
    setAttempt({ source: activeSource, count: count + 1 });
  };
  return { ref, src, status, onLoad, onError, retry };
}
