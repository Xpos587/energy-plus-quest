import mapDesktop from "../../design/scene-01/assets/current/map/carrier-desktop.webp";
import mapMobile from "../../design/scene-01/assets/current/map/carrier-mobile.webp";
import styles from "../App.module.css";

export function CityMap({ mode = "soft" }: { mode?: "soft" | "live" }) {
  const live = mode === "live";
  return (
    <section
      aria-label={live ? "Карта доступных перевозчиков" : "Карта маршрута"}
      className={styles.cityMap}
      data-mode={mode}
    >
      <div className={live ? styles.liveMapSurface : undefined}>
        <div className={styles.mapPicture}>
          {([mapMobile, mapDesktop] as const).map((source, index) => (
            <img
              alt=""
              aria-hidden="true"
              className={styles.mapImage}
              data-art-version="current"
              data-map-contract="warehouse-roads-four-trucks"
              data-map-media="generated"
              data-format={index === 0 ? "mobile" : "desktop"}
              fetchPriority={live ? "high" : undefined}
              loading={live ? "eager" : "lazy"}
              key={source}
              src={source}
            />
          ))}
        </div>
        <div aria-hidden="true" className={styles.mapShade} />
        {live && (
          <>
            {[1, 2, 3, 4].map((number) => (
              <span
                className={styles.truckNumber}
                data-truck={`truck-${number}`}
                data-truck-number
                key={number}
              >
                {number}
              </span>
            ))}
            <span className={styles.pickupLabel}>Забрать груз</span>
          </>
        )}
      </div>
    </section>
  );
}
