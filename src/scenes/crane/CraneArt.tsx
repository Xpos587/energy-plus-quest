import { useLayoutEffect, useRef, useState } from "react";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { ImageSources } from "../../components/ImageSources";
import { useArtworkLoading } from "../../components/useArtworkLoading";
import { imageAsset } from "../../game/imageAssets";
import { choiceLabel } from "../choiceLabel";
import type { SceneArtProps } from "../types";
import { craneArtwork, craneCaptions, type CraneFormat } from "./artwork";
import { craneScene } from "./index";
import styles from "./CraneArt.module.css";

/** Pick the drawing that shows the quay largest, then keep its key strip in frame. */
function camera(stage: { width: number; height: number }, zoomId?: string) {
  const fit = (format: CraneFormat) => {
    const { width, height, focus } = craneArtwork[format];
    const contain = Math.min(stage.width / width, stage.height / height);
    const cover = Math.max(stage.width / width, stage.height / height);
    const scale = Math.max(contain, Math.min(cover, stage.width / focus.width, stage.height / focus.height));
    return { format, scale, area: focus.width * focus.height * scale * scale };
  };
  const { format, scale: overview } = (Object.keys(craneArtwork) as CraneFormat[])
    .map(fit)
    .reduce((best, next) => (next.area > best.area ? next : best));
  const { width, height, zoom } = craneArtwork[format];
  // An open card frames the chosen way, as the city map follows a truck.
  const focus = (zoomId && (zoom as Record<string, typeof craneArtwork[CraneFormat]["focus"] | undefined>)[zoomId]) || craneArtwork[format].focus;
  const scale = Math.max(overview, Math.min(stage.width / focus.width, stage.height / focus.height));
  const place = (stageSize: number, size: number, start: number, span: number) => {
    const offset = stageSize / 2 - (start + span / 2) * scale;
    return size * scale <= stageSize
      ? (stageSize - size * scale) / 2
      : Math.max(stageSize - size * scale, Math.min(0, offset));
  };
  return {
    format,
    width: width * scale,
    height: height * scale,
    left: place(stage.width, width, focus.x, focus.width),
    top: place(stage.height, height, focus.y, focus.height),
  };
}

export function CraneArt({ context, selectedId, onSelect, showResult }: SceneArtProps) {
  const [hovered, setHovered] = useState<string>();
  // Animate camera moves only after the first measured frame, not from size 0.
  const [ready, setReady] = useState(false);
  const stage = useRef<HTMLElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  useLayoutEffect(() => {
    const element = stage.current;
    if (!element) return;
    const measure = () => {
      const { width, height } = element.getBoundingClientRect();
      setSize((old) => (old.width === width && old.height === height ? old : { width, height }));
    };
    measure();
    const frame = requestAnimationFrame(() => setReady(true));
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
    };
  }, []);
  const interactive = !showResult && !!onSelect;
  const view = camera(size, interactive ? selectedId : undefined);
  const art = craneArtwork[view.format];
  const artwork = useArtworkLoading(imageAsset(art.image));
  const options = craneScene.options(context);
  const markId = interactive ? (hovered ?? selectedId) : undefined;
  const mark: { frames: readonly { x: number; y: number; width: number; height: number }[]; path?: string } | undefined =
    markId ? art.marks[markId as keyof typeof art.marks] : undefined;
  const at = (x: number, y: number) => ({ left: `${(x / art.width) * 100}%`, top: `${(y / art.height) * 100}%` });

  return (
    <figure
      ref={stage}
      className={styles.stage}
      data-barge-art={view.format}
      data-selected={selectedId}
      data-zoomed={(interactive && !!selectedId) || undefined}
      data-ready={ready || undefined}
      aria-label={craneScene.title}
    >
      <div className={styles.plane} style={{ width: view.width, height: view.height, left: view.left, top: view.top }}>
        <picture>
          <ImageSources src={artwork.src} />
          <img
            ref={artwork.ref}
            className={styles.image}
            src={artwork.src}
            onLoad={artwork.onLoad}
            onError={artwork.onError}
            width={art.width}
            height={art.height}
            decoding="async"
            draggable={false}
            alt="Причал на Оби: Иван за пультом в офисе ПРУ, подарок на поддоне, высокий кран с пустой кабиной и лестницей до неё, баржа с трубами у причала и дальний кран, где сидит Пётр рядом со своими ящиками."
          />
        </picture>
        {mark && (
          <svg key={markId} className={styles.marks} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true" data-barge-mark={markId}>
            <defs>
              <marker id="crane-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                <path d="M1 1 L9 5 L1 9 Z" fill="#ff5500" stroke="#fff" strokeWidth="1.2" />
              </marker>
            </defs>
            {mark.frames.map((frame) => (
              <rect key={`${frame.x},${frame.y}`} className={styles.frame} x={frame.x} y={frame.y} width={frame.width} height={frame.height} rx={18} />
            ))}
            {mark.path && (
              <>
                <path className={styles.halo} d={mark.path} />
                <path className={styles.route} d={mark.path} markerEnd="url(#crane-arrow)" />
              </>
            )}
          </svg>
        )}
        <span className={styles.chip} data-barge-chip="barge" style={at(art.chips.barge.x, art.chips.barge.y)}>
          Баржа готова к отходу
        </span>
        <span className={styles.chip} data-barge-chip="gift" data-tone="gift" style={at(art.chips.gift.x, art.chips.gift.y)}>
          Подарок
        </span>
        {options.map((option, index) => {
          const point = art.hotspots[option.id as keyof typeof art.hotspots];
          const caption = craneCaptions[option.id as keyof typeof craneCaptions];
          return (
            <button
              key={option.id}
              type="button"
              className={styles.hotspot}
              data-hotspot={option.id}
              data-side={point.side}
              style={at(point.x, point.y)}
              aria-label={`Вариант ${index + 1}. ${choiceLabel(option.label)}`}
              aria-pressed={selectedId === option.id}
              disabled={!interactive}
              onClick={() => onSelect?.(option.id)}
              onPointerEnter={() => setHovered(option.id)}
              onPointerLeave={() => setHovered(undefined)}
              onFocus={() => setHovered(option.id)}
              onBlur={() => setHovered(undefined)}
            >
              <span className={styles.badge} aria-hidden="true">{index + 1}</span>
              <span className={styles.caption} aria-hidden="true">{caption}</span>
            </button>
          );
        })}
      </div>
      <ArtworkLoading viewport status={artwork.status} onRetry={artwork.retry} />
    </figure>
  );
}
