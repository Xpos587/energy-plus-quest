/** Optional enhancement: insecure/older embedded browsers continue through normal networking. */
export function registerGameCache(): void {
  if (
    !import.meta.env.PROD ||
    !window.isSecureContext ||
    !("serviceWorker" in navigator)
  )
    return;
  const register = () => {
    try {
      const base = new URL(import.meta.env.BASE_URL, document.baseURI);
      void navigator.serviceWorker
        .register(new URL("quest-cache.js", base).href, {
          scope: base.href,
          updateViaCache: "none",
        })
        .then(async () => {
          const registration = await navigator.serviceWorker.ready;
          const seen = new Set<string>();
          const warm = (urls: string[]) => {
            const fresh = urls.filter((url) => url && !seen.has(url));
            for (const url of fresh) seen.add(url);
            if (fresh.length)
              registration.active?.postMessage({
                type: "QUEST_CACHE_VISITED",
                urls: fresh,
              });
          };
          const urls = new Set(
            performance.getEntriesByType("resource").map((entry) => entry.name),
          );
          for (const image of document.images)
            if (image.complete && image.naturalWidth > 0)
              urls.add(image.currentSrc || image.src);
          warm([...urls]);
          // The first page stays uncontrolled. Keep retaining its newly loaded scenes.
          document.addEventListener(
            "load",
            (event) => {
              const image = event.target;
              if (image instanceof HTMLImageElement && image.naturalWidth > 0)
                warm([image.currentSrc || image.src]);
            },
            true,
          );
          if ("PerformanceObserver" in window) {
            try {
              const observer = new PerformanceObserver((entries) =>
                warm(entries.getEntries().map((entry) => entry.name)),
              );
              observer.observe({ entryTypes: ["resource"] });
            } catch {
              // Image load events retain the fallback in embedded browsers.
            }
          }
        })
        .catch(() => {});
    } catch {
      // Some embedded/private browsers expose the API but block its use.
    }
  };
  // The current illustration gets the network first; installation has no UI prompt.
  if (document.readyState === "complete") register();
  else window.addEventListener("load", register, { once: true });
}
