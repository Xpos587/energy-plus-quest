import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { RotateCcw, ZoomIn, MousePointer2 } from "lucide-react";
import { carrierFacts, mapCarrierIds } from "../game/carrierFacts";
import { carrierFrame } from "../game/carrierTracking";
import type { CarrierId } from "../game/types";
import styles from "./IllustratedCityMap.module.css";
import { imageAsset } from "../game/imageAssets";
import { constrainedConnection, observedSlowTransfer } from "../game/network";
import { useCityMapZoom } from "./useCityMapZoom";
import { startCityVideoLoop } from "./cityVideoLoop";

const asset = (name: string) =>
  `${import.meta.env.BASE_URL}scene1-live/separated-routes/${name}?v=23`;
const videoSources = {
  mobile: asset("city-motion-mobile.mp4"),
  tablet: asset("city-motion-tablet.mp4"),
  desktop: asset("city-motion-desktop.mp4"),
};
const poster = imageAsset("scene1-live/separated-routes/city-poster.webp");

// The tracking points sit on the roofs. Align each transparent hit area with
// the vehicle's direction so its trailer remains clickable through turns.
function truckAngle(time: number, index: number) {
  const [x, y] = carrierFrame(time)[index];
  const [nextX, nextY] = carrierFrame(time + 8 / 24)[index];
  return Math.atan2(nextY - y, (nextX - x) * 1.44);
}

