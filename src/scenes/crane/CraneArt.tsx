import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { ImageSources } from "../../components/ImageSources";
import { useArtworkLoading } from "../../components/useArtworkLoading";
import { imageAsset } from "../../game/imageAssets";
import { choiceLabel } from "../choiceLabel";
import type { SceneArtProps } from "../types";
import { craneArtwork, craneCaptions, craneWorld, type CraneFormat, type Rect } from "./artwork";
import { craneBeat, craneDeckDelta, craneDuration, craneRest, craneSail } from "./consequence";
import { craneScene } from "./index";
import styles from "./CraneArt.module.css";

/** Pick the drawing that shows the quay largest, then keep its key strip in frame. */
function camera(stage: { width: number; height: number }, zoomId?: string) {
  const fit = (format: CraneFormat) => {
    const { width, height, focus } = craneArtwork[format];
    const contain = Math.min(stage.width / width, stage.height / height);
    const cover = Math.max(stage.width / width, stage.height / height);
    const scale = Math.max(contain, Math.min(cover, stage.width / focus.width, stage.height / focus.height));
    // The drawing composed for the closest screen shape needs the least crop.
    const mismatch = Math.abs(Math.log(width / height / (stage.width / Math.max(1, stage.height))));
    return { format, scale, mismatch };
  };
  const { format, scale: overview } = (Object.keys(craneArtwork) as CraneFormat[])
    .map(fit)
    .reduce((best, next) => (next.mismatch < best.mismatch ? next : best));
  const { width, height, zoom } = craneArtwork[format];
  // An open card frames the chosen way, as the city map follows a truck.
  const focus: Rect = (zoomId && zoom[zoomId]) || craneArtwork[format].focus;
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

/** Runs the quay consequence of a confirmed way, then reports back; reduced motion skips it. */
function useConsequence(playing: string | undefined, onPlayed: (() => void) | undefined) {
  const [ms, setMs] = useState(0);
  const done = useRef(onPlayed);
  done.current = onPlayed;
  useEffect(() => {
    setMs(0);
    if (!playing) return;
    const still = typeof window.matchMedia !== "function" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const total = craneDuration(playing);
    if (still || !total) {
      done.current?.();
      return;
    }
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const elapsed = now - start;
      setMs(elapsed);
      if (elapsed >= total + 250) done.current?.();
      else frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing]);
  return playing ? craneBeat(playing, ms) : craneRest;
}

const sub = (a: readonly number[], b: readonly number[]) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]] as const;
const scaleBy = (a: readonly number[], k: number) => [a[0] * k, a[1] * k, a[2] * k] as const;

