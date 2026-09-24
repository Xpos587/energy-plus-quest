import { type ReactNode, useLayoutEffect, useRef, useState } from "react";
import mapStyles from "../App.module.css";
import { parcelNames } from "./names";
import type { SceneArtProps, SceneId, SceneOption } from "./types";
import styles from "./WorldArt.module.css";
import manifest from "./worldManifest.json";

type WorldArtProps = SceneArtProps & {
  scene: SceneId;
  title: string;
  options: SceneOption[];
  markers?: boolean;
  placement?: number;
  outcome?: string;
  giftLocation?: string;
  rescue?: string;
  children?: ReactNode;
  illustration?: (format: "desktop" | "mobile") => ReactNode;
};

export function WorldArt({
  scene,
  title,
  options,
  markers = false,
  context,
  selectedId,
  onSelect,
  showResult,
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

  const views = manifest.scenes[scene];
  const containedArea = (view: typeof views.desktop) => {
    const scale = Math.min(size.width / view.width, size.height / view.height);
    return view.width * view.height * scale * scale;
  };
  const format =
    containedArea(views.mobile) > containedArea(views.desktop)
      ? "mobile"
      : "desktop";
  const view = manifest.scenes[scene][format];
  const width =
    size.width && size.height
      ? Math.min(size.width, (size.height * view.width) / view.height)
      : undefined;
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
    active ? `Выбор: ${active.label}.` : "",
    placement ? `Размещение: №${placement}.` : "",
  ]
    .filter(Boolean)
    .join(" ");

  const selectedPoint =
    !illustration && !markers && active
      ? view.hotspots.find((point) => point.id === selectedId)
      : undefined;
  return (
    <figure
      ref={stage}
      className={styles.stage}
      aria-label={title}
      data-world-scene={scene}
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
    >
      <div
        className={styles.plane}
        data-world-plane
        style={{
          width: width ?? "100%",
          aspectRatio: `${view.width} / ${view.height}`,
        }}
      >
        {illustration ? (
          <div
            className={styles.illustration}
            role={scene === "compact" ? "group" : "img"}
            aria-label={description}
            data-concept-art
          >
            {illustration(format)}
          </div>
        ) : (
          <picture>
            <img
              className={styles.image}
              src={`${import.meta.env.BASE_URL}${view.image}`}
              width={view.width}
              height={view.height}
              alt={description}
              draggable={false}
            />
          </picture>
        )}
        {children}
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
        {markers &&
          view.hotspots.map((point) => {
            const index = options.findIndex(
              (candidate) => candidate.id === point.id,
            );
            const option = options[index];
            if (!option) return null;
            return (
              <button
                key={point.id}
                type="button"
                data-hotspot={point.id}
                className={`${mapStyles.mapNumber} ${styles.marker}`}
                style={{ left: `${point.x * 100}%`, top: `${point.y * 100}%` }}
                aria-label={[option.label, option.accessibleDescription]
                  .filter(Boolean)
                  .join(". ")}
                aria-pressed={markerId === point.id}
                disabled={showResult || !onSelect}
                onClick={() => onSelect?.(point.id)}
              >
                {index + 1}
              </button>
            );
          })}
      </div>
    </figure>
  );
}