export function IllustratedCityMap({
  onSelect,
  selectedId,
  interactive = true,
}: {
  onSelect?: (id: CarrierId) => void;
  selectedId?: CarrierId;
  interactive?: boolean;
}) {
  const description = useId();
  const video = useRef<HTMLVideoElement>(null);
  const standbyVideo = useRef<HTMLVideoElement>(null);
  const viewport = useRef<HTMLElement>(null);
  const navigation = useCityMapZoom(viewport, onSelect, { enabled: interactive });
  const camera = useRef(navigation);
  camera.current = navigation;
  const selected = useRef(selectedId);
  selected.current = selectedId;
  const displayedTime = useRef(0);
  const targets = useRef<(HTMLButtonElement | null)[]>([]);
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);
  const [reduced, setReduced] = useState(false);
  const [videoSource, setVideoSource] = useState<string>();
  const [videoReady, setVideoReady] = useState(false);
  const [hintStage, setHintStage] = useState(0);
  const showZoomHint = hintStage === 0;
  const [touch, setTouch] = useState(false);
  useEffect(() => { setTouch(matchMedia("(pointer: coarse)").matches); }, []);

  useEffect(() => {
    const element = viewport.current;
    const dismiss = () => setHintStage(stage => Math.min(2, stage + 1));
    element?.addEventListener("scene-map-gesture-start", dismiss);
    return () => element?.removeEventListener("scene-map-gesture-start", dismiss);
  }, []);

  useLayoutEffect(() => {
    if (selectedId) setHintStage(2);
    const index = mapCarrierIds.findIndex(id => id === selectedId);
    const position = index >= 0 ? carrierFrame(displayedTime.current)[index] : undefined;
    camera.current.inspect(position ? selectedId : undefined, position ? { x: position[0], y: position[1] } : undefined);
  }, [selectedId]);

  useEffect(() => {
    const ready = () => {
      if ([...document.images].every((image) => image.complete)) {
        const rect = viewport.current?.getBoundingClientRect();
        if (!rect?.width || !rect.height) return;
        const limited = constrainedConnection() || observedSlowTransfer();
        const saveData = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection?.saveData === true;
        const coverWidth = Math.max(rect.width, rect.height * 1.44);
        // Desktop gets the detailed stream before playback; smaller viewports
        // account for the covered map width and display pixel density.
        // Keep the selected stream: replacing src during a gesture resets the
        // decoder and can jump the vehicles even when currentTime is restored.
        // A slow individual request (including a cold local load) must not
        // downgrade desktop detail. Only an explicit data-saving preference does.
        const displayWidth = rect.width >= 1100
          ? (saveData ? 2560 : 3600)
          : coverWidth * (limited ? 1 : Math.max(1, window.devicePixelRatio || 1));
        // Keep the tallest, highest-resolution decode off small touch devices.
        const requiredWidth = rect.width < 1100 && matchMedia("(pointer: coarse)").matches
          ? Math.min(displayWidth, 2560)
          : displayWidth;
        const variant = requiredWidth <= 1920 ? "mobile" : requiredWidth <= 2560 ? "tablet" : "desktop";
        setVideoSource(current => current ?? videoSources[variant]);
        setVideoReady(true);
      }
    };
    document.addEventListener("load", ready, true);
    document.addEventListener("error", ready, true);
    window.addEventListener("resize", ready);
    ready();
    return () => {
      document.removeEventListener("load", ready, true);
      document.removeEventListener("error", ready, true);
      window.removeEventListener("resize", ready);
    };
  }, []);

  useEffect(() => {
    const preference = matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => setReduced(preference.matches);
    sync();
    preference.addEventListener("change", sync);
    return () => preference.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    const element = video.current;
    const paint = (time: number) => {
      const discontinuity = time < displayedTime.current || time - displayedTime.current > .5;
      displayedTime.current = time;
      carrierFrame(time).forEach(([x, y], index) => {
        const target = targets.current[index];
        if (target) {
          target.style.left = `${x * 100}%`;
          target.style.top = `${y * 100}%`;
          target.style.transform = `translate(-50%, -50%) rotate(${truckAngle(time, index)}rad)`;
        }
        if (mapCarrierIds[index] === selected.current) camera.current.track({ x, y }, discontinuity);
      });
    };
    if (!element || !standbyVideo.current || failed || reduced || !videoReady) {
      paint(0);
      return;
    }
    return startCityVideoLoop(element, standbyVideo.current, paint, () => setFailed(true), () => setPlaying(true));
  }, [failed, reduced, videoReady]);

  return (
    <div className={styles.root}>
      {interactive && hintStage < 2 && !selectedId && (
        <p key={hintStage} className={styles.zoomHint} data-map-zoom-hint>
          {showZoomHint ? <ZoomIn size={20} aria-hidden="true" /> : <MousePointer2 size={20} aria-hidden="true" />}
          <span>{showZoomHint ? (touch ? "Раздвиньте пальцы, чтобы приблизить" : "Прокрутите колёсико, чтобы приблизить") : "Перетащите карту или нажмите на фуру"}</span>
        </p>
      )}
      {interactive && navigation.isZoomed && (
        <button
          type="button"
          className={styles.reset}
          data-map-controls
          onClick={() => {
            navigation.reset();
            viewport.current?.focus({ preventScroll: true });
          }}
        >
          <RotateCcw size={18} aria-hidden="true" /> Вернуть карту
        </button>
      )}
      <section
        inert={!interactive}
        ref={viewport}
        className={styles.map}
        aria-label="Карта доступных перевозчиков"
        aria-describedby={description}
        data-mode="live"
        data-renderer="painted-video"
        data-map-viewport
        data-map-scale={navigation.scale}
        // biome-ignore lint/a11y/noNoninteractiveTabindex: Keyboard zoom and arrow navigation expose the entire city.
        tabIndex={interactive ? 0 : -1}
      >
        <div
          className={styles.surface}
          style={navigation.style}
          data-map-surface
          data-motion-reason={failed ? "playback-error" : reduced ? "reduced-motion" : !videoReady ? "images-loading" : "ready"}
          data-motion-state={
            playing && !failed && !reduced && videoReady
              ? "playing"
              : "paused"
          }
        >
          {failed || reduced || !videoReady ? (
            <img
              className={styles.video}
              src={poster}
              alt="Город, склад и четыре грузовика"
              data-city-poster
            />
          ) : (
            <>{[video, standbyVideo].map((ref, index) => <video
              key={index}
              ref={ref}
              src={videoSource}
              className={styles.video}
              data-city-video={index === 0 ? "" : undefined}
              style={{ opacity: index === 0 ? 1 : 0 }}
              aria-label="Город, склад и четыре движущихся грузовика"
              poster={poster}
              muted
              playsInline
              loop
              preload="auto"
              disablePictureInPicture
              onPlaying={(event) => {
                if (event.currentTarget.hasAttribute("data-city-video")) setPlaying(true);
              }}
              onPause={(event) => {
                if (event.currentTarget.hasAttribute("data-city-video")) setPlaying(false);
              }}
            />)}</>
          )}
          {onSelect &&
            mapCarrierIds.map((id, index) => (
              <button
                ref={(element) => {
                  targets.current[index] = element;
                }}
                type="button"
                key={id}
                className={styles.target}
                data-carrier-choice={id}
                style={{
                  left: `${carrierFrame(0)[index][0] * 100}%`,
                  top: `${carrierFrame(0)[index][1] * 100}%`,
                  transform: `translate(-50%, -50%) rotate(${truckAngle(0, index)}rad)`,
                }}
                aria-label={`Рассмотреть: ${carrierFacts[id].label}`}
                aria-pressed={selectedId === id}
                onClick={() => {
                  onSelect(id);
                }}
              />
            ))}
        </div>
        <p id={description} className={styles.hidden}>
          Раздвигайте и сводите пальцы, чтобы менять масштаб карты. На компьютере
          используйте колёсико мыши или жест масштабирования на тачпаде.
          Перемещайте карту пальцем или перетаскивайте её, зажав кнопку мыши.
          Нажмите на фуру, чтобы рассмотреть её. С клавиатуры: плюс и минус меняют
          масштаб, стрелки перемещают карту, Home возвращает начальный вид.
        </p>
      </section>
    </div>
  );
}
