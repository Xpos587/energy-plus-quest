import { imageAsset } from "../../game/imageAssets";
import { type CSSProperties, useLayoutEffect, useRef, useState } from "react";
import { parcelNames } from "../names";
import type { SceneArtProps } from "../types";
import {
  CargoBay,
  cargoSpaces,
} from "./CargoBay";
import styles from "./CompactSectors.module.css";
import { compactScene } from "./index";
import { compactResultArtwork, compactResultFrames } from "./resultArtwork";
import { layoutRegions } from "./layout";
import { useCompactLayout } from "./editor/useCompactLayout";

const failedLoadingArt = {
  old: { portrait: imageAsset('compact-art/boat-zone3-no-fit-old-v50.webp'), wide: imageAsset('compact-art/boat-zone3-no-fit-wide-old-v50.webp') },
  old4: { portrait: imageAsset('compact-art/boat-zone3-no-fit-old4-v50.webp'), wide: imageAsset('compact-art/boat-zone3-no-fit-wide-old4-v50.webp') },
  near: { portrait: imageAsset('compact-art/boat-zone3-no-fit-v48.webp'), wide: imageAsset('compact-art/boat-zone3-no-fit-wide-v48.webp') },
  crew: { portrait: imageAsset('compact-art/boat-zone3-no-fit-crew-v50.webp'), wide: imageAsset('compact-art/boat-zone3-no-fit-wide-crew-v50.webp') },
  express: { portrait: imageAsset('compact-art/boat-zone3-no-fit-crew-v50.webp'), wide: imageAsset('compact-art/boat-zone3-no-fit-wide-crew-v50.webp') },
} as const;

