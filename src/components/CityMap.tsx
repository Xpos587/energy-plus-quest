import {
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { createPortal } from "react-dom";
import mapDesktopVideo from "../../design/scene-01/assets/current/map/carrier-desktop.mp4";
import mapDesktop from "../../design/scene-01/assets/current/map/carrier-desktop.webp";
import mapMobileVideo from "../../design/scene-01/assets/current/map/carrier-mobile.mp4";
import mapMobile from "../../design/scene-01/assets/current/map/carrier-mobile.webp";
import styles from "../App.module.css";
import { MapInspection } from "./MapInspection";

type MapFormat = "desktop" | "mobile";

const mapFormats = {
  desktop: { poster: mapDesktop, video: mapDesktopVideo },
  mobile: { poster: mapMobile, video: mapMobileVideo },
} as const;

const mapDescription =
  "№1 и №4: старые с выхлопом, дальние маршруты; №2: у склада, очень медленно; №3: новая фура, 2 водителя, внешний маршрут.";

export function CityMap({
  mode = "soft",
  controlsHost,
}: {
  mode?: "soft" | "live";
  controlsHost?: HTMLElement | null;
}) {
  const live = mode === "live";
  const descriptionId = useId();
  const mapRef = useRef<HTMLElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const pausedRef = useRef(false);
  const [format, setFormat] = useState<MapFormat | null>(null);
  const [motionReady, setMotionReady] = useState(false);
  const [reducedMotion, setReducedMotion] = useState<boolean | null>(null);
  const [paused, setPaused] = useState(false);
  const [motionBlocked, setMotionBlocked] = useState(false);
  const [motionFailed, setMotionFailed] = useState(false);
  const [posterFailed, setPosterFailed] = useState(false);

  useLayoutEffect(() => {
    const surface = mapRef.current;
    if (!surface) return;

    const updateFormat = () => {
      const { width, height } = surface.getBoundingClientRect();
      if (width && height)
        setFormat(width / height <= 1.607143 ? "mobile" : "desktop");
      setMotionReady(true);
    };

    updateFormat();
    const observer = new ResizeObserver(updateFormat);
    observer.observe(surface);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReducedMotion(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  const shouldShowVideo =
    live &&
    motionReady &&
    format !== null &&
    reducedMotion === false &&
    !motionFailed;

  const attemptPlay = useCallback(
    (video: HTMLVideoElement, autoplay: boolean) => {
      const source = video.getAttribute("src");
      void video.play().then(
        () => {
          if (
            videoRef.current === video &&
            video.getAttribute("src") === source
          ) {
            pausedRef.current = false;
            setPaused(false);
            setMotionBlocked(false);
          }
        },
        (error: unknown) => {
          // A resize/unmount interrupts the obsolete media request; never poison its replacement.
          if (
            videoRef.current !== video ||
            video.getAttribute("src") !== source ||
            (error instanceof DOMException && error.name === "AbortError")
          )
            return;
          if (autoplay) setMotionBlocked(true);
          else setMotionBlocked(true);
        },
      );
    },
    [],
  );

  useEffect(() => {
    const onVisibilityChange = () => {
      const video = videoRef.current;
      if (!video) return;
      if (document.hidden) video.pause();
      else if (!pausedRef.current && !motionBlocked) attemptPlay(video, true);
    };
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () =>
      document.removeEventListener("visibilitychange", onVisibilityChange);
  }, [attemptPlay, motionBlocked]);

  const setVideo = useCallback((element: HTMLVideoElement | null) => {
    const previous = videoRef.current;
    if (previous && previous !== element) previous.pause();
    videoRef.current = element;
  }, []);

  const toggleMotion = () => {
    const video = videoRef.current;
    if (!video) return;
    if (paused || motionBlocked) {
      pausedRef.current = false;
      attemptPlay(video, false);
      return;
    }
    video.pause();
    pausedRef.current = true;
    setPaused(true);
  };

  const activeFormat = format ?? "desktop";
  const media = mapFormats[activeFormat];
  const status = motionFailed
    ? `Анимация карты недоступна. ${mapDescription}`
    : reducedMotion
      ? `Движение остановлено по настройке устройства. ${mapDescription}`
      : motionBlocked
        ? `Движение ожидает запуска. ${mapDescription}`
        : mapDescription;

  return (
    <section
      aria-label={live ? "Карта доступных перевозчиков" : "Карта маршрута"}
      className={styles.cityMap}
      aria-describedby={live ? descriptionId : undefined}
      data-mode={mode}
      ref={mapRef}
    >
      <div className={live ? styles.liveMapSurface : undefined}>
        <div className={styles.mapPicture}>
          {shouldShowVideo ? (
            <>
              <video
                aria-label={`Анимированная карта, формат ${activeFormat}`}
                className={styles.mapImage}
                data-art-version="r23"
                data-format={activeFormat}
                data-map-contract="warehouse-roads-four-trucks"
                data-map-media="authored-video"
                disablePictureInPicture
                loop
                muted
                onCanPlay={(event) => {
                  if (!pausedRef.current && !document.hidden && !motionBlocked)
                    attemptPlay(event.currentTarget, true);
                }}
                onError={() => setMotionFailed(true)}
                playsInline
                poster={media.poster}
                preload="metadata"
                ref={setVideo}
                src={media.video}
              />
              {motionBlocked &&
                (posterFailed ? (
                  <div
                    aria-hidden="true"
                    className={`${styles.mapImage} ${styles.mapFallback}`}
                    data-map-media="fallback"
                  />
                ) : (
                  <img
                    alt=""
                    aria-hidden="true"
                    className={styles.mapImage}
                    data-map-media="poster"
                    onError={() => setPosterFailed(true)}
                    src={media.poster}
                  />
                ))}
            </>
          ) : posterFailed ? (
            <div
              aria-hidden="true"
              className={`${styles.mapImage} ${styles.mapFallback}`}
              data-map-media="fallback"
            />
          ) : (
            <img
              alt="Карта города с четырьмя вариантами перевозчиков."
              className={styles.mapImage}
              data-art-version="r23"
              data-format={activeFormat}
              data-map-contract="warehouse-roads-four-trucks"
              data-map-media="poster"
              fetchPriority={live ? "high" : undefined}
              onError={() => setPosterFailed(true)}
              src={media.poster}
            />
          )}
        </div>
        <div aria-hidden="true" className={styles.mapShade} />
        {live && (
          <MapInspection
            format={activeFormat}
            video={videoRef}
            playing={shouldShowVideo && !motionBlocked}
          />
        )}
        {live && (
          <span className={styles.pickupLabel} data-pickup-label>
            Склад
          </span>
        )}
      </div>
      {live &&
        controlsHost &&
        createPortal(
          <>
            {shouldShowVideo && (
              <button
                aria-pressed={paused}
                className={styles.motionToggle}
                onClick={toggleMotion}
                type="button"
              >
                <svg
                  aria-hidden="true"
                  viewBox="0 0 24 24"
                  className={styles.motionIcon}
                >
                  <path
                    d={
                      paused || motionBlocked
                        ? "M7 4v16l14-8z"
                        : "M6 4h4v16H6zM14 4h4v16h-4z"
                    }
                    fill="currentColor"
                  />
                </svg>
                <span>
                  {paused
                    ? "Продолжить движение"
                    : motionBlocked
                      ? "Запустить движение"
                      : "Приостановить движение"}
                </span>
              </button>
            )}
            <p
              aria-live="polite"
              className={
                paused || reducedMotion || motionFailed || motionBlocked
                  ? styles.motionDescription
                  : styles.motionDescriptionHidden
              }
              id={descriptionId}
              data-visually-hidden={
                !(paused || reducedMotion || motionFailed || motionBlocked)
              }
              data-motion-description
            >
              {status}
            </p>
          </>,
          controlsHost,
        )}
    </section>
  );
}
