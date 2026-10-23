import optimizedImages from "virtual:optimized-images";
import responsiveImages from "virtual:responsive-images";
import thumbnailImages from "virtual:thumbnail-images";

export function thumbnailAsset(src: string): string {
  const base = import.meta.env.BASE_URL;
  const key = src.startsWith(base) ? src.slice(base.length) : src;
  return thumbnailImages[key] ? base + thumbnailImages[key] : src;
}

export function imageAsset(path: string): string {
  return `${import.meta.env.BASE_URL}${optimizedImages[path] ?? path}`;
}

export function imageVariants(src: string) {
  const [base, query] = src.split("?");
  const original = Object.keys(responsiveImages).find(
    (path) => imageAsset(path) === base,
  );
  const variants = original && responsiveImages[original];
  if (!variants) return undefined;
  const url = (path: string) =>
    `${import.meta.env.BASE_URL}${path}${query ? `?${query}` : ""}`;
  const srcset = (value: string) =>
    value
      .split(",")
      .map((part) => {
        const [path, width] = part.trim().split(/\s+/);
        return `${url(path)} ${width}`;
      })
      .join(", ");
  return {
    ...variants,
    avif: url(variants.avif),
    desktopAvif: variants.desktopAvif ? url(variants.desktopAvif) : undefined,
    desktopWebp: variants.desktopWebp ? url(variants.desktopWebp) : undefined,
    avifSrcSet: srcset(variants.avifSrcSet),
    webpSrcSet: srcset(variants.webpSrcSet),
  };
}

/** SVG cannot use picture; offer full native detail with the WebP as fallback. */
export function detailImageAsset(src: string): string {
  return imageVariants(src)?.desktopAvif ?? src;
}

type Warmup = {
  src: string;
  sizes: string;
  webpOnly: boolean;
  picture?: HTMLPictureElement;
  cancelled: boolean;
};
const queue: Warmup[] = [];
const warmed = new Set<string>();
let running: Warmup | undefined;
let observing = false;

function pump() {
  if (
    running ||
    [...document.images].some(
      (img) =>
        !img.closest("[data-image-warmup]") &&
        img.getAttribute("src") &&
        !img.complete,
    )
  )
    return;
  const next = queue.shift();
  if (!next) return;
  if (next.cancelled) {
    pump();
    return;
  }
  running = next;
  const picture = document.createElement("picture");
  picture.hidden = true;
  picture.dataset.imageWarmup = "";
  const variants = imageVariants(next.src);
  if (variants && !next.webpOnly) {
    if (variants.desktopAvif || variants.desktopWebp) {
      const detail = document.createElement("source");
      detail.type = variants.desktopAvif ? "image/avif" : "image/webp";
      detail.media = "(min-width: 1100px)";
      detail.srcset = (variants.desktopAvif ?? variants.desktopWebp)!;
      picture.append(detail);
    }
    const source = document.createElement("source");
    source.type = "image/avif";
    source.srcset = variants.avifSrcSet;
    source.sizes = next.sizes;
    picture.append(source);
    const fallback = document.createElement("source");
    fallback.type = "image/webp";
    fallback.srcset = variants.webpSrcSet;
    fallback.sizes = next.sizes;
    picture.append(fallback);
  }
  const image = new Image();
  image.setAttribute("fetchpriority", "low");
  image.decoding = "async";
  const done = () => {
    if (running !== next) return;
    if (image.naturalWidth) warmed.add(next.src);
    picture.remove();
    running = undefined;
    pump();
  };
  image.onload = done;
  image.onerror = done;
  next.picture = picture;
  picture.append(image);
  document.body.append(picture);
  image.src = next.src;
}

/** Native picture selection works even where prefetch/connection APIs are absent. */
export function prefetchImage(
  src: string,
  sizes = "(min-aspect-ratio: 2/1) 100vw, 200vh",
  webpOnly = false,
): (() => void) | undefined {
  const connection = (
    navigator as Navigator & {
      connection?: { saveData?: boolean; effectiveType?: string };
    }
  ).connection;
  if (
    connection?.saveData ||
    /^(slow-)?2g$/.test(connection?.effectiveType ?? "") ||
    warmed.has(src) ||
    running?.src === src ||
    queue.some((item) => item.src === src && !item.cancelled)
  )
    return;
  if (!observing) {
    document.addEventListener("load", pump, true);
    document.addEventListener("error", pump, true);
    observing = true;
  }
  const item: Warmup = { src, sizes, webpOnly, cancelled: false };
  queue.push(item);
  pump();
  return () => {
    item.cancelled = true;
    if (running === item) {
      item.picture?.remove();
      running = undefined;
    }
    pump();
  };
}

export function resetImageQueue() {
  queue.length = 0;
  running?.picture?.remove();
  running = undefined;
  warmed.clear();
  document.removeEventListener("load", pump, true);
  document.removeEventListener("error", pump, true);
  observing = false;
}
