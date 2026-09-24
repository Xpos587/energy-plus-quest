import styles from "../App.module.css";
import { IllustratedCityMap } from "./IllustratedCityMap";

export function CityMap({ mode = "soft" }: { mode?: "soft" | "live" }) {
  if (mode === "live") return <IllustratedCityMap />;
  return (
    <section
      aria-label="Карта маршрута"
      className={styles.cityMap}
      data-mode="soft"
    >
      <div>
        <div className={styles.mapPicture}>
          <img
            alt=""
            aria-hidden="true"
            className={styles.mapImage}
            src={`${import.meta.env.BASE_URL}scene1-live/separated-routes/city-poster.webp`}
          />
        </div>
      </div>
    </section>
  );
}
