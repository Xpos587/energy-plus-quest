import { useId } from "react";
import type { SceneArtProps } from "../types";
import { WorldArt } from "../WorldArt";
import { compactScene } from "./index";
import sectors from "./sectors.json";
import styles from "./CompactSectors.module.css";

export function CompactArt(props: SceneArtProps) {
  const { selectedId, showResult, context, onSelect } = props;
  const gradient = useId();
  const manual = /^place-([1-4])$/.exec(selectedId ?? "");
  const placement =
    selectedId === "auto" && showResult
      ? context.parcel === "boat"
        ? 4
        : 3
      : manual
        ? Number(manual[1])
        : undefined;
  const options = compactScene.options(context);
  const locked = showResult || !onSelect;
  return (
    <WorldArt
      {...props}
      scene="compact"
      title={compactScene.title}
      options={[]}
      markers
      placement={placement}
      outcome={
        showResult && placement ? `${context.parcel}-${placement}` : undefined
      }
      illustration={() => (
        <svg
          viewBox="0 0 2048 1143"
          className={styles.art}
          role="group"
          aria-label="Четыре сектора погрузки в кузове"
        >
          <defs>
            <linearGradient id={gradient} x1="0" y1="0" x2="0" y2="1">
              <stop stopColor="#2799db" stopOpacity=".07" />
              <stop offset="1" stopColor="#2799db" stopOpacity=".27" />
            </linearGradient>
          </defs>
          <image
            href={`${import.meta.env.BASE_URL}compact-art/loading-neutral-v2.png`}
            width="2048"
            height="1143"
          />
          {sectors.map((sector, index) => (
            <g
              key={sector.id}
              className={styles.sector}
              data-loading-zone={sector.id}
              data-hotspot={sector.id}
              data-active={placement === sector.number}
              role="button"
              tabIndex={locked ? -1 : 0}
              aria-disabled={locked}
              aria-label={`${options[index].label}. ${options[index].accessibleDescription}`}
              aria-pressed={placement === sector.number}
              onClick={() => {
                if (!locked) onSelect(sector.id);
              }}
              onKeyDown={(event) => {
                if (!locked && (event.key === "Enter" || event.key === " ")) {
                  event.preventDefault();
                  onSelect(sector.id);
                }
              }}
            >
              <path
                className={styles.volume}
                d={sector.volume}
                fill={`url(#${gradient})`}
              />
              <path className={styles.edge} d={sector.edge} />
              <path className={styles.surface} d={sector.surface} />
              <path className={styles.near} d={sector.near} />
              <g
                className={styles.number}
                transform={`translate(${sector.x} ${sector.y}) rotate(-9)`}
              >
                <rect x="-18" y="-20" width="36" height="40" rx="10" />
                <text y="8">{sector.number}</text>
              </g>
            </g>
          ))}
        </svg>
      )}
    />
  );
}
