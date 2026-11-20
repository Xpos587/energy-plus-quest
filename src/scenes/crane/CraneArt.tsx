import { Footprints, Monitor, UsersRound } from "lucide-react";
import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from "react";
import { ArtworkLoading } from "../../components/ArtworkLoading";
import { ImageSources } from "../../components/ImageSources";
import type { ArtworkStatus } from "../../components/useArtworkLoading";
import { imageAsset } from "../../game/imageAssets";
import { choiceLabel } from "../choiceLabel";
import type { SceneArtProps } from "../types";
import { craneArtwork, craneCaptions, cranePins, craneWorld, type CraneFormat, type Rect } from "./artwork";
import { craneBeat, craneDeckDelta, craneDuration, craneRest } from "./consequence";
import { craneScene } from "./index";
import { fitTapTargets } from "./tapTargets";
import styles from "./CraneArt.module.css";

// Same icons as the option list (SceneChoices), so a pin and its row read as one choice.
const pinIcons = { remote: Monitor, rush: Footprints, petr: UsersRound } as const;

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

/** A quay walk with its kinks rounded off (r metres on the ground); a projected quadratic stays a quadratic. */
function roundedRoute(route: readonly (readonly number[])[], project: (p: readonly number[]) => readonly number[], r = 1.5) {
  const at = (p: readonly number[]) => project(p).map((v) => v.toFixed(1)).join(" ");
  const toward = (c: readonly number[], e: readonly number[]) => {
    const leg = Math.hypot(e[0] - c[0], e[1] - c[1]);
    const t = Math.min(r, leg / 2) / leg;
    return [c[0] + (e[0] - c[0]) * t, c[1] + (e[1] - c[1]) * t, c[2]];
  };
  const corners = route.slice(1, -1).map((c, i) => ` L${at(toward(c, route[i]))} Q${at(c)} ${at(toward(c, route[i + 2]))}`);
  return `M${at(route[0])}${corners.join("")} L${at(route[route.length - 1])}`;
}

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
  const [attempt, setAttempt] = useState(0);
  const source = (path: string) => {
    const src = imageAsset(path);
    return attempt ? `${src}${src.includes("?") ? "&" : "?"}artwork-retry=${attempt}` : src;
  };
  const artworkKey = `${view.format}:${attempt}`;
  const [readiness, setReadiness] = useState<{ key: string; status: ArtworkStatus }>({ key: artworkKey, status: "loading" });
  const status = readiness.key === artworkKey ? readiness.status : "loading";
  useLayoutEffect(() => {
    if (status !== "loading") return;
    let cancelled = false;
    // The plate and transparent sprites must enter the first painted frame together.
    const images = [...stage.current!.querySelectorAll("img")];
    Promise.all(images.map((image) => image.decode())).then(
      () => { if (!cancelled) setReadiness({ key: artworkKey, status: "ready" }); },
      () => { if (!cancelled) setReadiness({ key: artworkKey, status: "error" }); },
    );
    return () => { cancelled = true; };
  // While initially loading, a rail choice can replace cast images. Track source changes,
  // not every position/frame; once revealed, normal animation never blanks the scene.
  }, [artworkKey, status, beat.lifted, beat.onDeck]);
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
  // R19 round 2: on a 320px phone the ladder and the empty cab were 22px boxes that touched.
  // Same places on the picture, but each target is at least 44px and keeps 8px clear of its neighbour.
  const hotspot = new Map(options.map((option) => {
    const rect = art.targets[option.id];
    // Plane coordinates: the hotspot box sits inside the plane, which is drawn 1:1 to the picture.
    const x = (rect.x / art.width) * view.width;
    const y = (rect.y / art.height) * view.height;
    return [option.id, { x, y, w: (rect.w / art.width) * view.width, h: (rect.h / art.height) * view.height }];
  }));
  // Only the part of the plane the stage shows is usable for a finger.
  const frame = { x: -view.left, y: -view.top, w: size.width, h: size.height };
  // A zoomed card can crop an actor out of frame; its pin would be clamped onto empty quay, so it hides instead.
  const ids = options.map((option) => option.id).filter((id) => {
    const r = hotspot.get(id)!;
    return !size.width || (r.x + r.w > frame.x && r.x < frame.x + frame.w && r.y + r.h > frame.y && r.y < frame.y + frame.h);
  });
  const fitted = new Map(fitTapTargets(ids.map((id) => hotspot.get(id)!), size, { frame }).map((rect, i) => [ids[i], rect]));
  const hotspotStyle = (id: string): CSSProperties => {
    const rect = fitted.get(id);
    if (!rect) return {};
    // The pin stands over its box; tell it how much stage it has on each side so it never leaves the screen.
    const centre = rect.x + view.left + rect.w / 2;
    return {
      left: rect.x, top: rect.y, width: rect.w, height: rect.h,
      ["--room-left" as string]: `${centre}px`, ["--room-right" as string]: `${size.width - centre}px`,
    };
  };
  // A pin that would stick out of the top of the stage hangs under its box instead (chip 34 px + pointer 7 px).
  // Where two chips above their actors would collide (Petr stands by the ladder), the smaller actor's chip hangs below.
  const below = new Set(ids.filter((id) => (fitted.get(id)?.y ?? 0) + view.top < 52));
  const narrow = size.width <= 560;
  // ponytail: chip width estimated from its text (Roboto Condensed ≈ 0.55 em per letter); measure the chips if names grow.
  const chipBox = (id: string) => {
    const rect = fitted.get(id)!;
    const { name, detail } = cranePins[id as keyof typeof cranePins];
    const text = narrow ? (name ?? "") : name ? `${name} · ${detail}` : detail;
    const w = (narrow ? 32 : 40) + text.length * (narrow ? 7.2 : 8.3);
    const h = narrow ? 30 : 34;
    const y = below.has(id) ? rect.y + rect.h + 7 : rect.y - 7 - h;
    return { x: rect.x + rect.w / 2 - w / 2, y, w, h };
  };
  for (const [i, a] of ids.entries())
    for (const b of ids.slice(i + 1)) {
      if (!fitted.has(a) || !fitted.has(b)) continue;
      const [p, q] = [chipBox(a), chipBox(b)];
      if (p.x < q.x + q.w + 4 && q.x < p.x + p.w + 4 && p.y < q.y + q.h + 4 && q.y < p.y + p.h + 4)
        below.add(fitted.get(a)!.h < fitted.get(b)!.h ? a : b);
    }
  const pinBelow = (id: string) => below.has(id);
  // Pulsing hint rings (Grisha 09.11): one ring size for every actor, and the ring sits on the box the
  // finger actually hits — the fitted tap target, not a separate guess at where the actor is.
  const toArt = view.width ? art.width / view.width : 0;
  const artBox = (id: string) => {
    const rect = fitted.get(id);
    return (rect && toArt ? { x: rect.x * toArt, y: rect.y * toArt, w: rect.w * toArt, h: rect.h * toArt } : art.targets[id]);
  };
  const ringSize = Math.max(0, ...ids.map((id) => Math.max(artBox(id).w, artBox(id).h))) * 0.36;
  const ringAt = (id: string) => {
    const rect = artBox(id);
    return ringSize ? { x: rect.x + rect.w / 2, y: rect.y + rect.h / 2, r: ringSize } : undefined;
  };
  // A world move is a pure screen shift for the orthographic quay camera.
  const move = (r: { w: number; h: number }, delta: readonly number[]): CSSProperties => {
    const [[ax, ay, az], [bx, by, bz]] = art.affine;
    const dx = ax * delta[0] + ay * delta[1] + az * delta[2];
    const dy = bx * delta[0] + by * delta[1] + bz * delta[2];
    return { transform: `translate(${(dx / r.w) * 100}%, ${(dy / r.h) * 100}%)` };
  };
  const hookAt = beat.hook ? sub(beat.hook, [craneWorld.gift[0], craneWorld.gift[1], craneWorld.hookAttach]) : undefined;
  const [tipX, tipY] = art.project(craneWorld.tips[beat.frame]);
  const [hookX, hookY] = beat.hook ? art.project(beat.hook) : [0, 0];
  const s = art.sprites;
  const sheetStyle = {
    width: `${art.top.cols * 100}%`, height: `${art.top.rows * 100}%`,
    transform: `translate(${(-(beat.frame % art.top.cols) / art.top.cols) * 100}%, ${(-Math.floor(beat.frame / art.top.cols) / art.top.rows) * 100}%)`,
  };
  const anchor = art.anchors;
  // Overlay marks are drawn in drawing px; keep them readable when a big drawing is shrunk to a phone.
  const k = view.width ? Math.max(1, (0.8 * art.width) / view.width) : 1;
  // Choice marks sized to the people (Grisha: body-wide dashes looked sloppy): a footpath of 0.35 m round dots
  // every 0.8 m. Zero-length dashes with round caps are always whole dots, even on the rounded corners.
  const metre = Math.hypot(art.affine[0][0], art.affine[1][0]);
  const dot = { width: 0.35 * metre * k, step: 0.8 * metre * k };
  const dotted = { strokeWidth: dot.width, strokeDasharray: `0 ${dot.step}`, ["--dash" as string]: `${-dot.step}` };
  // Rush: Ivan's own sprite slides along the rush route (by length), with a small step bob.
  const walkShift = (() => {
    if (beat.walk === undefined) return undefined;
    const route = craneWorld.routes.rush;
    const legs = route.slice(1).map((p, i) => Math.hypot(p[0] - route[i][0], p[1] - route[i][1]));
    let d = beat.walk * legs.reduce((a, b) => a + b, 0);
    let i = 0;
    while (i < legs.length - 1 && d > legs[i]) d -= legs[i++];
    const t = legs[i] ? Math.min(1, d / legs[i]) : 1;
    const at = route[i].map((v, j) => v + (route[i + 1][j] - v) * t);
    const [x0, y0] = art.project(route[0]);
    const [x, y] = art.project(at);
    const bob = beat.walk < 1 ? -Math.abs(Math.sin(d * Math.PI / 0.8)) * 0.25 * metre : 0;
    return { transform: `translate(${((x - x0) / s.ivan.w) * 100}%, ${((y - y0 + bob) / s.ivan.h) * 100}%)` };
  })();
  // Only while choosing: a marching dotted way; after confirming, the crane loading tells the story.
  const routeId = !playing && (litId === "rush" || litId === "petr") ? litId : undefined;
  const routePath = routeId && roundedRoute(craneWorld.routes[routeId], art.project);
  // Remote: a radio signal arcs from the ПРУ roof over both cranes to the barge crane's cab.
  const showSignal = litId === "remote" && (!playing || beat.signal);
  const [sx, sy] = [anchor.pru[0], anchor.pru[1] - 2 * metre];
  const [ex, ey] = [anchor.nearCabin[0], anchor.nearCabin[1] - 2.4 * metre];
  const lift = 34 * Math.abs(art.affine[1][2]);
  const signalPath = `M${sx} ${sy} Q${(sx + ex) / 2} ${Math.min(sy, ey) - lift} ${ex} ${ey}`;
  const sprite = (name: keyof typeof s, extra?: { style?: CSSProperties; lit?: boolean; className?: string; data?: string }) => (
    <img
      className={[styles.layer, extra?.className].filter(Boolean).join(" ")}
      src={source(s[name].src)}
      alt=""
      draggable={false}
      decoding="sync"
      data-layer={name}
      data-lit={extra?.lit || undefined}
      data-busy={(playing && beat.busy === name) || undefined}
      data-walking={extra?.data}
      style={{ ...box(s[name]), ...extra?.style }}
    />
  );

  return (
    <figure
      ref={stage}
      className={styles.stage}
      data-world-scene="crane"
      data-artwork-ready={status === "ready"}
      data-barge-art={view.format}
      data-selected={playing ?? selectedId}
      data-playing={playing}
      data-cast={playing ? "" : undefined}
      data-zoomed={(interactive && !!selectedId) || undefined}
      data-ready={ready || undefined}
      aria-label={craneScene.title}
    >
      <div className={styles.plane} style={{ width: view.width, height: view.height, left: view.left, top: view.top, visibility: status === "ready" ? "visible" : "hidden" }}>
        <picture>
          <ImageSources src={source(art.plate)} />
          <img
            className={styles.image}
            src={source(art.plate)}
            width={art.width}
            height={art.height}
            decoding="sync"
            draggable={false}
            alt="Причал на Оби: Иван у офиса ПРУ слева, ближний кран, подарок на тележке, а далеко справа у баржи с трубами — портальный кран с пустой кабиной и лестницей. Пётр стоит у своего крана, под стрелой — его ящики и маленькая баржа."
          />
        </picture>
        {routePath && (
          <svg className={styles.overlay} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            <path className={styles.route} data-barge-route={routeId} d={routePath}
              style={{ stroke: routeId === "rush" ? "#FF8A00" : "#2FA84F", ...dotted }} />
          </svg>
        )}
        {/* Everything standing on the quay, over the routes: the walks pass behind cranes, crates and trees. */}
        <img className={styles.layer} src={source(art.occluder)} alt="" draggable={false} decoding="sync" data-layer="occluder" style={box({ x: 0, y: 0, w: art.width, h: art.height })} />
        {!beat.lifted && !beat.onDeck && sprite("gift")}
        {beat.walk !== undefined && sprite("porch")}
        {(beat.office !== "empty" || walkShift) && sprite("ivan", { lit: lit.has("ivan"), style: walkShift, data: walkShift && "walking" })}
        {sprite("ladder", { lit: lit.has("ladder") })}
        {beat.cab !== "empty" && sprite("far", { lit: lit.has("far") })}
        {sprite("barge")}
        {beat.onDeck && sprite("gift", { style: move(s.gift, craneDeckDelta) })}
        <div className={styles.layer} style={box(art.top)} data-layer="top" data-lit={lit.has("near") || undefined}>
          <img
            className={styles.sheet}
            src={source(art.top.src)}
            alt=""
            draggable={false}
            decoding="sync"
            style={sheetStyle}
          />
        </div>
        {beat.hook && (
          <svg className={styles.cable} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            <line x1={tipX} y1={tipY} x2={hookX} y2={hookY} />
          </svg>
        )}
        {(showSignal || beat.emote || beat.later) && (
          <svg className={styles.overlay} viewBox={`0 0 ${art.width} ${art.height}`} aria-hidden="true">
            {showSignal && (
              // Moonlight-yellow on a dark casing reads over trees, road and sky; bright packets run along the arc.
              <g data-barge-signal>
                <path className={styles.signalCasing} style={{ strokeWidth: dot.width * 2.2 }} d={signalPath} />
                <path className={styles.signal} style={{ strokeWidth: dot.width }} d={signalPath} />
                <path className={styles.packets} pathLength={100} style={{ strokeWidth: dot.width * 1.8 }} d={signalPath} data-barge-packets />
                {[0, 1, 2].map((i) => (
                  <path key={i} className={styles.wave} style={{ animationDelay: `${i * 0.5}s`, strokeWidth: dot.width }}
                    d={`M${sx - 3.6 * metre} ${sy - metre} Q${sx} ${sy - 4.8 * metre} ${sx + 3.6 * metre} ${sy - metre}`} />
                ))}
              </g>
            )}
            {beat.later && (
              // Petr left his own cargo (crates on his small barge): it waits for the next run, as the result says.
              // Hangs under the crates (pointer tip on petrCargo), so the chip sits over the pontoon and water, off the quay edge.
              <g className={styles.emote} data-barge-later transform={`translate(${anchor.petrCargo[0]} ${anchor.petrCargo[1]}) scale(${k})`}>
                <path className={styles.tag} d="M-8 9 L0 0 L8 9" />
                <rect className={styles.tag} x="-96" y="8" width="192" height="32" rx="16" />
                <path d="M-7 10 H7" stroke="#fff" strokeWidth="3" />
                <circle className={styles.dial} cx="-76" cy="24" r="10" style={{ strokeWidth: 2.5 }} />
                <path className={styles.hand} d="M-76 18 V24 H-71" style={{ strokeWidth: 2.5, fill: "none" }} />
                <text className={styles.tagText} x="10" y="30">Груз Петра ждёт</text>
              </g>
            )}
            {beat.emote && (
              // The bubble tail tip (-4, 16) lands on the anchor over the head.
              <g transform={`translate(${art.emote[beat.emote.at][0] + 4 * k} ${art.emote[beat.emote.at][1] - 16 * k}) scale(${k})`}>
                <g className={styles.emote} data-barge-emote={beat.emote.kind} data-barge-emote-at={beat.emote.at}>
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
              // One ring size on every actor, centred on the actor, not on its tap box.
              const hint = ringAt(id);
              if (!hint) return null;
              return (
                <circle key={id} className={styles.ripple} data-barge-ripple={id} cx={hint.x} cy={hint.y} r={hint.r}
                  style={{ animationDelay: `${i * .7}s` }} />
              );
            })}
          </svg>
        )}
        {options.map((option) => (
          <button
            key={option.id}
            data-hotspot-lit={(hovered === option.id) || undefined}
            type="button"
            className={styles.hotspot}
            data-hotspot={option.id}
            data-offstage={!ids.includes(option.id) || undefined}
            style={hotspotStyle(option.id)}
            aria-label={`${craneCaptions[option.id as keyof typeof craneCaptions]}: ${choiceLabel(option.label)}`}
            aria-pressed={(playing ?? selectedId) === option.id}
            disabled={!interactive}
            onClick={() => onSelect?.(option.id)}
            onPointerEnter={() => setHovered(option.id)}
            onPointerLeave={() => setHovered(undefined)}
            // Only keyboard focus lights the actor; the programmatic focus restored after «Изменить выбор» must not (R19).
            onFocus={(event) => { if (event.currentTarget.matches(":focus-visible")) setHovered(option.id); }}
            onBlur={() => setHovered(undefined)}
          >
            <QuayPin id={option.id as keyof typeof cranePins} number={options.indexOf(option) + 1} below={pinBelow(option.id)} />
          </button>
        ))}
      </div>
      <ArtworkLoading status={status} onRetry={() => setAttempt((count) => count + 1)} />
    </figure>
  );
}

/** A tappable marker over an actor: the option icon with its number, and the person's name where there is one. */
function QuayPin({ id, number, below }: { id: keyof typeof cranePins; number: number; below: boolean }) {
  const Icon = pinIcons[id];
  const { name, detail } = cranePins[id];
  return (
    <span className={styles.pin} data-quay-pin={id} data-below={below || undefined} aria-hidden="true">
      <span className={styles.pinChip}>
        <span className={styles.pinIcon} data-choice-number={number}><Icon /></span>
        {name && <b className={styles.pinName}>{name}</b>}
        <span className={styles.pinDetail} data-named={!!name || undefined}>{detail}</span>
      </span>
    </span>
  );
}
