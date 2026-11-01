import { type CSSProperties, type ReactNode, useLayoutEffect, useRef, useState } from "react";
import mapStyles from "../App.module.css";
import { ArtworkLoading } from "../components/ArtworkLoading";
import { useArtworkLoading } from "../components/useArtworkLoading";
import { imageAsset } from "../game/imageAssets";
import { ImageSources } from "../components/ImageSources";
import { choiceLabel } from "./choiceLabel";
import { inventoryAlphabet } from "./inventory/alphabet";
import { warehouseCallouts, warehouseDrawing } from "./inventory/callouts";
import { parcelNames } from "./names";
import { lastmileChoiceArtwork } from "./lastmile/expandedArtwork";
import { lastmileChoiceImage } from "./lastmile/artworkFamily";
import type { SceneArtProps, SceneId, SceneOption } from "./types";
import styles from "./WorldArt.module.css";
import manifest from "./worldManifest.json";
import { LastmileZones } from "./lastmile/LastmileZones";
import { warehouseCamera } from "./inventory/warehouseCamera";

const shortMarkerLabels: Record<string, string> = {
  entrance: "У приёмки", alphabet: "По алфавиту", keeper: "Кладовщик", wms: "Система WMS",
  helicopter: "Вертолёт", rover: "Снегоболотоход", robot: "Тележка", "pipe-carrier": "Трубовоз",
};

const markerInset = 24;
// Keep destinations clear of the “choose transport” chip (smaller below 420px).
const lastmileTopInset = (width: number) => (width <= 420 ? 56 : 64);
const framingInset = 8; // Lastmile framing bounds objects, not markers; the outpainted canvas fills the rest.

function framingScale(
  stage: { width: number; height: number },
  view: { width: number; height: number },
  hotspots: readonly { x: number; y: number }[],
  inset = markerInset,
  fill = stage, // Area the plane should cover; lastmile fills under the instruction overlay too.
) {
  if (!stage.width || !stage.height) return 0;
  const contain = Math.min(stage.width / view.width, stage.height / view.height);
  const cover = Math.max(fill.width / view.width, fill.height / view.height);
  const limit = (stageSize: number, viewSize: number, values: number[]) => {
    const span = Math.max(...values) - Math.min(...values);
    return span > 0 ? (stageSize - inset * 2) / (viewSize * span) : cover;
  };
  return Math.max(
    contain,
    Math.min(
      cover,
      limit(stage.width, view.width, hotspots.map(({ x }) => x)),
      limit(stage.height, view.height, hotspots.map(({ y }) => y)),
    ),
  );
}

function framingOffset(
  stageSize: number,
  planeSize: number,
  values: number[],
  inset = markerInset,
) {
  const centered = (stageSize - planeSize) / 2;
  if (planeSize <= stageSize || values.length === 0) return centered;
  const lower = Math.max(
    stageSize - planeSize,
    inset - Math.min(...values) * planeSize,
  );
  const upper = Math.min(
    0,
    stageSize - inset - Math.max(...values) * planeSize,
  );
  return lower <= upper + 0.5 ? Math.max(lower, Math.min(upper, centered)) : centered;
}

type WorldArtProps = SceneArtProps & {
  scene: SceneId;
  title: string;
  options: SceneOption[];
  markers?: boolean;
  markerLabels?: Record<string, string>;
  placement?: number;
  outcome?: string;
  giftLocation?: string;
  rescue?: string;
  children?: ReactNode | ((composition: "wide" | "tall") => ReactNode);
  illustration?: (format: "desktop" | "mobile") => ReactNode;
};

