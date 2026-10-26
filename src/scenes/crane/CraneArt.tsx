import { type CSSProperties, useLayoutEffect, useRef, useState } from "react";
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
function camera(stage: { width: number; height: number }) {
  const fit = (format: CraneFormat) => {
    const { width, height, focus } = craneArtwork[format];
    const contain = Math.min(stage.width / width, stage.height / height);
    const cover = Math.max(stage.width / width, stage.height / height);
    const scale = Math.max(contain, Math.min(cover, stage.width / focus.width, stage.height / focus.height));
    return { format, scale, area: focus.width * focus.height * scale * scale };
  };
  const wide = fit("wide");
  const tall = fit("tall");
  const { format, scale } = wide.area >= tall.area ? wide : tall;
  const { width, height, focus } = craneArtwork[format];
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
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  const view = camera(size);
  const art = craneArtwork[view.format];
  const artwork = useArtworkLoading(imageAsset(art.image));
  const options = craneScene.options(context);
  const interactive = !showResult && !!onSelect;
  const at = (x: number, y: number) => ({ left: `${(x / art.width) * 100}%`, top: `${(y / art.height) * 100}%` });

  return (
    <figure
      ref={stage}
      className={styles.stage}
      data-barge-art={view.format}
      data-selected={selectedId}
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
            alt="Причал на Оби: Иван в офисе ПРУ, подарок на поддоне, высокий кран с лестницей до кабины, баржа с трубами у причала и дальний кран, где сидит Пётр рядом со своими ящиками."
          />
        </picture>
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
              style={{ ...at(point.x, point.y), "--ring": `${(point.r / art.width) * view.width}px` } as CSSProperties}
              aria-label={`Вариант ${index + 1}. ${choiceLabel(option.label)}`}
              aria-pressed={selectedId === option.id}
              disabled={!interactive}
              onClick={() => onSelect?.(option.id)}
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
