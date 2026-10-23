import styles from "../App.module.css";
import type { CarrierId } from "../game/types";
import { IllustratedCityMap } from "./IllustratedCityMap";
import { imageAsset } from "../game/imageAssets";

export function CityMap({
  mode = "soft",
  onSelect,
  selectedId,
  interactive = true,
}: {
  mode?: "soft" | "live";
  onSelect?: (id: CarrierId) => void;
  selectedId?: CarrierId;
  interactive?: boolean;
}) {
  if (mode === "live")
    return <IllustratedCityMap interactive={interactive} onSelect={onSelect} selectedId={selectedId} />;
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
            src={imageAsset("scene1-live/separated-routes/city-poster.webp")}
            decoding="async"
          />
        </div>
      </div>
    </section>
  );
}