export function WorldArt({
  scene,
  title,
  options,
  markers = false,
  markerLabels,
  context,
  selectedId,
  onSelect,
  showResult,
  focusedId,
  onFocusChange,
  placement,
  outcome,
  giftLocation,
  rescue,
  children,
  illustration,
}: WorldArtProps) {
  const stage = useRef<HTMLElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  useLayoutEffect(() => {
    const element = stage.current;
    if (!element) return;
    const measure = () => {
      const { width, height } = element.getBoundingClientRect();
      setSize((previous) =>
        previous.width === width && previous.height === height
          ? previous
          : { width, height },
      );
    };
    measure();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  // Lastmile name chips: each name goes right or left of its number; a name with no free side
  // waits for hover/focus. ponytail: brute force over 3^n placements, fine for a handful of vehicles.
  const [chips, setChips] = useState({ left: "", hidden: "" });
  useLayoutEffect(() => {
    const element = stage.current;
    if (scene !== "lastmile" || !element) return;
    const bounds = element.getBoundingClientRect();
    const markers = [...element.querySelectorAll<HTMLElement>("[data-hotspot]")].map((marker) => {
      const r = marker.getBoundingClientRect();
      return {
        id: marker.dataset.hotspot ?? "",
        width: marker.querySelector<HTMLElement>("[data-marker-caption]")?.offsetWidth ?? 0,
        x: r.left + r.width / 2 - bounds.left,
        y: r.top + r.height / 2 - bounds.top,
      };
    });
    const box = (m: (typeof markers)[number], side: number) =>
      side === 0 ? [m.x - 18, m.x - 18 + m.width] : [m.x + 18 - m.width, m.x + 18];
    const hits = (a: number[], ay: number, b: number[], by: number) =>
      Math.abs(ay - by) < 38 && a[0] < b[1] + 4 && b[0] < a[1] + 4;
    let best = { cost: Infinity, sides: [] as number[] };
    for (let code = 0; code < 3 ** markers.length; code++) {
      const sides = markers.map((_, i) => Math.floor(code / 3 ** i) % 3); // 0 right, 1 left, 2 hidden
      const ok = markers.every((m, i) => {
        if (sides[i] === 2) return true;
        const a = box(m, sides[i]);
        if (a[0] < 4 || a[1] > bounds.width - 4) return false;
        return markers.every((n, j) => j === i || (!hits(a, m.y, [n.x - 18, n.x + 18], n.y)
          && (j < i || sides[j] === 2 || !hits(a, m.y, box(n, sides[j]), n.y))));
      });
      const cost = sides.reduce((sum, side) => sum + (side === 2 ? 10 : side), 0);
      if (ok && cost < best.cost) best = { cost, sides };
    }
    const pick = (side: number) => markers.filter((_, i) => best.sides[i] === side).map((m) => m.id).join(" ");
    const next = { left: pick(1), hidden: pick(2) };
    setChips((previous) => previous.left === next.left && previous.hidden === next.hidden ? previous : next);
  });

  const views = manifest.scenes[scene];
  const containedArea = (view: typeof views.desktop) => {
    const scale = Math.min(size.width / view.width, size.height / view.height);
    return view.width * view.height * scale * scale;
  };
  const format =
    scene === "lastmile" && size.width < 600
      ? "mobile"
      : containedArea(views.mobile) > containedArea(views.desktop)
        ? "mobile"
        : "desktop";
  const lastmileFormat = size.width / size.height >= 1.15 ? "wide" : "tall";
  const lastmileComposition = scene === "lastmile"
    ? { ...lastmileChoiceArtwork[lastmileFormat], image: lastmileChoiceImage(lastmileFormat, context.recipient) }
    : undefined;
  const expandedArt = lastmileComposition;
  const composition = expandedArt;
  const inventoryComposition = format === "mobile" ? "tall" : "wide";
  const layers = typeof children === "function"
    ? children(scene === "inventory" ? inventoryComposition : lastmileFormat)
    : children;
  const view = composition ?? manifest.scenes[scene][format];
  const alphabet = inventoryAlphabet[context.parcel];
  const callouts = warehouseCallouts(context.parcel, inventoryComposition);
  const hotspots = view.hotspots.map((point) => {
    if (scene !== "inventory") return point;
    const callout = callouts[point.id as keyof typeof callouts];
    if (callout) {
      return { ...point, x: callout.x, y: callout.y };
    }
    return point;
  });
  const artwork = useArtworkLoading(imageAsset(
    composition?.image ?? view.image,
  ));
  const inventoryCamera = scene === "inventory"
    ? warehouseCamera(size, context.parcel, selectedId, warehouseDrawing(inventoryComposition))
    : undefined;
  const previousCamera = useRef<{
    width: number; height: number; scene: SceneId; artwork: string;
    selectedId?: string; moving: boolean;
  } | null>(null);
  const previous = previousCamera.current;
  // Only a player selection in an already framed scene may move the camera.
  // Mounting, measuring, changing artwork and responsive layout settle instantly.
  const cameraMoving = !!previous && size.width > 0 && size.height > 0 &&
    previous.width === size.width && previous.height === size.height &&
    previous.scene === scene && previous.artwork === artwork.src &&
    (previous.selectedId !== selectedId || previous.moving);
  useLayoutEffect(() => {
    previousCamera.current = { ...size, scene, artwork: artwork.src, selectedId, moving: cameraMoving };
  });
  const scale = inventoryCamera
    ? inventoryCamera.scale
    : composition
      ? framingScale({ ...size, height: Math.max(0, size.height - lastmileTopInset(size.width)) }, view, composition.framing, framingInset, size)
      : framingScale(size, view, hotspots);
  const interactiveMarkers = markers &&
    (scene !== "inventory" || (!showResult && !!onSelect));
  const planeWidth = view.width * scale;
  const planeHeight = planeWidth * view.height / view.width;
  const planeScale = planeWidth / view.width;
  const clampOffset = (offset: number, stageSize: number, planeSize: number) =>
    planeSize <= stageSize ? (stageSize - planeSize) / 2 : Math.max(stageSize - planeSize, Math.min(0, offset));
  const active = options.find((option) => option.id === selectedId);
  const markerId =
    scene === "compact"
      ? placement
        ? `place-${placement}`
        : undefined
      : selectedId;
  const description = [
    `${scene === "compact" ? "Грузовой отсек" : "Иллюстрация"}: ${title}. Подарок: ${parcelNames[context.parcel].nominative}.`,
    scene === "compact"
      ? "Загрузка через задние двери слева. Ближняя стенка кузова показана в разрезе."
      : "",
    scene === "inventory"
      ? `Алфавит идёт слева направо: от приёмки к отгрузке. Место подарка по алфавиту: буква ${alphabet.letter}, ${alphabet.resultPosition} склада.`
      : "",
    active ? `Выбор: ${active.label}.` : "",
    placement ? `Размещение: №${placement}.` : "",
  ]
    .filter(Boolean)
    .join(" ");

  const selectedPoint =
    !illustration && !markers && active
      ? hotspots.find((point) => point.id === selectedId)
      : undefined;
  const selectedTransport = scene === "lastmile"
    ? hotspots.find((point) => point.id === selectedId)
    : undefined;
  return (
    <figure
      ref={stage}
      className={styles.stage}
      aria-label={title}
      data-world-scene={scene}
      data-navigation="fixed"
      data-camera-moving={cameraMoving ? "true" : undefined}
      data-format={format}
      data-selected={selectedId}
      data-gift={context.parcel}
      data-recipient={context.recipient}
      data-placement={
        scene === "compact" ? (placement ?? "waiting") : undefined
      }
      data-outcome={outcome}
      data-event={scene === "lastmile" ? outcome : undefined}
      data-gift-location={giftLocation}
      data-rescue={rescue}
      style={scene === "lastmile" ? { "--world-art": `url("${artwork.src}")` } as CSSProperties : undefined}
    >
      <div
        className={styles.plane}
        data-world-plane
        style={{
          width: planeWidth,
          height: planeHeight,
          ...(inventoryCamera ? {
            left: inventoryCamera.left,
            top: inventoryCamera.top,
            transform: "none",
          } : composition ? {
            left: selectedTransport
              ? clampOffset(size.width / 2 - selectedTransport.x * composition.width * planeScale, size.width, planeWidth)
              : framingOffset(size.width, planeWidth, composition.framing.map(({ x }) => x), framingInset),
            top: selectedTransport
              ? clampOffset(size.height / 2 - selectedTransport.y * composition.height * planeScale, size.height, planeHeight)
              // Art taller than the stage never opens a band above it; shorter art keeps clear of the hint.
              : (planeHeight >= size.height ? (top: number) => Math.max(size.height - planeHeight, Math.min(0, top)) : (top: number) => top)(
                lastmileTopInset(size.width) + framingOffset(size.height - lastmileTopInset(size.width), planeHeight, composition.framing.map(({ y }) => y), framingInset)),
            transform: "none",
          } : {
            left: framingOffset(size.width, planeWidth, hotspots.map(({ x }) => x)),
            top: framingOffset(size.height, planeHeight, hotspots.map(({ y }) => y)),
            transform: "none",
          }),
        }}
      >
        {illustration ? (
          <section
            className={styles.illustration}
            aria-label={description}
            data-concept-art
          >
            {illustration(format)}
          </section>
        ) : (
          <picture>
            <ImageSources src={artwork.src} />
            <img
              ref={artwork.ref}
              className={styles.image}
              src={artwork.src}
              onLoad={artwork.onLoad}
              onError={artwork.onError}
              decoding="async"
              width={view.width}
              height={view.height}
              alt={description}
              draggable={false}
            />
          </picture>
        )}
        {scene === "lastmile" && interactiveMarkers && onSelect && <LastmileZones composition={lastmileFormat} selectedId={selectedId} onSelect={onSelect} focusedId={focusedId} onFocusChange={onFocusChange} />}
        {expandedArt ? (
          <div style={{
            position: "absolute",
            left: expandedArt.original.x * planeScale,
            top: expandedArt.original.y * planeScale,
            width: expandedArt.original.width * planeScale,
            height: expandedArt.original.height * planeScale,
            pointerEvents: "none",
          }}>
            {layers}
          </div>
        ) : layers}
        {selectedPoint && active && (
          <span
            role="img"
            data-selected-marker={selectedPoint.id}
            className={`${mapStyles.mapNumber} ${styles.selectedMarker}`}
            style={{
              left: `${selectedPoint.x * 100}%`,
              top: `${selectedPoint.y * 100}%`,
            }}
            aria-label={`Выбор №${options.indexOf(active) + 1}`}
          >
            {options.indexOf(active) + 1}
          </span>
        )}
        {interactiveMarkers &&
          hotspots.map((point) => {
            const index = options.findIndex(
              (candidate) => candidate.id === point.id,
            );
            const option = options[index];
            if (!option) return null;
            const caption = markerLabels?.[point.id] ?? (scene === "inventory"
              ? point.id === "alphabet" ? `Стеллаж «${alphabet.letter}»`
                : point.id === "wms" ? "WMS" : shortMarkerLabels[point.id]
              : shortMarkerLabels[point.id]);
            return (
              <button
                key={point.id}
                type="button"
                data-hotspot={point.id}
                data-choice-id={point.id}
                className={`${mapStyles.mapNumber} ${styles.marker}`}
                title={caption ?? choiceLabel(option.label)}
                style={{ left: `${point.x * 100}%`, top: `${point.y * 100}%` }}
                aria-label={[
                  `Вариант ${index + 1}`,
                  choiceLabel(option.label),
                  option.accessibleDescription,
                ]
                  .filter(Boolean)
                  .join(". ")}
                aria-pressed={markerId === point.id}
                data-focused={onFocusChange ? focusedId === point.id : undefined}
                data-caption-side={(inventoryCamera ? inventoryCamera.left + point.x * planeWidth > size.width / 2 : chips.left.split(" ").includes(point.id)) ? "left" : undefined}
                data-caption-hidden={scene === "lastmile" && chips.hidden.split(" ").includes(point.id) ? "" : undefined}
                onPointerEnter={onFocusChange && (() => onFocusChange(point.id))}
                onPointerLeave={onFocusChange && (() => onFocusChange(undefined))}
                disabled={showResult || !onSelect || (!!selectedId && selectedId !== point.id)}
                onClick={() => onSelect?.(point.id)}
              >
                <span aria-hidden="true">{index + 1}</span>
                {(scene === "lastmile" || scene === "inventory") && <span className={styles.markerCaption} data-marker-caption aria-hidden="true">{caption}</span>}
              </button>
            );
          })}
      </div>
      {!illustration && <ArtworkLoading viewport status={artwork.status} onRetry={artwork.retry} />}
    </figure>
  );
}