export function CraneArt({ context, selectedId, onSelect, showResult, playing, onPlayed }: SceneArtProps) {
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
  const beat = useConsequence(playing, onPlayed);
  const interactive = !showResult && !!onSelect && !playing;
  const view = camera(size, playing ? "play" : interactive ? selectedId : undefined);
  const art = craneArtwork[view.format];
  const plate = useArtworkLoading(imageAsset(art.plate));
  const options = craneScene.options(context);
  const litId = playing ?? (interactive ? (hovered ?? selectedId) : undefined);
  const lit = new Set<string>(litId ? art.actors[litId] ?? [] : []);
  const pct = (x: number, y: number) => ({ left: `${(x / art.width) * 100}%`, top: `${(y / art.height) * 100}%` });
  const box = (r: { x: number; y: number; w: number; h: number }) => ({
    ...pct(r.x, r.y), width: `${(r.w / art.width) * 100}%`, height: `${(r.h / art.height) * 100}%`,
  });
  // A world move is a pure screen shift for the orthographic quay camera.
  const move = (r: { w: number; h: number }, delta: readonly number[]): CSSProperties => {
    const [[ax, ay, az], [bx, by, bz]] = art.affine;
    const dx = ax * delta[0] + ay * delta[1] + az * delta[2];
    const dy = bx * delta[0] + by * delta[1] + bz * delta[2];
    return { transform: `translate(${(dx / r.w) * 100}%, ${(dy / r.h) * 100}%)` };
  };
  const sail = scaleBy(craneSail, beat.sail);
  const hookAt = beat.hook ? sub(beat.hook, [craneWorld.gift[0], craneWorld.gift[1], craneWorld.hookAttach]) : undefined;
  const [tipX, tipY] = art.project(craneWorld.tips[beat.frame]);
  const [hookX, hookY] = beat.hook ? art.project(beat.hook) : [0, 0];
  const s = art.sprites;
  const sprite = (name: keyof typeof s, extra?: { style?: CSSProperties; lit?: boolean; className?: string; data?: string }) => (
    <img
      className={[styles.layer, extra?.className].filter(Boolean).join(" ")}
      src={imageAsset(s[name].src)}
      alt=""
      draggable={false}
      decoding="async"
      data-layer={name}
      data-lit={extra?.lit || undefined}
      data-busy={(playing && beat.busy === name) || undefined}
      style={{ ...box(s[name]), ...extra?.style }}
    />
  );

  return (
    <figure
      ref={stage}
      className={styles.stage}
      data-barge-art={view.format}
      data-selected={playing ?? selectedId}
      data-playing={playing}
      data-zoomed={(interactive && !!selectedId) || undefined}
      data-ready={ready || undefined}
      aria-label={craneScene.title}
      onClick={playing ? () => onPlayed?.() : undefined}
    >
      <div className={styles.plane} style={{ width: view.width, height: view.height, left: view.left, top: view.top }}>
        <picture>
          <ImageSources src={plate.src} />
          <img
            ref={plate.ref}
            className={styles.image}
            src={plate.src}
            onLoad={plate.onLoad}
            onError={plate.onError}
            width={art.width}
            height={art.height}
            decoding="async"
            draggable={false}
            alt="Причал на Оби: Иван за пультом в офисе ПРУ, подарок на поддоне, высокий портальный кран с пустой кабиной и лестницей до неё, баржа с трубами у причала и дальний кран, где сидит Пётр рядом со своими ящиками."
          />
        </picture>
        {!beat.lifted && !beat.onDeck && sprite("gift")}
        {sprite("ivan", { lit: lit.has("ivan") })}
        {sprite("ladder", { lit: lit.has("ladder") })}
        {sprite("far", { lit: lit.has("far") })}
        <div className={styles.sail} style={move({ w: art.width, h: art.height }, sail)} data-sailing={beat.sail > 0 || undefined}>
          <div className={styles.bob}>
            {sprite("barge")}
            {beat.onDeck && sprite("gift", { style: move(s.gift, craneDeckDelta) })}
          </div>
          {sprite("smoke", { className: styles.smoke })}
        </div>
        <div className={styles.layer} style={box(art.top)} data-layer="top" data-lit={lit.has("near") || undefined}>
          <img
            className={styles.sheet}
            src={imageAsset(art.top.src)}
            alt=""
            draggable={false}
            decoding="async"
            style={{
              width: `${art.top.cols * 100}%`,
              height: `${art.top.rows * 100}%`,
              transform: `translate(${(-(beat.frame % art.top.cols) / art.top.cols) * 100}%, ${(-Math.floor(beat.frame / art.top.cols) / art.top.rows) * 100}%)`,
            }}
          />
        </div>
        {beat.hook && (
          <svg className={styles.cable} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            <line x1={tipX} y1={tipY} x2={hookX} y2={hookY} />
          </svg>
        )}
        {hookAt && !beat.lifted && sprite("hook", { style: move(s.hook, hookAt) })}
        {hookAt && beat.lifted && sprite("box", { style: move(s.box, hookAt) })}
        {!playing && (
          <>
            <span className={styles.chip} data-barge-chip="barge" style={pct(art.chips.barge.x, art.chips.barge.y)}>
              Баржа готова к отходу
            </span>
            <span className={styles.chip} data-barge-chip="gift" data-tone="gift" style={pct(art.chips.gift.x, art.chips.gift.y)}>
              Подарок
            </span>
          </>
        )}
        {options.map((option, index) => {
          const point = art.hotspots[option.id];
          const caption = craneCaptions[option.id as keyof typeof craneCaptions];
          return (
            <button
              key={option.id}
              type="button"
              className={styles.hotspot}
              data-hotspot={option.id}
              data-side={point.side}
              style={pct(point.x, point.y)}
              aria-label={`Вариант ${index + 1}. ${choiceLabel(option.label)}`}
              aria-pressed={(playing ?? selectedId) === option.id}
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
      {playing && <span className={styles.skip} aria-hidden="true">Нажмите, чтобы пропустить</span>}
      <ArtworkLoading viewport status={plate.status} onRetry={plate.retry} />
    </figure>
  );
}
