import mapDesktop from "../../design/scene-01/assets/feedback-v12/production/map/carrier-desktop.webp";
import mapMobile from "../../design/scene-01/assets/feedback-v12/production/map/carrier-mobile.webp";
import styles from "../App.module.css";
import type { CarrierId } from "../game/types";

type CityMapProps = {
  onSelect?: (carrier: CarrierId) => void;
  selected?: CarrierId;
  mode?: "soft" | "live" | "result";
};

const truckMarkers = [
  { id: "truck-1", number: 1, outcome: "old" },
  { id: "truck-2", number: 2, outcome: "near" },
  { id: "truck-3", number: 3, outcome: "crew" },
  { id: "truck-4", number: 4, outcome: "old" },
] as const satisfies ReadonlyArray<{
  id: string;
  number: number;
  outcome: CarrierId;
}>;

export function CityMap({ onSelect, selected, mode = "soft" }: CityMapProps) {
  return (
    <section
      aria-label={onSelect ? "Карта доступных перевозчиков" : "Карта маршрута"}
      className={styles.cityMap}
      data-mode={mode}
      data-selected={selected}
    >
      <div className={onSelect ? styles.liveMapSurface : undefined}>
        <picture className={styles.mapPicture}>
          <source
            height="1688"
            media="(max-width: 760px)"
            srcSet={mapMobile}
            type="image/webp"
            width="780"
          />
          <img
            alt=""
            aria-hidden="true"
            className={styles.mapImage}
            data-art-version="feedback-v12"
            data-map-contract="warehouse-roads-four-trucks"
            data-map-media="generated"
            fetchPriority={onSelect ? "high" : undefined}
            height="1800"
            loading={onSelect ? "eager" : "lazy"}
            src={mapDesktop}
            width="2880"
          />
        </picture>
        <div aria-hidden="true" className={styles.mapShade} />
        {onSelect &&
          truckMarkers.map((truck) => (
            <button
              aria-label={`Машина №${truck.number}`}
              className={styles.mapVehicle}
              data-carrier={truck.outcome}
              data-carrier-hotspot="true"
              data-truck={truck.id}
              key={truck.id}
              onClick={() => onSelect(truck.outcome)}
              type="button"
            >
              <span aria-hidden="true" data-truck-number="true">
                {truck.number}
              </span>
            </button>
          ))}
      </div>
    </section>
  );
}
