import { detailImageAsset, imageAsset } from "../../game/imageAssets";
import { type CSSProperties, useEffect, useLayoutEffect, useRef, useState } from "react";
import { parcelNames } from "../names";
import type { SceneArtProps } from "../types";
import {
  CargoBay,
  cargoSpaces,
  compactTerminal,
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
  // The result artwork is fetched while the card is read. Confirming keeps the
  // current truck on screen until that image decodes, so no loader flashes.
  const key = `${context.parcel}:${selectedId}`;
  const wantedOutcome = selectedId ? compactResultArtwork[key] : undefined;
  const [decodedOutcome, setDecodedOutcome] = useState(showResult ? wantedOutcome : undefined);
  useEffect(() => {
    if (!wantedOutcome) return;
    let live = true;
    const image = new Image();
    image.src = detailImageAsset(wantedOutcome);
    const done = () => live && setDecodedOutcome(wantedOutcome);
    // A failed decode still hands over to CargoBay, which owns fallback and retry.
    (image.decode?.() ?? Promise.resolve()).then(done, done);
    return () => { live = false; };
  }, [wantedOutcome]);
  const resultReady = !wantedOutcome || decodedOutcome === wantedOutcome;
  const frame = showResult && resultReady ? compactResultFrames[key] : undefined;
  const cameraDetail = !!frame;
  const outcomeImage = showResult && resultReady ? wantedOutcome : undefined;
  const [measuredHeight, setCanvasHeight] = useState(520);
  // A result never zooms: a taller stage extends the background around the whole truck.
  const canvasHeight = frame
    ? Math.max(frame.height ?? 874, measuredHeight)
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
    ? (canvasHeight - (frame?.height ?? 874)) / 2
    : outcomeImage
      ? -Math.max(0, Math.min(274, 874 - canvasHeight - 36))
      : (canvasHeight - (portrait ? 874 : 520)) / 2;
  const layoutProfile = frame?.unloaded ? "unloaded" : portrait ? "portrait" : "wide";
  const regions = layoutRegions(layout, layoutProfile);
  const markersVisible = showResult || !!onSelect || !!selectedId;
  // Compact is a fifth object in the same world, marked like the four places.
  const terminal = markersVisible && !showResult
    ? compactTerminal[portrait ? "portrait" : "wide"]
    : undefined;
  const choiceRegions = terminal
    ? [...regions, { ...terminal, id: "auto", number: 5 }]
    : regions;
  const activeSpaces = markersVisible
    ? choiceRegions.map((space) => ({ ...space, y: space.y + offsetY }))
    : [];
  const inspectedSpace = !showResult
    ? choiceRegions.find((space) => space.id === selectedId)
    : undefined;
  const manual = /^place-([1-4])$/.exec(selectedId ?? "");
  // Compact's pick stays hidden until the choice is confirmed.
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
          regions={markersVisible && !showResult ? regions : []}
          terminal={terminal}
          autoActive={selectedId === "auto"}
          offsetY={offsetY}
        />
        {activeSpaces.map((space, index) => {
          const badge = layout.profiles[layoutProfile][index]?.badge ??
            { x: space.x, y: space.y - offsetY, size: 24 };
          return (
          <button
            key={space.id}
            type="button"
            className={styles.marker}
            data-hotspot={space.id}
            data-focused={focused === space.id}
            data-choice-id={space.id}
            aria-label={`${options[index].label}. ${options[index].accessibleDescription}`}
            aria-pressed={space.id === "auto" ? selectedId === "auto" : placement === space.number}
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
            onFocus={(event) => { if (event.currentTarget.matches(":focus-visible")) setFocused(space.id); }}
            onBlur={() => setFocused(undefined)}
            onPointerEnter={() => setFocused(space.id)}
            onPointerLeave={() => setFocused(undefined)}
            onClick={() => onSelect?.(space.id)}
          >
            <span className={styles.number} data-layout-badge={space.id} style={{
              left: `calc(${badge.x - space.x} / 1040 * 100cqw)`,
              // The stand's badge sits by its base so phones still show the screen.
              top: space.id === "auto" ? `calc(100% - ${badge.size}px)` : `calc(${badge.y - (space.y - offsetY)} / 1040 * 100cqw)`,
              // Move only the result badge, not the choice hit target or other gifts.
              transform: showResult && context.parcel === "socks" && space.id === "place-3"
                ? "translateX(calc(-100% - 8px))" : undefined,
              width: badge.size,
              height: badge.size,
              fontSize: badge.size * 15 / 24,
            }}>{space.number}</span>
            {space.id === "auto" && (
              // Plain words: the player meets the Compact brand only in the card and result.
              <span className={styles.terminalCaption}>
                <b>Подобрать автоматически</b>
              </span>
            )}
          </button>
          );
        })}
      </div>
    </figure>
  );
}
