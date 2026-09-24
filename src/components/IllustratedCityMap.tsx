import { useEffect, useId, useRef, useState } from "react";
import styles from "./IllustratedCityMap.module.css";

const asset = (name: string) =>
  `${import.meta.env.BASE_URL}scene1-live/separated-routes/${name}`;
const poster = asset("city-poster.webp");

export function IllustratedCityMap() {
  const description = useId();
  const video = useRef<HTMLVideoElement>(null);
  const [blocked, setBlocked] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const element = video.current;
    if (!element || failed) return;
    let disposed = false;
    const sync = () => {
      if (document.hidden) element.pause();
      else {
        void element.play().catch((error: unknown) => {
          if (
            !disposed &&
            !document.hidden &&
            !(error instanceof DOMException && error.name === "AbortError")
          )
            setBlocked(true);
        });
      }
    };
    sync();
    document.addEventListener("visibilitychange", sync);
    return () => {
      disposed = true;
      element.pause();
      document.removeEventListener("visibilitychange", sync);
    };
  }, [failed]);

  return (
    <>
      <section
        className={styles.map}
        aria-label="Карта доступных перевозчиков"
        aria-describedby={description}
        data-mode="live"
        data-renderer="painted-video"
        // biome-ignore lint/a11y/noNoninteractiveTabindex: Focus enables native arrow-key scrolling of the map.
        tabIndex={0}
        onPointerDown={(event) => {
          if (
            event.pointerType !== "mouse" ||
            event.button !== 0 ||
            (event.target as Element).closest("button")
          )
            return;
          event.currentTarget.setPointerCapture(event.pointerId);
          event.currentTarget.focus({ preventScroll: true });
        }}
        onPointerMove={(event) => {
          if (
            event.pointerType !== "mouse" ||
            !event.currentTarget.hasPointerCapture(event.pointerId)
          )
            return;
          event.currentTarget.scrollBy(-event.movementX, -event.movementY);
        }}
        onPointerUp={(event) => {
          if (event.currentTarget.hasPointerCapture(event.pointerId))
            event.currentTarget.releasePointerCapture(event.pointerId);
        }}
      >
        <div
          className={styles.surface}
          data-map-surface
          data-motion-state={playing && !failed ? "playing" : "paused"}
        >
          {failed ? (
            <img
              className={styles.video}
              src={poster}
              alt="Город, склад и четыре грузовика"
              data-city-poster
            />
          ) : (
            <video
              ref={video}
              className={styles.video}
              data-city-video
              aria-label="Город, склад и четыре движущихся грузовика"
              poster={poster}
              autoPlay
              muted
              playsInline
              loop
              preload="auto"
              disablePictureInPicture
              onPlaying={() => {
                setPlaying(true);
                setBlocked(false);
              }}
              onPause={() => setPlaying(false)}
              onError={(event) => {
                // React also bubbles errors from sources skipped by their media query.
                const source = event.target;
                if (
                  source instanceof HTMLSourceElement &&
                  source.media &&
                  !matchMedia(source.media).matches
                )
                  return;
                setFailed(true);
              }}
            >
              <source
                media="(max-width: 640px) and (max-height: 560px)"
                src={asset("city-motion-mobile.mp4")}
                type="video/mp4"
              />
              <source
                media="(max-width: 1100px) and (max-height: 850px)"
                src={asset("city-motion-tablet.mp4")}
                type="video/mp4"
              />
              <source src={asset("city-motion-desktop.mp4")} type="video/mp4" />
            </video>
          )}
        </div>
        <p id={description} className={styles.hidden}>
          Четыре грузовика движутся по городу. Склад находится слева. Рядом с
          ним ездит №2, фуры №1, №3 и №4 — в дальнем районе. Кнопка «Рассмотреть
          карту» открывает крупный вид: перемещайте его пальцем, мышью или
          стрелками. Выберите перевозчика кнопками №1, №2, №3, №4 под картой или
          рядом с ней либо подберите транспорт автоматически.
        </p>
      </section>
      {blocked && !failed && (
        <button
          className={styles.retry}
          type="button"
          onClick={() => {
            void video.current?.play().catch(() => setBlocked(true));
          }}
        >
          Запустить движение
        </button>
      )}
      {failed && (
        <p className={styles.status} role="status">
          Не удалось загрузить видео. Выберите транспорт кнопками.
        </p>
      )}
    </>
  );
}