export function CompactArt({
  selectedId,
  showResult,
  context,
  onSelect,
  focusedId,
  onFocusChange,
}: SceneArtProps) {
  const stage = useRef<HTMLElement>(null);
  const layout = useCompactLayout();
  const [ownFocus, setOwnFocus] = useState<string>();
  const focused = onFocusChange ? focusedId : ownFocus;
  const setFocused = onFocusChange ?? setOwnFocus;
  // Inspection uses the same artwork and coordinate plane as the overview.
  // Only the camera transform changes; replacing the canvas loses the truck context.
  const frame = showResult
    ? compactResultFrames[`${context.parcel}:${selectedId}`]
    : undefined;
  const cameraDetail = !!frame;
  const outcomeImage = showResult
    ? compactResultArtwork[`${context.parcel}:${selectedId}`]
    : undefined;
  const [measuredHeight, setCanvasHeight] = useState(520);
  const canvasHeight = frame
    ? (frame.height ?? 874)
    : outcomeImage
      ? Math.max(390, Math.min(874, measuredHeight))
      : // Never crop the wide truck: a stage wider than 2:1 letterboxes instead.
        Math.max(520, measuredHeight);
  const portrait = !!outcomeImage || canvasHeight > 570;
  useLayoutEffect(() => {
    const element = stage.current;
    if (!element) return;
    const measure = () => {
      const { width, height } = element.getBoundingClientRect();
      if (width > 0 && height > 0) setCanvasHeight((1040 * height) / width);
    };
    measure();
    const observer =
      typeof ResizeObserver !== "undefined"
        ? new ResizeObserver(measure)
        : undefined;
    observer?.observe(element);
    window.addEventListener("resize", measure);
    return () => {
      observer?.disconnect();
      window.removeEventListener("resize", measure);
    };
  }, []);
  const offsetY = cameraDetail
    ? 0
    : outcomeImage
      ? -Math.max(0, Math.min(274, 874 - canvasHeight - 36))
      : (canvasHeight - (portrait ? 874 : 520)) / 2;
  const layoutProfile = frame?.unloaded ? "unloaded" : portrait ? "portrait" : "wide";
  const regions = layoutRegions(layout, layoutProfile);
  const markersVisible = showResult || !!onSelect || !!selectedId;
  const activeSpaces = markersVisible
    ? regions.map((space) => ({ ...space, y: space.y + offsetY }))
    : [];
  const inspectedId =
    selectedId === "auto"
      ? context.parcel === "boat"
        ? "place-4"
        : "place-3"
      : selectedId;
  const inspectedSpace = !showResult
    ? regions.find((space) => space.id === inspectedId)
    : undefined;
  // Include the selected space and the cabin's right edge, with a little breathing room.
  const inspectionScale = inspectedSpace
    ? Math.min(1.35, Math.max(1, 1040 / (1040 - inspectedSpace.x + 64)))
    : 1;
  const inspectionCenter = inspectedSpace
    ? Math.min((inspectedSpace.x + 1040) / 2, 1040 - 520 / inspectionScale)
    : 520;
  const manual = /^place-([1-4])$/.exec(selectedId ?? "");
  const placement =
    selectedId === "auto"
      ? context.parcel === "boat"
        ? 4
        : 3
      : manual
        ? Number(manual[1])
        : undefined;
  const options = compactScene.options(context);
  const locked = showResult || !onSelect;
  if (showResult && context.parcel === "boat" && selectedId === "place-3") {
    const art = failedLoadingArt[context.carrier ?? "near"];
    return (
      <figure
        ref={stage}
        className={styles.stage}
        data-world-scene="compact"
        data-fixed-result
        data-failure-art="boat-place-3"
      >
        <picture className={styles.failurePicture}>
          <source
            media="(min-width: 901px)"
            srcSet={art.wide}
          />
          <img
            className={styles.failureImage}
            src={art.portrait}
            alt="Лодка осталась на тележке снаружи фуры: рабочие оценивают слишком маленькое место над тремя коробками."
          />
        </picture>
      </figure>
    );
  }
  return (
    <figure
      ref={stage}
      className={styles.stage}
      tabIndex={showResult || !onSelect ? undefined : 0}
      data-fixed-choice={!showResult || undefined}
      aria-label={`${compactScene.title}. Боковой разрез кузова. Задние двери слева, кабина справа. Подарок: ${parcelNames[context.parcel].nominative}.`}
      data-world-scene="compact"
      data-fixed-result={showResult || undefined}
      data-camera-detail={cameraDetail || undefined}
      data-inspection-camera={!!inspectedSpace || undefined}
      data-detail-zone={cameraDetail ? selectedId : undefined}
      style={
        {
          "--inspection-scale": inspectionScale,
          "--inspection-center": inspectionCenter,
          "--inspection-shift": `${((520 - inspectionCenter) / 1040) * 100}%`,
          "--canvas-height": canvasHeight,
          "--canvas-aspect": `1040 / ${canvasHeight}`,
          "--detail-x": frame?.x,
          "--detail-desktop-x": frame?.desktopX ?? frame?.x,
          "--detail-y": frame?.y,
          "--detail-mobile-width": frame?.width,
          "--detail-desktop-width": frame?.desktopWidth,
          "--result-focus": `${(cargoSpaces[(placement ?? 3) - 1].markerX / 1040) * 100}%`,
        } as CSSProperties
      }
      data-selected={selectedId}
      data-layout-profile={layoutProfile}
      data-gift={context.parcel}
      data-recipient={context.recipient}
      data-placement={placement ?? "waiting"}
      data-outcome={
        showResult && placement ? `${context.parcel}-${placement}` : undefined
      }
    >
      <div
        className={styles.plane}
        data-world-plane
        data-map-surface={!showResult || undefined}
      >
        <CargoBay
          placement={placement}
          focused={focused}
          portrait={portrait}
          canvasHeight={canvasHeight}
          image={outcomeImage}
          imageHeight={frame?.height}
          carrier={context.carrier}
          regions={markersVisible ? regions : []}
          offsetY={offsetY}
        />
        {activeSpaces.map((space, index) => (
          <button
            key={space.id}
            type="button"
            className={styles.marker}
            data-hotspot={space.id}
            data-focused={focused === space.id}
            data-choice-id={space.id}
            aria-label={`${options[index].label}. ${options[index].accessibleDescription}`}
            aria-pressed={placement === space.number}
            aria-disabled={locked}
            disabled={locked}
            style={
              {
                "--marker-x": space.x,
                "--marker-y": space.y,
                "--marker-width": space.width,
                "--marker-height": space.height,
              } as CSSProperties
            }
            onFocus={() => setFocused(space.id)}
            onBlur={() => setFocused(undefined)}
            onPointerEnter={() => setFocused(space.id)}
            onPointerLeave={() => setFocused(undefined)}
            onClick={() => onSelect?.(space.id)}
          >
            <span className={styles.number} data-layout-badge={space.id} style={{
              left: `calc(${layout.profiles[layoutProfile][index].badge.x - space.x} / 1040 * 100cqw)`,
              top: `calc(${layout.profiles[layoutProfile][index].badge.y - (space.y - offsetY)} / 1040 * 100cqw)`,
              width: layout.profiles[layoutProfile][index].badge.size,
              height: layout.profiles[layoutProfile][index].badge.size,
              fontSize: layout.profiles[layoutProfile][index].badge.size * 15 / 24,
            }}>{space.number}</span>
          </button>
        ))}
      </div>
    </figure>
  );
}
