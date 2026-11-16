/** Keep focus through artwork reloads, but never take it back after user navigation. */
export function restoreArtworkFocus(target: HTMLElement) {
  const stop = () => {
    observer.disconnect();
    document.removeEventListener("focusin", moved);
    document.removeEventListener("pointerdown", moved);
  };
  const moved = (event: Event) => {
    if (!target.contains(event.target as Node) &&
        (event.type === "pointerdown" || event.target !== document.body)) stop();
  };
  const restore = () => {
    if (!target.isConnected ||
        (document.activeElement !== document.body && document.activeElement !== target)) {
      stop();
      return;
    }
    if (document.activeElement === document.body) target.focus({ preventScroll: true });
  };
  const observer = new MutationObserver(restore);
  for (let element: HTMLElement | null = target; element; element = element.parentElement)
    observer.observe(element, { attributes: true, childList: true });
  document.addEventListener("focusin", moved);
  document.addEventListener("pointerdown", moved);
  target.focus({ preventScroll: true });
  return stop;
}
