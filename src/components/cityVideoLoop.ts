// A paused decoder already holds frame zero. Switching only after its first
// presented frame avoids showing a seek, a poster, or an uninitialized surface.
export function startCityVideoLoop(
  first: HTMLVideoElement,
  second: HTMLVideoElement,
  paint: (time: number) => void,
  fail: () => void,
  handoff: () => void = () => {},
) {
  const videos = [first, second];
  let active = first;
  let pending: HTMLVideoElement | undefined;
  let priming: HTMLVideoElement | undefined;
  const warmed = new Set<HTMLVideoElement>();
  let disposed = false;
  const unavailable = new Set<HTMLVideoElement>();
  const callbacks = new Map<HTMLVideoElement, number>();
  let handoffTimer: ReturnType<typeof setTimeout> | undefined;
  let animation = 0;
  const show = (video: HTMLVideoElement) => {
    for (const element of videos) {
      element.toggleAttribute("data-city-video", element === video);
      element.style.opacity = element === video ? "1" : "0";
      element.setAttribute("aria-hidden", String(element !== video));
    }
  };
  const play = (video: HTMLVideoElement) => {
    void video.play().catch((error: unknown) => {
      if (disposed || document.hidden || (error instanceof DOMException && error.name === "AbortError")) return;
      if (video === active) fail();
      else {
        unavailable.add(video);
        if (pending === video) { pending = undefined; play(active); }
        if (priming === video) priming = undefined;
      }
    });
  };
  const frame = (video: HTMLVideoElement, time: number) => {
    if (disposed || document.hidden) return;
    if (video === priming) {
      priming = undefined;
      warmed.add(video);
      video.pause();
      if (time > 0) video.currentTime = 0;
      return;
    }
    if (video === pending && video.readyState >= 2 && !video.seeking) {
      const previous = active;
      active = video;
      pending = undefined;
      clearTimeout(handoffTimer);
      show(active);
      handoff();
      previous.pause();
      const previousCallback = callbacks.get(previous);
      if (previousCallback) previous.cancelVideoFrameCallback(previousCallback);
      callbacks.delete(previous);
      previous.currentTime = 0;
      warmed.delete(previous);
    }
    if (video !== active) return;
    paint(time);
    const standby = videos.find(element => element !== active)!;
    if (!pending && !priming && !warmed.has(standby) && time >= video.duration - 3 && time < video.duration - 1 / 24 - .001 &&
      standby.readyState >= 2 && !standby.seeking && !unavailable.has(standby)) {
      priming = standby;
      watch(standby);
      play(standby);
    }
    // The encodes run at 24 fps. Keep the final frame until the replacement
    // decoder presents frame zero; native looping remains the fallback.
    if (!pending && !priming && warmed.has(standby) && Number.isFinite(video.duration) && time >= video.duration - 1 / 24 - .001 &&
      standby.readyState >= 2 && !standby.seeking && !unavailable.has(standby)) {
      pending = standby;
      priming = undefined;
      const existing = callbacks.get(standby);
      if (existing) standby.cancelVideoFrameCallback(existing);
      watch(standby);
      video.pause();
      play(standby);
      clearTimeout(handoffTimer);
      handoffTimer = setTimeout(() => {
        if (disposed || pending !== standby) return;
        pending = undefined;
        unavailable.add(standby);
        standby.pause();
        if (!document.hidden) play(active);
      }, 500);
    }
  };
  const errors = videos.map(video => () => {
    if (video === active) fail();
    else {
      unavailable.add(video);
      if (priming === video) priming = undefined;
      if (pending === video) { pending = undefined; play(active); }
    }
  });
  const sync = () => {
    if (document.hidden) {
      videos.forEach(video => video.pause());
      if (pending) { pending.currentTime = 0; pending = undefined; }
      if (priming) { priming.currentTime = 0; priming = undefined; }
    } else play(active);
  };
  const watch = (video: HTMLVideoElement) => {
    if (typeof video.requestVideoFrameCallback !== "function") return;
    const callback: VideoFrameRequestCallback = (_, metadata) => {
      frame(video, metadata.mediaTime);
      if (!disposed && (video === active || video === pending || video === priming)) callbacks.set(video, video.requestVideoFrameCallback(callback));
    };
    callbacks.set(video, video.requestVideoFrameCallback(callback));
  };
  show(active);
  if (typeof first.requestVideoFrameCallback === "function" && typeof second.requestVideoFrameCallback === "function") {
    watch(first);
  } else {
    // Older browsers retain one native loop and track that decoder only.
    unavailable.add(second);
    const callback = () => {
      if (!document.hidden) paint(active.currentTime);
      if (!disposed) animation = requestAnimationFrame(callback);
    };
    animation = requestAnimationFrame(callback);
  }
  videos.forEach((video, index) => video.addEventListener("error", errors[index]));
  document.addEventListener("visibilitychange", sync);
  sync();
  return () => {
    disposed = true;
    clearTimeout(handoffTimer);
    videos.forEach((video, index) => {
      video.pause();
      const callback = callbacks.get(video);
      if (callback) video.cancelVideoFrameCallback(callback);
      video.removeEventListener("error", errors[index]);
    });
    cancelAnimationFrame(animation);
    document.removeEventListener("visibilitychange", sync);
  };
}
