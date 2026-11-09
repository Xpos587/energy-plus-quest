import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { ImageSources } from "../../components/ImageSources";
import { useArtworkLoading } from "../../components/useArtworkLoading";
import { imageAsset } from "../../game/imageAssets";
import { choiceLabel } from "../choiceLabel";
import type { SceneArtProps } from "../types";
import { craneArtwork, craneCaptions, craneWorld, type CraneFormat, type Rect } from "./artwork";
import { castSrc, craneCast } from "./cast";
import { craneBeat, craneDeckDelta, craneDuration, craneRest, craneSail } from "./consequence";
import { craneScene } from "./index";
import styles from "./CraneArt.module.css";

/** Pick the drawing that fills the stage and crops least of the quay story, then keep that strip in frame. */
function camera(stage: { width: number; height: number }, zoomId?: string) {
  const fit = (format: CraneFormat) => {
    const { width, height, focus, focusPad } = craneArtwork[format];
    // Always cover: an empty band of sky colour reads as a broken picture.
    const scale = Math.max(stage.width / width, stage.height / height);
    // How much of the story itself (focus minus its air) falls outside the screen.
    const lost = Math.max(0, (focus.width - 2 * focusPad) * scale - stage.width) / stage.width
      + Math.max(0, (focus.height - 2 * focusPad) * scale - stage.height) / stage.height;
    // Among drawings that keep the story, the one composed for the closest screen shape.
    const mismatch = Math.abs(Math.log(width / height / (stage.width / Math.max(1, stage.height))));
    return { format, scale, lost, mismatch };
  };
  const { format, scale: overview } = (Object.keys(craneArtwork) as CraneFormat[])
    .map(fit)
    .reduce((best, next) => (next.lost < best.lost - 1e-3 || (Math.abs(next.lost - best.lost) <= 1e-3 && next.mismatch < best.mismatch) ? next : best));
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

export function CraneArt({ context, selectedId, onSelect, showResult, playing, onPlayed, focusedId, onFocusChange }: SceneArtProps) {
  // The rail cards and the quay pins light the same actors.
  const [ownHover, setOwnHover] = useState<string>();
  const hovered = ownHover ?? focusedId;
  const setHovered = (id: string | undefined) => { setOwnHover(id); onFocusChange?.(id); };
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
  // Pointing at an actor lights its outline (scene 5 pattern, nothing is dimmed); untried actors breathe.
  const pointed = interactive ? (hovered ?? selectedId) : undefined;
  const [seen, setSeen] = useState<string[]>([]);
  useEffect(() => { if (selectedId) setSeen((s) => (s.includes(selectedId) ? s : [...s, selectedId])); }, [selectedId]);
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
  const cast = craneCast[view.format];
  const anchor = art.anchors;
  // Overlay marks are drawn in drawing px; keep them readable when a big drawing is shrunk to a phone.
  const k = view.width ? Math.max(1, (0.8 * art.width) / view.width) : 1;
  const emoteAt = { office: [anchor.ivan[0] + 46, anchor.ivan[1] - 52], near: [anchor.nearCabin[0] + 38, anchor.nearCabin[1] - 46], far: [anchor.farCabin[0] - 40, anchor.farCabin[1] - 30] } as const;
  const walker = cast && beat.walker && (() => {
    const [x, y] = art.project(beat.walker.at);
    // ponytail: cartoon figures drawn ~1.8x true scale so they read at quay zoom.
    const h = 2.4 * 2.3 * Math.abs(art.affine[1][2]);
    const w = h * (cast.figs[beat.walker.pose] ?? 0.5);
    return { x: x - w / 2, y: y - h, w, h };
  })();
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
      data-world-scene="crane"
      data-barge-art={view.format}
      data-selected={playing ?? selectedId}
      data-playing={playing}
      data-cast={(cast && playing) ? "" : undefined}
      data-zoomed={(interactive && !!selectedId) || undefined}
      data-ready={ready || undefined}
      aria-label={craneScene.title}
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
        {/* Remote way: the whole ПРУ building glows, not Ivan inside its glass. */}
        {cast && <img className={styles.layer} src={imageAsset(castSrc(view.format, "office"))} alt="" draggable={false} decoding="async" data-layer="pru" data-lit={lit.has("ivan") || undefined} style={box(cast.office)} />}
        {!beat.lifted && !beat.onDeck && sprite("gift")}
        {!(cast && beat.office) && sprite("ivan", { lit: !cast && lit.has("ivan") })}
        {cast && beat.office && (
          <img className={styles.layer} src={imageAsset(castSrc(view.format, `ivan-${beat.office}`))} alt="" draggable={false} data-layer="office" style={box(cast.window)} />
        )}
        {sprite("ladder", { lit: lit.has("ladder") })}
        {sprite("far", { lit: lit.has("far") })}
        {cast && beat.cab && (
          <img className={styles.layer} src={imageAsset(castSrc(view.format, `far-${beat.cab}`))} alt="" draggable={false} data-layer="cab" style={box(cast.cab)} />
        )}
        <div className={styles.sail} style={move({ w: art.width, h: art.height }, sail)} data-sailing={beat.sail > 0 || undefined}>
          <div className={styles.bob}>
            {sprite("barge")}
            {beat.onDeck && sprite("gift", { style: move(s.gift, craneDeckDelta) })}
          </div>
          {sprite("smoke", { className: styles.smoke })}
        </div>
        {walker && beat.walker && (
          <img
            className={styles.layer}
            src={imageAsset(castSrc(view.format, beat.walker.pose))}
            alt=""
            draggable={false}
            data-layer="walker"
            style={{ ...box(walker), transform: beat.walker.flip ? "scaleX(-1)" : undefined }}
          />
        )}
        <div className={styles.layer} style={box(art.top)} data-layer="top" data-lit={lit.has("near") || undefined}>
          <img
            className={styles.sheet}
            src={imageAsset(cast && beat.operator ? art.top.src.replace(/top\.webp$/, `top-${beat.operator}.webp`) : art.top.src)}
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
        {cast && (beat.signal || beat.clock !== undefined || beat.emote || beat.later) && (
          <svg className={styles.overlay} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            {beat.signal && (
              <path className={styles.signal} d={`M${anchor.pru[0]} ${anchor.pru[1] - 20} Q${(anchor.pru[0] + anchor.nearCabin[0]) / 2} ${Math.min(anchor.pru[1], anchor.nearCabin[1]) - 170} ${anchor.nearCabin[0]} ${anchor.nearCabin[1] - 24}`} />
            )}
            {beat.clock !== undefined && (
              <g transform={`translate(${(anchor.nearCabin[0] + anchor.farCabin[0]) / 2} ${anchor.nearCabin[1] - 40}) scale(${k})`}>
                <circle className={styles.dial} r="26" />
                <line className={styles.hand} y2="-12" transform={`rotate(${beat.clock * 90})`} />
                <line className={styles.hand} y2="-19" transform={`rotate(${beat.clock * 1080})`} />
                <text className={styles.badgeText} y="48">+{Math.floor(beat.clock * 3 + 0.001)} ч</text>
              </g>
            )}
            {beat.later && (
              // Petr left his own crates: they wait for the next run, as the result says.
              <g className={styles.emote} data-barge-later transform={`translate(${anchor.crates[0]} ${anchor.crates[1] - 30 - 18 * k}) scale(${k})`}>
                <rect className={styles.tag} x="-96" y="-16" width="192" height="32" rx="16" />
                <circle className={styles.dial} cx="-76" r="10" style={{ strokeWidth: 2.5 }} />
                <path className={styles.hand} d="M-76 -6 V0 H-71" style={{ strokeWidth: 2.5, fill: "none" }} />
                <text className={styles.tagText} x="10" y="6">Груз Петра ждёт</text>
              </g>
            )}
            {beat.emote && (
              <g transform={`translate(${emoteAt[beat.emote.at][0]} ${emoteAt[beat.emote.at][1]}) scale(${k})`}>
                <g className={styles.emote} data-barge-emote={beat.emote.kind}>
                  <path className={styles.bubble} d="M-22 -40 h44 a10 10 0 0 1 10 10 v24 a10 10 0 0 1 -10 10 h-16 l-10 12 l-2 -12 h-16 a10 10 0 0 1 -10 -10 v-24 a10 10 0 0 1 10 -10z" />
                  {beat.emote.kind === "question" ? (
                    <text className={styles.mark} y="-10">?</text>
                  ) : beat.emote.kind === "tired" ? (
                    // Out of breath but kind: closed eyes, a smile, one drop of sweat.
                    <>
                      <path className={styles.mouth} d="M-13 -24 q5 4 10 0 M3 -24 q5 4 10 0" />
                      <path className={styles.mouth} d="M-8 -13 Q0 -6 8 -13" />
                      <path className={styles.drop} d="M30 -46 C36 -36 38 -30 30 -26 C22 -30 24 -36 30 -46Z" />
                    </>
                  ) : (
                    // Sad, not angry: soft brows raised in the middle, a small frown.
                    <>
                      <path className={styles.mouth} d="M-13 -30 L-4 -33 M13 -30 L4 -33" style={{ strokeWidth: 2.4 }} />
                      <circle className={styles.ink} cx="-8" cy="-23" r="2.6" />
                      <circle className={styles.ink} cx="8" cy="-23" r="2.6" />
                      <path className={styles.mouth} d="M-7 -10 Q0 -15 7 -10" />
                    </>
                  )}
                </g>
              </g>
            )}
          </svg>
        )}
        {hookAt && !beat.lifted && sprite("hook", { style: move(s.hook, hookAt) })}
        {hookAt && beat.lifted && sprite("box", { style: move(s.box, hookAt) })}
        {interactive && (
          <svg className={styles.overlay} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            {!pointed && !selectedId && options.filter(({ id }) => !seen.includes(id)).map(({ id }, i) => {
              const t = art.targets[id];
              return (
                <circle key={id} className={styles.ripple} data-barge-ripple={id} cx={t.x + t.w / 2} cy={t.y + t.h / 2}
                  r={Math.max(t.w, t.h) * .42} style={{ animationDelay: `${i * .7}s` }} />
              );
            })}
            {/* Waiting is nobody moving: a clock on the empty cab, not a person on the ladder. */}
            {pointed === "wait" && (
              <g className={styles.wait} data-barge-wait transform={`translate(${anchor.nearCabin[0] - 110} ${anchor.nearCabin[1] - 50}) scale(${k})`}>
                <circle className={styles.dial} r="30" />
                <line className={styles.hand} y2="-14" transform="rotate(90)" />
                <line className={`${styles.hand} ${styles.spin}`} y2="-22" />
                <text className={styles.badgeText} y="58">через 3 ч</text>
              </g>
            )}
          </svg>
        )}
        {options.map((option) => (
          <button
            key={option.id}
            type="button"
            className={styles.hotspot}
            data-hotspot={option.id}
            style={box(art.targets[option.id])}
            aria-label={`${craneCaptions[option.id as keyof typeof craneCaptions]}: ${choiceLabel(option.label)}`}
            aria-pressed={(playing ?? selectedId) === option.id}
            disabled={!interactive}
            onClick={() => onSelect?.(option.id)}
            onPointerEnter={() => setHovered(option.id)}
            onPointerLeave={() => setHovered(undefined)}
            // Only keyboard focus lights the actor; the programmatic focus restored after «Изменить выбор» must not (R19).
            onFocus={(event) => { if (event.currentTarget.matches(":focus-visible")) setHovered(option.id); }}
            onBlur={() => setHovered(undefined)}
          />
        ))}
      </div>
      <ArtworkLoading viewport status={plate.status} onRetry={plate.retry} />
    </figure>
  );
}
